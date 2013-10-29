/*
 * Treeview 1.4.1 - jQuery plugin to hide and show branches of a tree
 *
 * http://bassistance.de/jquery-plugins/jquery-plugin-treeview/
 * http://docs.jquery.com/Plugins/Treeview
 *
 * Copyright (c) 2007 Jörn Zaefferer
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Revision: $Id: jquery.treeview.js 5759 2008-07-01 07:50:28Z joern.zaefferer $
 *
 */
;(function(e){e.extend(e.fn,{swapClass:function(e,t){var n=this.filter("."+e);this.filter("."+t).removeClass(t).addClass(e);n.removeClass(e).addClass(t);return this},replaceClass:function(e,t){return this.filter("."+e).removeClass(e).addClass(t).end()},hoverClass:function(t){t=t||"hover";return this.hover(function(){e(this).addClass(t)},function(){e(this).removeClass(t)})},heightToggle:function(e,t){e?this.animate({height:"toggle"},e,t):this.each(function(){jQuery(this)[jQuery(this).is(":hidden")?"show":"hide"]();if(t)t.apply(this,arguments)})},heightHide:function(e,t){if(e){this.animate({height:"hide"},e,t)}else{this.hide();if(t)this.each(t)}},prepareBranches:function(e){if(!e.prerendered){this.filter(":last-child:not(ul)").addClass(t.last);this.filter((e.collapsed?"":"."+t.closed)+":not(."+t.open+")").find(">ul").hide()}return this.filter(":has(>ul)")},applyClasses:function(n,r){this.filter(":has(>ul):not(:has(>a))").find(">span").unbind("click.treeview").bind("click.treeview",function(t){if(this==t.target)r.apply(e(this).next())}).add(e("a",this)).hoverClass();if(!n.prerendered){this.filter(":has(>ul:hidden)").addClass(t.expandable).replaceClass(t.last,t.lastExpandable);this.not(":has(>ul:hidden)").addClass(t.collapsable).replaceClass(t.last,t.lastCollapsable);var i=this.find("div."+t.hitarea);if(!i.length)i=this.prepend('<div class="'+t.hitarea+'"/>').find("div."+t.hitarea);i.removeClass().addClass(t.hitarea).each(function(){var t="";e.each(e(this).parent().attr("class").split(" "),function(){t+=this+"-hitarea "});e(this).addClass(t)})}this.find("div."+t.hitarea).click(r)},treeview:function(n){function i(n,r){function i(r){return function(){s.apply(e("div."+t.hitarea,n).filter(function(){return r?e(this).parent("."+r).length:true}));return false}}e("a:eq(0)",r).click(i(t.collapsable));e("a:eq(1)",r).click(i(t.expandable));e("a:eq(2)",r).click(i())}function s(){e(this).parent().find(">.hitarea").swapClass(t.collapsableHitarea,t.expandableHitarea).swapClass(t.lastCollapsableHitarea,t.lastExpandableHitarea).end().swapClass(t.collapsable,t.expandable).swapClass(t.lastCollapsable,t.lastExpandable).find(">ul").heightToggle(n.animated,n.toggle);if(n.unique){e(this).parent().siblings().find(">.hitarea").replaceClass(t.collapsableHitarea,t.expandableHitarea).replaceClass(t.lastCollapsableHitarea,t.lastExpandableHitarea).end().replaceClass(t.collapsable,t.expandable).replaceClass(t.lastCollapsable,t.lastExpandable).find(">ul").heightHide(n.animated,n.toggle)}}function o(){function t(e){return e?1:0}var r=[];a.each(function(t,n){r[t]=e(n).is(":has(>ul:visible)")?1:0});e.cookie(n.cookieId,r.join(""),n.cookieOptions)}function u(){var t=e.cookie(n.cookieId);if(t){var r=t.split("");a.each(function(t,n){e(n).find(">ul")[parseInt(r[t])?"show":"hide"]()})}}n=e.extend({cookieId:"treeview"},n);if(n.toggle){var r=n.toggle;n.toggle=function(){return r.apply(e(this).parent()[0],arguments)}}this.data("toggler",s);this.addClass("treeview");var a=this.find("li").prepareBranches(n);switch(n.persist){case"cookie":var f=n.toggle;n.toggle=function(){o();if(f){f.apply(this,arguments)}};u();break;case"location":var l=this.find("a").filter(function(){return this.href.toLowerCase()==location.href.toLowerCase()});if(l.length){var c=l.addClass("selected").parents("ul, li").add(l.next()).show();if(n.prerendered){c.filter("li").swapClass(t.collapsable,t.expandable).swapClass(t.lastCollapsable,t.lastExpandable).find(">.hitarea").swapClass(t.collapsableHitarea,t.expandableHitarea).swapClass(t.lastCollapsableHitarea,t.lastExpandableHitarea)}}break}a.applyClasses(n,s);if(n.control){i(this,n.control);e(n.control).show()}return this}});e.treeview={};var t=e.treeview.classes={open:"open",closed:"closed",expandable:"expandable",expandableHitarea:"expandable-hitarea",lastExpandableHitarea:"lastExpandable-hitarea",collapsable:"collapsable",collapsableHitarea:"collapsable-hitarea",lastCollapsableHitarea:"lastCollapsable-hitarea",lastCollapsable:"lastCollapsable",lastExpandable:"lastExpandable",last:"last",hitarea:"hitarea"}})(jQuery);
