$('#viewTaskModal').on('show.bs.modal', function (event) {
    console.log('yoo')
    let button = $(event.relatedTarget)
    let user_id = button.data('id')
    fetchTaskData(user_id)
})

function fetchTaskData(task_id) {
    $.ajax({
        url: HOST + `/api/get-task-data/${task_id}`,
        type: 'GET',
        success: onSuccess,
        error: (res) => {
            console.log(res.message)
        }
    })
}

function onSuccess(data) {
    const task_giver_photo = $('#id_task_giver_photo_img')
    const assigned_to_photo = $('#id_assigned_to_img')
    const task_giver_name = $('#id_task_giver_name')
    const assigned_to_name = $('#id_assigned_to_name')
    const task_name = $('#id_task_name')
    const task_context = $('#id_task_context')
    const deadline = $('#id_task_deadline')
    const date_given = $('#id_date_given')

    task_giver_name.html('')
    assigned_to_name.html('')
    task_context.val('')
    task_name.val('')
    deadline.val('')


    task_giver_photo.attr('src', data['task']['task_giver']['photo'])
    assigned_to_photo.attr('src', data['task']['assigned_to']['photo'])

    task_giver_name.html(data['task']['task_giver']['name'])
    assigned_to_name.html(data['task']['assigned_to']['name'])

    task_name.val(data['task']['name'])
    task_context.val(data['task']['context'])
    deadline.val(data['task']['deadline'])

    if (data['can_edit']) {
        task_name.prop('disabled', false)
        task_context.prop('disabled', false)
        deadline.prop('disabled', false)
    }else {
        task_name.prop('disabled', true)
        task_context.prop('disabled', true)
        deadline.prop('disabled', true)
    }

}
