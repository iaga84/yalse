function byte_to_size(bytes) {
    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes == 0) return '0 Byte';
    var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
}


$(document).ready(function () {
    $('#search_input').focus();
    $('#search_input').keyup(function (e) {
        $.ajax({
            data: {
                "query": this.value
            },
            dataType: "json",
            url: "http://localhost:8000/search",
            success: function (data) {
                $('#search_result').empty();
                $.each(data.hits.hits, function (key, val) {
                    let html = `
<div class="card mb-3">
  <div class="row no-gutters">
    <div class="col-md-1 d-flex align-items-center justify-content-center file-format file-format-${val._source.extension}">
     ${val._source.extension}
    </div>
    <div class="col-md-8">
      <div class="card-body">
        <h5 class="card-title">${val._source.name}</h5>
        <p class="card-text">This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.</p>
        <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
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
            url: "http://localhost:8000/documents",
            success: function (data) {
            }
        });
    });
    $('#delete_index').click(function () {
        $.ajax({
            url: "http://localhost:8000/reset",
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
                url: "http://localhost:8000/index-stats",
                success: function (data) {
                    $('#number_of_documents').html(data._all.total.docs.count);
                    $('#index_size').html(byte_to_size(data._all.total.store.size_in_bytes));
                }
            });
            $.ajax({
                data: {
                    "query": this.value
                },
                dataType: "json",
                url: "http://localhost:8000/library-size",
                success: function (data) {
                    $('#library_size').html(byte_to_size(data.aggregations.library_size.value));
                }
            });
            $.ajax({
                data: {
                    "query": this.value
                },
                dataType: "json",
                url: "http://localhost:8000/queue-stats",
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

        }, 2000);
    });
});
