$(document).ready(function () {
    $('#navbar').load('/navbar.html');

    $.ajax({
        data: {
            "query": this.value
        },
        dataType: "json",
        url: "/api/library/stats/extensions/size",
        success: function (data) {

            let ctx_chart_extensions = document.getElementById('chart_extensions').getContext('2d');
            let display_data = {
                datasets: [{
                    data: [],
                    backgroundColor:[]
                }, {
                    data: [],
                    backgroundColor:[]
                }],
                labels: []
            };

            for (var item in data.aggregations.extensions.buckets) {
                display_data.labels.push(data.aggregations.extensions.buckets[item].key.toUpperCase());
                display_data.datasets[0].data.push(data.aggregations.extensions.buckets[item].doc_count);
                display_data.datasets[0].backgroundColor.push(COLORS[data.aggregations.extensions.buckets[item].key]);
                display_data.datasets[1].data.push((data.aggregations.extensions.buckets[item].size.value / 1024 / 1024 / 1024).toFixed(2));
                display_data.datasets[1].backgroundColor.push(COLORS[data.aggregations.extensions.buckets[item].key]);
            }
            let chart_extensions = new Chart(ctx_chart_extensions, {
                type: 'doughnut',
                data: display_data,
                options: {
                    circumference: Math.PI,
                    rotation: -Math.PI,
                    responsive: true,
                    legend: {position: 'right', align: 'start'}
                }
            });
        }
    })
    ;
})
;