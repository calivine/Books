$(function () {
    $('button.refresh-accounts').bind('click', function () {


        $.get('/refresh', {
            account_id: $(this).attr('id')
        }, function (data) {

        });
        return false;
    });
});