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
        var $checkboxes = $($dataTable.cells().nodes()).find('input.consensus');
        $('#select-all').click(function(evt) {
            if ($(evt.target).prop('checked')) {
                $checkboxes.prop('checked', true);
            } else {
                $checkboxes.prop('checked', false);
            }
        });
    }

    function setupBuildReportListener() {
        $('#custom-report-builder button').click(function() {
            var chbxs = getSelectedCheckboxes();
            if (isValidSelection(chbxs)) {
                var parts = window.location.href.split('/'),
                    tag = parts[parts.length-1];
                requestReport(chbxs, tag);
            }
        });
    }

    /* Kicks off custom report builder and redirects user.
     */
    function requestReport(chbxs, tag) {
        $.ajax({
            url: 'report/' + tag + '/custom',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                gene_signatures: chbxs
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
        var isValid,
            platform;
        if (chbxs.length === 0) {
            alert('Please select a gene signature.');
            return false;
        }
        if (vizType === 'pca' && chbxs.length < 3) {
            alert('3D PCA requires at least 3 dimensions.');
            return false;
        }

        isValid = true;

        // Disable for now in favor of select all!
        // ---------------------------------------
        //platform = chbxs[0].platform;
        //$.each(chbxs, function(i, obj) {
        //    if (obj.platform !== platform) {
        //        isValid = false;
        //        return false; // Early return.
        //    }
        //});
        //
        //if (!isValid) {
        //    alert('Every gene signature must come from the same platform.');
        //}

        return isValid;
    }
});