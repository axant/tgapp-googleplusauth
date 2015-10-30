# -*- coding: utf-8 -*-
"""Main Controller"""
from tg import TGController, config, hooks
from tg import expose, flash, redirect
from tg.i18n import ugettext as _
import json
from googleplusauth import model
from googleplusauth.lib.utils import redirect_on_fail, login_user, has_googletoken_expired, add_param_to_query_string
from tgext.pluggable import app_model
from datetime import datetime
from urllib import urlopen


class RootController(TGController):
    @expose('googleplusauth.templates.index')
    def index(self):
        user = model.provider.query(app_model.User, filters=dict(email_address="manager@somedomain.com"))[1][0]
        flash(_("Hello World!"))
        return dict(sample=user)

    @expose()
    def login(self, token, came_from=None, remember=None):
        gplusanswer = urlopen('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=%s' % token)
        google_id = None
        google_token_expiry = None
        google_email = None
        answer = None

        try:
            answer = json.loads(gplusanswer.read())

            if answer['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                flash(_("Login error"), "error")
                return redirect_on_fail()
            if not answer['sub']:
                flash(_("Login error"), "error")
                return redirect_on_fail()

            google_id = answer['sub']
            google_token_expiry = datetime.fromtimestamp(int(answer['exp']))

        except Exception:
            flash(_('Fatal error while trying to contact Google'), 'error')
            return redirect_on_fail()
        finally:
            gplusanswer.close()

        ga_user = model.GoogleAuth.ga_user_by_google_id(google_id)

        if ga_user:
            #If the user already exists, just login him.
            login_user(ga_user.user.user_name, remember)

            if has_googletoken_expired(ga_user):
                ga_user.access_token = token
                ga_user.access_token_expiry = google_token_expiry

            hooks.notify('googleplusauth.on_login', args=(answer, ga_user.user))
            redirect_to = add_param_to_query_string(config.sa_auth['post_login_url'], 'came_from', came_from)

            return redirect(redirect_to)

        # User not present
        u = app_model.User(user_name='g+:%s' % google_id,
                           display_name=answer['email'],
                           email_address=answer['email'],
                           password=token)

        #  Create new user
        hooks.notify('googleplusauth.on_registration', args=(answer, u))

        #  Create new Google Plus Login User for store data
        gpl = model.GoogleAuth(
            user=u,
            google_id=google_id,
            registered=True,
            just_connected=True,
            access_token=token,
            access_token_expiry=google_token_expiry,
            profile_picture=answer['picture']
        )

        model.provider.add_user(u)

        #  Now login and redirect to request page
        login_user(u.user_name, remember)
        redirect_to = add_param_to_query_string(config.sa_auth['post_login_url'], 'came_from', came_from)

        return redirect(redirect_to)

    @expose()
    def login_error(self):
        flash(_("Login error"), "error")
        return redirect_on_fail()
