from django.dispatch import Signal


friendship_invitation_sent = Signal(providing_args=["from_user", "to_user", "invitation"])
friendship_acceptance_sent = Signal(providing_args=["from_user", "to_user"])

