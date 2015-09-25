var _menu = new function() {
    var self = this;

    self.update_urls = function() {
        var url = window.location.href;
        $('a.url').each(function(index, item) {
            item = $(item);
            var current = item.attr('href');
            var index = current.indexOf('ref');
            if (index >= 0)
                current = current.substr(0, index);
            item.attr('href', current + '?ref=' + url);
        });
    };
}

$(document).ready(function() {

    _menu.update_urls();
});

