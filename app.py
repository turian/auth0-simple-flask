import logging
import os

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, redirect, session, url_for
from six.moves.urllib.parse import urlencode

logging.basicConfig(level=logging.DEBUG)


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_APP_SECRET_KEY")

app.config["SESSION_TYPE"] = "filesystem"

oauth = OAuth(app)
auth0 = oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    api_base_url=os.getenv("AUTH0_BASE_URL"),
    access_token_url=os.getenv("AUTH0_BASE_URL") + "/oauth/token",
    authorize_url=os.getenv("AUTH0_BASE_URL") + "/authorize",
    jwks_uri=os.getenv("AUTH0_BASE_URL") + "/.well-known/jwks.json",
    client_kwargs={
        "scope": "openid profile email",
    },
)


@app.route("/login")
def login():
    logging.debug("Initiating login process")
    redirect_uri = "http://localhost:8863/callback"
    logging.debug(f"Redirect URI: {redirect_uri}")
    return auth0.authorize_redirect(redirect_uri=redirect_uri)


@app.route("/callback")
def callback_handling():
    logging.debug("Handling callback")
    try:
        token = auth0.authorize_access_token()
        logging.debug(f"Token: {token}")
        resp = auth0.get("userinfo")
        userinfo = resp.json()
        session["jwt_payload"] = userinfo
        logging.debug(f"userinfo: {userinfo}")
        session["profile"] = {
            "user_id": userinfo["sub"],
            "name": userinfo["name"],
            "picture": userinfo["picture"],
            "email": userinfo["email"],
            "email_verified": userinfo["email_verified"],
        }
        return redirect("/dashboard")
    except Exception as e:
        logging.error("Error in callback handling", exc_info=True)
        return str(e)


@app.route("/dashboard")
def dashboard():
    return (
        "Your email: "
        + session["profile"].get("name")
        + f'<br><img src="{session["profile"].get("picture")}">'
        + '<br><a href="/logout">Logout</a>'
    )


@app.route("/logout")
def logout():
    session.clear()
    params = {
        "returnTo": url_for("home", _external=True),
        "client_id": os.getenv("AUTH0_CLIENT_ID"),
    }
    return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))


@app.route("/")
def home():
    if "profile" in session:
        logging.debug(os.environ)
        # if 'jwt_payload' in session:
        # User is authenticated, redirect to /dashboard or display a message
        return redirect("/dashboard")
    else:
        # User is not authenticated, display the home page or initiate the Auth0 login process
        # return 'Welcome to the Home Page'
        return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, port=8863)
