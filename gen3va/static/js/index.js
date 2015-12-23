$(function() {

    var currentFilter = '*';

    var $container = $('#isotope').isotope({
        itemSelector: '.tag-box',
        layoutMode: 'fitRows',
        sortBy: 'name',
        getSortData: {
            name: '.tag-name'
        }
    });

    setTimeout(function() {
        $container.isotope({filter: currentFilter});
    }, 0);

    $('#filters').on('click', 'button', function() {
        var filterValue = $(this).attr('data-filter');
        currentFilter = filterValue;
        $container.isotope({filter: filterValue});
    });

    // Isotope doesn't always resize correctly, but calling this once the DOM
    // has been built seems to work.
    $(window).on('resize', function() {
        setTimeout(function() {
            $container.isotope({filter: currentFilter});
        }, 50);
    });
});