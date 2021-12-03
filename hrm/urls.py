from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginView, name='login'),
    path('console/', views.console, name='console'),
    path('add_employee', views.addEmployeeView, name='add_employee'),
    path('register/<str:token>', views.RegisterView.as_view(), name='register'),
    # path('employee', views.employeeView, name='employee'),
    path('employees/<str:pk>', views.employeeProfileView, name='employee_profile'),
    path('create_task', views.createTaskView, name='create_task'),
    path('edit_task/<str:pk>', views.editTaskView, name='edit_task'),
    path('logout', views.logoutView, name='logout'),
    path('task_info/<str:pk>', views.taskInfoView, name='task_info'),
    path('send_notification', views.sendNotificationView, name='send_notification'),
    path('tasks/', views.tasksView, name='tasks'),
    path('statistics', views.statisticsView, name='statistics'),
    path('change_position', views.changePosition, name='change_position'),
    path('add_section', views.addSectionView, name='add_section'),
    path('my_section', views.mySectionView, name='my_section'),
    path('view-task/<str:pk>', views.viewTaskView, name='view_task'),
    # path('edit-profile/', views.editProfileView, name='edit_profile')
    path('employee_profile_test/', TemplateView.as_view(template_name='hrm/tests/employee_profile.html')),
    path('settings/', views.settingsView, name='settings')
]
