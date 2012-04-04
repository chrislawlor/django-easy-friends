from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User


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

    def create_suggestions_for_user_using_imported_contacts(self, user):
        """
        Creates friendship suggestions using contacts imported by user.
        """
        from friends.contrib.suggestions.models import ImportedContact
        from friends.models import Friendship

        created = 0
        imported_contacts = ImportedContact.objects.filter(owner=user)
        for imported_contact in imported_contacts:
            try:
                suggested_friend = User.objects.get(email=imported_contact.email)
            except User.DoesNotExist:
                suggested_friend = None
            if suggested_friend and suggested_friend != user \
            and not Friendship.objects.are_friends(user, suggested_friend) \
            and not self.are_suggested_friends(user, suggested_friend):
                self.create(from_user=user, to_user=suggested_friend)
                created += 1
        return created


