# django stuff
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import *
# my tools
from .decorators import redirect_if_authenticated, authenticated_required, allowed_users
from .my_tools import fullNameParser, groupName, firstFormError
from .models import *

# filters and Forms
from .forms import CreateTaskForm, CreateUserForm
from .filters import EmployeeFilter, TaskFilter

# built in tools
import datetime as dt


@redirect_if_authenticated
@authenticated_required
def home(request):
    return render(request, 'hrm/home.html')


def registerView(request, pk):
    if len(pk) == 36:
        gen_link = GenLink.objects.filter(link=uuid.UUID(pk))
        if gen_link:
            if request.method == 'POST':
                request_post = fullNameParser(request)
                if request_post:
                    if '@' in request.POST.get('username'):
                        context = {
                            'error': '@ is not allowed in username',
                            'full_name': request.POST.get('full_name'),
                            'username': request.POST.get('username'),
                            'password1': request.POST.get('password1'),
                            'password2': request.POST.get('password2')
                        }
                        return render(request, 'hrm/register.html', context)
                    else:
                        form = CreateUserForm(request_post)
                        if form.is_valid():
                            employee = gen_link[0].employee
                            user = employee.user
                            user.username = request_post.get('username')
                            user.set_password(request_post.get('password1'))
                            employee.first_name = request_post.get('first_name')
                            employee.last_name = request_post.get('last_name')
                            user.save()
                            employee.save()
                            gen_link.delete()
                            return redirect('login')
                        else:
                            context = {
                                'error': firstFormError(form),
                                'full_name': request.POST.get('full_name'),
                                'username': request.POST.get('username'),
                                'password1': request.POST.get('password1'),
                                'password2': request.POST.get('password2')
                            }
                            return render(request, 'hrm/register.html', context)
                else:
                    context = {
                        'error': 'Wrong full name!',
                        'full_name': request.POST.get('full_name'),
                        'username': request.POST.get('username'),
                        'password1': request.POST.get('password1'),
                        'password2': request.POST.get('password2')
                    }
                    return render(request, 'hrm/register.html', context)
            return render(request, 'hrm/register.html')
        else:
            return HttpResponse("<h1>404 not found")
    else:
        return HttpResponse("<h1>404 not found")


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
            return render(request, 'hrm/login.html', context)
    return render(request, 'hrm/login.html')


@authenticated_required
@allowed_users(['Director'])
def console(request):
    # navbar properties
    home_active = 'active'
    sections = Section.objects.all()

    employees = Employee.objects.filter(position__name='Employee')
    managers = Employee.objects.filter(position__name='Manager')

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
        'home_active': home_active,
        'sections': sections
    }

    return render(request, 'hrm/console.html', context)


@authenticated_required
@allowed_users(['Director', 'Manager'])
def addEmployeeView(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.create_user(username=email, email=email)
        if groupName(request) == 'Director':
            if request.POST.get("as_manager") == "true":
                position = Position.objects.get(name='Manager')
            else:
                position = Position.objects.get(name='Employee')
        else:
            position = Position.objects.get(name='Employee')
        user.save()

        employee = user.employee
        employee.position = position
        employee.section = Section.objects.get(id=request.POST.get("section_id"))
        employee.save()

        return redirect(request.POST.get("next"))
    else:
        return HttpResponse('<h3>404 not found </h3>')


@authenticated_required
@allowed_users(['Employee', 'Manager'])
def employeeView(request):
    employee = request.user.employee
    messages = request.user.received_messages.all()

    tasks = employee.tasks_to_me.all()
    tasks_count = tasks.count()
    tasks_done_count = tasks.filter(status='done').count()

    # filtering tasks
    task_filter = TaskFilter(request.GET, queryset=tasks)
    tasks = task_filter.qs

    progresses = []
    for task in tasks:
        max_seconds = (task.deadline - task.date_given).total_seconds()
        delta_seconds = (dt.datetime.today() - task.date_given).seconds
        percentage = (delta_seconds / max_seconds) * 100
        deadline_color = ''
        if percentage >= 100:
            deadline_color = 'red'
        status_color = {'new': '', 'processing': 'blue', 'done': 'green'}
        progresses.append({
            'value': delta_seconds,
            'max': max_seconds,
            'percentage': percentage,
            'deadline_color': deadline_color,
            'status_color': status_color[task.status]
        })
    tasks = zip(tasks, progresses)

    context = {
        'employee': employee,
        'messages': messages,
        'tasks': tasks,
        'tasks_count': tasks_count,
        'tasks_done_count': tasks_done_count,
        'filter': task_filter,

        # navbar properties
        'home_active': 'active',
    }
    return render(request, 'hrm/employee.html', context)


@authenticated_required
@allowed_users(['Manager', 'Director'])
def employeeProfileView(request, pk):
    # navbar properties
    sections = Section.objects.all()

    try:
        employee = Employee.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponse("<h3>404 not found!</h3>")

    if employee == request.user.employee:
        return redirect('/')

    tasks = employee.tasks_to_me.all()
    tasks_count = tasks.count()
    tasks_done_count = tasks.filter(status='done').count()

    progresses = []
    for task in tasks:
        max_seconds = (task.deadline - task.date_given).total_seconds()
        delta_seconds = (dt.datetime.today() - task.date_given).seconds
        percentage = (delta_seconds/max_seconds)*100
        deadline_color = ''
        if percentage >= 100:
            deadline_color = 'red'
        status_color = {'new': '', 'processing': 'blue', 'done': 'green'}
        progresses.append({
            'value': delta_seconds,
            'max': max_seconds,
            'percentage': percentage,
            'deadline_color': deadline_color,
            'status_color': status_color[task.status]
        })

    tasks = zip(tasks, progresses)

    if request.method == "POST":
        if request.POST.get("post_status") == "sendMessage":
            Notification.objects.create(sender=request.user, receiver=employee.user, text=request.POST.get('message'))

    context = {
        'employee': employee,
        'tasks': tasks,
        'tasks_count': tasks_count,
        'tasks_done_count': tasks_done_count,

        # navbar properties
        'sections': sections
    }
    return render(request, 'hrm/employee_profile.html', context)


@authenticated_required
@allowed_users(['Director', 'Manager'])
def createTaskView(request, pk):
    # navbar properties
    sections = Section.objects.all()

    try:
        user = Employee.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponse("<h3>404 employee not found</h3>")

    form = CreateTaskForm(initial={'assigned_to': user, 'status': 'new'})

    if request.method == "POST":
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            task.task_giver = request.user.employee
            task.save()
            return redirect(request.GET.get('next'))
        else:
            pass

    context = {
        'form': form,

        # navbar properties
        'sections': sections,
    }
    return render(request, 'hrm/create_task.html', context)


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
        try:
            employee = Employee.objects.get(id=request.POST.get("employee_id"))
        except ObjectDoesNotExist:
            return HttpResponse("<h3>receiver not found!</h3>")

        if len(request.POST.get('message')) > 0:
            Notification.objects.create(sender=request.user, receiver=employee.user, text=request.POST.get('message'))

        return redirect(request.POST.get("next"))


@authenticated_required
@allowed_users(['Director'])
def sectionView(request, pk):
    # navbar properties
    sections = Section.objects.all()
    try:
        section = Section.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponse("<h3>404 section not found!")

    employees_in_section = section.employees_by_section.all()

    employees = employees_in_section.filter(position__name='Employee')
    managers = employees_in_section.filter(position__name='Manager')

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
        'sections_active': 'active',
        'section': section,
        'sections': sections
    }
    return render(request, 'hrm/section.html', context)


@authenticated_required
@allowed_users(['Director', 'Manager'])
def tasksView(request):
    # navbar properties
    sections = Section.objects.all()
    tasks = None

    if groupName(request) == 'Manager':
        tasks = Task.objects.filter(task_giver__section=request.user.employee.section)
    elif groupName(request) == 'Director':
        tasks = Task.objects.all()

    tasks_count = tasks.count()
    tasks_done_count = tasks.filter(status='done').count()
    tasks_processing_count = tasks.filter(status='processing').count()
    tasks_new_count = tasks_count - tasks_done_count - tasks_processing_count

    # filtering tasks
    task_filter = TaskFilter(request.GET, queryset=tasks)
    tasks = task_filter.qs

    progresses = []
    for task in tasks:
        max_seconds = (task.deadline - task.date_given).total_seconds()
        delta_seconds = (dt.datetime.today() - task.date_given).seconds
        percentage = (delta_seconds / max_seconds) * 100
        deadline_color = ''
        if percentage >= 100:
            deadline_color = 'red'
        status_color = {'new': '', 'processing': 'blue', 'done': 'green'}
        progresses.append({
            'value': delta_seconds,
            'max': max_seconds,
            'percentage': percentage,
            'deadline_color': deadline_color,
            'status_color': status_color[task.status]
        })
    tasks = zip(tasks, progresses)

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
    return render(request, 'hrm/tasks.html', context)


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
    employees_in_section = request.user.employee.section.employees_by_section.all()

    employees = employees_in_section.filter(position__name='Employee')
    managers = employees_in_section.filter(position__name='Manager')

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


@authenticated_required
def editProfileView(request):
    context = {}
    if request.method == 'POST':
        r_post = fullNameParser(request)
        if r_post:
            try:
                user = request.user
                user.username = r_post.get("username")
                user.save()

                employee = request.user.employee
                employee.first_name = r_post.get("first_name")
                employee.last_name = r_post.get("last_name")
                employee.email = r_post.get("email")
                employee.phone = r_post.get("phone")
                employee.about = r_post.get("about")
                address = Address.objects.create(
                    street=r_post.get("street"),
                    state=r_post.get("state"),
                    city=r_post.get("city"),
                    zip_code=int(r_post.get("zip_code")),
                    country=r_post.get("country")
                )
                employee.address = address
                employee.save()
            except Exception:
                pass
        else:
            context['error'] = 'wrong full name'

    employee = request.user.employee
    context = {
        'employee': employee
    }
    return render(request, 'hrm/edit_profile.html', context)
