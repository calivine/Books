$(function () {
    var compare = {
        name: function(a, b) {
          if (a < b) {
              return -1;
          }  else {
              return a > b ? 1 : 0;
          }
        },
        date: function (a, b) {
            a = new Date(a);
            b = new Date(b);

            return a - b;
        },
        amount: function (a, b) {
            a = a.replace(/^\$/g, '');
            b = b.replace(/^\$/g, '');
            return Number(a) - Number(b);
        }
    };

    $('.sortable').each(function () {
        // Store variables
        var $table = $(this);
        var $tbody = $table.find('tbody');
        var $controls = $table.find('th');
        var rows = $tbody.find('tr').toArray(); // Store array  containing rows

        $controls.on('click', function () {
            $('th').css('background-color', '#e6e6e6');
            var $header = $(this);
            var order = $header.data('sort');
            var column;
            $header.css('background-color', '#83EDEC');

            if ($header.is('.ascending') || $header.is('.descending')) {
                $header.toggleClass('ascending descending');
                $tbody.append(rows.reverse());
            } else {
                $header.addClass('ascending');
                $header.siblings().removeClass('ascending descending');
                if (compare.hasOwnProperty(order)) {
                    column = $controls.index(this);

                    rows.sort(function (a, b) {
                        a = $(a).find('td').eq(column).text();
                        b = $(b).find('td').eq(column).text();
                        return compare[order](a, b);
                    });

                    $tbody.append(rows);
                }
            }
        });
    });
});
