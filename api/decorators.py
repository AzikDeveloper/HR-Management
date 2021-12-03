from rest_framework.response import Response


def authenticated_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return Response(data={'message': 'you are not authorized to get this data'}, status=401)

    return wrapper


def allowed_users(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            position = request.user.groups.filter(name__in=allowed_roles)
            if position:
                request.session['position'] = position[0].name
                return view_func(request, *args, **kwargs)
            else:
                return Response(data={'message': 'you are not authorized to get this data'}, status=401)

        return wrapper

    return decorator
