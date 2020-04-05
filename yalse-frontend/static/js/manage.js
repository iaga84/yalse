$(document).ready(function () {
    $('#navbar').load('/navbar.html');

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
