/*$(document).ready(function() {
    $('#data').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/table",
            "type": "POST"
        },
        'columns': [
            {'data': 'geneName'},
            {'data': 'cellType'},
            {'data': 'geneType'},
            {'data': 'expr'},
            {'data': 'expr_next'},
            {'data': 'expr_diff'}
        ]
    });
} );*/

var sliders = [];
var returned_data;
var data = {
    'order': 'expr',
    'direction': true
};

var tableLinks = function() {
    $('#data tbody tr').click( function() {
        window.location = $(this).find('a').attr('href');
    }).hover( function() {
        $(this).toggleClass('hover');
    });
}


var tableUpdate = function() {
    $('#data tbody').empty();

    var post_data = {};

    if (data.order) {
        post_data.order = data.order;
        post_data.direction = data.direction;
    }

    post_data['method'] = 'sliders';
    $.each(sliders, function(index, slider) {
        post_data[slider.name] = slider.getValue();
    });

    console.log(post_data);

    $.post('/table', post_data,
    function(data, status) {
        console.log('data: ' + data);
        console.log('status: ' + status);
        data = jQuery.parseJSON(data);
        returned_data = data;

        if (status == 'success') {
            var table = $('table#data tbody');
            $.each(data, function(index, item) {
                var row = []
                row.push('<a href="/gene?id=' + item.id +'">' + item.geneName + '</a>')
                row.push(item.cellType)
                row.push(item.geneType)
                row.push(item.expr)
                row.push(item.expr_next)
                row.push(item.expr_diff)

                table.append(['<tr><td>',row.join('</td><td>'),'</td></tr>'].join(''))
            });

            tableLinks();
        }
    });
}


$(document).ready(function() {
    tableLinks();

    //sorting function

    $("table#data th").each(function(index, item) {
        var key = item.getAttribute('value');
        console.log('key: ' + key)
        $(item).click({value: key}, function(event) {
            console.log(event);
            console.log('table header clicked: ' + event.data.value);
            if (data.order == event.data.value) data.direction = !data.direction;
            data.order = event.data.value;
            tableUpdate();
        })
    });


    $("input.table-filter.range").each(function(index, item) {
        var slider = new Slider(item)
        slider.name=item.getAttribute('name');
        slider.on('slideStop', tableUpdate);
        slider.on('slide', function(item) {
            console.log(item);
            for (var i = 0; i < sliders.length; i++) {
                if (sliders[i].getValue() == item) {
                    $(sliders[i].element).siblings("span#value").text(item.join(':'));
                }
            }
        });
        sliders.push(slider);
    });
});