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
        enableAutoTitle: false
    });

    var dv = $('#diva-wrapper').data('diva');

    $('#form').submit(function () {
        var query = $('#query-input').val();
        var type = $('#query-type option:selected').val();
        console.log(type);
        console.log(query);
        $.ajax({
            url: 'query',
            data: {
                type: type,
                query: query,
                zoom: dv.getZoomLevel()
            },
            cache: false,
            dataType: 'json',
            error: function (data) {
                console.log("AHHHHHHH");
            },
            success: function (data) {
                var realType = $('option[value=' + type + ']').text().toLowerCase();
                console.log(data);
                var numResults = data.length;
                console.log("omg");
                $('#placeholder-text').hide();
                var resultText = $('#result-text');
                resultText.find('.current').text(1);
                resultText.find('.total').text(numResults);
                resultText.find('.query').text(query);
                resultText.find('.type').text(realType);
                $('#result-text').show();
            }
        });
        var boxes
        return false;
    });
});
