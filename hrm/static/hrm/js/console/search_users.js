$('#id_users_search_button').click(function () {
    preSearch(1)
})


$('#id_position_select').on('change', () => {

    const this_value = $('#id_position_select').val()
    const search_keyword_input = $('#id_search_users_keyword')
    const search_section_select = $('#id_sections_select').val()

    if (this_value === 'all') {
        if (search_section_select === 'all') {
            search_keyword_input.attr('placeholder', `search ${this_value} in all sections`)
        } else {
            search_keyword_input.attr('placeholder', `search ${this_value.toLowerCase()} in ${search_section_select} section`)
        }
    } else {
        if (search_section_select === 'all') {
            search_keyword_input.attr('placeholder', `search ${this_value.toLowerCase()}s in all sections`)
        } else {
            search_keyword_input.attr('placeholder', `search ${this_value.toLowerCase()}s in ${search_section_select} section`)
        }
    }

})
$('#id_sections_select').on('change', () => {

    const this_value = $('#id_sections_select').val()
    const search_keyword_input = $('#id_search_users_keyword')
    const search_position_select = $('#id_position_select').val()

    if (this_value === 'all') {
        if (search_position_select === 'all') {
            search_keyword_input.attr('placeholder', `search all in ${this_value} section`)
        } else {
            search_keyword_input.attr('placeholder', `search ${search_position_select.toLowerCase()} in ${this_value} section`)
        }
    } else {
        if (search_position_select === 'all') {
            search_keyword_input.attr('placeholder', `search all in ${this_value} section`)
        } else {
            search_keyword_input.attr('placeholder', `search ${search_position_select.toLowerCase()}s in ${this_value} section`)
        }
    }
})
