(function($) {
    $('#success').hide();
    var environment = $('.plaid-environment').attr('id');
    var handler = Plaid.create({
        apiVersion: 'v2',
        clientName: 'The Vault',
        env: environment,
        product: ['auth', 'transactions'],
        key: '246a82fe1a27ee4ddaecc9090d145f',
        onSuccess: function(public_token) {
            $.post('/user/get_access_token', {
                public_token: public_token
            }, function() {
                $('#container').fadeOut('fast', function() {
                    $('#success').fadeIn('slow');
                });
            });
        },
        onExit: function(err, metadata) {
            if ( err != null ) {
                console.log(err['error_message'])
            }
        }
    });

    $('#link-btn').on('click', function(e) {
        handler.open();
    });

})(jQuery);