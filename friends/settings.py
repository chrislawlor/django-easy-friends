from django.conf import settings
gettext = lambda s: s


SHOW_FRIENDS_OF_FRIEND = getattr(settings,
                                'SHOW_FRIENDS_OF_FRIEND',
                                False)

NOTIFY_ABOUT_NEW_FRIENDS_OF_FRIEND = getattr(settings,
                                             'NOTIFY_ABOUT_NEW_FRIENDS_OF_FRIEND',
                                             False)
