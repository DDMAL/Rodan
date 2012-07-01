$(document).ready(function () {
    $('#diva-wrapper').diva({
        adaptivePadding: 0.07,
        fixedHeightGrid: false,
        tileFadeSpeed: 0,
        iipServerURL: $('#iipServerURL').val(),
        divaserveURL: 'divaserve',
        imageDir: '',
        enableCanvas: false,
        contained: true,
        enableAutoTitle: false,
        onZoom: function (zoomLevel) {
            if (settings.query) {
                loadSearch(zoomLevel);
            }
        },
        onPageLoad: function (pageIndex) {
            // If we're in a query, show any relevant boxes
            var box;

            if (settings.query) {
                if (pageExists(pageIndex)) {
                    for (boxIndex in settings.pages[pageIndex]) {
                        box = settings.pages[pageIndex][boxIndex];
                        drawBox(pageIndex, box);
                    }
                }
            }
        }
    });

    var dv = $('#diva-wrapper').data('diva');

    // Start search stuff
    var settings = {
        query: '',
        // The key is the pageIndex as defined by solr (the sequence field)
        pages: {},
        boxes: []
    };

    $('#form').submit(function () {
        loadSearch();
        return false;
    });

    var loadSearch = function (zoomLevel) {
        clearResults();
        var query = $('#query-input').val();
        settings.query = query;
        var type = $('#query-type option:selected').val();
        var zoomLevel = (zoomLevel !== undefined) ? zoomLevel : dv.getZoomLevel();

        // Switch out of grid mode if necessary
        dv.leaveGrid();
        $.ajax({
            url: 'query',
            data: {
                type: type,
                query: query,
                zoom: zoomLevel
            },
            cache: false,
            dataType: 'json',
            error: function (data) {
                console.log("AHHHHHHH");
            },
            success: function (data) {
                // Update the status stuff
                var realType = $('option[value=' + type + ']').text().toLowerCase();
                var numResults = data.length;
                $('#placeholder-text').hide();
                var resultText = $('#result-text');
                resultText.find('.current').text(1);
                resultText.find('.total').text(numResults);
                resultText.find('.query').text(query);
                resultText.find('.type').text(realType);
                $('#result-text').show();

                // Load the actual boxes
                loadBoxes(data);
            }
        });
    };

    var loadBoxes = function (boxes) {
        // Save the boxes so that we can scroll and stuff
        settings.boxes = boxes;
        var box, pageIndex;
        for (boxIndex in boxes) {
            box = boxes[boxIndex];
            pageIndex = box.p - 1;
            if (pageExists(pageIndex)) {
                drawBox(pageIndex, box);
            }

            if (pageIndex in settings.pages) {
                settings.pages[pageIndex].push(box);
            } else {
                settings.pages[pageIndex] = [box];
            }
        }
    };

    var getPageSelector = function (pageIndex) {
        var filename = (pageIndex + 1) + '.tiff';
        var realIndex = dv.getPageIndex(filename);
        return $('#1-diva-page-' + realIndex);
    };

    var pageExists = function (pageIndex) {
        return getPageSelector(pageIndex).length;
    };

    var drawBox = function (pageIndex, box) {
        getPageSelector(pageIndex).append('<div class="search-box" style="width: ' + box.w + 'px; height: ' + box.h + 'px; left: ' + box.x + 'px; top: ' + box.y + 'px;"></div>');
    };

    var clearResults = function () {
        // Reset some things
        $('.search-box').remove();
    };
});
