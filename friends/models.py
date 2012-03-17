from django.conf import settings
from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from django.dispatch import receiver

from friends.utils import get_datetime_now
from friends.managers import FriendshipManager, FriendshipInvitationManager
from friends.signals import invitation_received, invitation_sent, acceptance_received, acceptance_sent
from friends import settings as friends_settings


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
            acceptance_received.send(sender=None, from_user=self.from_user, to_user=self.to_user)
            acceptance_sent.send(sender=None, from_user=self.from_user, to_user=self.to_user)
        self.delete()

    def decline(self):
        self.delete()



@receiver(signals.pre_delete, sender=Friendship)
def delete_friendship(sender, instance, **kwargs):
    friendship_invitations = FriendshipInvitation.objects.filter(
        to_user=instance.to_user,
        from_user=instance.from_user,
    )
    for friendship_invitation in friendship_invitations:
        friendship_invitation.delete()


if friends_settings.FRIENDS_USE_NOTIFICATION_APP and "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

@receiver(invitation_received)
def send_invitation_received_notification(sender, from_user, to_user, invitation, **kwargs):
    if notification:
        notification.send([to_user], "friends_invite", {"invitation": invitation})

@receiver(invitation_sent)
def send_invitation_sent_notification(sender, from_user, to_user, invitation, **kwargs):
    if notification:
        notification.send([from_user], "friends_invite_sent", {"invitation": invitation})

@receiver(acceptance_received)
def send_acceptance_received_notification(sender, from_user, to_user, **kwargs):
    if notification:
        notification.send([from_user], "friends_accept", {"to_user": to_user})

@receiver(acceptance_sent)
def send_acceptance_sent_notification(sender, from_user, to_user, **kwargs):
    if notification:
        notification.send([to_user], "friends_accept_sent", {"from_user": from_user})

