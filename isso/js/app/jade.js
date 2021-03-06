define(["libjs-jade-runtime", "app/utils", "jade!app/text/postbox", "jade!app/text/replybox", "jade!app/text/codebox", "jade!app/text/comment", "jade!app/text/thread", "jade!app/text/comment-loader"], function(runtime, utils, tt_postbox, tt_replybox, tt_codebox, tt_comment, tt_thread, tt_comment_loader) {
    "use strict";

    var globals = {},
        templates = {};

    var load = function(name, js) {
        templates[name] = (function(jade) {
                var fn;
                eval("fn = " + js);
                return fn;
            })(runtime);
    };

    var set = function(name, value) {
        globals[name] = value;
    };

    load("postbox", tt_postbox);
    load("replybox", tt_replybox);
    load("codebox", tt_codebox);
    load("comment", tt_comment);
    load("thread", tt_thread);
    load("comment-loader", tt_comment_loader);

    set("bool", function(arg) { return arg ? true : false; });
    set("humanize", function(date) {
        if (typeof date !== "object") {
            date = new Date(parseInt(date, 10) * 1000);
        }

        return date.toString();
    });
    set("datetime", function(date) {
        if (typeof date !== "object") {
            date = new Date(parseInt(date, 10) * 1000);
        }

        return [
            date.getUTCFullYear(),
            utils.pad(date.getUTCMonth(), 2),
            utils.pad(date.getUTCDay(), 2)
        ].join("-") + "T" + [
            utils.pad(date.getUTCHours(), 2),
            utils.pad(date.getUTCMinutes(), 2),
            utils.pad(date.getUTCSeconds(), 2)
        ].join(":") + "Z";
    });

    set("human_abs", function(date) {
        if (typeof date !== "object") {
            date = new Date(parseInt(date, 10) * 1000);
        }
        return date.toDateString();
    });

    set("days_rel", function(end_date, start_date) {
        if (typeof start_date !== "object") {
            start_date = new Date(parseInt(start_date, 10) * 1000);
        }
        if (typeof end_date !== "object") {
            end_date = new Date(parseInt(end_date, 10) * 1000);
        }
        var oneDay = 24*60*60*1000;
        return Math.round((end_date.getTime() - start_date.getTime())/(oneDay));
    });

    set("today", function() {
        return (new Date()).toDateString();
    });

    return {
        "set": set,
        "render": function(name, locals) {
            var rv, t = templates[name];
            if (! t) {
                throw new Error("Template not found: '" + name + "'");
            }

            locals = locals || {};

            var keys = [];
            for (var key in locals) {
                if (locals.hasOwnProperty(key) && !globals.hasOwnProperty(key)) {
                    keys.push(key);
                    globals[key] = locals[key];
                }
            }

            rv = templates[name](globals);

            for (var i = 0; i < keys.length; i++) {
                delete globals[keys[i]];
            }

            return rv;
        }
    };
});
