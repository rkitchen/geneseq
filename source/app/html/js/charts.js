
$(document).ready(function() {
    var id = $('div#_id').attr('value');
    var human_id = $('div#human_id').attr('value');
    if (mouse != null) {
        var mouse_node = $('<div />', {
            id: 'mouse-chart',
            class: 'chart'
        }).appendTo('div#content-wrapper');

        mouse.plot(id, '/mouse/chart', {'node': 'div#mouse-chart'});
    }
    if (bodymap != null) {
        var bodymap_node = $('<div />', {
            id: 'bodymap-chart',
            class: 'chart'
        }).appendTo('div#content-wrapper');

        bodymap.plot(human_id, '/human/chart/bodymap', {'node': 'div#bodymap-chart'});
    }

    if (brainspan != null) {
        var brainspan_node = $('<div />', {
            id: 'brainspan-chart',
            class: 'chart'
        }).appendTo('div#content-wrapper');

        brainspan.plot(human_id, '/human/chart/brainspan', {'node': 'div#brainspan-chart',
                                                            'width': 100});
    }
});
