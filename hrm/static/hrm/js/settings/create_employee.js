$('#id_create_employee_form').on('submit', (e) => {
    e.preventDefault()
    const email = $('#id_email_input')
    const section = $('#id_section_select')
    const position = $('#id_position_select')

    const create_button = $('#id_create_employee_button')
    create_button.prop('disabled', true)

    const loader = $('#id_create_task_loader')
    const loader_text = $('#id_create_task_loader_text')
    loader.attr('class', 'loader mr-auto')
    loader_text.attr('class', 'mr-auto')
    loader_text.html('')

    const csrftoken = getCookie('csrftoken');
    const data = {
        email: email.val(),
        section: section.val(),
        position: position.val()
    }
    $.ajax({
        url: HOST + '/api/create-employee',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        type: 'POST',
        data: JSON.stringify(data),
        success: onCreateEmployeeSuccess,
        error: onCreateEmployeeError
    })

    function onCreateEmployeeSuccess(data) {
        console.log(data)
        create_button.prop('disabled', false)
        loader.attr('class', 'd-none')
        loader_text.attr('class', 'd-none')
    }

    function onCreateEmployeeError(res) {
        create_button.prop('disabled', false)
        loader.attr('class', 'd-none')
        console.log(res)
        loader_text.html(`<span class="text-danger">${res['responseJSON']['message']}</span>`)
        if (res['status'] === 401) {
            window.location.replace("http://127.0.0.1:8000/login");
        }
    }
})

