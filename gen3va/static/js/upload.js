/* Handles the file upload form.
 */

$(function() {

    var upGenes,
        downGenes,
        fields = {},
        $exampleBtn = $('#example-btn');

    $exampleBtn.click(showExample);
    $('#add-metadata-btn').click(addMetadataField);

    function addMetadataField(evt) {
        if (evt) {
            evt.preventDefault();
        }
        var field = MetadataField(),
            id = field.getId();
        fields[id] = field;
        field.listenForDestroy(function() {
            delete fields[id];
        });
        return id;
    }

    function showExample(evt) {
        evt.preventDefault();
        var $textarea = $('textarea');
        if (isCombinedPage()) {
            $textarea.val(upGenes.concat(downGenes).join('\n'));
        } else {
            $textarea.eq(0).val(upGenes.join('\n'));
            $textarea.eq(1).val(downGenes.join('\n'));
        }

        $('input[name="tags"]').val('TEST_TAG');
        for (var idx in fields) {
            fields[idx].destroy();
        }
        var id = addMetadataField();
        fields[id].setKeyVal('gene', 'STAT3');
        $('input[name="name"]').val('My test signature');
    }

    (function simpleFormValidation() {
        var fieldsToValidate = [
            'input[name="name"]', 'textarea[name="genes"]',
            'textarea[name="up-genes"]', 'textarea[name="down-genes"]'
        ];
        fieldsToValidate.forEach(function(selector, i) {
            watchFormField(selector);
        });
    })();

    function watchFormField(cssSelector) {
        $(cssSelector).focusout(function() {
            var $input = $(this),
                $label = $(this).parent().find('label'),
                red = '#F15A5A',
                value = $input.val().replace(/ /g,'');
            if (value === '') {
                $label.css({ 'color': red });
                $input.css({ 'border-color': red });
            } else {
                validateFormField($label, $input);
            }
            $exampleBtn.click(function() {
                validateFormField($label, $input);
            });
        });
    }

    function validateFormField($label, $input) {
        $label.css({ 'color': 'black' });
        $input.css({ 'border-color': '#cccccc' });
    }

    function isCombinedPage() {
        return window.location.pathname === '/gen3va/upload/combined';
    }

    upGenes = [
        'KIAA0907',
        'KDM5A',
        'CDC25A',
        'EGR1',
        'GADD45B',
        'RELB',
        'TERF2IP',
        'SMNDC1',
        'TICAM1',
        'NFKB2',
        'RGS2',
        'NCOA3',
        'ICAM1',
        'TEX10',
        'CNOT4',
        'ARID4B',
        'CLPX',
        'CHIC2',
        'CXCL2',
        'FBXO11',
        'MTF2',
        'CDK2',
        'DNTTIP2',
        'GADD45A',
        'GOLT1B',
        'POLR2K',
        'NFKBIE',
        'GABPB1',
        'ECD',
        'PHKG2',
        'RAD9A',
        'NET1',
        'KIAA0753',
        'EZH2',
        'NRAS',
        'ATP6V0B',
        'CDK7',
        'CCNH',
        'SENP6',
        'TIPARP',
        'FOS',
        'ARPP19',
        'TFAP2A',
        'KDM5B',
        'NPC1',
        'TP53BP2',
        'NUSAP1'
    ];

    downGenes = [
        'SCCPDH',
        'KIF20A',
        'FZD7',
        'USP22',
        'PIP4K2B',
        'CRYZ',
        'GNB5',
        'EIF4EBP1',
        'PHGDH',
        'RRAGA',
        'SLC25A46',
        'RPA1',
        'HADH',
        'DAG1',
        'RPIA',
        'P4HA2',
        'MACF1',
        'TMEM97',
        'MPZL1',
        'PSMG1',
        'PLK1',
        'SLC37A4',
        'GLRX',
        'CBR3',
        'PRSS23',
        'NUDCD3',
        'CDC20',
        'KIAA0528',
        'NIPSNAP1',
        'TRAM2',
        'STUB1',
        'DERA',
        'MTHFD2',
        'BLVRA',
        'IARS2',
        'LIPA',
        'PGM1',
        'CNDP2',
        'BNIP3',
        'CTSL1',
        'CDC25B',
        'HSPA8',
        'EPRS',
        'PAX8',
        'SACM1L',
        'HOXA5',
        'TLE1',
        'PYGL',
        'TUBB6',
        'LOXL1'
    ];
});