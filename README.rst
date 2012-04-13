###################
Django Easy Friends
###################

Django Easy Friends is a friendship tool for Django framework. It has features like sending invitations, friendship creation, blocking users, importing contacts from external services and auto suggesting friends based on imported contacts. It consist of two applications: **friends** and **friends.contrib.suggestions**.

*******************
friends application
*******************

Features
========
* Sending invitations
* Accepting and declining invitations
* Blocking users from sending invitations (TODO)
* Listing friends
* Listing friends of friend (optional)

Requirements
============
* `Django <https://www.djangoproject.com/>`_
* `django-notification <https://github.com/jtauber/django-notification>`_ (optional)

Installation
============
* Add to your ``INSTALLED_APPS`` and run syncdb::

    INSTALLED_APPS = (
        ...,
        'friends',
    )

* Add to your ``urlpatterns`` in projects ``urls.py`` file::

    urlpatterns = patterns('',
        ...
        url(r'^friends/', include('friends.urls')),
    )

* Overwrite ``friends/base.html`` template and insert ``{% block friends_title %}{% endblock %}`` into block where page title should be and ``{% block friends_content %}{% endblock %}`` into block where page content should be.

Configuration
=============
Availale settings:

* ``FRIENDS_USE_NOTIFICATION_APP`` (default: ``True``)
  By default ``notification`` app is used if it is enabled in ``INSTALLED_APPS``, if this setting is set to ``False`` ``notification`` app will not be used.
* ``SHOW_FRIENDS_OF_FRIEND`` (default: ``False``)
  Allow users to view list of friends of their friends.
* ``NOTIFY_ABOUT_NEW_FRIENDS_OF_FRIEND`` (default: ``False``)
  If ``notification`` app is enabled and ``FRIENDS_USE_NOTIFICATION_APP`` is set to ``True`` and this setting is set to ``True`` users will be notified when one of their friends have new friend.
* ``NOTIFY_ABOUT_FRIENDS_REMOVAL`` (default: ``False``)
  If ``notification`` app is enabled and ``FRIENDS_USE_NOTIFICATION_APP`` is set to ``True`` and this setting is set to ``True`` users will be notified when one of their friends removes them from friends.

Advanced usage
==============
If you want to take some actions when invitation or friendship is created or deleted then check sample signals usage in file ``friends/models.py``.

Credits
=======
This app is a fork of `django-friends <https://github.com/pinax/django-friends>`_ app.




***************************************
friends.contrib.suggestions application
***************************************

Features
========
* importing contacts from:

  * Facebook
  * Google
  * Yahoo
  * Twitter
  * LinkedIn

* creating friendship suggestions based on imported contacts

Requirements
============
* `httplib2 <http://code.google.com/p/httplib2/>`_ (``pip install httplib2``)
* `python-oauth2 <https://github.com/simplegeo/python-oauth2>`_ (``pip install -e git://github.com/simplegeo/python-oauth2.git#egg=python-oauth2``)
* `django-oauth-access <https://github.com/eldarion/django-oauth-access>`_ (``pip install -e git://github.com/eldarion/django-oauth-access.git#egg=django-oauth-access``)
* `gdata <http://code.google.com/p/gdata-python-client/>`_ (``pip install gdata``)
* `facebook-sdk <https://github.com/pythonforfacebook/facebook-sdk>`_ (``pip install -e git://github.com/pythonforfacebook/facebook-sdk.git#egg=facebook-sdk``)
* `python-twitter <http://code.google.com/p/python-twitter/>`_ (``pip install python-twitter``)
* `django-celery <http://ask.github.com/django-celery/>`_ (``pip install django-celery``) (optional but highly recommended)

Installation
============
* ``friends`` app must be installed already (read above)
* Add to your ``INSTALLED_APPS`` and run syncdb::

    INSTALLED_APPS = (
        ...,
        'friends.contrib.suggestions',
    )

* Add to your ``urlpatterns`` in projects ``urls.py`` file::

    urlpatterns = patterns('',
        ...
        url(r'^friends/suggestions/', include('friends.contrib.suggestions.urls')),
    )

Configuration
=============
Available settings:

* ``FRIENDS_SUGGESTIONS_IMPORT_RUNNER`` (default: ``friends.contrib.suggestions.backends.runners.SynchronousRunner``)
  This is class that is used for importing contacts. Default is synchronous runner but you should really use `Celery <http://celeryproject.org/>`_ (and `django-celery <http://ask.github.com/django-celery/>`_) so this setting should be set to ``friends.contrib.suggestions.backends.runners.AsyncRunner``.
* There is one setting that is needed for ``django-oauth-access``::

    OAUTH_ACCESS_SETTINGS = {
        'facebook': {
            'keys': {
                'KEY': 'YOURAPPKEY',
                'SECRET': 'yourappsecretcode',
            },
           'endpoints': {
                'authorize': 'https://graph.facebook.com/oauth/authorize',
                'access_token': 'https://graph.facebook.com/oauth/access_token',
                'callback': 'friends.contrib.suggestions.views.import_facebook_contacts',
            },
        },
        'twitter': {
            'keys': {
                'KEY': 'YOURAPPKEY',
                'SECRET': 'yourappsecretcode',
            },
            'endpoints': {
                'request_token': 'https://api.twitter.com/oauth/request_token',
                'authorize': 'http://twitter.com/oauth/authorize',
                'access_token': 'https://twitter.com/oauth/request_token',
                'callback': 'friends.contrib.suggestions.views.import_twitter_contacts',
            },
        },
        'yahoo': {
            'keys': {
                'KEY': 'YOURAPPKEY',
                'SECRET': 'yourappsecretcode',
            },
            'endpoints': {
                'request_token': 'https://api.login.yahoo.com/oauth/v2/get_request_token',
                'authorize': 'https://api.login.yahoo.com/oauth/v2/request_auth',
                'access_token': 'https://api.login.yahoo.com/oauth/v2/get_token',
                'callback': 'friends.contrib.suggestions.views.import_yahoo_contacts',
            },
        },
        'linkedin': {
            'keys': {
                'KEY': 'YOURAPPKEY',
                'SECRET': 'yourappsecretcode',
            },
            'endpoints': {
                'request_token': 'https://api.linkedin.com/uas/oauth/requestToken',
                'authorize': 'https://api.linkedin.com/uas/oauth/authorize',
                'access_token': 'https://api.linkedin.com/uas/oauth/accessToken',
                'callback': 'friends.contrib.suggestions.views.import_linkedin_contacts',
            },
        },
    }

  Remember to change ``YOURAPPKEY`` and ``yourappsecretcode`` for each service. You can get them by registering your applications on this sites:

    * Facebook: https://developers.facebook.com/apps
    * Twitter: https://dev.twitter.com/apps/new
    * Yahoo: https://developer.apps.yahoo.com/projects
    * LinkedIn: https://www.linkedin.com/secure/developer

Advanced usage
==============
By default friends suggestions are created after each contacts import but there are other situations when you could want to create friends suggestions. One example is when new user is registered on your site. This new user has no imported contacts yet but other users have some imported contacts and maybe new user matches some of the already imported contact.
Here is how to create friends suggestions on user activation using some signals:

* First create signal receiver::

    def find_friends_suggestions(sender, user, **kwargs):
        from friends.contrib.suggestions.models import FriendshipSuggestion
        FriendshipSuggestion.objects.create_suggestions_for_user_using_imported_contacts(user)

* If `django-easy-userena <https://github.com/barszczmm/django-easy-userena/>`_ app is used for managing users registration::

    from userena.signals import activation_complete
    activation_complete.connect(find_friends_suggestions, dispatch_uid="find_friends_suggestions_on_activation_complete")

* If `django-registration <https://bitbucket.org/ubernostrum/django-registration/>`_ app is used::

    from registration.signals import user_activated
    user_activated.connect(find_friends_suggestions, dispatch_uid="find_friends_suggestions_on_activation_complete")


Credits
=======
This app is based on `django-contacts-import <https://github.com/eldarion/django-contacts-import>`_ app with some code taken from its forks.



