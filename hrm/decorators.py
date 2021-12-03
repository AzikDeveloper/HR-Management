from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.http import HttpResponseNotAllowed


def redirect_if_authenticated(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Director').exists():
                return redirect('console')
            else:
                return redirect('employee')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper


def authenticated_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')

    return wrapper


def allowed_users(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=allowed_roles).exists():
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseNotAllowed('You are not authorized to see this page!')

        return wrapper

    return decorator
