function buildTasksCount(data) {
    $('#id_tasks_total_count').html(data['total'])
    $('#id_tasks_new_count').html(data['new'])
    $('#id_tasks_processing_count').html(data['processing'])
    $('#id_tasks_done_count').html(data['done'])
}
preSearch(1)

function preSearch(page, not_send_filter) {
    const section = $('#id_section_select').val()
    const name = $('#id_name_input')
    const status = $('#id_status_select')
    const task_giver = $('#id_task_giver_input')
    const assigned_to = $('#id_assigned_to_input')
    if (!not_send_filter) {
        const data = {
            page: page,
            section: section,
            name: name.val(),
            task_giver: task_giver.val(),
            assigned_to: assigned_to.val(),
            status: status.val()
        }
        searchTasks(data)
    } else {
        const data = {
            page: page,
            section: section,
            name: '',
            task_giver: '',
            assigned_to: '',
            status: 'all'
        }
        searchTasks(data)
        name.val('')
        task_giver.val('')
        assigned_to.val('')
        status.val('all')
    }

}

function buildTasks(data) {
    const tbody = $('#id_tbody_tasks')
    tbody.html('')
    paginate({
        page: data['pagination']['page'],
        num_pages: data['pagination']['num_pages']
    })
    data['tasks'].map(
        (task) => {
            var status_color = ''
            var deadline_color = ''
            if (task['status'] === 'done') {
                status_color = 'green'
            }
            if (task['deadline_percentage'] === 100) {
                deadline_color = 'red'
            }
            const row = $(`<tr class="d-flex">
                    <td class="col-2">${task['name']}</td>
                    <td class="col-2"><a href="" style="color: rgba(10,85,201,0.87)">${task['task_giver']}</a></td>
                    <td class="col-2"><a href="" style="color: rgba(10,85,201,0.87)">${task['assigned_to']}</a></td>
                    <td class="col-1">${task['date_given']}</td>
                    <td class="col-2" title="${Math.trunc(task['deadline_percentage'])}%">
                        <progress id="progress" value="${task['deadline_percentage']}" max="100">
                            ${task['deadline_percentage']}%
                        </progress>
                    </td>
                    <td class="col-1" style="color: ${deadline_color};">${task['deadline']}</td>
                    <td class="col-1" style="color: ${status_color};"><b>${task['status']}</b></td>

                    <td class="col-1 text-center"><button type="button"
                           class="btn btn-sm btn-info" data-toggle="modal"
                                        data-target="#viewTaskModal" data-id="${task['id']}"
                                        data-backdrop="static" data-keyboard="false">View</button>
                    </td>
                </tr>`)
            tbody.append(row)
        }
    )
}


