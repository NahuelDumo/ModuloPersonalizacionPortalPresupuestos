/**
 * Minimal helper to open a PDF URL and trigger print.
 * We'll bind this to a button in the portal template once we confirm the version and template IDs.
 */
(function () {
    'use strict';
    function openAndPrint(url) {
        var win = window.open(url, '_blank');
        if (!win) {
            // Popup blocked; fallback to navigate current window
            window.location.href = url;
            return;
        }
        var tryPrint = function () {
            try {
                win.focus();
                win.print();
            } catch (e) {
                // ignore
            }
        };
        // Give it a moment to load
        setTimeout(tryPrint, 800);
    }

    // Expose globally for template onclick usage
    window.salePortalQuoteOpenAndPrint = openAndPrint;
})();
