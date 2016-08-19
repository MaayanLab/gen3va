$(function() {

    var $dataTable,
        extractionId = getUrlParameter('extraction_id');

    if (extractionId) {
        setupDataTables(extractionId);
        highlightSignature(extractionId);
    } else {
        setupDataTables();
    }

    setupBuildReportListener();
    setupSelectAll();

    function setupDataTables($tr) {
        var $tr = getRowFromExtractionId(extractionId),
            idx = parseInt($tr.find('td').first().text()) - 1,
            firstRow,
            thisRow;
        $dataTable = $('.data-table').eq(0).DataTable({
            bPaginate: true,
            iDisplayLength: 20
        });
        firstRow = $dataTable.row(0).data();
        thisRow = $dataTable.row(idx).data();
        $dataTable.row(0).data(thisRow);
        $dataTable.row(idx).data(firstRow);
    }

    function highlightSignature($tr) {
        var $tr = getRowFromExtractionId(extractionId);
        $tr.css({ 'background-color': '#fff169' });
        $tr.find('.optional-metadata-content').css({ 'background-color': '#e5d85e' });
    }

    function getRowFromExtractionId(extractionId) {
        return $('input[name="' + extractionId + '"]').parent().parent();
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
                metadataField = getMetadataField(),
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
            requestReport(chbxs, tag, reportName, metadataField);
        });
    }

    /* Kicks off custom report builder and redirects user.
     */
    function requestReport(chbxs, tag, reportName, category) {
        var payload = {
            gene_signatures: chbxs,
            report_name: reportName
        };
        if (category) {
            payload['category'] = category
        }
        $.ajax({
            url: 'report/custom/' + tag,
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(payload),
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

    /* Helper function that returns the metadata field if one has been
     * selected.
     */
    function getMetadataField() {
        var value = $('#custom-report-builder select').val();
        if (value === '(Select a metadata field)') {
            return;
        }
        return value
    }

    /* Returns the query string parameter requested.
     * Credit: http://stackoverflow.com/a/21903119.
     */
    function getUrlParameter(param) {
        var sPageURL = decodeURIComponent(window.location.search.substring(1)),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === param) {
                return sParameterName[1] === undefined ? true : sParameterName[1];
            }
        }
    };
});