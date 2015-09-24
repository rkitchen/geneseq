$(document).ready(function() {

    var url = $('form#login').attr('value');
    console.log('url ', url);
    if (url == window.location.href) url = '/';
    $('form#login').submit(function(event) {
        event.preventDefault();
        window.location.replace(url);
    });
});
