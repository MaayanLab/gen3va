$(function() {

    var $dataTable;

    setupDataTables();
    setupBuildReportListener();
    setupSelectAll();

    function setupDataTables() {
        $dataTable = $('.data-table').eq(0).DataTable({
            bPaginate: true,
            iDisplayLength: 20
        });
    }

    function setupSelectAll() {
        var $allCheckboxes = $($dataTable.cells().nodes()).find('input.consensus');


        $('#select-all').click(function(evt) {
            var searchText = $('.dataTables_filter input').val();
            if ($(evt.target).prop('checked')) {

                // If the user has input search text, we want to only check the selected results.
                if (searchText) {
                    $dataTable.rows({ search: 'applied' }).data().each(function(value) {
                        var name = $(value[5]).attr('name'),
                            input = $dataTable.$('input[name="' + name + '"]');
                        input.prop('checked', true);
                    });

                // Otherwise, we can select all the rows.
                } else {
                    $allCheckboxes.prop('checked', true);
                }
            } else {
                $allCheckboxes.prop('checked', false);
            }
        });
    }

    function setupBuildReportListener() {
        $('#custom-report-builder button').click(function() {
            var chbxs = getSelectedCheckboxes(),
                reportName = $('input[name="report-name"]').val();
            if (!isValidSelection(chbxs)) {
                return;
            }
            if (!reportName) {
                alert('Custom reports require names');
                return;
            }
            var parts = window.location.href.split('/'),
                tag = parts[parts.length-1];
            requestReport(chbxs, tag, reportName);
        });
    }

    /* Kicks off custom report builder and redirects user.
     */
    function requestReport(chbxs, tag, reportName) {
        $.ajax({
            url: 'report/custom/' + tag,
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                gene_signatures: chbxs,
                report_name: reportName
            }),
            success: function(data) {
                window.location = data.new_url;
            }
        });
    }

    /* Helper function for collecting data from selected checkboxes.
     */
    function getSelectedCheckboxes() {
        var selected = [],
            $checkboxes = $($dataTable.cells().nodes()).find('input.consensus');
        $checkboxes.each(function(i, checkbox) {
            var $checkbox = $(checkbox);
            if ($checkbox.is(':checked')) {
                selected.push({
                    extractionId: $checkbox.attr('name'),
                    platform: $checkbox.closest('tr').find('.platform').text()
                });
            }
        });
        return selected;
    }

    /* Helper function that validates the selected checkboxes, alerting and
     * returning false if invalid.
     */
    function isValidSelection(chbxs, vizType) {
        if (chbxs.length < 3) {
            alert('Reports require at least three signatures.');
            return false;
        }
        return true;
    }
});