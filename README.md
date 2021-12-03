# Hr management app.
### Description:
This app lets you control your employees in your company by giving tasks.

### Positions in the app
There are 3 types of positions in this app: director, manager, employee.
Director can add employees and managers. Director can change the position of managers and employees.
Managers can add employees but can't add managers.

### Sections
Director can add company sections.
all the employees and managers are belong to only one section.

### Tasks
Every task includes: name, date given, context, deadline time and status.
There are 3 types of statuses in a task: new, processing, done.

### Giving tasks
Director can give tasks to managers and employees.
Managers can only give tasks to employees.
Only task authors can change task informations. Even Director can't modify a task if he is not the giver of the task.

### Director, Manager, Employee rights
Director can access to Django's default administration panel and control over the whole database.
Managers can only see the tasks whose task givers are in the section that is the same section of himself.
Employees can see the tasks that are assigned to them. Employees can change the status of a task and write a note in the task.

### Registering employees
In a section Director or Managers can add employees by just their emails.
Director can set an employee as a manager while adding.
When a new employee is added, an unique link will be generated and send to the email.
Email owner can click on the link and complete their registration by adding username, full name and password.
