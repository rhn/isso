define(function() {

    "use strict";
    var domready = function(callback) {
        // HTML5 standard to listen for dom readiness
        document.addEventListener('DOMContentLoaded', function() {
            callback();
        });

        // if dom is already ready, just run callback
        if (document.readyState === "interactive" || document.readyState === "complete" ) {
            callback();
        }
    };

    return domready;
});
