let cookieBanner = (function () {
    'use strict';

    class CookieBanner {
        constructor() {
            this.localStorageKey = 'policy_accepted';
            this.elementId = 'cookie_banner';
        }

        hide() {
            document.getElementById(this.elementId).style.display = 'None';
        }

        accept() {
            this.hide();
            localStorage.setItem(this.localStorageKey, true);
        }

        hideIfAccepted() {
            if (localStorage.getItem(this.localStorageKey)) {
                this.hide();
            }
        }
    }

    return new CookieBanner();
})();

cookieBanner.hideIfAccepted();