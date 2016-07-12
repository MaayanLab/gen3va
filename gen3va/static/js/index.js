var GEN3VA = GEN3VA || {};

GEN3VA.setupTagSearch = function(bioCategories) {

    var lists = [],
        options = {
            valueNames: ['name']
        };

    $.each(bioCategories, function(i, bioCategoryName) {
        var list = new List(bioCategoryName, options);
        lists.push(list);
    });

    $('.tag-search').keyup(function() {
        var searchTerm = $(this).val();
        $.each(lists, function(i, list) {
            // If the list is empty, List.js throws an error. Just catch it so
            // we can search all lists in the DOM.
            try {
                list.search(searchTerm);
            } catch(e) {}
        });
    });
};

GEN3VA.hideEmptyBioCategories = function(bioCategories) {
    $.each(bioCategories, function(i, bioCategoryName) {
        var $category = $('#' + toCssSelector(bioCategoryName))
        var $list = $category.find(' ul li');
        if (!$list.length) {
            $category.hide();
        }
    });
    function toCssSelector(value) {
        return value.toLowerCase().replace(/ /g, '-').replace(/_/g, '');
    }
};
