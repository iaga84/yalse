$(document).ready(function () {
    $('#navbar').load('/navbar.html');
    $('#search_input').focus();
    let search_result_record = Handlebars.compile($('#search_result_record').html());
    $('#search_input').keyup(function (e) {
        $.ajax({
            data: {
                "query": this.value
            },
            dataType: "json",
            url: "/api/documents/search",
            success: function (data) {
                $('#search_result').empty();
                $.each(data.hits.hits, function (key, val) {
                    try {
                        lang = val._source.meta.language.toUpperCase()
                    } catch (e) {
                        lang = 'N/A'
                    }
                    $('#search_result').append(search_result_record({
                        background: COLORS[val._source.extension],
                        extension: val._source.extension,
                        title: val._source.path.split(`/`).pop().split('.').slice(0, -1).join('.'),
                        language: lang,
                        path: val._source.path.split(`/`).slice(1).join(`/`),
                        indexing_time: time_difference(val._source.timestamp)
                    }));
                });
            }
        });
    });
});