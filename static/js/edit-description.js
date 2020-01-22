$('td.description-edit, td.category-edit').each(function () {
    $(this).hide();
});
$(function () {
    $('td.description-edit-icon').each(function () {
        $(this).on('click', function () {
            console.log($(this));
            console.log($(this).next());
            $(this).next().show();
            $(this).hide();
        });
    });
});
$(function () {
    $('button.description-edit-submit').each(function () {
        $(this).bind('click', function () {
            $.getJSON('/dashboard/update_description', {
                update_name: $(this).prev().val(),
                id: $(this).prev().attr('id')
            }, function (data) {
                let updatedDescription = $('td[id=' + data.id + '][class="description-edit-icon"]');
                console.log(updatedDescription);
                console.log(updatedDescription.text());
                updatedDescription.text(data.description).show();
                // updatedDescription.append($(" <i class='fas fa-edit' id='edit-icon'></i>")).show();
                // updatedDescription.show();
                updatedDescription.next().hide();
            });
            return false;
        });
    });
});

$(function () {
    $('button.description-edit-cancel').each(function () {
        $(this).on('click', function () {
            console.log($(this));
            console.log($(this).next());
            $(this).parent().prev().show();
            $(this).parent().hide();
        });
    });
});
