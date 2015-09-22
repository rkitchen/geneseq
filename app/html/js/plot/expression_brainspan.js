var brainspan = new function() {
    var self = this;
    var margin = {};
    margin.left = 60;
    margin.right = 20;
    margin.top = 45;
    margin.bottom = 80;
    margin.inner = 5;

    var max_width = 500;
    var default_radius = 1.25;
    var default_height = 400;
    var fit_windows = 20;
    var fit_width = 5;

    var x_tick_values = [10, 100, 273, 1000];
    self.canvases = {};

    var get_width = function(count) {
        var width = $(window).width() - 200;
        var ret = {'normal': width,
            'inner': (width - margin.inner * (count - 1)) / count,
            'outer': width + margin.left + margin.right};
        return ret;

    };

    var get_height = function() {
        var height = default_height;
        var ret = {'normal': height,
            'outer': height + margin.top + margin.bottom};
        return ret;
    };

    var get_ticks = function(max) {
        for (var p = 4; p > -3; p--) {
            power = Math.pow(10, p);
            if (max / Math.pow(10, p) < 5) continue;

            var ytick = _.range(Math.floor(max / power) + 1);
            for (var i = 0; i < ytick.length; i++) ytick[i] = ytick[i] * power;
            console.log('y tick values', ytick);
            return ytick;
        }
    };

    var draw_plot = function(canvas, data, dimen, axis, scales) {
        var width = dimen.width;
        var height = dimen.height;

        var line = d3.svg.line()
        .x(function(d) {return scales.x(d[0])})
        .y(function(d) {
            return scales.y(d[1]);
        })
        .interpolate('bundle');

        var draw_line = function(e) {
            var params = e.data;
            var name = params.name;
            var values = JSON.parse(params.values);
            self.canvases[params.name].append('path')
            .datum(values)
            .attr('d', line)
            .attr('fill', 'none')
            .attr('stroke', 'red')
            .attr('stroke-width', 2)
            .attr('opacity', .7);
        };

        console.log('dimen', dimen);

        console.log(canvas);
        self.canvas = canvas;

        canvas.append('rect')
        .attr('width', width)
        .attr('height', height + margin.top + margin.bottom)
        .attr('transform', 'translate(0,' + -margin.top + ')')
        .attr('fill', '#DDD');

        canvas.selectAll('circle')
            .data(data.points)
            .enter()
            .append('circle')
            .attr('cx', function(d) {
                return scales.x(d[0]);
            })
            .attr('cy', function(d) {
                return scales.y(d[1]);
            })
            .attr('fill', 'red')
            .attr('r', dimen.radius);

        canvas.append('path')
        .datum(data.points)
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', 'blue')
        .attr('stroke-width', 2)
        .attr('opacity', .1);

        canvas.append('g')
            .attr('class', 'axis')
            .attr('transform', 'translate(0,' + height + ')')
            .call(axis.x)
            .selectAll('text')
            .attr('x', '-.3em')
            .attr('y', '-.3em')
            .attr('transform', 'rotate(-90)');

        canvas.append('text')
            .attr('class', 'title-2')
            .attr('x', (width / 2))
            .attr('y', - (margin.top / 4))
            .attr('text-anchor', 'middle')
            .text(data.title);

        self.canvases[data.title] = canvas;
        var worker = new Worker('/js/plot/fit_worker.js');
        worker.addEventListener('message', draw_line);
        worker.postMessage({'name': data.title, 'domain': dimen.duration, 'values': JSON.stringify(data.points)});
    };

    var draw_svg = function(id, source, params) {
        var width;

        var height = get_height();
        var radius = params.radius;

        console.log('width: ' + width);
        console.log('height: ' + height);

        var xscale = d3.scale.log();
        var yscale = d3.scale.linear();

        self.xscale = xscale;
        self.yscale = yscale;

        var yaxis = d3.svg.axis()
            .scale(yscale)
            .orient('left')
            .outerTickSize(0);
        var xaxis = d3.svg.axis()
            .scale(xscale)
            .orient('bottom')
            .innerTickSize(-height.normal)
            .outerTickSize(0)
            .tickFormat(function(d) {
                return d;
            })
            .tickValues(x_tick_values);

        var done = false;
        $.post(source, {'gene_id': id}, function(data, status) {
            if (status == 'success' && data != null) {
                data = jQuery.parseJSON(data);
                console.log('data: ' + data);
                console.log('status: ' + status);

                self.data = data;

                width = get_width(data.names.length);
                yaxis.innerTickSize(-width.normal);
                //.tickValues(get_ticks(data.max));

                xscale.domain([10, data.duration])
                      .range([0, width.inner]);

                yscale.domain([0, data.max])
                      .range([height.normal, 0]);

                console.log(data.names);

                var svg;
                if (params.node != null) svg = d3.select(params.node);
                else svg = d3.select('div#content-wrapper');

                svg = svg.append('svg')
                    .attr('width', width.outer)
                    .attr('height', height.outer);
                svg.append('rect')
                    .attr('width', width.outer)
                    .attr('height', height.outer)
                    .attr('fill', '#f0f0f0');
                var canvas = svg
                    .append('g')
                    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

                $.each(data.names, function(index, item) {
                    var translate = index * (width.inner + margin.inner);
                    console.log(width);
                    console.log(margin.inner);
                    console.log(index);
                    console.log(translate);

                    var chart = canvas.append('g')
                    .attr('transform', 'translate(' + translate + ',' + margin.top + ')');

                    var plot_data = {'title': item,
                        'points': data[item]};
                    var scales = {'x': xscale, 'y': yscale};
                    var axis = {'x': xaxis, 'y': yaxis};
                    console.log('height', height);
                    var dimen = {'width': width.inner,
                        'height': height.normal,
                        'radius': default_radius,
                        'duration': data.duration};
                    draw_plot(chart, plot_data, dimen, axis, scales);
                });

                canvas.append('g')
                .attr('class', 'axis')
                .attr('transform', 'translate(0,' + margin.top + ')')
                .call(yaxis);

                svg.append('text')
                .attr('class', 'title')
                .attr('x', (width.outer / 2))
                .attr('y', margin.top / 2)
                .attr('text-anchor', 'middle')
                .text('Brainspan Expression');
            }
        });


    };

    var avg = function(list) {
        var sum = 0;
        for (var i = 0; i < list.length; i++) {
            sum += list[i];
        }
        var out = sum / list.length;
        console.log('average:', out);
        return out;
    };

    this.plot = function(id, source, params) {
        console.log('brainspan');
        //if (params.width == null) params.width = get_width();
        //if (params.height == null) params.height = get_height(params.width);
        if (params.radius == null) params.radius = default_radius;

        debug_params = params;
        console.log(params);

        draw_svg(id, source, params);
    };
}
