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

    this.updateBudget = function (t, self) {
        let updateForm = t.parent().parent();
        let hiddenPlannedValue = t.parent().parent().next();
        $.post('/budget/update', {
            new_value: $('input.update-input').val(),
            budget_period: $('h3#budget-period').text(),
            category: t.parent().parent().prev().text()
        }, function (data) {
            hiddenPlannedValue.text(data);
            console.log(hiddenPlannedValue);
            // Insert update planned budget value
            updateForm.fadeOut();
            hiddenPlannedValue.fadeIn();
            // Remove update form
            updateForm.remove();
            self.getPlannedTotal();
        });
        return false;
    };

    this.cancel = function (t) {
        this.anchor = t.parent().parent().next();
        this.updateForm = t.parent().parent();
        this.updateForm.fadeOut();
        this.anchor.fadeIn();
        this.updateForm.remove();
    };

    this.budgetUpdateInput = function (value) {
        return '<td class="budget-update-form"><input type="text" autofocus class="update-input" name="budget_update" value=' + value + '><div class="button-container"><button class="budget-update-button" id="budget-update-submit">Save</button><button class="budget-update-button" id="budget-update-cancel">Cancel</button></div></td>';
    };

    this.createNewCategoryForm = function (t) {
        this.newCategoryForm = $('<div id="new-category-form"></div>');
        this.categoryNameInput = '<label for="category">Category</label><input id="new-category-input" class="new-category-form-input" name="category" type="text" required>';
        this.plannedBudget = '<label for="planned">Planned Budget</label><input id="new-planned-input" class="new-category-form-input" name=planned" type="text"><button id="category-submit" type="submit">Save</button><button id="category-cancel" type="button">Cancel</button>';
        this.newCategoryForm.append(this.categoryNameInput);
        this.newCategoryForm.append(this.plannedBudget);
        this.newCategoryContainer = $('<div id="new-category-container"></div>');
        this.newCategoryContainer.append(this.newCategoryForm);
        return t.before(this.newCategoryContainer);
    };

    this.saveNewCategory = function (t) {
        $.post('/budget/new/category', {
            name: $('input#new-category-input').val(),
            planned: $('input#new-planned-input').val()

        }, function (data) {
            // Insert new category line after last category row already in table
            // .prepend() on <tr id='budget-totals'>
            let newRow = $('<tr class="budget-category"></tr>');
            let newCategoryName = '<td class="budget-category-name">' + data['category'] + '</td>';
            let newCategoryPlanned = '<td class="budget-category-planned">' + data['planned'] + '</td><td>0</td><td>' + data['planned'] + '</td>';
            newRow.append(newCategoryName, newCategoryPlanned);
            console.log(newRow);
            $('tr#budget-totals').before(newRow);
            $('div#new-category-form').remove();
            $('span#add-new-category').fadeIn();

        });
        return false;
    }


}