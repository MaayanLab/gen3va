var GEN3VA = GEN3VA || {};

GEN3VA.setupIndexPage = function(bioCategories) {

    !function setupTagSearch() {
        hideEmptyBioCategories();

        var lists = [],
            options = {
                valueNames: ['name']
            };

        $.each(bioCategories, function(i, name) {
            name = toCssSelector(name);
            var list = new List(name, options);
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
            hideEmptyBioCategories();
        });
    }();

    function hideEmptyBioCategories() {
        $.each(bioCategories, function(i, name) {
            var $category = $('#' + toCssSelector(name))
            var $list = $category.find(' ul li');
            if (!$list.length) {
                $category.hide();
            } else {
                $category.show();
            }
        });
    }

    function toCssSelector(value) {
        return value.toLowerCase().replace(/ /g, '-').replace(/_/g, '');
    }
};
