from django.urls import path
from .views import getUserInfoView, getInfoView, createTaskView, searchUsersView, getTasksView, getTaskData, \
    createEmployeeView

urlpatterns = [
    path('get-user-info/<str:user_id>', getUserInfoView),
    path('get-info', getInfoView),
    path('create-task', createTaskView),
    path('search-users', searchUsersView),
    path('get-tasks', getTasksView),
    path('get-task-data/<str:task_id>', getTaskData),
    path('create-employee', createEmployeeView)
]
