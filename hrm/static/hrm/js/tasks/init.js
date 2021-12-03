var HOST = 'http://127.0.0.1:8000'

function fetchData() {
    $.ajax({
        url: HOST + `/api/get-info`,
        type: 'GET',
        data: {
            sections: 'get'
        },
        success: (data) => {
            console.log(data)
            $('#id_nav_tasks').attr('class', 'nav-item active')

            data['sections'].map((section) => {
                    const select_option = $(`<option value="${section.name}">${section.name}</option>`)
                    $('#id_section_select').append(select_option)
                }
            )

        },
        error: (res) => {
            alert('error')
        },
    })
}


function searchTasks(data) {
    $.ajax({
        url: HOST + '/api/get-tasks',
        type: 'GET',
        data: data,
        success: (res) => {
            $('#id_body').css('display', 'block')
            console.log(res)
            buildTasksCount(res['counts'])
            buildTasks(res)
        },
        error: (res) => {
            console.log(res.message)
        }
    })
}

fetchData()


