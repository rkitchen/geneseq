/*$(document).ready(function() {
    $('#data').DataTable({
        'processing': true,
        'serverSide': true,
        'ajax': {
            'url': '/table',
            'type': 'POST'
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
var global = {
    'sort': ['expression', -1]
};

var getSortIcon = function(item) {
    console.log('item: ' + item);
    console.log('sort: ' + global.sort);
    if (item == global.sort[0]) {
        if (global.sort[1] == -1) return 'arrow_drop_down';
        else return 'arrow_drop_up';
    } else return 'more_horiz';
};

var tableLinks = function() {
    $('#data tbody tr').click(function() {
        window.location = $(this).find('a').attr('href');
    }).hover(function() {
        $(this).toggleClass('hover');
    });
};


var tableUpdate = function() {
    $('#data tbody').empty();

    var post_data = {};

    if (global.sort) {
        post_data.sort = global.sort;
    }

    post_data['sliders'] = true;
    var history_update = [];
    $.each(sliders, function(index, slider) {
        value = slider.getValue()
        post_data[slider.name] = value;

        if (typeof value != 'number') value = '[' + value + ']';
        history_update.push(slider.name + '=' + value);
    });
    console.log(history_update.join('&'));
    history.replaceState(null, null, './table?' + history_update.join('&'));
    
    post_data = JSON.stringify(post_data);
    console.log(post_data);

    $.post('./table', {'json': post_data}, 
    function(data, status) {
        console.log('data: ' + data);
        console.log('status: ' + status);
        data = jQuery.parseJSON(data);
        returned_data = data;

        if (status == 'success') {
            var table = $('table#data tbody');
            $.each(data, function(index, item) {
                var row = [];
                var columns = global.columns;
                console.log('columns: ' + columns);
                row.push('<a href="./gene?id=' +
                    item['_id'] + '">' +
                    item['_id'] +
                    '</a>');
                for (var i = 1; i < columns.length; i++) {
                    row.push(item[columns[i]]);
                }

                table.append(['<tr><td>',
                    row.join('</td><td>'),
                    '</td></tr>'].join(''));
            });

            $('table#data thead th').each(function(index, item) {
                $(item).children('i').
                    text(getSortIcon(item.getAttribute('value')));
            });

            tableLinks();
        }
    });
};


$(document).ready(function() {
    tableLinks();

    //sorting function

    $('table#data th').each(function(index, item) {
        var key = item.getAttribute('value');
        console.log('key: ' + key);
        $(item).click({value: key}, function(event) {
            console.log(event);
            console.log('table header clicked: ' + event.data.value);
            if (global.sort[0] == event.data.value) {
                global.sort[1] = -global.sort[1];
            } else {
                global.sort = [event.data.value, -1];
            }

            tableUpdate();
        });
    });

    $('input.table-filter.range').each(function(index, item) {
        var slider = new Slider(item);
        slider.name = item.getAttribute('name');
        slider.on('slideStop', tableUpdate);
        slider.on('slide', function(item) {
            console.log(item);
            for (var i = 0; i < sliders.length; i++) {
                if (sliders[i].getValue() == item) {
                    $(sliders[i].element).siblings('span#value').text(item);
                }
            }
        });
        sliders.push(slider);
    });

    var columns = [];
    $('table#data thead th').each(function(index, item) {
        columns.push(item.getAttribute('value'));
    });
    global['columns'] = columns;
});
