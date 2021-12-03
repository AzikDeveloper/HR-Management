
$('#createTaskModal').on('show.bs.modal', function (event) {
    let button = $(event.relatedTarget)
    let assign_to = button.data('id')
    let assign_to_name = button.data('name')
    $("#id_assigned_to_id").val(assign_to);
    $('#id_assigned_to_input').val(assign_to_name)
})

$("#id_create_task_form").on('submit', (e) => {
    const csrftoken = getCookie('csrftoken');

    const loader = $('#id_create_task_loader')
    const loader_text = $('#id_create_task_loader_text')
    loader.attr('class', 'loader mr-auto')
    loader_text.attr('class', 'mr-auto')
    loader_text.html('Loading&#8230;')

    e.preventDefault()
    const data = {
        'assigned_to': $('#id_assigned_to_id').val(),
        'name': $('#id_name').val(),
        'context': $('#id_context').val(),
        'deadline': $('#id_deadline').val()
    }

    $.post({
        url: HOST + '/api/create-task',
        type: 'POST',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify(data),
        success: onCreateTaskSuccess,
        error: onCreateTaskError
    })

    function onCreateTaskSuccess(res) {
        loader.attr('class', 'd-none')
        loader_text.attr('class', 'd-none')
        $(function () {
            $('#createTaskModal').modal('toggle');
        });
    }

    function onCreateTaskError(res) {
        loader.attr('class', 'd-none')
        loader_text.html(`<span class="text-danger">Failed to create task! error[${res.status}]</span>`)
        if (res['status'] === 401) {
            window.location.replace("http://127.0.0.1:8000/login");
        }
    }
})
