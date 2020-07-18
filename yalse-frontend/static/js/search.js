$(document).ready(function () {
    $('#navbar').load('/navbar.html');
    $('#search_input').focus();
    let search_result_record = Handlebars.compile($('#search_result_record').html());
    $('#search_input').keyup(function (e) {
        $.ajax({
            data: JSON.stringify({
                "q": this.value
            }),
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            type: "POST",
            dataType: "json",
            url: "/api/library/search",

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
                        title: val._source.name,
                        // language: lang,
                        // path: val._source.path.split(`/`).slice(1).join(`/`),
                        file_hash: val._id,
                        // indexing_time: time_difference(val._source.timestamp)
                    }));
                });
            }
        });
    });
});