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
var tableUpdate = function(slider) {
    $('#data tbody').empty();
    console.log(slider)
    $.each(sliders, function(index) {
        console.log(sliders[index].getValue());
        console.log($(sliders[index]));
    });

    var post_data = {};
    post_data['method'] = 'sliders';
    $.each(sliders, function(index, slider) {
        post_data[slider.name] = slider.getValue();
    });

    $.post('/table', post_data,
    function(data, status) {
        console.log('data: ' + data);
        console.log('status: ' + status);
    });
}


$(document).ready(function() {
    $('#data tbody tr').click( function() {
        window.location = $(this).find('a').attr('href');
    }).hover( function() {
        $(this).toggleClass('hover');
    });
    $("input.table-filter.range");
    $("input.table-filter.range").each(function(index, item) {
        var slider = new Slider(item)
        slider.name=item.getAttribute('name');
        slider.on('slideStop', tableUpdate);
        sliders.push(slider);
    });
});