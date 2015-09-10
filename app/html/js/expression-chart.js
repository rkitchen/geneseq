var w = 400;
var h = 250;

var margin = {};
margin.left = 60;
margin.right = 20;
margin.top = 15;
margin.bottom = 200;

var xscale = d3.scale.linear();
var yscale = d3.scale.linear();
var namescale = d3.scale.ordinal();

var yaxis = d3.svg.axis()
    .scale(yscale)
    .orient('left')
    .innerTickSize(-w)
    .outerTickSize(0)
    .ticks(5);
var xaxis = d3.svg.axis()
    .scale(namescale)
    .innerTickSize(-h)
    .outerTickSize(0)
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
                  .range([0, w]);
            console.log(1);
            yscale.domain([data.min, data.max])
                  .range([h, 0]);
            console.log(data.names);
            namescale.domain(data.names.map(function(d) {return d[1]}))
                .range(data.names.map(function(d) {return xscale(d[0])}));
            xaxis.scale(namescale);

            if (data.names.length <= 10) {
                colorscale = d3.scale.category10();
            } else {
                colorscale = d3.scale.category20();
            }

            var svg = d3.select('div#content-wrapper')
                .append('svg')
                .attr('width', w + margin.left + margin.right)
                .attr('height', h + margin.top + margin.bottom)
            svg.append('rect')
                .attr('width', w + margin.left + margin.right)
                .attr('height', h + margin.top + margin.bottom)
                .attr('fill', '#DDD');
            var canvas = svg
                .append('g')
                .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            canvas.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(0," + h + ")")
                .call(xaxis)
                .selectAll('text')
                .attr('x', '-.3em')
                .attr('y', '-.3em')
                .attr('transform', 'rotate(-65)');

            canvas.append("g")
                .attr("class", "axis")
                .call(yaxis);

            canvas.selectAll('circle')
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
                .attr("r", 5);
        }
    });
});
