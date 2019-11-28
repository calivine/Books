// BudgetWorker class
// purpose is to encapsulate all functionality that goes along with the budget table

function BudgetWorker() {
    this.getPlannedTotal = function () {
        let plannedTotal = 0;
        $('td.budget-category-planned').each(function () {
            plannedTotal += Number($(this).text());
        });
        $('td#planned-total').text(plannedTotal);
    };

    this.updateBudget = function (t) {
        let updateForm = t.parent();
        let hiddenPlannedValue = t.parent().next();
        $.post('/budget/update', {
            new_value: $('input.update-input').val(),
            budget_period: $('h3#budget-period').text(),
            category: t.parent().prev().text()
        }, function (data) {
            hiddenPlannedValue.text(data);
            // Insert update planned budget value
            updateForm.fadeOut();
            hiddenPlannedValue.fadeIn();
            // Remove update form
            updateForm.remove();
        });
        return false;
    };

    this.cancelUpdate = function (t) {
        this.anchor = t.parent().next();
        this.updateForm = t.parent();
        this.updateForm.fadeOut();
        this.anchor.fadeIn();
        this.updateForm.remove();
    };

    this.budgetUpdateInput = function (value) {
        return '<td class="budget-update-form"><input type="text" class="update-input" name="budget_update" value=' + value + '><button class="btn-primary budget-update" id="budget-update-submit">Save</button><button class="btn-secondary" id="budget-update-cancel">Cancel</button></td>';
    };

    this.createNewCategoryForm = function (t) {
        this.newCategoryForm = $('<form action="#" method="post"></form>');
        this.categoryNameInput = '<label for="category">Category</label><input id="new-category-input" name="category" type="text" required>';
        this.plannedBudget = '<label for="planned">Planned Budget</label><input id="new-planned-input" name"planned" type="text"><button id="categorySubmit" type="submit">Save</button>';
        this.newCategoryForm.append(this.categoryNameInput);
        this.newCategoryForm.append(this.plannedBudget);
        return t.after(this.newCategoryForm);
    };

    this.saveNewCategory = function (t) {
        $.post('/budget/new/category', {
            name: $('input#new-category-input').val(),
            planned: $('input#new-planned-input').val()

        }, function (data) {

        });
        return false;
    }


}