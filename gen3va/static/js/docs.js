$(function() {
    var hash = location.hash.replace('#', '');
    if (hash) {
        selectH1(hash);
    }

    $('#doc-nav li a').click(function(evt) {
        var id = $(evt.target).attr('href').split('#')[1];
        selectH1(id);
    });

    function selectH1(id) {
        $('h1').removeClass('selected');
        $('h1#' + id).addClass('selected');
    }
});
