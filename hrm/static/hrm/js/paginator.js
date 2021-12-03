function paginate(data) {
    const paginator_holder = $('#pagination-holder')
    paginator_holder.html('');
    paginator_holder.html('<ul id="pagination-demo" class="pagination-sm col-auto"></ul>');

    $('#pagination-demo').twbsPagination({
        startPage: data['page'],
        totalPages: data['num_pages'],
        initiateStartPageClick: false,
        visiblePages: 5,
        onPageClick: function (event, page) {
            preSearch(page)
        }
    })
}

