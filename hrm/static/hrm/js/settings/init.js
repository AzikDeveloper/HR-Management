var HOST = 'http://127.0.0.1:8000'

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$('#id_nav_settings').attr('class', 'nav-item active')

function fetchData() {
    $.ajax({
        url: HOST + '/api/get-info', type: 'GET', data: {
            sections: 'get', positions: 'get'
        }, success: onSuccess, error: (res) => {
            alert('error')
        }
    })
}

function onSuccess(data) {
    console.log(data)
    data['sections'].map((section) => {
        const select_option = $(`<option value="${section.id}">${section.name}</option>`)
        $('#id_section_select').append(select_option)
    })
    data['positions'].map((position) => {
        console.log(position.name)
        if (position.name !== 'Director') {
            const select_option = $(`<option value="${position.id}" ${(position.name === 'Employee') ? 'selected' : ''}>${position.name}</option>`)
            $('#id_position_select').append(select_option)
        }
    })
}

fetchData()