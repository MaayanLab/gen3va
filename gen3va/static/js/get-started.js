$(function() {

    (function watchGEOForm() {
        $('form').submit(function(evt) {
            evt.preventDefault();
            var keyword = $('#search-box').val();
            window.location.href = 'http://www.ncbi.nlm.nih.gov/gds/?term=' + keyword;
        });
    })();

    function isChromeBrowser() {
        var isChromium = window.chrome,
            winNav = window.navigator,
            vendorName = winNav.vendor,
            isOpera = winNav.userAgent.indexOf("OPR") > -1,
            isIEedge = winNav.userAgent.indexOf("Edge") > -1,
            isIOSChrome = winNav.userAgent.match("CriOS"),
            isChrome;

        if (isIOSChrome) {
            isChrome = true;
        } else if (
            isChromium !== null && isChromium !== undefined &&
            vendorName === "Google Inc." &&
            !isOpera &&
            !isIEedge) {

            isChrome = true;
        } else {
            isChrome = false;
        }

        return isChrome;
    }

    function isExtensionInstalled(cb) {
        setTimeout(function() {
            var extensionInstalled = false;
            if ($('#geo2enrichr-extension-installed-div').length) {
                extensionInstalled = true;
            }
            cb(extensionInstalled);
        }, 500);
    }

    function setChecklistItemStatus(itemChecked, cssSelector, message) {
        var $el = $(cssSelector);
        if (itemChecked) {
            $el.html('<span class="pass">&#10003;</span>');
        } else {
            $el.html('<span class="fail">&#x2718; ' + message + '</span>');
        }
    }

    setChecklistItemStatus(
        isChromeBrowser(),
        '#is-chrome-browser span',
        'Please install <a href="https://www.google.com/chrome/" target="_blank">Google Chrome</a>.'
    );

    isExtensionInstalled(function(extensionInstalled) {
        setChecklistItemStatus(
            extensionInstalled,
            '#geo2enrichr-is-installed span',
            'Please install <a href="https://chrome.google.com/webstore/detail/geo2enrichr/pcbdeobileclecleblcnadplfcicfjlp" target="_blank">GEO2Enrichr</a>.'
        );
    });
});
