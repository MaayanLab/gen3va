$(function() {

    var hash = getHash();
    if (hash) {
        highlightSection(hash);
    }

    $('#documentation-nav li a').click(function(evt) {
        var $this = $(this),
            id = $this.attr('href').split('#')[1];
        scrollTo(id);
        highlightSection(id);
        addHash(id);
    });

    function highlightSection(id) {
        $('h2').removeClass('selected');
        $('h2#' + id).addClass('selected');
    }

    function scrollTo(id) {
        var top  = $('h2#' + id).offset().top;
        $('html, body')
            .stop()
            .animate({ scrollTop: top }, 700, function() {
                addHash(id);
            });
    }

    function addHash(id) {
        var hash = getHash(),
            node = $('#' + id);
        node.attr('id', '');
        window.location.hash = id;
        node.attr('id', hash);
    }

    function getHash() {
        return window.location.hash.replace('#', '');
    }
});
