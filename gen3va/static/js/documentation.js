$(function() {
    var hash = location.hash.replace('#', '');
    if (hash) {
        selectH1(hash);
    }

    $('#documentation-nav li a').click(function(evt) {
        var id = $(evt.target).attr('href').split('#')[1];
        selectH1(id);
    });

    function selectH1(id) {
        $('h2').removeClass('selected');
        $('h2#' + id).addClass('selected');
    }
});
