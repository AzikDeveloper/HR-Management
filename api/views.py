from django.db.models import Q
from django.contrib.auth.models import Group
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.decorators import authenticated_required, allowed_users
from django.contrib.auth.models import User
from api.serializers import UserSerializer, ConsoleUserSerializer, SectionSerializer, TaskSerializer, \
    PositionSerializer, TaskViewSerializer
from django.core.paginator import Paginator, EmptyPage
from hrm.forms import CreatePreUserForm
from hrm.models import Section, Task
from .tools import andQ


@api_view(['GET'])
@authenticated_required
def getUserInfoView(request, user_id):
    user = User.objects.get(id=user_id)
    user = UserSerializer(user)
    return Response(user.data)


@api_view(['POST'])
@authenticated_required
@allowed_users(['Director', 'Manager'])
def createTaskView(request):
    assigned_to_user = User.objects.get(id=request.data['assigned_to'])
    if request.session['position'] == 'Director' or assigned_to_user.info.section == request.user.info.section:
        pass
    else:
        return Response(status=400)
    request.data['task_giver'] = request.user.id

    task = TaskSerializer(data=request.data)

    if task.is_valid():
        task.save()
        return Response({'message': 'Task is created!'})
    else:
        print(task.errors)
        return Response({'message': 'Failed to create task'}, status=400)


@api_view(['GET'])
@authenticated_required
@allowed_users(['Director'])
def getInfoView(request):
    response = {}
    if 'sections' in request.GET.keys():
        sections = Section.objects.all()
        response['sections'] = SectionSerializer(sections, many=True).data

    if 'positions' in request.GET.keys():
        groups = Group.objects.all()
        response['positions'] = PositionSerializer(groups, many=True).data

    # if 'permissions' in request.GET.keys():
    #     pass
    #
    # if 'users' in request.GET.keys():
    #     pass

    return Response(data=response)


@api_view(['GET'])
@authenticated_required
@allowed_users(['Director'])
def searchUsersView(request):
    max_num_in_per_page = 20

    page = int(request.GET.get('page'))

    keyword = request.GET.get('keyword')
    position = request.GET.get('position'), request.GET.get('_position')
    section = request.GET.get('section'), request.GET.get('_section')

    q_c = {
        Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(username__icontains=keyword):
            (keyword, '+'),
        Q(groups__name=position[0].capitalize()): (position[0] != 'all', position[1]),
        Q(info__section__name=section[0]): (section[0] != 'all', section[1])
    }
    filter_mask = andQ(q_c)

    users = User.objects.filter(filter_mask) if filter_mask else User.objects.all()
    users_paginator = Paginator(users.exclude(groups__name='Director').order_by('first_name'), max_num_in_per_page)
    num_pages = users_paginator.num_pages

    try:
        paginated_users = users_paginator.page(page)
    except EmptyPage:
        page = 1
        paginated_users = users_paginator.page(page)

    serializer = ConsoleUserSerializer(paginated_users, many=True)

    return Response(data={
        'users': serializer.data,
        'num_pages': num_pages,
        'page': page
    })


@api_view(['GET'])
@authenticated_required
@allowed_users(['Director', 'Manager'])
def getTasksView(request):
    max_num_in_per_page = 20

    page = int(request.GET.get('page'))
    section = request.GET.get('section')
    name = request.GET.get('name')
    task_giver = request.GET.get('task_giver')
    assigned_to = request.GET.get('assigned_to')
    status = request.GET.get('status')

    tasks = None
    if request.session['position'] == 'Director':
        q_c = {
            Q(task_giver__info__section__name=section): (section != 'all', '+')
        }
        tasks = Task.objects.filter(andQ(q_c))
    elif request.session['position'] == 'Manager':
        tasks = Task.objects.filter(
            Q(task_giver__info__section__id=request.user.info.section.id) |
            Q(assigned_to__info__section_id=request.user.info.section.id)
        )
    tasks_count = tasks.count()
    tasks_done_count = tasks.filter(status='done').count()
    tasks_processing_count = tasks.filter(status='processing').count()
    tasks_new_count = tasks_count - tasks_done_count - tasks_processing_count

    q_c = {
        Q(name__contains=name): (name, '+'),
        Q(task_giver__username__icontains=task_giver): (task_giver, '+'),
        Q(assigned_to__username__icontains=assigned_to): (assigned_to, '+'),
        Q(status=status): (status != 'all', '+')
    }
    filter_mask = andQ(q_c)

    tasks = tasks.filter(filter_mask)

    tasks_paginator = Paginator(tasks.order_by('name'), max_num_in_per_page)
    num_pages = tasks_paginator.num_pages
    try:
        paginated_tasks = tasks_paginator.page(page)
    except EmptyPage:
        page = 1
        paginated_tasks = tasks_paginator.page(page)

    response = {
        'counts': {
            'total': tasks_count,
            'new': tasks_new_count,
            'processing': tasks_processing_count,
            'done': tasks_done_count
        },
        'tasks': TaskSerializer(paginated_tasks, many=True).data,
        'pagination': {
            'page': page,
            'num_pages': num_pages
        }
    }
    return Response(data=response)


@api_view(['GET'])
@authenticated_required
@allowed_users(['Director', 'Manager', 'Employee'])
def getTaskData(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.session['position'] == 'Manager' and task.task_giver.info.section == request.user.info.section or \
            request.session['position'] == 'Director':
        pass
    else:
        return Response(data={
            'ok': False,
            'message': 'You are not authorized to access this data!'
        }, status=401)

    serializer = TaskViewSerializer(task)

    can_edit = False
    if request.session['position'] == 'Director':
        can_edit = True
    elif request.user == task.task_giver:
        can_edit = True

    data = {
        'can_edit': can_edit,
        'task': serializer.data
    }
    return Response(data=data)


@api_view(['POST'])
@authenticated_required
@allowed_users(['Director', 'Manager'])
def createEmployeeView(request):
    email = request.data.get("email")
    if request.session['position'] == 'Director':
        section = Section.objects.get(id=request.data.get("section"))
        group = Group.objects.get(id=request.data.get("position"))
    else:
        section = request.user.info.section
        group = Group.objects.get(name='Employee')

    form = CreatePreUserForm(username=email, email=email, section=section, group=group)
    if form.is_created():
        return Response(data={
            'ok': True,
            'message': 'employee is created'
        })
    else:
        return Response(data={
            'ok': False,
            'message': form.error_message
        }, status=400)
