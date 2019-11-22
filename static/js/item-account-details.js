$(function () {
    $('td.item-info').each(function () {
        let mask = this.id;
        console.log(mask);
        // let mask = $(this).attr('id');
        $(this).on('click', function () {
            $('div#item-details-display').remove();
            $.post('/user/item/account/details', {
                item_mask: mask
            }, function (item) {
                let $item_details_display = '<div id="item-details-display"><ul id="item-details-list"></ul></div>';
                $('div#container').prepend($item_details_display);

                for (let i = 0; i < 6; i++) {
                    $('ul#item-details-list').append(getListItem(i, item));
                }
                let $item_details_close = '<button id="close-details" class="secondary">Ok</button>';
                $('ul#item-details-list').after($item_details_close);
                // $('div#item-details-display').addClass('item-details-popup');
                console.log($item_details_display);
                $('button#close-details').on('click', function () {
                    $('div#item-details-display').remove();
                });
            });
        });
    });
});

const getListItem = (i, item) => {
    let display_items = [
                    '<li class="item-details-list-item">' + 'ID: ' + item['item_id'] + '</li>',
                    '<li class="item-details-list-item">' + 'Institution ID: ' + item['institution'] + '</li>',
                    '<li class="item-details-list-item">' + 'Last updated: ' + item['last_update'] + '</li>',
                    '<li class="item-details-list-item">' + 'Last failed update: ' + item['last_failed_update'] + '</li>',
                    '<li class="item-details-list-item">' + 'Account name: ' + item['account1']['name'] + '</li>',
                    '<li class="item-details-list-item">' + 'Balance: ' + item['account1']['current_balance'] + '</li>'
                ];
    return display_items[i];
};