from django.conf import settings
from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User

from friends.utils import get_datetime_now
from friends.managers import FriendshipManager, FriendshipInvitationManager


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None


class Friendship(models.Model):
    """
    A friendship is a bi-directional association between two users who
    have both agreed to the association.
    """

    to_user = models.ForeignKey(User, related_name="friends")
    from_user = models.ForeignKey(User, related_name="_unused_")
    added = models.DateTimeField(default=get_datetime_now)

    objects = FriendshipManager()

    class Meta:
        unique_together = [("to_user", "from_user")]


class FriendshipInvitation(models.Model):
    """
    A friendship invite is an invitation from one user to another to be
    associated as friends.
    """

    from_user = models.ForeignKey(User, related_name="invitations_from")
    to_user = models.ForeignKey(User, related_name="invitations_to")
    message = models.TextField()
    sent = models.DateTimeField(default=get_datetime_now)

    objects = FriendshipInvitationManager()

    def accept(self):
        if not Friendship.objects.are_friends(self.to_user, self.from_user):
            friendship = Friendship(to_user=self.to_user, from_user=self.from_user)
            friendship.save()
            if notification:
                notification.send([self.from_user], "friends_accept", {"to_user": self.to_user})
                notification.send([self.to_user], "friends_accept_sent", {"from_user": self.from_user})
        self.delete()

    def decline(self):
        self.delete()



def delete_friendship(sender, instance, **kwargs):
    friendship_invitations = FriendshipInvitation.objects.filter(
        to_user = instance.to_user,
        from_user = instance.from_user,
    )
    for friendship_invitation in friendship_invitations:
        friendship_invitation.delete()


signals.pre_delete.connect(delete_friendship, sender=Friendship)
