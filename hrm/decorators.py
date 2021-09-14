from django.shortcuts import redirect
from django.shortcuts import HttpResponse


def redirect_if_authenticated(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.employee.position.name == 'Director':
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
            position = None
            if request.user.employee.position:
                position = request.user.employee.position.name
            if position in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('You are not authorized to see this page!')
        return wrapper
    return decorator
