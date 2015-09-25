/**
 * @overview Calculates coordinates for spline fit-line.
 * @module Spline Worker
 * @author Michael Laraia
 */

var fit_windows = 20;
var fit_width = .4;

self.addEventListener('message', function(e) {
    params = e.data;
    values = JSON.parse(params.values);
    console.log('received data: ', params);
    done(params.name, fit_line(values, params.domain));
});

/**
 * Returns message to parent after calculations finish
 * @param {string} name - name of brain region 
 * @param {Array} values - Array of (x,y) coordinates for fit line
 */
var done = function(name, values) {
    data = {};
    data.name = name;
    data.values = JSON.stringify(values);
    console.log('data: ', data);
    self.postMessage(data);
    self.close();
};

/**
 * Calculates average of given Array
 * @param {Array} list - list to be averaged
 * @return {int} Average of list
 */
var avg = function(list) {
    var sum = 0;
    for (var i = 0; i < list.length; i++) {
        sum += list[i];
    }
    var out = sum / list.length;
    console.log('average:', out);
    return out;
};

/**
 * Calculates fit line
 * @param {Array} data - Array of (x,y) brainspan coordinates
 * @param {int} domain - Max time value being rendered in chart
 * @return {Array} - Array of (x,y) coordinates for fit line
 */
var fit_line = function(data, domain) {
    var width = Math.log10(domain) * fit_width;
    var windows = Math.log10(domain) / fit_windows;

    console.log('domain', domain);
    console.log('width: ', width);

    var getWindow = function(data, left, right) {
        var x = [];
        var y = [];

        var count = data.length;
        for (var i = 0; i < data.length; i++) {
            if (data[i][0] > left && data[i][0] < right) {
                x.push(data[i][0]);
                y.push(data[i][1]);
            }
        }
        console.log('left: ', left, 'right: ', right);
        console.log('y: ', y);
        console.log('x: ', x);

        if (x.length == 0 || y.length == 0) return null;

        var yavg = avg(y);
        return yavg;
    };

    var out = [];
    var init = Math.floor(Math.log10(data[0][0]) / Math.log10(domain) * fit_windows);
    console.log('init: ', init);
    for (var i = init; i <= fit_windows; i++) {
        var mid = i * windows;
        var left = Math.pow(10, mid - width / 2);
        var right = Math.pow(10, mid + width / 2);

        var average = getWindow(data, left, right);
        if (average != null) out.push([Math.pow(10, mid), average]);
    }

    console.log('out: ');
    console.log(out);
    console.log(out[0]);
    return out;
};
