$(document).ready(function() {

    var url = $('form#login').attr('value');
    console.log('url ', url);
    if (url == window.location.href) url = '/';
    $('form#login').submit(function(event) {
        event.preventDefault();
        var user = $('input#inputUser').val();
        var pass = $('input#inputPassword').val();
        $.post('/login', {'user': user, 'pass': pass}, function(message, status) {
            status = JSON.parse(message);
            if (status.success) window.location.replace(url);
            else window.location.replace(window.location.href + '&invalid=True')
        });
    });
});
