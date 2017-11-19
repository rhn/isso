/*
 * Copyright 2014, Martin Zimmermann <info@posativ.org>. All rights reserved.
 * Distributed under the MIT license
 */

require(["app/lib/ready", "app/config", "app/i18n", "app/api", "app/isso", "app/marginalia", "app/count", "app/dom", "app/text/css", "app/text/svg", "app/jade"], function(domready, config, i18n, api, isso, marginalia, count, $, css, svg, jade) {

    "use strict";

    jade.set("conf", config);
    jade.set("i18n", i18n.translate);
    jade.set("pluralize", i18n.pluralize);
    jade.set("svg", svg);

    var thread = function() {
        if ($("#isso-thread") === null) {
            return;
        }
        if (config["css"]) {
            var style = $.new("style");
            style.type = "text/css";
            style.textContent = css.inline;
            $("head").append(style);
        }

        $("#isso-thread").append($.new('h4'));
        if (config["readonly"]) {
            var lines = {'enter': i18n.translate('postcode-enter'),
                         'check': i18n.translate('codebox-activate')}
            $("#isso-thread").append(new isso.Codebox(lines));
        } else {
            $("#isso-thread").append(new isso.Postbox(null));
        }
        $("#isso-thread").append('<div id="isso-root"></div>');

        api.fetch($("#isso-thread").getAttribute("data-isso-id"),
            config["max-comments-top"],
            config["max-comments-nested"]).then(
            function(rv) {
                if (rv.replies.length == 0) {
                    $("#isso-thread > h4").textContent = i18n.translate("no-comments");
                    return;
                }

                var lastcreated = 0;
                var count = rv.replies.length;
                rv.replies.forEach(function(comment) {
                    isso.insert(comment, false, rv.date_added);
                    if(comment.created > lastcreated) {
                        lastcreated = comment.created;
                    }
                    count = count + comment.replies.length;
                });

                if(rv.hidden_replies > 0) {
                    isso.insert_loader(rv, lastcreated);
                }

                if (window.location.hash.length > 0) {
                    $(window.location.hash).scrollIntoView();
                }
            },
            function(err) {
                console.log(err);
            }
        );
    };
    
    var bookcode = function() {
        if ($("#isso-code") === null) {
            return;
        }
        var lines = {enter: i18n.translate("bookcode-enter"),
                     check: i18n.translate("bookcode-check")};
        $("#isso-code").append(new isso.Codebox(lines));
    };

    
    var overview = function() {
        if ($("#isso-overview") === null) {
            return;
        }
        $("#isso-overview").append('<div id="isso-root"></div>');

        api.threads().then(
            function(rv) {
                rv.threads.forEach(function(thread) {
                    marginalia.insert(thread);
                });

                if(rv.hidden_threads > 0) {
                    isso.insert_loader(rv, lastcreated);
                }

                if (window.location.hash.length > 0) {
                    $(window.location.hash).scrollIntoView();
                }
            },
            function(err) {
                console.log(err);
            }
        );
    };
        
    domready(overview);
    domready(bookcode);
    domready(thread);
});
