from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from friends.models import Friendship, FriendshipInvitation
from friends.forms import InviteFriendForm, RemoveFriendForm


@login_required
def list_friends(request):
    """
    Lists friends of currently logged user.
    """
    users = Friendship.objects.friends_for_user(request.user)
    return render_to_response('friends/friends_list.html',
                              {'users': users},
                              context_instance=RequestContext(request))

@login_required
def invite_friend(request, username, redirect_to_view=None, message=_("Friends? :)")):
    """
    Invite user to be user friend.
    """
    if request.method == "POST":
        form = InviteFriendForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Friendship invitation for %(username)s was created.") % {'username': username}, fail_silently=True)
            if not redirect_to_view:
                redirect_to_view = list_sent_invitations
            return redirect(redirect_to_view)
    else:
        form = InviteFriendForm(initial={'to_user': username, 'message': message})
    return render_to_response('friends/friend_invite.html',
                              {'form': form,
                               'username': username},
                              context_instance=RequestContext(request))

@login_required
def remove_friend(request, username, redirect_to_view=None):
    """
    Remove user from friends.
    """
    if request.method == "POST":
        form = RemoveFriendForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("User %(username)s removed from friends.") % {'username': username}, fail_silently=True)
            if not redirect_to_view:
                redirect_to_view = list_friends
            return redirect(redirect_to_view)
    else:
        form = RemoveFriendForm(initial={'to_user': username})
    return render_to_response('friends/friend_remove.html',
                              {'form': form,
                               'username': username},
                              context_instance=RequestContext(request))

@login_required
def list_received_invitations(request):
    """
    List invitations received by user.
    """
    invitations = FriendshipInvitation.objects.filter(to_user=request.user)
    return render_to_response('friends/invitations_list.html',
                              {'invitations': invitations,
                               'status': 'received'},
                              context_instance=RequestContext(request))

@login_required
def list_sent_invitations(request):
    """
    List invitations sent by user.
    """
    invitations = FriendshipInvitation.objects.filter(from_user=request.user)
    return render_to_response('friends/invitations_list.html',
                              {'invitations': invitations,
                               'status': 'sent'},
                              context_instance=RequestContext(request))

@login_required
def show_invitation(request, invitation_id):
    """
    Show friendship invitation.
    """
    invitation = get_object_or_404(FriendshipInvitation,
        Q(to_user=request.user) | Q(from_user=request.user),
        pk=invitation_id
    )
    return render_to_response('friends/invitation_show.html',
                              {'invitation': invitation},
                              context_instance=RequestContext(request))

@login_required
def remove_invitation(request, invitation_id, redirect_to_view=None):
    """
    Remove invitation (only sender shoul be able to remove invitation
    and only before it was accepted or rejected).
    """
    invitation = get_object_or_404(FriendshipInvitation,
        Q(to_user=request.user) | Q(from_user=request.user),
        pk=invitation_id
    )
    invitation.delete()
    messages.success(request, _("Invitation deleted."), fail_silently=True)
    if not redirect_to_view:
        redirect_to_view = list_friends
    return redirect(redirect_to_view)

@login_required
def respond_to_invitation(request, invitation_id, resp='a', redirect_to_view=None):
    """
    Accept or decline invitation.
    """
    invitation = get_object_or_404(FriendshipInvitation,
        to_user=request.user,
        pk=invitation_id
    )
    if resp == 'a':
        invitation.accept()
        messages.success(request, _("Invitation accepted."), fail_silently=True)
    elif resp == 'd':
        invitation.decline()
        messages.success(request, _("Invitation declined."), fail_silently=True)
    if not redirect_to_view:
        redirect_to_view = list_friends
    return redirect(redirect_to_view)


