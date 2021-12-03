$('#id_tasks_form').submit((e) => {
    e.preventDefault()
    preSearch(1)
    return false
})
$('#id_section_select').on('change', (e) => {
    preSearch(1, true)
})

