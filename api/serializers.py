from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField, DateTimeField
from django.contrib.auth.models import User
from hrm.models import Info, Address, Task, Section
from django.contrib.auth.models import Group
import datetime as dt


class TaskViewSerializer(ModelSerializer):
    task_giver = SerializerMethodField()
    assigned_to = SerializerMethodField()

    class Meta:
        model = Task
        fields = ['task_giver', 'assigned_to', 'name', 'date_given', 'deadline', 'context', 'note']

    def get_task_giver(self, task):
        try:
            name = f'{task.task_giver.first_name} {task.task_giver.last_name}'
        except AttributeError:
            name = '-----'

        try:
            photo = task.task_giver.info.photo.url
        except ValueError:
            photo = f'https://avatars.dicebear.com/api/gridy/{task.task_giver.id}.svg'
        except AttributeError:
            photo = 'https://avatars.dicebear.com/api/gridy/-1.svg'
        data = {
            'name': name,
            'photo': photo
        }
        return data

    def get_assigned_to(self, task):
        try:
            name = f'{task.assigned_to.first_name} {task.assigned_to.last_name}'
        except AttributeError:
            name = '-----'
        try:
            photo = task.assigned_to.info.photo.url
        except ValueError:
            photo = f'https://avatars.dicebear.com/api/gridy/{task.assigned_to.id}.svg'
        except AttributeError:
            photo = 'https://avatars.dicebear.com/api/gridy/-1.svg'

        data = {
            'name': name,
            'photo': photo
        }
        return data


class TaskSerializer(ModelSerializer):
    deadline_percentage = SerializerMethodField('get_percentage')
    task_giver = CharField()
    assigned_to = CharField()
    deadline = DateTimeField(format='%d.%m.%Y')
    date_given = DateTimeField(format='%d.%m.%Y', required=False)

    class Meta:
        model = Task
        fields = ['id', 'name', 'task_giver', 'assigned_to', 'date_given', 'deadline', 'status', 'deadline_percentage']

    def create(self, validated_data):
        data = validated_data
        data['task_giver'] = User.objects.get(id=int(validated_data['task_giver']))
        data['assigned_to'] = User.objects.get(id=int(validated_data['assigned_to']))

        task = Task.objects.create(**data)
        return task

    def get_percentage(self, task):
        max_time = (task.deadline - task.date_given).total_seconds()

        if task.deadline <= dt.datetime.today():
            percentage = 100
        else:
            delta_time = (dt.datetime.today() - task.date_given).total_seconds()
            percentage = (delta_time / max_time) * 100
        return percentage


class PositionSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class SectionSerializer(ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name']


class InfoSerializer(ModelSerializer):
    address = AddressSerializer()
    section = SectionSerializer()
    photo = SerializerMethodField()

    class Meta:
        model = Info
        fields = ['photo', 'salary', 'phone', 'about', 'section', 'address']

    def get_photo(self, info):
        try:
            photo = info.photo.url
        except ValueError:
            photo = f'https://avatars.dicebear.com/api/gridy/{info.user.id}.svg'
        return photo


class UserSerializer(ModelSerializer):
    info = InfoSerializer()
    tasks_count_info = SerializerMethodField()
    group = SerializerMethodField()
    rating = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'info', 'tasks_count_info', 'group', 'rating']

    def get_group(self, user):
        return user.groups.first().name

    def get_tasks_count_info(self, user):
        tasks = user.tasks_to_me.all()
        self._tasks = tasks
        total_count = tasks.count()
        done_count = tasks.filter(status='done').count()
        processing_count = tasks.filter(status='processing').count()
        new_count = total_count - done_count - processing_count

        result = {
            'total': total_count,
            'done': done_count,
            'processing': processing_count,
            'new': new_count
        }
        return result

    def get_rating(self, user):
        sum_rate = 0
        rated_tasks = self._tasks.exclude(rate__isnull=True)
        for task in rated_tasks:
            sum_rate += task.rate
        if rated_tasks:
            rate = format(round(sum_rate / rated_tasks.count(), 1), '.1f')
        else:
            rate = 0
        return rate


class ConsoleUserSerializer(ModelSerializer):
    position = SerializerMethodField()
    section = CharField(source='info.section')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'position', 'section']

    def get_position(self, user):
        return user.groups.first().name
