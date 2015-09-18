
$(document).ready(function() {
    var id = $('div#_id').attr('value');
    var human_id = $('div#human_id').attr('value');
    if (scatter_plot != null) {
        var cns = $('<div />', {
            id: 'cns-chart',
            class: 'chart'
        }).appendTo('div#content-wrapper');

        var bodymap = $('<div />', {
            id: 'bodymap-chart',
            class: 'chart'
        }).appendTo('div#content-wrapper');

        scatter_plot(id, '/mouse/chart', {'node': 'div#cns-chart'});
        scatter_plot(human_id, '/human/chart', {'node': 'div#bodymap-chart'});
    }
});