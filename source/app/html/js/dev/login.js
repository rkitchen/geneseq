$(function() {

    var getRef = function() {
        var url = window.location.href;
        url = url.substr(url.indexOf('?'));
        var index = url.indexOf('ref=');

        if (index < 0) return '/';

        var ref = url.substr(index + 4);
        return ref;
    };

    $('#login-form-link').click(function(e) {
        $('#login-form').delay(100).fadeIn(100);
        $('#register-form').fadeOut(100);
        $('#register-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });
    $('#register-form-link').click(function(e) {
        $('#register-form').delay(100).fadeIn(100);
        $('#login-form').fadeOut(100);
        $('#login-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });

    $('form#register-form').validate({
        rules: {
            username: {
                required: true,
                minlength: 1,
                maxlength: 50
            },
            email: {
                required: true,
                email: true
            },
            password1: {
                required: true,
                minlength: 5
            },
            password2: {
                required: true,
                equalTo: '#password1'
            }
        },
        messages: {
            username: 'Username must be between 1 and  50 characters',
            email: 'Please enter a valid email address',
            password1: 'Password must be at least 5 characters',
            password2: 'Passwords must match'
        },
        highlight: function(element) {
            $(element).closest('.form-group').removeClass('success').addClass('error');
        },
        success: function(element) {
            element.text('OK!').addClass('valid')
            .closest('.form-group').removeClass('error').addClass('success');
        },
        submitHandler: function(form) {
            $(form).on('submit', function(event) {
                console.log('submitting');
                var f = $(form);
                var data = {
                    'method': 'register',
                    'user': f.find('input#username').val(),
                    '_pass': f.find('input#password1').val(),
                    '_pass2': f.find('input#password2').val(),
                    'email': f.find('input#email').val()
                };
                console.log('data', data);
                $.post('/login', data, function(message, status) {
                    status = JSON.parse(message);
                    if (status.success) window.location.replace(getRef());
                    else {
                        $('#invalid').text(status.invalid).removeClass('hidden');
                    }
                 });
            });
        }
    });

    $('form#login-form').validate({
        rules: {
            username: {
                required: true
            },
            password: {
                required: true,
            }
        },
        messages: {
            username: 'Username is required',
            password: 'password is required'
        },
        highlight: function(element) {
            $(element).closest('.form-group').removeClass('success').addClass('error');
        },
        success: function(element) {
            element.text('OK!').addClass('valid')
            .closest('.form-group').removeClass('error').addClass('success');
        },
        submitHandler: function(form) {
            $(form).on('submit', function(event) {
                console.log('submitting');
                var f = $(form);
                var data = {
                    'method': 'login',
                    'user': f.find('input#username').val(),
                    '_pass': f.find('input#password').val()
                };
                console.log('data', data);
                $.post('/login', data, function(message, status) {
                    status = JSON.parse(message);
                    if (status.success) window.location.replace(getRef());
                    else {
                        $('#invalid').text(status.invalid).removeClass('hidden');
                    }
                });
            });
        }
    });
});
