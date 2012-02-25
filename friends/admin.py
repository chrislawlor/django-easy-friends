from django.contrib import admin

from friends.models import Friendship, FriendshipInvitation


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ["id", "from_user", "to_user", "added"]


class FriendshipInvitationAdmin(admin.ModelAdmin):
    list_display = ["id", "from_user", "to_user", "sent"]


admin.site.register(Friendship, FriendshipAdmin)
admin.site.register(FriendshipInvitation, FriendshipInvitationAdmin)
