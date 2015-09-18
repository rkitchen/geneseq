
$(document).ready(function() {
    var id = $('div#_id').attr('value');
    var human_id = $('div#human_id').attr('value');
    if (scatter != null) {
        var cns = $('<div />', {
            id: 'cns-chart',
            class: 'chart'
        }).appendTo('div#content-wrapper');

        var bodymap = $('<div />', {
            id: 'bodymap-chart',
            class: 'chart'
        }).appendTo('div#content-wrapper');

        scatter.plot(id, '/mouse/chart', {'node': 'div#cns-chart'});
        scatter.plot(human_id, '/human/chart/bodymap', {'node': 'div#bodymap-chart'});
    }

    if (brainspan != null) {
        var brainspan_node = $('<div />', {
            id: 'brainspan-chart',
            class: 'chart'
        }).appendTo('div#content-wrapper');

        brainspan.plot(human_id, '/human/chart/brainspan', {'node': 'div#brainspan-chart', 'width': 100});
    }
});