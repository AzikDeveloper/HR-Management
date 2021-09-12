from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from .decorators import authenticated
from .decorators import authenticated_required, allowed_users
import uuid
from . import models
from .forms import CreateTaskForm, CreateUserForm
from django.contrib.auth.models import Group
import datetime as dt
from .filters import EmployeeFilter, TaskFilter
import re
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def apiTestView(request):
    response = ''
    if request.user.is_authenticated:
        response = 'AUTHED'
    else:
        response = 'NOT AUTHED'
    return Response(response)


def groupName(request=None, user=None):
    if user is None:
        return request.user.groups.all()[0].name
    else:
        return str(user.groups.all()[0].name)


def fullNameParser(request):
    full_name = str(request.POST.get('full_name')).strip()
    if full_name.count(' ') == 1:
        if any(char.isdigit() for char in full_name):
            return False
        else:
            pattern = re.compile("[A-Za-z]+")
            first_name, last_name = full_name.split()
            if pattern.fullmatch(first_name) and pattern.fullmatch(last_name):
                rpost_copy = request.POST.copy()
                rpost_copy['first_name'] = first_name
                rpost_copy['last_name'] = last_name
                rpost_copy.pop('full_name')
                return rpost_copy
            else:
                return False
    else:
        return False


@authenticated
@authenticated_required
def home(request):
    return render(request, 'hrm/home.html')


def registerView(request, pk):
    if len(pk) == 36:
        genLink = models.GenLink.objects.filter(link=uuid.UUID(pk))
        if genLink:
            print("exist link")
            if request.method == 'POST':
                print(request.POST)
                if '@' in request.POST.get('username'):
                    context = {'error': 'only a-z characters allowed'}
                    return render(request, 'hrm/register.html', context)
                else:
                    request_post = fullNameParser(request)
                    if request_post:
                        form = CreateUserForm(request_post)
                        if form.is_valid():
                            employee = genLink[0].employee
                            user = employee.user
                            user.username = request_post.get('username')
                            user.set_password(request_post.get('password1'))
                            employee.first_name = request_post.get('first_name')
                            employee.last_name = request_post.get('last_name')
                            user.save()
                            employee.save()
                            genLink.delete()
                            return redirect('login')
                        else:
                            print("invalid form")
                            for error in form.errors:
                                print(error)
                            errors = form.errors.as_text().split('\n')
                            print(errors)

                            return render(request, 'hrm/register.html')
                    else:
                        return render(request, 'hrm/register.html', context={'error': 'Wrong full name!'})
            return render(request, 'hrm/register.html')
        else:
            return HttpResponse("<h1>404 not found")
    else:
        return HttpResponse("<h1>404 not found")


@authenticated
def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            print("invalid!")
    return render(request, 'hrm/login.html')


@authenticated_required
@allowed_users(['director'])
def console(request):
    # navbar properties
    home_active = 'active'

    sections = models.Section.objects.all()

    _employees = models.User.objects.filter(groups__name='employee')
    _managers = models.User.objects.filter(groups__name='manager')

    employees = models.Employee.objects.none()
    managers = models.Employee.objects.none()
    for _manager in _managers:
        managers |= models.Employee.objects.filter(pk=_manager.employee.id)
    for _employee in _employees:
        employees |= models.Employee.objects.filter(pk=_employee.employee.id)

    if request.method == 'GET':
        if 'search_employee' in request.GET:
            e_filter = EmployeeFilter(request.GET, queryset=_employees)
            employees = e_filter.qs
        elif 'search_manager' in request.GET:
            m_filter = EmployeeFilter(request.GET, queryset=_managers)
            managers = m_filter.qs
    context = {'employees': employees, 'managers': managers, 'home_active': home_active, 'sections': sections}

    return render(request, 'hrm/console.html', context)


@authenticated_required
@allowed_users(['director', 'manager'])
def addEmployeeView(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = models.User.objects.create_user(username=email, email=email)
        if groupName(request) == 'director':
            if request.POST.get("as_manager") == "true":
                group = Group.objects.get(name='manager')
            else:
                group = Group.objects.get(name='employee')
        else:
            group = Group.objects.get(name='employee')
        user.groups.add(group)
        user.save()
        employee = user.employee
        employee.section = models.Section.objects.get(id=request.POST.get("section_id"))
        employee.save()

        return redirect(request.POST.get("next"))


@authenticated_required
@allowed_users(['employee', 'manager'])
def employeeView(request):
    # navbar properties
    tasks_display = 'none'
    sections_display = 'none'
    if groupName(request) == 'manager':
        tasks_display = ''

    my_section = request.user.employee.section
    employee = models.Employee.objects.get(id=request.user.employee.id)
    position = groupName(user=employee.user)
    messages = models.Message.objects.filter(receiver=request.user)

    tasks = employee.task_set.all()
    tasks_count = tasks.count()
    tasks_done_count = tasks.filter(status='done').count()

    home_active = 'active'
    progresses = []
    task_filter = TaskFilter(request.GET, queryset=tasks)
    tasks = task_filter.qs
    for task in tasks:
        max = (task.deadline - task.date_given).total_seconds()
        val = (dt.datetime.today() - task.date_given).seconds
        percentage = (val / max) * 100
        deadline_color = ''
        if percentage >= 100:
            deadline_color = 'red'
        status_color = {'new': '', 'processing': 'blue', 'done': 'green'}
        progresses.append({'value': val, 'max': max, 'percentage': percentage, 'deadline_color': deadline_color,
                           'status_color': status_color[task.status]})
    tasks = zip(tasks, progresses)

    context = {
        'employee': employee,
        'position': position,
        'my_section': my_section,
        'messages': messages,
        'tasks': tasks,
        'tasks_count': tasks_count,
        'tasks_done_count': tasks_done_count,
        'tasks_display': tasks_display,
        'sections_display': sections_display,
        'home_active': home_active,
        'filter': task_filter,
    }
    return render(request, 'hrm/employee.html', context)


@authenticated_required
@allowed_users(['manager', 'director'])
def employeeProfileView(request, pk):
    # navbar properties
    sections_display = 'none'
    my_section = ''
    position = groupName(request)
    if groupName(request) == 'director':
        sections_display = ''
    elif groupName(request) == 'manager':
        my_section = request.user.employee.section
    home_active = ''

    sections = models.Section.objects.all()
    employee = models.Employee.objects.get(id=pk)
    if employee == request.user.employee:
        return redirect('/')
    employee_position = groupName(user=employee.user)
    tasks = employee.task_set.all()
    tasks_count = tasks.count()
    tasks_done_count = tasks.filter(status='done').count()
    progresses = []
    for task in tasks:
        max = (task.deadline - task.date_given).total_seconds()
        val = (dt.datetime.today() - task.date_given).seconds
        percentage = (val/max)*100
        deadline_color = ''
        if percentage >= 100:
            deadline_color = 'red'
        status_color = {'new': '', 'processing': 'blue', 'done': 'green'}
        progresses.append({'value': val, 'max': max, 'percentage': percentage, 'deadline_color': deadline_color, 'status_color': status_color[task.status]})
    tasks = zip(tasks, progresses)
    if request.method == "POST":
        if request.POST.get("post_status") == "sendMessage":
            models.Message.objects.create(sender=request.user, receiver=employee.user, text=request.POST.get('message'))

    context = {
        'employee': employee,
        'employee_position': employee_position,
        'position': position,
        'my_section': my_section,
        'tasks': tasks,
        'tasks_count': tasks_count,
        'tasks_done_count': tasks_done_count,
        'home_active': home_active,
        'sections_display': sections_display,
        'sections': sections
    }
    return render(request, 'hrm/employee_profile.html', context)


@authenticated_required
@allowed_users(['director', 'manager'])
def createTaskView(request, pk):
    # navbar properties
    sections_display = 'none'
    my_section = ''
    position = ''
    if groupName(request) == 'director':
        sections_display = ''
    elif groupName(request) == 'manager':
        position = 'manager'
        my_section = request.user.employee.section

    form = None
    user = None
    if pk == "-1":
        form = CreateTaskForm(initial={'status': 'new'})
    else:
        user = models.Employee.objects.get(id=pk)
        form = CreateTaskForm(initial={'assigned_to': user, 'status': 'new'})

    sections = models.Section.objects.all()
    context = {
        'form': form,
        'sections': sections,
        'sections_display': sections_display,
        'position': position,
        'my_section': my_section
    }
    if request.method == "POST":
        form = CreateTaskForm(request.POST, initial={'task_giver': request.user.employee})
        if form.is_valid():
            task = form.save()
            task.task_giver = request.user.employee
            task.save()
            try:
                return redirect(request.GET.get("next"))
            except:
                return redirect('/')
        else:
            print(form.errors)
            print("fard")
    return render(request, 'hrm/create_task.html', context)


@authenticated_required
@allowed_users(['director', 'manager'])
def editTaskView(request, pk):
    if request.user == models.Task.objects.get(id=pk).task_giver.user:
        # navbar properties
        sections_display = 'none'
        position = ''
        my_section = ''
        if groupName(request) == 'director':
            sections_display = ''
        elif groupName(request) == 'manager':
            position = 'manager'
            my_section = request.user.employee.section

        task = models.Task.objects.get(id=pk)
        form = CreateTaskForm(instance=task)
        home_active = ''
        sections = models.Section.objects.all()
        context = {'form': form, 'sections': sections, 'home_active': home_active, 'sections_display': sections_display, 'position': position, 'my_section': my_section}
        if request.method == "POST":
            if 'save' in request.POST:
                task_giver = task.task_giver
                form = CreateTaskForm(request.POST, instance=task)
                note = task.note
                if form.is_valid():
                    if str(form.cleaned_data['assigned_to']) != str(task.assigned_to.user.username):
                        task = form.save()
                        task.status = 'new'
                        task.note = note
                        task.task_giver = task_giver
                        task.save()
                    else:
                        task = form.save()
                        task.note = note
                        task.task_giver = task_giver
                        task.save()
                    try:
                        return redirect(request.GET.get('next'))
                    except:
                        return redirect('/')
                else:
                    print(form.errors)
                    print("fard")
            if 'delete' in request.POST:
                employee = task.assigned_to
                task.delete()
                try:
                    return redirect(request.GET.get('next'))
                except:
                    return redirect('/')
        return render(request, 'hrm/edit_task.html', context)
    else:
        return redirect('view_task', pk=pk)


@authenticated_required
@allowed_users(['director', 'manager'])
def enterTaskView(request, pk):
    if request.method == 'POST':
        try:
            return redirect(request.GET.get('next'))
        except:
            return redirect('/')

    # navbar properties
    sections_display = 'none'
    position = ''
    my_section = ''
    if groupName(request) == 'director':
        sections_display = ''
    elif groupName(request) == 'manager':
        position = 'manager'
        my_section = request.user.employee.section

    task = models.Task.objects.get(id=pk)
    task_giver = task.task_giver
    assigned_to = task.assigned_to

    context = {'task': task, 'assigned_to': assigned_to}
    return render(request, 'hrm/enter_task.html', context)


@authenticated_required
def logoutView(request):
    logout(request)
    return redirect('login')


@authenticated_required
@allowed_users(['manager', 'employee'])
def taskInfoView(request, pk):
    # navbar properties
    sections_display = 'none'
    position = ''
    section_active = ''
    my_section = ''
    if groupName(request) == 'director':
        sections_display = ''
    elif groupName(request) == 'manager':
        position = 'manager'
        my_section = request.user.employee.section
    task = models.Task.objects.get(id=pk)
    if task.assigned_to == request.user.employee:
        select_selection = task.status
        select_options = {
            'new': ('selected' if select_selection == 'new' else ''),
            'processing': ('selected' if select_selection == 'processing' else ''),
            'done': ('selected' if select_selection == 'done' else ''),
        }
        print(select_options)
        context = {'task': task, 'select_options': select_options, 'sections_display': sections_display, 'position': position, 'my_section': my_section}
        statuses = ['new', 'processing', 'done']
        if request.method == "POST":
            if request.POST.get("status") in statuses:
                task.status = request.POST.get("status")
                task.note = request.POST.get("note")
                task.save()
                return redirect('/')
        return render(request, 'hrm/taskinfo.html', context)
    else:
        return HttpResponse("<h1>you are not authorised to see this page</h1>")


@authenticated_required
@allowed_users(['director', 'manager'])
def sendMessage(request):
    if request.method == "POST":
        employee = models.Employee.objects.get(id=request.POST.get("employee_id"))
        models.Message.objects.create(sender=request.user, receiver=employee.user, text=request.POST.get('message'))
        return redirect(request.POST.get("next"))


@authenticated_required
@allowed_users(['director'])
def sectionView(request, pk):
    section = models.Section.objects.get(id=pk)
    sections = models.Section.objects.all()
    users = section.employee_set.all()
    _users = models.User.objects.filter(employee__in=users)

    _employees = _users.filter(groups__name='employee')
    _managers = _users.filter(groups__name='manager')

    employees = models.Employee.objects.none()
    managers = models.Employee.objects.none()
    for _manager in _managers:
        managers |= models.Employee.objects.filter(pk=_manager.employee.id)
    for _employee in _employees:
        employees |= models.Employee.objects.filter(pk=_employee.employee.id)

    if request.method == 'GET':
        if 'search_employee' in request.GET:
            e_filter = EmployeeFilter(request.GET, queryset=_employees)
            employees = e_filter.qs
        elif 'search_manager' in request.GET:
            m_filter = EmployeeFilter(request.GET, queryset=_managers)
            managers = m_filter.qs

    context = {'section': section, 'sections': sections, 'employees': employees, 'managers': managers, 'sections_active': 'active'}
    return render(request, 'hrm/section.html', context)


@authenticated_required
@allowed_users(['director', 'manager'])
def tasksView(request):
    # navbar properties
    sections_display = 'none'
    section = ''
    position = ''
    if groupName(request) in ['director']:
        sections_display = ''
    elif groupName(request) == 'manager':
        section = request.user.employee.section.name
        position = 'manager'
    else:
        section = request.user.employee.section.name

    sections = models.Section.objects.all()
    tasks_active = 'active'
    tasks = models.Task.objects.none()
    if groupName(request=request) == 'manager':
        emps = request.user.employee.section.employee_set.all()
        managers = models.Employee.objects.none()
        for emp in emps:
            if groupName(user=emp.user) == 'manager':
                managers |= models.Employee.objects.filter(id=emp.id)
        tasks_ids = managers.values_list('my_tasks', flat=True)
        for task_id in tasks_ids:
            tasks |= models.Task.objects.filter(id=task_id)
    elif groupName(request=request) == 'director':
        tasks = models.Task.objects.all()

    tasks_count = tasks.count()
    tasks_done_count = tasks.filter(status='done').count()
    tasks_processing_count = tasks.filter(status='processing').count()
    tasks_new_count = tasks_count - tasks_done_count - tasks_processing_count

    progresses = []
    task_filter = TaskFilter(request.GET, queryset=tasks)
    tasks = task_filter.qs
    for task in tasks:
        max = (task.deadline - task.date_given).total_seconds()
        val = (dt.datetime.today() - task.date_given).seconds
        percentage = (val / max) * 100
        deadline_color = ''
        if percentage >= 100:
            deadline_color = 'red'
        status_color = {'new': '', 'processing': 'blue', 'done': 'green'}
        progresses.append({'value': val, 'max': max, 'percentage': percentage, 'deadline_color': deadline_color,
                           'status_color': status_color[task.status]})
    tasks = zip(tasks, progresses)

    context = {
        'tasks': tasks,
        'tasks_count': tasks_count,
        'tasks_new_count': tasks_new_count,
        'tasks_done_count': tasks_done_count,
        'tasks_processing_count': tasks_processing_count,
        'tasks_active': tasks_active,
        'sections_display': sections_display,
        'section': section,
        'my_section': section,
        'position': position,
        'sections': sections,
        'filter': task_filter,
    }
    return render(request, 'hrm/tasks.html', context)


@authenticated_required
@allowed_users(['director', 'managers'])
def statisticsView(request):
    return render(request, 'hrm/statistics.html')


@authenticated_required
@allowed_users(['director'])
def changePosition(request):
    if request.method == 'POST':
        _employee = models.Employee.objects.get(id=request.POST.get('employee_id')).user
        group = Group.objects.get(name=groupName(user=_employee))
        group_employee = Group.objects.get(name='employee')
        group_manager = Group.objects.get(name='manager')
        if group.name == 'manager':
            group.user_set.remove(_employee)
            _employee.groups.add(group_employee)
        if group.name == 'employee':
            group.user_set.remove(_employee)
            _employee.groups.add(group_manager)
        return redirect(request.POST.get('next'))


@authenticated_required
@allowed_users(['director'])
def addSectionView(request):
    if request.method == 'POST':
        models.Section.objects.create(name=request.POST.get("section_name"))
        return redirect(request.POST.get("next"))


@authenticated_required
@allowed_users(['manager'])
def mySectionView(request):

    employee = request.user.employee
    my_section = employee.section

    emps = request.user.employee.section.employee_set.all()
    managers = models.Employee.objects.none()
    employees = models.Employee.objects.none()
    for emp in emps:
        if groupName(user=emp.user) == 'manager':
            managers |= models.Employee.objects.filter(id=emp.id)
    for emp in emps:
        if groupName(user=emp.user) == 'employee':
            employees |= models.Employee.objects.filter(id=emp.id)

    if request.method == 'GET':
        if 'search_employee' in request.GET:
            e_filter = EmployeeFilter(request.GET, queryset=employees)
            employees = e_filter.qs
        elif 'search_manager' in request.GET:
            m_filter = EmployeeFilter(request.GET, queryset=managers)
            managers = m_filter.qs
    context = {'employees': employees, 'managers': managers, 'position': 'manager', 'my_section': my_section, 'sections_display': 'none', 'section_active': 'active'}

    return render(request, 'hrm/my_section.html', context=context)


@authenticated_required
def editProfileView(request):
    # navbar properties
    sections_display = 'none'
    section = ''
    position = ''
    if groupName(request) in ['director']:
        sections_display = ''
    elif groupName(request) == 'manager':
        section = request.user.employee.section.name
        position = 'manager'
    else:
        section = request.user.employee.section.name

    employee = request.user.employee
    context = {'employee': employee, 'position': position, 'sections_display': sections_display, 'my_section': section}
    return render(request, 'hrm/edit_profile.html', context)
