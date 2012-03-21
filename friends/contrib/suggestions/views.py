from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from gdata.contacts.service import ContactsService

from friends.contrib.suggestions.backends.importers import GoogleImporter
from friends.contrib.suggestions.settings import RUNNER


def _import_success(request, results):
    if results.ready():
        if results.status == "DONE":
            messages.success(request, _("%(total)s people with email found, %(imported)s contacts imported.") % results.result)
        elif results.status == "FAILURE":
            messages.error(request, message=_("There was an error importing your contacts."))
    else:
        messages.info(request, _("We're still importing your contacts. We'll let you know when they're ready, it shouldn't take too long."))
        request.session["import_contacts_task_id"] = results.task_id
    return HttpResponseRedirect(request.path)


@login_required
def import_contacts(request, template_name="suggestions/import_contacts.html"):
    """
    """

    runner_class = RUNNER

    google_authsub_token = request.session.pop("google_authsub_token", None)

    if google_authsub_token:
        runner = runner_class(GoogleImporter,
                              user=request.user,
                              authsub_token=google_authsub_token)
        results = runner.import_contacts()
        return _import_success(request, results)

    ctx = {}

    return render_to_response(template_name,
                              ctx,
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


