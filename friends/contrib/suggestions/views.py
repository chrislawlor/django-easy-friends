from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from gdata.contacts.service import ContactsService

from friends.contrib.suggestions.backends.importers import GoogleImporter
from friends.contrib.suggestions.settings import RUNNER
from friends.contrib.suggestions.models import FriendshipSuggestion


@login_required
def suggested_friends(request, template_name="friends/suggestions/suggested_friends.html"):
    """
    List suggested friends.
    """
    suggested_friends = FriendshipSuggestion.objects.suggested_friends_for_user(request.user)
    return render_to_response(template_name,
                              {"suggested_friends": suggested_friends},
                              context_instance=RequestContext(request))


def _import_status(request, results):
    """
    Check import task state and set appropriate messages.
    Returns True if import is finished, False otherwise.
    """
    if results.ready():
        if results.status == "SUCCESS":
            messages.success(request, _("%(total)s people with email found, %(imported)s new contacts imported, %(suggestions)s new friendship suggestions added.") % results.result)
        elif results.status == "FAILURE":
            messages.error(request, message=_("There was an error importing your contacts."))
        return True
    else:
        messages.info(request, _("We're still importing your contacts. We'll let you know when they're ready, it shouldn't take too long."))
        request.session["import_contacts_task_id"] = results.task_id
        return False


@login_required
def import_contacts(request, template_name="friends/suggestions/import_contacts.html"):
    """
    If there is import_contacts_task_id in session pop it up and show info about
    this task using _import_status method.
    If there is no import_contacts_task_id in session check if there is 
    google_authsub_token in session and import Google contacts if it is.
    """

    import_in_progress = False

    import_contacts_task_id = request.session.pop("import_contacts_task_id", None)
    if import_contacts_task_id:
        from celery.result import AsyncResult
        results = AsyncResult(import_contacts_task_id)
        import_in_progress = _import_status(request, results)

    else:
        google_authsub_token = request.session.pop("google_authsub_token", None)
        if google_authsub_token:
            runner_class = RUNNER
            runner = runner_class(GoogleImporter,
                                  user=request.user,
                                  authsub_token=google_authsub_token)
            results = runner.import_contacts()
            import_in_progress = _import_status(request, results)

    return render_to_response(template_name,
                              {'import_in_progress': import_in_progress},
                              context_instance=RequestContext(request))


def import_google_contacts(request, redirect_to=None):
    """
    If no token in GET params then redirect to Google page for granting permissions.
    If token is available, save it into session and redirect to import_contacts view. 
    """
    if redirect_to is None:
        redirect_to = reverse("friends_suggestions_import_contacts")
    if "token" in request.GET:
        request.session["google_authsub_token"] = request.GET["token"]
        return HttpResponseRedirect(redirect_to)
    authsub_url = ContactsService().GenerateAuthSubURL(next=request.build_absolute_uri(),
                                                       scope='http://www.google.com/m8/feeds/',
                                                       secure=False,
                                                       session=True)
    return HttpResponseRedirect(authsub_url)


