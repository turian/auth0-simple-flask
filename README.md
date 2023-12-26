# auth0-simple-flask

Simple demonstration of auth0 authentication with a Flask app.

```
pip install python-dotenv
```

Copy `.env.tmpl` to `.env`

Configure auth0. Allowed Callback URLs:
```
http://localhost:8863/callback
```
Allowed Logout URLs:
```
http://localhost:8863/
```


```
flask run --port=8863
```

Visit: `https://localhost:8863`
