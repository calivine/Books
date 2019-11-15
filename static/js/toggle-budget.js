$(function() {
    $('input.toggle-budget').each(function() {
        $(this).on('change', function() {
            $.getJSON('/toggle_budget', {
                transaction_id: $(this).attr('id')
            }, function(data) {
                console.log(data);
                $('span#monthly-spending').text(data.spending);
                let income = Number($('span#monthly-income').text());
                let spending = Number($('span#monthly-spending').text());
                console.log(income, spending);
            });
            return false;
        });
    });
});