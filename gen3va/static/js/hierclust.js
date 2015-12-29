$(function() {

    var $enrichr = $('#enrichr-hier-clusts'),
        $clusts = $enrichr.find('iframe');

    // Hide all but the first library's hierarchical clustering.
    $clusts.not($clusts.first()).hide();

    // When the user selects a new library, toggle the visible library.
    $enrichr.find('select').change(function(evt) {
        var new_enrichr_library = $(evt.target).val();
        $clusts.hide();
        $enrichr.find('iframe[data-enrichr-library=' + new_enrichr_library+ ']').show();
    });
});