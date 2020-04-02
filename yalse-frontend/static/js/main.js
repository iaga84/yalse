function byte_to_size(bytes) {
    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes == 0) return '0 Byte';
    var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
}

function time_difference(timestamp) {

    current = new Date().getTime();
    previous = Date.parse(timestamp)

    var msPerMinute = 60 * 1000;
    var msPerHour = msPerMinute * 60;
    var msPerDay = msPerHour * 24;
    var msPerMonth = msPerDay * 30;
    var msPerYear = msPerDay * 365;

    var elapsed = current - previous;

    if (elapsed < msPerMinute) {
        return Math.round(elapsed / 1000) + ' seconds ago';
    } else if (elapsed < msPerHour) {
        return Math.round(elapsed / msPerMinute) + ' minutes ago';
    } else if (elapsed < msPerDay) {
        return Math.round(elapsed / msPerHour) + ' hours ago';
    } else if (elapsed < msPerMonth) {
        return 'approximately ' + Math.round(elapsed / msPerDay) + ' days ago';
    } else if (elapsed < msPerYear) {
        return 'approximately ' + Math.round(elapsed / msPerMonth) + ' months ago';
    } else {
        return 'approximately ' + Math.round(elapsed / msPerYear) + ' years ago';
    }
}

$(document).ready(function () {
    $('#search_input').focus();
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
                    try {lang = val._source.meta.language.toUpperCase()} catch (e) {
                        lang = 'N/A'
                    }
                    let html = `
<div class="card mb-3">
  <div class="row no-gutters">
    <div class="col-md-1 d-flex align-items-center justify-content-center file-format file-format-${val._source.extension}">
     ${val._source.extension}
    </div>
    <div class="col-md-8">
      <div class="card-body">
        <h5 class="card-title">${val._source.path.split(`/`).pop().split('.').slice(0, -1).join('.')}</h5>
        <p class="card-text">[<strong>${lang}</strong>] ${val._source.path.split(`/`).slice(1).join(`/`)} <small class="text-muted">(indexed ${time_difference(val._source.timestamp)})</small></p>
      </div>
    </div>
  </div>
</div>
`;
                    $('#search_result').append(html);
                });
            }
        });
    });
    $('#index_documents').click(function () {
        $.ajax({
            url: "/api/library/scan",
            type: 'PUT',
            success: function (data) {
            }
        });
    });
        $('#index_metadata').click(function () {
        $.ajax({
            url: "/api/library/metadata/scan",
            type: 'PUT',
            success: function (data) {
            }
        });
    });
            $('#index_content').click(function () {
        $.ajax({
            url: "/api/library/content/scan",
            type: 'PUT',
            success: function (data) {
            }
        });
    });
    $('#index_duplicates').click(function () {
        $.ajax({
            url: "/api/documents/duplicates/scan",
            type: 'PUT',
            success: function (data) {
            }
        });
    });
    $('#delete_index').click(function () {
        $.ajax({
            url: "/api/library/index",
            type: 'DELETE',
            success: function (data) {
            }
        });
    });

    $(function () {
        setInterval(function () {
            $.ajax({
                data: {
                    "query": this.value
                },
                dataType: "json",
                url: "/api/library/stats",
                success: function (data) {
                    $('#number_of_documents').html(data.indices.library.total.docs.count);
                    $('#number_of_duplicates').html(Math.round(data.indices.duplicates.total.docs.count / 2));
                    $('#index_size').html(byte_to_size(data.indices.library.total.store.size_in_bytes));
                }
            });
            $.ajax({
                data: {
                    "query": this.value
                },
                dataType: "json",
                url: "/api/library/size",
                success: function (data) {
                    $('#library_size').html(byte_to_size(data.aggregations.library_size.value));
                }
            });
            $.ajax({
                data: {
                    "query": this.value
                },
                dataType: "json",
                url: "/api/queue/stats",
                success: function (data) {
                    $.each(data.queues, function (key, val) {
                        if (val.name === 'default') {
                            $('#queued_tasks').html(val.count);
                        }
                        if (val.name === 'failed') {
                            $('#failed_tasks').html(val.count);
                        }
                    });

                }
            });
            $.ajax({
                data: {
                    "query": this.value
                },
                dataType: "json",
                url: "/api/queue/workers",
                success: function (data) {
                    $('#workers').html(data.workers.length);
                }
            });
        }, 2000);
    });
});
