const HOST = 'http://127.0.0.1:8000'

function fetchData() {
    $.ajax({
        url: HOST + `/api/get-info`,
        type: 'GET',
        data: {
            sections: 'get',
            positions: 'get'
        },
        success: (data) => {
            $('#id_nav_home').attr('class', 'nav-item active')

            data['sections'].map((section) => {
                    const select_option = $(`<option value="${section.name}">${section.name}</option>`)
                    $('#id_sections_select').append(select_option)
                }
            )
            data['positions'].map((position) => {
                    if (position.name !== 'Director') {
                        const select_option = $(`<option value="${position.name}">${position.name}</option>`)
                        $('#id_position_select').append(select_option)
                    }
                }
            )
        },
        error: (res) => {
            alert('error')
        },
    })
    preSearch(1)
}


fetchData()

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

function preSearch(page) {
    const keyword = $('#id_search_users_keyword').val()
    const position = $('#id_position_select').val()
    const section = $('#id_sections_select').val()
    const position_not = $('#id_checkbox_position_not').is(':checked')
    const section_not = $('#id_checkbox_section_not').is(':checked')

    var _position = ''
    var _section = ''

    if (position_not) {
        _position = '-'
    }
    if (section_not) {
        _section = '-'
    }
    const data = {
        keyword: keyword,
        position: position,
        _position: _position,
        section: section,
        _section: _section,
        page: page
    }

    searchUsers(data)
}

function searchUsers(data) {
    $.ajax({
        url: HOST + '/api/search-users',
        type: 'GET',
        data: data,
        success: (res) => {
            paginate({
                page: res['page'],
                num_pages: res['num_pages']
            })
            $('#id_body').css('display', 'block')
            buildUserList(res['users'], data['keyword'][0])
        },
        error: (res) => {
            console.log(res.message)
        }
    })
}

function buildUserList(data, highlight) {
    const tbody = $(`#id_users_table_tbody`)
    tbody.html('')
    const highlight_checkbox = $('#id_checkbox_highlight').is(':checked')
    data.map(
        (user) => {
            const data_name = (user.first_name || '---') + ' ' + (user.last_name || '---') + ' ' + user.username
            const row = $(`
                        <tr class="d-flex">
                                <td class="col-2 ">${highlightText(user.first_name, highlight, highlight_checkbox)}</td>
                                <td class="col-2 ">${highlightText(user.last_name, highlight, highlight_checkbox)}</span></td>
                                <td class="col-3 ">${highlightText(user.username, highlight, highlight_checkbox)}</td>
                                <td class="col-2 ">${user.section}</td>
                                <td class="col-1 ">${user.position}</td>
                                <td class="col-1 text-center">
                                    <button
                                        class="btn btn-sm btn-outline-info" data-toggle="modal"
                                        data-target="#createTaskModal" data-id="${user.id}"
                                        data-name="${data_name}" data-backdrop="static" data-keyboard="false"
                                        >+</button>
                                </td>
                                <td class="col-1 text-center">
                                    <button
                                        class="btn btn-sm btn-outline-info" data-toggle="modal"
                                        data-target="#employeeProfileModal" data-id="${user.id}">View</button>
                            </tr>
                    `)
            tbody.append(row)
        }
    )

}

function highlightText(word, highlight, highlight_checkbox) {
    if (highlight && highlight_checkbox && word) {
        if (word.toLowerCase().includes(highlight.toLowerCase())) {
            return `<span class="highlight">${word}</span>`
        }
    }
    return placeHolderForNull(word)
}

function placeHolderForNull(word) {
    if (word) {
        return word
    } else {
        return '-----'
    }
}

