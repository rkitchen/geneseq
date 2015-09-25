/**
 * @overview Draws plot for bodymap expression.
 * @module Bodymap
 * @author Michael Laraia
 */

/**
 * Manages the bodymap chart
 * @this bodymap namespace
 * @class bodymap
 * @constructor
 */
var bodymap = new function() {
    var self = this;
    var margin = {};
    margin.left = 60;
    margin.right = 20;
    margin.top = 45;
    margin.bottom = 200;

    var max_width = 500;
    var default_radius = 5;

    /**
     * Gets width for plot
     * @return {int} width of plot
     */
    var get_width = function() {
        var width = $(window).width();
        if (width > max_width) return max_width;
        else return width;
    };

    /**
     * Gets height for plot
     * @param {int} width - width of the plot
     * @return {int} height of plot
     */
    var get_height = function(width) {
        return Math.floor(width / 1.6);
    };

    /**
     * Draws creates plot
     * @param {string} id - gene id to plot
     * @param {string} source data source to POST to
     * @param {dict} params JSON object containing height, widht, and radius
     */
    var draw_plot = function(id, source, params) {
        var width = params.width;
        var height = params.height;
        var radius = params.radius;

        var colorscale;

        var xscale = d3.scale.ordinal();
        var yscale = d3.scale.linear();

        var yaxis = d3.svg.axis()
            .scale(yscale)
            .orient('left')
            .innerTickSize(-width)
            .outerTickSize(0)
            .ticks(5);
        var xaxis = d3.svg.axis()
            .scale(xscale)
            .orient('bottom')
            .innerTickSize(-height)
            .outerTickSize(0);

        var done = false;
        $.post(source, {'gene_id': id}, function(data, status) {
            if (status == 'success' && data != null) {
                console.log('data: ' + data);
                console.log('status: ' + status);

                data = jQuery.parseJSON(data);
                self.data = data;

                margin.bottom = 10 + data.axis_length * 5;
                xscale.domain(data.names)
                      .rangePoints([0, width]);
                yscale.domain([data.min, data.max])
                      .range([height, 0]);
                console.log(data.names);

                if (data.names.length <= 10) {
                    colorscale = d3.scale.category10();
                } else {
                    colorscale = d3.scale.category20();
                }

                colorscale.domain(data.names);

                var svg;
                if (params.node != null) svg = d3.select(params.node);
                else svg = d3.select('div#content-wrapper');

                svg = svg.append('svg')
                    .attr('width', width + margin.left + margin.right)
                    .attr('height', height + margin.top + margin.bottom);
                svg.append('rect')
                    .attr('width', width + margin.left + margin.right)
                    .attr('height', height + margin.top + margin.bottom)
                    .attr('fill', '#DDD');
                var canvas = svg
                    .append('g')
                    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

                canvas.append('g')
                    .attr('class', 'axis')
                    .attr('transform', 'translate(0,' + height + ')')
                    .call(xaxis)
                    .selectAll('text')
                    .attr('x', '-.3em')
                    .attr('y', '-.3em')
                    .attr('transform', 'rotate(-65)');

                canvas.append('g')
                    .attr('class', 'axis')
                    .call(yaxis);

                canvas.selectAll('circle')
                    .data(data.values)
                    .enter()
                    .append('circle')
                    .attr('cx', function(d) {
                        return xscale(d[0]);
                    })
                    .attr('cy', function(d) {
                        return yscale(d[1]);
                    })
                    .attr('fill', function(d) {
                        return colorscale(d[0]);
                    })
                    .attr('r', radius);

                canvas.append('text')
                    .attr('class', 'title')
                    .attr('x', (width / 2))
                    .attr('y', - (margin.top / 2))
                    .attr('text-anchor', 'middle')
                    .text(data.title);
            }
            done = true;
        });


    };

    /**
     * Public function to draw plot
     * @param {string} id - gene id to plot
     * @param {string} source - data source to POST to
     * @param {dict} params
     */
    this.plot = function(id, source, params) {
        console.log(params);
        if (params.width == null) params.width = get_width();
        if (params.height == null) params.height = get_height(params.width);
        if (params.radius == null) params.radius = default_radius;

        draw_plot(id, source, params);
    };
}
