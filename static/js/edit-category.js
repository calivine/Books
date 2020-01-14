$('td.category-edit').each(function () {
    $(this).hide();
});

function displayEdit(tag)
{
    $(tag).each(function () {
        $(this).on('click', function () {
            console.log($(this));
            console.log($(this).next());
            $(this).next().show();
            $(this).hide();
        });
    });
}

function cancelButton(button)
{
    $(button).each(function () {
        $(this).on('click', function () {
            console.log($(this));
            console.log($(this).next());
            $(this).parent().prev().show();
            $(this).parent().hide();
        });
    });
}

// Display select
$(displayEdit('td.budget-category'));


$(function () {
    $('button.category-edit-submit').each(function () {
        $(this).bind('click', function () {
            $.getJSON('/dashboard/update_category', {
                update_name: $(this).prev().val(),
                id: $(this).prev().attr('id')
            }, function (data) {
                let updatedDescription = $('td[id=' + data.id + '][class="budget-category"]');
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


// Cancel Button
$(cancelButton('button.category-edit-cancel'));
