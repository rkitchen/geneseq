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

var tableLinks = function() {
    $('#data tbody tr').click( function() {
        window.location = $(this).find('a').attr('href');
    }).hover( function() {
        $(this).toggleClass('hover');
    });
}


var tableUpdate = function(slider) {
    $('#data tbody').empty();

    var post_data = {};
    post_data['method'] = 'sliders';
    $.each(sliders, function(index, slider) {
        post_data[slider.name] = slider.getValue();
    });

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