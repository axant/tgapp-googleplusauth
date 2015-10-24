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
    return '''<script src="https://apis.google.com/js/client:platform.js?onload=renderButton"></script>'''


def login_button(client_id, scope=None, data_button='', data_cookiepolicy='single_host_origin', remember='',
                 callback='', **kwargs):
    #  https://www.googleapis.com/auth/plus.login
    default_scope = "https://www.googleapis.com/auth/userinfo.email"
    if not scope:
        scope = default_scope
    else:
        scope += " "+default_scope
    html = '''
    <button class="btn btn-default" onclick="perform_google_login()" id="gConnect">Login Google</button>
    <script type="text/javascript">
    var auth2 = {};
    var helper = (function() {
      return {
        /**
         * Hides the sign in button and starts the post-authorization operations.
         *
         * @param {Object} authResult An Object which contains the access token and
         *   other authentication information.
         */
        onSignInCallback: function(authResult) {
          console.log("Auth Result:");

          if (authResult.isSignedIn.get()) {
            $('#gConnect').hide();
            helper.profile();
          } else if (authResult['error'] ||
              authResult.currentUser.get().getAuthResponse() == null) {
              // There was an error, which means the user is not signed in.
              console.log('There was an error: ' + authResult['error']);
              var loginUrl = "/googleplusauth/login_error";
              window.location = loginUrl;

              $('#gConnect').show();
          }
        },

        /**
         * Calls the OAuth2 endpoint to disconnect the app for the user.
         */
        disconnect: function() {
          // Revoke the access token.
          auth2.disconnect();
        },


        /**
         * Gets the currently signed in user's profile data.
         */

        profile: function(){
          var profile = auth2.currentUser.get().getBasicProfile();
          console.log('ID: ' + profile.getId());
          console.log('Name: ' + profile.getName());
          console.log('Image URL: ' + profile.getImageUrl());
          console.log('Email: ' + profile.getEmail());

          var token = auth2.currentUser.get().getAuthResponse().id_token;
          console.log(token);
          //send the token to server for validation
          var remember = "%(remember)s";
          var loginUrl = "/googleplusauth/login?token="+ token +"&came_from=%(came_from)s";
          console.log(loginUrl);
          if (remember){
              loginUrl += '&remember=' + remember;
          }
          window.location = loginUrl;
        }

      };
    })();


    /**
     * Handler for when the sign-in state changes.
     *
     * @param {boolean} isSignedIn The new signed in state.
     */
    var updateSignIn = function() {
      console.log('update sign in state');
      if (auth2.isSignedIn.get()) {
        console.log('signed in');
        helper.onSignInCallback(gapi.auth2.getAuthInstance());
      }else{
        console.log('signed out');
        helper.onSignInCallback(gapi.auth2.getAuthInstance());
      }
    }

    /**
     * This method sets up the sign-in listener after the  user click on the button.
     */
    var loaded = false;
    function perform_google_login() {
      console.log("Start Google Login");

      gapi.load('auth2', function() {
          gapi.auth2.init({
              client_id: '%(client_id)s',
              fetch_basic_profile: true,
              cookie_policy: '%(data_cookiepolicy)s',
              scope:'%(scope)s'}).then(
                function (){
                  console.log('init sdk');
                  auth2 = gapi.auth2.getAuthInstance();
                  auth2.isSignedIn.listen(updateSignIn);
                  auth2.then(updateSignIn());
                  loaded=true;
                  if(!auth2.isSignedIn.get())
                    {
                      console.log("sloggato");
                      auth2.signIn();
                    }
                });
      });
      if(loaded == true) {
        console.log("sdk already loaded. auth2: "+auth2);
        auth2.signIn();
      }
    }
    </script>
        ''' % dict(client_id=client_id, data_cookiepolicy=data_cookiepolicy, scope=scope, remember=remember, came_from=quote_plus(request.url))

    script = load_js_sdk()

    return Markup(html + script)