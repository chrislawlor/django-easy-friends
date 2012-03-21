from django.db import models
from django.db.models import Q


class FriendshipSuggestionManager(models.Manager):

    def suggested_friends_for_user(self, user):
        suggested_friends = []
        qs = self.filter(Q(from_user=user) | Q(to_user=user)).select_related(depth=1)
        for friendship_suggestion in qs:
            if friendship_suggestion.from_user == user:
                suggested_friends.append(friendship_suggestion.to_user)
            else:
                suggested_friends.append(friendship_suggestion.from_user)
        return suggested_friends

    def are_suggested_friends(self, user1, user2):
        return self.filter(
            Q(from_user=user1, to_user=user2) |
            Q(from_user=user2, to_user=user1)
        ).count() > 0

    def remove(self, user1, user2):
        if self.filter(from_user=user1, to_user=user2):
            friendship_suggestion = self.filter(from_user=user1, to_user=user2)
        elif self.filter(from_user=user2, to_user=user1):
            friendship_suggestion = self.filter(from_user=user2, to_user=user1)
        friendship_suggestion.delete()

