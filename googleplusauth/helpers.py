# -*- coding: utf-8 -*-

"""WebHelpers used in tgapp-googlePlusAuth."""
#  For more scope: https://developers.google.com/oauthplayground/

#from webhelpers import date, feedgenerator, html, number, misc, text
from urllib import quote_plus
from markupsafe import Markup
from tg import request


def bold(text):
    return Markup('<strong>%s</strong>' % text)


def load_js_sdk():
    return '''
    <script type="text/javascript">
      (function() {
       var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
       po.src = 'https://apis.google.com/js/client:plusone.js';
       var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
     })();
    </script>'''


def login_callback(request, remember):
    return '''
    <script type="text/javascript">
        function signinCallback(authResult) {
        console.log("signinCallback");
          if (authResult['access_token']) {
            // Autorizzazione riuscita
            // Nascondi il pulsante di accesso ora che l'utente e autorizzato. Ad esempio:
            document.getElementById('signinButton').setAttribute('style', 'display: none');
            console.log(authResult);
            var remember = "%(remember)s";
            var loginUrl = "/googleplusauth/login?token="+ authResult['id_token'] +"&came_from=%(came_from)s";
            console.log(loginUrl);
            if (remember){
                loginUrl += '&remember=' + remember;
            }
            window.location = loginUrl;

          } else if (authResult['error']) {
            // Si e verificato un errore.
            // Possibili codici di errore:
            //   "access_denied" - L'utente ha negato l'accesso alla tua app
            //   "immediate_failed" - Impossibile eseguire l'accesso automatico dell'utente
            console.log('There was an error: ' + authResult['error']);
          }
        }
    </script>''' % dict(came_from=quote_plus(request.url), remember=remember)


def login_button(client_id, scope=None, data_button='', data_cookiepolicy='single_host_origin', remember='', **kwargs):
    #  https://www.googleapis.com/auth/plus.login
    default_scope = "https://www.googleapis.com/auth/userinfo.email"
    if not scope:
        scope = default_scope
    else:
        scope += " "+default_scope
    html = '''
    <span id="signinButton">
      <span
        data-scope="%(scope)s"
        class="g-signin"
        data-clientid="%(client_id)s"
        data-cookiepolicy="%(data_cookiepolicy)s"
        data-callback="signinCallback"

        %(data_button)s

        >
      </span>
    </span>''' % dict(client_id=client_id, data_cookiepolicy=data_cookiepolicy, scope=scope, data_button=data_button)
    #  data-width="iconOnly"
    script = load_js_sdk() + login_callback(request, remember)

    return Markup(html + script)