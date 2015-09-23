$(document).ready(function() {

    var url = $('form#login').attr('value');
    $('form#login').submit(function(event) {
        window.location.replace(url);
    });
});
