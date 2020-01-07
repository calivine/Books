$(function () {
    $('#add-new-category').hide();
    let worker = new BudgetWorker;
    // Tally total 'planned' budget
    worker.getPlannedTotal();
    // User can update planned value by clicking on the value itself
    $('.budget-category-planned').each(function () {
        $(this).on('click', function () {
            const currentValueText = $(this).text();
            // let currentValue = initializeInput($(this).text());
            let currentValue = worker.budgetUpdateInput($(this).text());
            let inputAnchor = $(this).prev();
            inputAnchor.after(currentValue);
            $(this).hide();
            $(function () {
                $('button#budget-update-submit').each(function () {
                    $(this).on('click', function () {
                        worker.updateBudget($(this), worker);
                    });
                });
                $('button#budget-update-cancel').each(function () {
                    $(this).on('click', function () {
                        worker.cancel($(this));
                    });
                });
            });

        });
    });
    $(function () {
        $('span#plus-icon-container').on('click', function () {
            $(this).hide();
            let newCategoryForm = worker.createNewCategoryForm($(this));
            console.log(newCategoryForm.next());
            $('button#category-submit').on('click', function () {
                worker.saveNewCategory($(this));
            });
            $('button#category-cancel').each(function () {
                $(this).on('click', function () {
                    worker.cancel($(this));
                });
            });
        });

    });
});

$(function () {
   $('#plus-icon-container').on('mouseover', function() {
       $('#add-new-category').slideToggle();

   });
    $('#plus-icon-container').on('mouseout', function() {
       $('#add-new-category').slideToggle();
   })
});