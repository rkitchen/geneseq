var fit_windows = 100;
var fit_width = 10;

self.addEventListener('message', function(e) {
    params = e.data;
    values = JSON.parse(params.values);
    console.log('received data: ', params);
    done(params.name, fit_line(values));
});

var done = function(name, values) {
    data = {};
    data.name = name;
    data.values = JSON.stringify(values);
    console.log('data: ', data);
    self.postMessage(data);
    self.close();
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

var fit_line = function(data) {
    var min = data[0][0];
    var max = data[data.length - 1][0];
    var range = max / min;
    var width = Math.log10(max) / fit_width;
    var windows = Math.log10(max) / fit_windows;

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

        var xavg = avg(x);
        var yavg = avg(y);

        return [xavg, yavg];
    };

    var out = [data[0]];
    for (var i = 0; i < fit_windows; i++) {
        var mid = i * windows;
        var left = Math.pow(10, mid - width / 2);
        var right = Math.pow(10, mid + width / 2);
        //var left = min + Math.pow(10, i * width);
        //var right = min + Math.pow(10, (i + 1) * width);

        (right > max) ? max : right;

        var average = getWindow(data, left, right);
        //console.log('pushing: ', average);
        if (average != null) out.push(average);
    }

    console.log('out: ');
    console.log(out);
    console.log(out[0]);
    return out;
};
