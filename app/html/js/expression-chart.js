var w = 400;
var h = 250;

var paddingh = 40;
var paddingv = 20

var xscale = d3.scale.linear();
var yscale = d3.scale.linear();

var yaxis = d3.svg.axis()
    .scale(yscale)
    .orient('left')
    .ticks(5);
var xaxis = d3.svg.axis()
    .scale(xscale)
    .orient('bottom');
var colorscale;
var data;

$(document).ready(function() {
    id = $('#geneID').attr('value');

    $.post('/data?geneid=' + id, {},
        function(return_data, status) {

        data = return_data;
        console.log('data: ' + data);
        console.log('status: ' + status);
        data = jQuery.parseJSON(data);

        if (status == 'success') {
            console.log(0);
            xscale.domain([0, data.names.length])
                  .range([paddingh, w - paddingh]);
            console.log(1);
            yscale.domain([data.min, data.max])
                  .range([h - paddingv, paddingv]);

            xaxis.ticks(data.names.length);

            if (data.names.length <= 10) {
                colorscale = d3.scale.category10();
            } else {
                colorscale = d3.scale.category20();
            }

            var svg = d3.select('div#content-wrapper')
                .append('svg')
                .attr('width', w)
                .attr('height', h);
            svg.append('rect')
                .attr('width', w)
                .attr('height', h)
                .attr('fill', '#DDD');
            svg.selectAll('circle')
                .data(data.values)
                .enter()
                .append("circle")
                .attr("cx", function(d) {
                    return xscale(d[0]);
                })
                .attr("cy", function(d) {
                    return yscale(d[1]);
                })
                .attr('fill', function(d) {
                    return colorscale(d[0]);
                })
                .attr("r", 7);
            svg.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(0," + (h - paddingv) + ")")
                .call(xaxis);

            svg.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(" + paddingh + ",0)")
                .call(yaxis);
        }
    });
});
