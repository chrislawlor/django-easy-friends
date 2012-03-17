from django.dispatch import Signal

invitation_received = Signal(providing_args=["from_user", "to_user", "invitation"])
invitation_sent = Signal(providing_args=["from_user", "to_user", "invitation"])
acceptance_received = Signal(providing_args=["from_user", "to_user"])
acceptance_sent = Signal(providing_args=["from_user", "to_user"])
# TODO: create signal when friend id having new friend
