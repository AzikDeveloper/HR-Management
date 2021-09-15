import re


def firstFormError(form):
    errors = form.errors.as_text().split('\n')
    if len(errors) >= 2:
        return str(errors[1])[3:]
    else:
        return None


def groupName(request=None, user=None):
    if user is None:
        return request.user.employee.position.name
    else:
        return user.employee.position.name


def fullNameParser(request):
    full_name = str(request.POST.get('full_name')).strip()
    if full_name.count(' ') == 1:
        if any(char.isdigit() for char in full_name):
            return False
        else:
            pattern = re.compile("[A-Za-z]+")
            first_name, last_name = full_name.split()
            if pattern.fullmatch(first_name) and pattern.fullmatch(last_name):
                r_post_copy = request.POST.copy()
                r_post_copy['first_name'] = first_name
                r_post_copy['last_name'] = last_name
                r_post_copy.pop('full_name')
                return r_post_copy
            else:
                return False
    else:
        return False
