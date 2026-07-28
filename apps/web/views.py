from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def home(request) -> HttpResponse:
    if request.user.is_authenticated:
        return render(
            request,
            "web/app_home.html",
            context={
                "active_tab": "dashboard",
                "page_title": _("Dashboard"),
            },
        )
    else:
        return render(request, "web/landing_page.html")


@user_passes_test(lambda u: u.is_superuser)
def simulate_error(request) -> HttpResponse:
    raise Exception("This is a simulated error.")
