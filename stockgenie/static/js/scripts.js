$(document).ready(function() {

    $('#search-item').select2({
        ajax: {
            url: '/api/stockSearch',
            delay: 500,
            minimumInputLength: 1,
            data: function (params) {
                var query = {
                    q: params.term
                }

                // Query parameters will be ?search=[term]&type=public
                return query;
            },
            processResults: function (data) {
                // Tranforms the top-level key of the response object from 'items' to 'results'
                return JSON.parse(data);
            }
        }
    });
});
