from flask import current_app, redirect
from flask_dance.contrib.google import make_google_blueprint, google
from app.core.auth.service import upsert_user, create_jwt_for_user


def init_oauth(app):
    bp = make_google_blueprint(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=['openid','email','profile'],
    )
    app.register_blueprint(bp, url_prefix='/login')

    @bp.route('/authorized')
    def auth_cb():
        resp = google.get('/oauth2/v2/userinfo')
        resp.raise_for_status()
        user = upsert_user(app.extensions['db'].session, resp.json())
        token = create_jwt_for_user(user)
        return redirect(f"{app.config['FRONTEND_URL']}?token={token}")
