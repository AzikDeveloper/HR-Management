import datetime as dt


def in_groups(request, groups=None):
    if groups is None:
        groups = []
    if request.user.groups.filter(name__in=groups).exists():
        return True
    else:
        return False


def calculateProgresses(tasks):
    progresses = []
    for task in tasks:
        max_time = (task.deadline - task.date_given).total_seconds()

        if task.deadline <= dt.datetime.today():
            percentage = 100
        else:
            delta_time = (dt.datetime.today() - task.date_given).total_seconds()
            percentage = (delta_time / max_time) * 100

        deadline_color = ''
        if percentage >= 100:
            deadline_color = 'red'

        status_color = {'new': '', 'processing': 'blue', 'done': 'green'}
        progresses.append({
            'percentage': percentage,
            'deadline_color': deadline_color,
            'status_color': status_color[task.status]
        })

    return progresses
