(function ($) {
    //Setup
    $(document).ready(function () {
        "use strict";
        var sidebarWidth = $("#sidebar").css("width");
        var sidebarFontSize = $("#sidebar").css("font-size");
        var contentWidth = $("#content").css("width");
        var contentPaddingLeft = $("#content").css("padding-left");/*
        window.setInterval(function () {
                if ($("#sidebar").css("width") == sidebarWidth) {
                    $("#sidebar").animate({
                            "width":'0px',
                            "font-size":'0px'
                        },
                        500);
                    $("#content").animate({
                            "width":'100%',
                            "padding-left":'0px'
                        },
                        500);
                } else {
                    $("#sidebar").animate({
                            "width":sidebarWidth,
                            "font-size":sidebarFontSize
                        },
                        500);
                    $("#content").animate({
                            "width":contentWidth,
                            "padding-left":contentPaddingLeft
                        },
                        500);
                }
            },
            2000);*/
    });
})(jQuery)
