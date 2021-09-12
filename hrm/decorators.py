from django.shortcuts import redirect
from django.shortcuts import HttpResponse


def authenticated(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.all()[0].name == 'director':
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


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('You are not authorized to see this page!')
        return wrapper
    return decorator
