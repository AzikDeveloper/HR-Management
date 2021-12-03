function fetchUserViewData(user_id) {
    $.get({
        url: HOST + `/api/get-user-info/${user_id}`,
        type: 'GET',
        success: onSuccess,
        error: onError,
    })


    function onSuccess(data) {
        const pic = $('#id_profile_picture')
        pic.attr('src', ``)
        pic.attr('src', data['info']['photo'])

        pic.on('load', () => {
                $('#id_profile_view').attr('class', 'modal-body p-0 m-0')
                $('#id_profile_loader').attr('class', 'd-none')
                $('#id_profile_loader_text').attr('class', 'd-none')
            }
        )


        $('#id_first_name').html(data['first_name'])
        $('#id_last_name').html(data['last_name'])
        $('#id_username').html('@' + data['username'])
        $('#id_tasks_count').html(data['tasks_count_info']['total'])
        $('#id_tasks_done_count').html((data['tasks_count_info']['done']))
        $('#id_group').html(data['group'])
        $('#id_section').html((data['info']['section']['name']))
        $('#id_rating').html(data['rating'])
        $('#id_about').html(data['info']['about'])
        $('#id_section_href').attr('href', 'http://127.0.0.1:8000/sections/' + data['info']['section']['id'])
        $('#id_profile_go').attr('href', 'http://127.0.0.1:8000/employees/' + data['id']).attr('style', 'display: block')

        let address = data['info']['address']
        if (address == null) {
            address = ''
        } else {
            address = `${data['info']['address']['home_number']} ${data['info']['address']['street']} ${data['info']['address']['state']} ${data['info']['address']['city']} ${data['info']['address']['country']}`
        }

        $('#id_address').html(address + '<br><br>')

    }

    function onError(data) {
        $('#id_profile_loader').attr('class', '')
        $('#id_profile_loader_text').html('<span class="text-danger">Failed to retrieve data!</span>').attr('class', 'mr-auto')
        if (data['status'] === 401) {
            window.location.replace("http://127.0.0.1:8000/login");
        }
    }


}


$('#employeeProfileModal').on('show.bs.modal', function (event) {
    $('#id_address_h').attr('class', '')
    $('#id_profile_go').attr('style', 'display: none;')
    $('#id_profile_view').attr('class', 'modal-body p-0 m-0 d-none')
    $('#id_profile_loader').attr('class', 'loader mr-auto')
    $('#id_profile_loader_text').attr('class', 'mr-auto').html(`Loading&#8230;`)
    let button = $(event.relatedTarget)
    let user_id = button.data('id')
    fetchUserViewData(user_id)
})
