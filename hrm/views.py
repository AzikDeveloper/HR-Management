# imports
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseGone, HttpResponseBadRequest
from django.views.generic import View

# my tools
from .decorators import redirect_if_authenticated, authenticated_required, allowed_users
from .my_tools import calculateProgresses
from .my_tools import in_groups
from .models import *

# filters and Forms
from .forms import CreateTaskForm, CreatePreUserForm, RegisterUserForm
from .filters import EmployeeFilter, TaskFilter

# built in tools
import datetime as dt


@redirect_if_authenticated
@authenticated_required
def home(request):
    return render(request, 'hrm/home.html')


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        token_validator = self.validate_token(kwargs['token'])
        if token_validator == 'valid':
            return render(request, 'hrm/auth/register.html')
        else:
            return token_validator

    def post(self, request, *args, **kwargs):
        token_validator = self.validate_token(kwargs['token'], _return=True)

        if isinstance(token_validator, GenLink):
            gen_link = token_validator

            form = RegisterUserForm(instance=gen_link.user, data=request.POST)
            if form.is_valid():
                form.save()
                gen_link.used = True
                gen_link.save()
                return redirect('login')
            else:
                errors = form.errors.as_data()
                context = {
                    'form': form,
                }
                if 'first_name' in errors:
                    context['first_name_error'] = list(errors['first_name'][0])[0]
                if 'last_name' in errors:
                    context['last_name_error'] = list(errors['last_name'][0])[0]
                if 'username' in errors:
                    context['username_error'] = list(errors['username'][0])[0]
                if 'password2' in errors:
                    context['password_error'] = list(errors['password2'][0])[0]
                return render(request, 'hrm/auth/register.html', context=context)
        else:
            return token_validator

    def validate_token(self, token, _return=False):
        try:
            token = uuid.UUID(token)
        except ValueError:
            return HttpResponseBadRequest("Invalid link")

        gen_link: GenLink = get_object_or_404(GenLink, token=token)

        if not gen_link.used and not gen_link.is_expired():
            if _return:
                return gen_link
            else:
                return 'valid'
        else:
            return HttpResponseGone("This link is expired")


@redirect_if_authenticated
def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            context = {'error': 'username or password is not correct!'}
            return render(request, 'hrm/auth/login.html', context)
    return render(request, 'hrm/auth/login.html')


@authenticated_required
@allowed_users(['Director'])
def console(request):
    return render(request, 'hrm/console.html')


@authenticated_required
@allowed_users(['Director', 'Manager'])
def addEmployeeView(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if in_groups(request, ['Director']):
            section = Section.objects.get(id=request.POST.get("section_id"))
            if request.POST.get("as_manager") == "true":
                group = Group.objects.get(name='Manager')
            else:
                group = Group.objects.get(name='Employee')
        else:
            section = request.user.employee.section
            group = Group.objects.get(name='Employee')

        form = CreatePreUserForm(username=email, email=email, section=section, group=group)
        if form.is_created():
            messages.warning(request, 'Employee is created!')
            return redirect(request.POST.get("next"))
        else:
            messages.error(request, form.error_message)
            return redirect(request.POST.get("next"))


# @authenticated_required
# @allowed_users(['Employee', 'Manager'])
# def employeeView(request):
#     employee = request.user
#     notifications = employee.received_notifications.all()
#
#     tasks = employee.tasks_to_me.all()
#     tasks_count = tasks.count()
#     tasks_done_count = tasks.filter(status='done').count()
#
#     # filtering tasks
#     task_filter = TaskFilter(request.GET, queryset=tasks)
#     tasks = task_filter.qs
#
#     tasks = calcu(tasks)
#
#     context = {
#         'employee': employee,
#         'notifications': notifications,
#         'tasks': tasks,
#         'tasks_count': tasks_count,
#         'tasks_done_count': tasks_done_count,
#         'filter': task_filter,
#
#         # navbar properties
#         'home_active': 'active',
#     }
#
#
# pass


@authenticated_required
@allowed_users(['Manager', 'Director'])
def employeeProfileView(request, pk):
    # navbar properties
    sections = Section.objects.all()
    employee = get_object_or_404(User, id=pk)

    if not (employee.info.section == request.user.info.section or in_groups(request, ['Director'])):
        return HttpResponseForbidden('You are not authorised to see this page')

    tasks = employee.tasks_to_me.all()
    # filtering tasks
    task_filter = TaskFilter(request.GET, queryset=tasks)
    tasks = task_filter.qs

    tasks_count = tasks.count()
    tasks_done_count = tasks.filter(status='done').count()

    tasks = tasksProcessor(tasks)

    if request.method == "POST":
        if request.POST.get("post_status") == "sendMessage":
            Notification.objects.create(sender=request.user, receiver=employee, text=request.POST.get('message'))

    context = {
        'employee': employee,
        'tasks': tasks,
        'filter': task_filter,
        'tasks_count': tasks_count,
        'tasks_done_count': tasks_done_count,

        # navbar properties
        'sections': sections
    }
    return render(request, 'hrm/employee_profile.html', context)


@authenticated_required
@allowed_users(['Director', 'Manager'])
def createTaskView(request):
    if request.method == 'POST':
        print(request.POST)
        employee = get_object_or_404(User, id=request.POST.get('assigned_to'))

        if not ((employee.info.section == request.user.info.section and employee.groups.filter(
                name='Employee').exists()) or in_groups(request, ['Director'])):
            return HttpResponse('<h3>You are not authorized to see this page!')

        form = CreateTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'new'
            task.task_giver = request.user
            task.save()
            messages.success(request, 'Task is created!')

        else:
            messages.error(request, 'Failed to create task. Invalid credentials!')

        if request.POST.get('next'):
            return redirect(request.POST.get('next'))
        else:
            return redirect('/')


@authenticated_required
@allowed_users(['Director', 'Manager'])
def editTaskView(request, pk):
    # navbar properties
    sections = Section.objects.all()

    try:
        task = Task.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponse("<h3>404 not found</h3>")

    if request.user == task.task_giver.user:
        form = CreateTaskForm(instance=task)

        if request.method == "POST":
            if 'save' in request.POST:
                task_giver = task.task_giver
                note = task.note

                form = CreateTaskForm(request.POST, instance=task)
                if form.is_valid():
                    task = form.save()
                    task.note = note
                    task.task_giver = task_giver
                    task.save()
                    return redirect(request.GET.get('next'))
                else:
                    print(form.errors)
            if 'delete' in request.POST:
                task.delete()
                return redirect(request.GET.get('next'))

        context = {
            'form': form,

            # navbar properties
            'sections': sections,
        }
        return render(request, 'hrm/edit_task.html', context)
    else:
        return redirect('view_task', pk=pk)


@authenticated_required
@allowed_users(['Director', 'Manager'])
def viewTaskView(request, pk):
    # navbar properties
    sections = Section.objects.all()

    if request.method == 'POST':
        return redirect(request.GET.get('next'))
    try:
        task = Task.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponse("<h3>404 not found</h3>")

    context = {
        'task': task,

        # navbar properties
        'sections': sections
    }
    return render(request, 'hrm/view_task.html', context)


@authenticated_required
def logoutView(request):
    logout(request)
    return redirect('login')


@authenticated_required
@allowed_users(['Manager', 'Employee'])
def taskInfoView(request, pk):
    try:
        task = Task.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponse('<h3>404 not found!</h3>')

    if task.assigned_to == request.user.employee:
        if request.method == "POST":
            if request.POST.get("status") in ['new', 'processing', 'done']:
                task.status = request.POST.get("status")
                task.note = request.POST.get("note")
                task.save()
                return redirect('/')

        select_selection = task.status
        select_options = {
            'new': ('selected' if select_selection == 'new' else ''),
            'processing': ('selected' if select_selection == 'processing' else ''),
            'done': ('selected' if select_selection == 'done' else ''),
        }

        context = {
            'task': task,
            'select_options': select_options
        }
        return render(request, 'hrm/task_info.html', context)
    else:
        return HttpResponse("<h3>you are not authorised to see this page</h1>")


@authenticated_required
@allowed_users(['Director', 'Manager'])
def sendNotificationView(request):
    if request.method == "POST":

        employee = get_object_or_404(User, id=request.POST.get("employee_id"))

        if not employee.info.section == request.user.info.section:
            return HttpResponse('<h3>You can\'t send notification to this employee')

        if request.POST.get('message'):
            Notification.objects.create(sender=request.user, receiver=employee, text=request.POST.get('message'))

        return redirect(request.POST.get("next"))


@authenticated_required
@allowed_users(['Director'])
def settingsView(request):
    return render(request, 'hrm/tests/settings.html')


@authenticated_required
@allowed_users(['Director', 'Manager'])
def tasksView(request):
    # navbar properties
    sections = Section.objects.all()

    if in_groups(request, ['Director']):
        tasks = Task.objects.all()
    elif in_groups(request, ['Manager']):
        tasks = Task.objects.filter(task_giver__section=request.user.employee.section)

    tasks_count = tasks.count()
    tasks_done_count = tasks.filter(status='done').count()
    tasks_processing_count = tasks.filter(status='processing').count()
    tasks_new_count = tasks_count - tasks_done_count - tasks_processing_count

    # filtering tasks
    task_filter = TaskFilter(request.GET, queryset=tasks)
    tasks = zip(tasks, calculateProgresses(task_filter.qs))
    context = {
        'tasks': tasks,
        'tasks_count': tasks_count,
        'tasks_new_count': tasks_new_count,
        'tasks_done_count': tasks_done_count,
        'tasks_processing_count': tasks_processing_count,

        'filter': task_filter,

        # navbar properties
        'tasks_active': 'active',
        'sections': sections,
    }
    return render(request, 'hrm/tests/tasks.html', context)


@authenticated_required
@allowed_users(['Director', 'Managers'])
def statisticsView(request):
    return render(request, 'hrm/statistics.html')


@authenticated_required
@allowed_users(['Director'])
def changePosition(request):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(id=request.POST.get('employee_id'))
        except ObjectDoesNotExist:
            return redirect(request.POST.get('next'))

        if employee.position.name == 'Manager':
            employee.position = Position.objects.get(name='Employee')
            employee.save()
        elif employee.position.name == 'Employee':
            employee.position = Position.objects.get(name='Manager')
            employee.save()

        return redirect(request.POST.get('next'))


@authenticated_required
@allowed_users(['Director'])
def addSectionView(request):
    if request.method == 'POST':
        if len(request.POST.get('section_name')) > 0:
            Section.objects.create(name=request.POST.get("section_name"))
            return redirect(request.POST.get("next"))
        else:
            return redirect('/')


@authenticated_required
@allowed_users(['Manager'])
def mySectionView(request):
    employees_in_section = request.user.info.section.employees_by_section.all()

    employees = User.objects.filter(info__section=request.user.info.section, groups__name='Employee')

    managers = User.objects.filter(info__section=request.user.info.section, groups__name='Manager')

    if request.method == 'GET':
        if 'search_employee' in request.GET:
            e_filter = EmployeeFilter(request.GET, queryset=employees)
            employees = e_filter.qs
        elif 'search_manager' in request.GET:
            m_filter = EmployeeFilter(request.GET, queryset=managers)
            managers = m_filter.qs

    context = {
        'employees': employees,
        'managers': managers,

        # navbar properties
        'section_active': 'active'
    }
    return render(request, 'hrm/my_section.html', context=context)

# @authenticated_required
# def editProfileView(request):
#     context = {}
#     if request.method == 'POST':
#         r_post = fullNameParser(request)
#         if r_post:
#             try:
#                 user = request.user
#                 user.username = r_post.get("username")
#                 user.save()
#
#                 employee = request.user.employee
#                 employee.first_name = r_post.get("first_name")
#                 employee.last_name = r_post.get("last_name")
#                 employee.email = r_post.get("email")
#                 employee.phone = r_post.get("phone")
#                 employee.about = r_post.get("about")
#                 if employee.address:
#                     address = employee.address
#                     address.street = r_post.get("street")
#                     address.state = r_post.get("state")
#                     address.city = r_post.get("city")
#                     address.zip_code = r_post.get("zip_code")
#                     address.country = r_post.get("country")
#                     address.save()
#                 else:
#                     address = Address.objects.create(
#                         street=r_post.get("street"),
#                         state=r_post.get("state"),
#                         city=r_post.get("city"),
#                         zip_code=int(r_post.get("zip_code")),
#                         country=r_post.get("country")
#                     )
#                     employee.address = address
#                 employee.save()
#             except Exception:
#                 pass
#         else:
#             context['error'] = 'wrong full name'
#
#     employee = request.user.employee
#     context = {
#         'employee': employee
#     }
#     return render(request, 'hrm/edit_profile.html', context)
