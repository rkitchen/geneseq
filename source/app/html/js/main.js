$(document).ready(function() {

    var url = window.location.href;
    $('a.url').each(function(index, item) {
        item = $(item);
        var current = item.attr('href');
        item.attr('href', current + '?ref=' + url);
    });
});
