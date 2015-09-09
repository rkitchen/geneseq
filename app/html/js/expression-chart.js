var w = 300;
var h = 200;
var data

$(document).ready(function() {
    id = $('#geneID').attr('value');

    $.post('/data?geneid=' + id, {},
        function(return_data, status) {
            data = return_data;
            console.log('data: ' + data);
            console.log('status: ' + status);
            data = jQuery.parseJSON(data);

            if (status == 'success') {
                d3.select('div#content-wrapper')
                    .append('svg')
                    .attr('width', w)
                    .attr('height', h)
                    .selectAll('rect')
                    .data(data)
                    .enter()
                    .append("rect")
                    .attr("x", function(d, i) {
                        return 25 * i;
                    })
                    .attr("y", 0)
                    .attr("width", 20)
                    .attr("height", function(d) {
                        return Math.abs(d.values[0] * 25);
                    });
            }
    });
});
