$(function() {

    var $container = $('#isotope').isotope({
        itemSelector: '.tag-box',
        layoutMode: 'fitRows',
        sortBy: 'name',
        getSortData: {
            name: '.tag-name'
        }
    });

    setTimeout(function() {
        $container.isotope({filter: '*'});
    }, 0);

    $('#filters').on('click', 'button', function() {
        var filterValue = $(this).attr('data-filter');
        $container.isotope({filter: filterValue});
    });
});