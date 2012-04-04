from django.db import models
from django.db.models import Q


class FriendshipManager(models.Manager):

    def friends_for_user(self, user):
        friends = []
        qs = self.filter(Q(from_user=user) | Q(to_user=user)).select_related(depth=1)
        for friendship in qs:
            if friendship.from_user == user:
                friends.append(friendship.to_user)
            else:
                friends.append(friendship.from_user)
        return friends

    def are_friends(self, user1, user2):
        return self.filter(
            Q(from_user=user1, to_user=user2) |
            Q(from_user=user2, to_user=user1)
        ).count() > 0

    def remove(self, user1, user2):
        friendship = self.filter(from_user=user1, to_user=user2)
        if not friendship:
            friendship = self.filter(from_user=user2, to_user=user1)
        if friendship:
            friendship.delete()


