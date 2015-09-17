
$(document).ready(function() {
    var id = $('div#_id').attr('value');
    var human_id = $('div#human_id').attr('value');
    if (scatter_plot != null) {
        scatter_plot(id, '/mouse/chart', {});
        scatter_plot(human_id, '/human/chart', {});
    }
});