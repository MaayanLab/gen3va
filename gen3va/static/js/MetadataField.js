
function MetadataField() {

    var id = Math.random().toString(36).substring(7),
        $parentElem = $('#optional-metadata #fields'),
        $elem, $key, $val;

    function create() {
        $parentElem.append(
            '<div class="form-group metadata" id="' + id + '">' +
            '   <input ' +
            '       placeholder="Name" ' +
            '       name="metadata-key-' + id + '" ' +
            '       class="form-control" ' +
            '       type="text"/>' +
            '   <input ' +
            '       placeholder="Value" ' +
            '       name="metadata-val-' + id + '" ' +
            '       class="form-control" ' +
            '       type="text"/>' +
            '   <button class="btn btn-warning remove-btn">' +
            '       &#10006;' +
            '   </button>' +
            '</div>'
        );
    }

    function destroy() {
        $elem.remove();
    }

    function listenForDestroy(destroyCb) {
        $elem.find('button').click(function() {
            destroy();
            destroyCb();
        });
    }

    function getKeyVal() {
        return {
            key: $key.val(),
            val: $val.val()
        }
    }

    function setKeyVal(key, val) {
        $key.val(key);
        $val.val(val);
    }

    create();
    $elem = $parentElem.find('#' + id);
    $key = $elem.find('input[name="metadata-key-' + id + '"]');
    $val = $elem.find('input[name="metadata-val-' + id + '"]');

    return {
        getId: function() { return id; },
        getKeyVal: getKeyVal,
        setKeyVal: setKeyVal,
        destroy: destroy,
        listenForDestroy: listenForDestroy
    }
}
