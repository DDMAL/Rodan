(function ($)
{
    var RKRotate = function(element, options)
    {
        var defaults = {
            imageUrl: null,
            gridFadeTime: 200,
            gridBoxHeight: 80,
            gridBoxWidth: 112,
            textBoxOutput: null,
            displayPrecision: 3,
            controlOutput: null,
            controlOutputMultiplier: 1
        };

        var settings = $.extend({}, defaults, options);

        var instanceVariables = {
            imageObject:  null,
            imageCanvas: null,
            gridObject:   null,
            currentAngle: null  // radians
        };

        $.extend(settings, instanceVariables);

        var self = this;  // Use self, not this, inside private functions. 

        var init = function()
        {
            settings.imageCanvas = document.createElement('canvas');
            settings.rkRotateElement.appendChild(settings.imageCanvas);
            settings.imageObject = new Image();

            settings.imageObject.onload = function ()
            {
                _setUpCanvas();
                _setUpGrid();
                _setUpRotateByDraggingTheImage();
            };

            settings.imageObject.src = settings.imageUrl;
            _updateAngle(0);
        };

        this.rotate = function (angle)
        {
            angle = modulo(angle, 2 * Math.PI);

            var canvas = this.getImageCanvas(),
                context = canvas.getContext('2d'),
                image = this.getImage();

            context.save();
            context.clearRect(0, 0, canvas.width, canvas.height);
            context.translate(canvas.width / 2, canvas.height / 2);
            context.rotate(angle);
            context.translate(-canvas.width / 2, -canvas.height / 2);
            context.drawImage(settings.imageObject, (canvas.width - image.width)/2, (canvas.height - image.height)/2, image.width, image.height);
            context.restore();

            _updateAngle(angle);
        };

        this.getImage = function ()
        {
            return settings.imageObject;
        };

        this.getImageCanvas = function ()
        {
            return settings.imageCanvas;
        };

        this.getGridFadeTime = function ()
        {
            return settings.gridFadeTime;
        };

        this.setGridFadeTime = function (newGridFadeTime)
        {
            settings.gridFadeTime = newGridFadeTime;
        };

        this.getGridBoxWidth = function ()
        {
            return settings.gridBoxWidth;
        };

        this.setGridBoxWidth = function (newGridBoxWidth)
        {
            settings.gridBoxWidth = newGridBoxWidth;
            _drawGrid();
        };

        this.getGridBoxHeight = function ()
        {
            return settings.gridBoxHeight;
        };

        this.setGridBoxHeight = function (newGridBoxHeight)
        {
            settings.gridBoxHeight = newGridBoxHeight;
            _drawGrid();
        };

        this.getRkRotateElement = function ()
        {
            return settings.rkRotateElement;
        };

        this.getCurrentAngle = function ()
        {
            return settings.currentAngle;
        };

        this.getGrid = function ()
        {
            return settings.gridObject;
        };

        this.showGrid = function ()
        {
            var grid = this.getGrid();

            $(grid).stop();
            $(grid).fadeIn(settings.gridFadeTime);
        };

        this.hideGrid = function ()
        {
            var grid = this.getGrid();

            $(grid).stop();
            $(grid).fadeOut(settings.gridFadeTime);
        };

        var _setUpCanvas = function()
        {
            var context = settings.imageCanvas.getContext('2d'),
                canvas = settings.imageCanvas,
                w = settings.imageObject.width,
                h = settings.imageObject.height,
                neededSize = Math.ceil(Math.sqrt(h*h + w*w)),
                rkRotateElement = settings.rkRotateElement;

            rkRotateElement.style.height = neededSize.toString() + 'px';
            rkRotateElement.style.width  = neededSize.toString() + 'px';
            $(rkRotateElement).css({position: 'relative'});

            canvas.height = neededSize;
            canvas.width  = neededSize;
            $(canvas).css({'zIndex' : '1'});
            context.drawImage(settings.imageObject, (neededSize - w)/2, (neededSize - h)/2, w, h);
        };

        var _setUpGrid = function()
        {
            settings.gridObject = document.createElement('canvas');
            $(settings.gridObject).css({
                'position': 'absolute',
                'left': '0px',
                'top': '0px',
                'zIndex' : '2'
            });
            settings.gridObject.height = settings.imageCanvas.height;
            settings.gridObject.width = settings.imageCanvas.width;

            _drawGrid();
        };

        var _drawGrid = function()
        {
            var gridObject = settings.gridObject,
                canvasSize = settings.imageCanvas.width,
                gridBoxHeight = self.getGridBoxHeight(),
                gridBoxWidth  = self.getGridBoxWidth(),
                gridContext = gridObject.getContext('2d');

            gridContext.clearRect(0, 0, gridObject.width, gridObject.height);
            gridContext.beginPath();

            // The initializers of these for loops help ensure that 
            //   - the centre of the image lies on a gridline crossing
            //   - the lines are drawn in the centre of the pixels so that they're one pixel thick, (hence the +0.5)
            for (var x = Math.floor(canvasSize / 2) % gridBoxWidth + 0.5; x <= canvasSize; x += gridBoxWidth)
            {
                gridContext.moveTo(x, 0);
                gridContext.lineTo(x, canvasSize);
            }

            for (var y = Math.floor(canvasSize / 2) % gridBoxHeight + 0.5; y <= canvasSize; y += gridBoxHeight)
            {
                gridContext.moveTo(0, y);
                gridContext.lineTo(canvasSize, y);
            }

            gridContext.lineWidth = 1;
            gridContext.strokeStyle = "rgba(0, 0, 150, 0.3)";
            gridContext.stroke();
            $(gridObject).hide();
            settings.gridObject = gridObject;
            settings.rkRotateElement.appendChild(gridObject);
        };

        var _setUpRotateByDraggingTheImage = function()
        {
            var imageCanvas = self.getImageCanvas();

            $(imageCanvas).mousedown( function()
            {
                // if (! self.clickedInsideImage(event))
                //     return;

                self.showGrid();
                _disableSelection();

                var clickLocation = {x: event.pageX, y: event.pageY},
                    previousAngle = self.getCurrentAngle(),
                    canvasOffset = $(imageCanvas).offset(),
                    centre = {x: canvasOffset.left + imageCanvas.width / 2, y: canvasOffset.top + imageCanvas.height / 2},
                    clickAngle = Math.atan2(clickLocation.y - centre.y, clickLocation.x - centre.x);

                $(window).mousemove( function(event)
                {
                    var dragAngle = Math.atan2(event.pageY - centre.y, event.pageX - centre.x),
                        newAngle = dragAngle - clickAngle + previousAngle;

                    self.rotate(newAngle);
                });
            });

            var grid = self.getGrid();

            $(grid).mousedown( function()
            {
                $(imageCanvas).trigger('mousedown');
            });

            $(window).mouseup( function()
            {
                $(window).unbind("mousemove");
                self.hideGrid();
                _enableSelection();
            });
        };

        var _updateAngle = function (angle)
        {
            settings.currentAngle = angle;
            _updateTextBoxOutput(angle);
            _updateControlOutput(angle);
        };

        var _updateTextBoxOutput = function (angle)
        {
            if (settings.textBoxOutput)
            {
                $(settings.textBoxOutput).val((angle * 180 / Math.PI).toFixed(settings.displayPrecision));
            }
        };

        var _updateControlOutput = function (angle)
        {
            if (settings.controlOutput)
            {
                var M = settings.controlOutputMultiplier;

                settings.controlOutput.val(angle * 180 / Math.PI * M);
                settings.controlOutput.trigger('change');
            }
        };

        var _disableSelection = function ()
        {
            $('body').css({
              '-webkit-user-select': 'none',
              '-moz-user-select:': '-moz-none',
              '-ms-user-select': 'none',
              'user-select': 'none'
          });
        };

        var _enableSelection = function ()
        {
            $('body').css({
              '-webkit-user-select': '',
              '-moz-user-select:': '',
              '-ms-user-select': '',
              'user-select': ''
          });
        };

        var modulo = function (dividend, divisor)
        {
            // The % modulo operator is incorrect when the dividend is negative.
            // http://javascript.about.com/od/problemsolving/a/modulobug.htm
            return ((dividend % divisor) + divisor) % divisor;
        };

        init();
    };

    $.fn.RKRotate = function(options)
    {
        return this.each(function ()
        {
            var element = $(this);

            if (element.data('RKRotate'))
                return;

            options.rkRotateElement = element[0];

            var template = new RKRotate(this, options);

            element.data('RKRotate', template);
        });
    };
}
)(jQuery);
