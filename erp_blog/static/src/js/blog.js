/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { useService } from "@web/core/utils/hooks";

publicWidget.registry.ErpWebsiteBlog = publicWidget.Widget.extend({
    selector: ".website_blog",
    events: {
        'click .nav-link, nav-item': '_onItemClick',
        'click .post-loader': '_loadMore'
    },

    setup() {
        this.rpc = useService("rpc");
        this._super(...arguments);
    },
    _loadMore: function (ev) {
         ev.preventDefault();
         const url = ev.currentTarget.getAttribute("href");
         const pager = ev.target.closest('.post-loader');
         if (pager){
            pager.remove();
         }
         fetch(url, { method: "GET" }).then(function (response) {
            return response.text()
         }).then((result) => {
             const tempDiv = document.createElement("div");
             tempDiv.innerHTML = result;
             const newItem = tempDiv.querySelector("#o_wblog_index_content");
             const currentItem = $("#o_wblog_index_content").last();
             if (newItem && currentItem) {
                currentItem.after(newItem);
                history.pushState({}, "", url);
                var publicWidgetApp = new publicWidget.registry.ErpWebsiteBlog();
                publicWidgetApp.attachTo(newItem);
             }
         })
    },
    _onItemClick: function (ev) {
        ev.preventDefault();
        const url = ev.currentTarget.getAttribute("href");
         this.el.querySelectorAll(".nav-link").forEach(el => {
            el.classList.remove("active");
        });
        ev.currentTarget.classList.add("active");
        fetch(url, { method: "GET" })
            .then(function (response) {
                return response.text();
            })
            .then((result) => {
                const tempDiv = document.createElement("div");
                tempDiv.innerHTML = result;

                const newItem = tempDiv.querySelector("#o_wblog_index_content");

                const currentItem = this.el.querySelector("#o_wblog_index_content");
                this.el.querySelectorAll("#o_wblog_index_content").forEach(el => {
                    if (el !== currentItem) {
                        el.remove();
                    }
                });
                if (newItem && currentItem) {
                    currentItem.replaceWith(newItem);
                    history.pushState({}, "", url);
                    var publicWidgetApp = new publicWidget.registry.ErpWebsiteBlog();
                    publicWidgetApp.attachTo(newItem);
                }

            })
            .catch(function (error) {
                console.error("Fetch error:", error);
        });
    }
});

