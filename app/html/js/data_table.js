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
    'sort': ['expression', -1],
    'celltype': []
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

//attaches listener to column headers for sorting
var initTableHeaders = function() {
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
}

//creates sidebar sliders
var initSliders = function() {
    $('input.table-filter.range').each(function(index, item) {
        var slider = new Slider(item);
        slider.name = item.getAttribute('name');
        slider.init = slider.getValue();
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
}

var selection_setAll = function(inputGroup, state) {
    options = [];
    $(inputGroup).find('input').each(function(index, item) {
        $(item).prop('checked', state);
        options.push($(item).attr('value'));
    });
    if (!state) global.celltype = options;
    else global.celltype = [];
    tableUpdate();
};

//initializes sidebar options list
var initSelection = function() {
    var selections = $('li.table-filter.selection');
    selections.find('input.selection').change(function() {
        console.log($(this).is(':checked'));
        console.log($(this).attr('value'));
        value = $(this).attr('value');
        if ($(this).is(':checked')) {
            index = global.celltype.indexOf(value);
            if (index > -1) {
                global.celltype.splice(index, 1);
            }
        } else {
            global.celltype.push($(this).attr('value'));
        }
        console.log(global.celltype);
        tableUpdate();
    });

    selections.each(function(index, item) {
        console.log(item);
        $(item).find('#select-all').click(function(event) {
            event.preventDefault();
            inputGroup = $(this).parent().parent()
            selection_setAll(inputGroup, true);
        });
        $(item).find('#deselect-all').click(function(event) {
            event.preventDefault();
            inputGroup = $(this).parent().parent()
            selection_setAll(inputGroup, false);
        });
    });
}

var update_url = function() {
    var requests = global.requests;
    console.log('update_url requests: ' + requests);
    var url = [];
    if (requests.length > 0) {
        for (var i = 0; i < requests.length; i++) {
            url.push(requests[i].join('='))
        }
        url = url.join('&');
        history.replaceState(null, null, './table?' + url);
    } else history.replaceState(null, null, './table');
}

var add_request = function(key, value) {
    var requests = global.requests
    var exists = false;
    for (var i = 0; i < requests.length; i++) {
        if (key == requests[i][0]) {
            requests[i][1] = value;
            exists = true;
            break;
        }
    }

    if (!exists) {
        console.log('pushing');
        requests.push([key, value]);
        console.log('requets: ' + requests);
    }
    global.requests = requests;
    console.log('global.requests after add: ' + global.requests);
};

var remove_request = function(key) {
    console.log('removing key ' + key);
    requests = global.requests;
    if (requests.length > 0) {
        for (var i = 0; i < requests.length; i++) {
            if (requests[i][0] == key) {
                console.log('found');
                requests.splice(i, 1);
                global.requests = requests;
                break;
            }
        }

        console.log('after remove: ' + global.requests);
    }
}

var init_requests = function() {
    console.log('initializing requests');
    var current = window.location.search.substring(1);
    if (current.length <= 0) global.requests = [];
    else {
        var requests = []
        $.each(current.split('&'), function(index, item) {
            requests.push(item.split('='));
        });
        global.requests = requests;
    }
}


var tableUpdate = function() {
    $('#data tbody').empty();

    var post_data = {};

    //sets sorting to post data
    if (global.sort) {
        post_data.sort = global.sort;
    }

    //sets celltypes to post data and updates url
    if (global.celltype.length > 0) {
        post_data.celltype = global.celltype;
        value = '[' + global.celltype + ']';
        add_request('celltype', value);
    } else remove_request('celltype');

    //sets slider values to post data and updates url
    post_data['sliders'] = true;
    $.each(sliders, function(index, slider) {
        if (slider.getValue() != slider.init) {
            value = slider.getValue();
            post_data[slider.name] = value;
            if (typeof value != 'number') value = '[' + value + ']';
            add_request(slider.name, value);
        }
    });

    console.log(global.requests);
    update_url();
    
    //convert data to json to prevent nested object data loss
    post_data = JSON.stringify(post_data);
    console.log(post_data);

    $.post('./table', {'json': post_data}, 
    function(data, status) {
        console.log('data: ' + data);
        console.log('status: ' + status);
        data = jQuery.parseJSON(data);
        returned_data = data;

        if (status == 'success') {
            //propagates data to table
            var table = $('table#data tbody');
            $.each(data, function(index, item) {
                var row = [];
                var columns = global.columns;
                console.log('columns: ' + columns);
                row.push('<a href="./gene?id=' +
                    item['_id'] + '">' +
                    item[columns[0]] +
                    '</a>');
                for (var i = 1; i < columns.length; i++) {
                    row.push(item[columns[i]]);
                }

                table.append(['<tr><td>',
                    row.join('</td><td>'),
                    '</td></tr>'].join(''));
            });

            //sets sort icons
            $('table#data thead th').each(function(index, item) {
                $(item).children('i').
                    text(getSortIcon(item.getAttribute('value')));
            });

            //adds click listener to each table row
            tableLinks();
        }
    });
};


$(document).ready(function() {
    tableLinks();
    init_requests();

    initTableHeaders();
    initSliders();
    initSelection();

    var columns = [];
    $('table#data thead th').each(function(index, item) {
        columns.push(item.getAttribute('value'));
    });
    global['columns'] = columns;
});
