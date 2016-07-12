$(function() {
    var dataTable = $('table').dataTable({
        bPaginate: false,
        // Initialize sorted by number of signatures.
        order: [[ 1, 'desc' ]]
    });
    $('.dataTables_filter').hide();
    $('#search-box').keyup(function() {
       dataTable.fnFilter(this.value);
    });
});
