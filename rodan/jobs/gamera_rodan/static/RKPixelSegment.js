(function ($)
{
    /**
     * Main Pixel Segmentation app object.
     */
    var PixelSegmentation = function(aSettings)
    {

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PUBLIC
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        /**
         * Returns the geometries.
         */
        this.getGeometries = function()
        {
            return _geometries;
        };

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// INITIALIZATION
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Starts the application.
         */
        var run = function()
        {
            _initialize();
            _layerImage.loadImage(_settings.image.source);
        };

        /**
         * Initialization method.
         */
        var _initialize = function()
        {
            _geometries = [];
            _initializeKinetic();
            _layerImage = _createLayerImage();
            _layerCorrections = _createLayerCorrections();
            _layerUISegmentation = _createLayerUISegmentation();
            _stage.add(_layerImage);
            _stage.add(_layerCorrections);
            _stage.add(_layerUISegmentation);
            $('body').keydown(_processEvent);
            _imageContext = $('#container canvas')[0].getContext('2d');
            _correctionsContext = $('#container canvas')[1].getContext('2d');
            _setUIImageInfo();
            _setState(_STATE.IDLE);
        };

        /**
         * initialization for Kinetic.
         */
         var _initializeKinetic = function()
         {
            _stage = new Kinetic.Stage(_settings.kinetic.stage);
         };

        /**
         * Creates Kinetic layer: image.
         */
        var _createLayerImage = function()
        {
            var layer = new Kinetic.Layer(_settings.kinetic.layers.image);
            layer.on('click', _processEvent);
            layer.on('mousemove', _processEvent);
            layer.loadImage = _loadImage;
            return layer;
        };

        /**
         * Creates Kinetic layer: corrections.
         */
        var _createLayerCorrections = function()
        {
            var layer = new Kinetic.Layer(_settings.kinetic.layers.image);
            return layer;
        };

        /**
         * Creates Kinetic layer: front segmentation UI.
         */
        var _createLayerUISegmentation = function()
        {
            var layer = new Kinetic.Layer(_settings.kinetic.layers.image);
            layer.on('click', _processEvent);
            layer.on('mousemove', _processEvent);
            return layer;
        };

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// EVENT HANDLING
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Process state event.
         */
        var _processEvent = function(aEvent)
        {
            switch(_state)
            {
                case _STATE.IDLE:
                    _handleStateIdle(aEvent);
                    break;

                case _STATE.POLYGON:
                    _handleStatePolygon(aEvent);
                    break;

                case _STATE.RECTANGLE:
                    _handleStateRectangle(aEvent);
                    break;

                case _STATE.GLYPH_COLOURING:
                    _handleStateGlyphColouring(aEvent);
                    break;

                default:
                    // Do nothing.
                    break;
            }

            // Event output.
            if(aEvent.type != 'mousemove')
            {
                outputEvent(aEvent);
            }
        };

        /**
         * Handles 'Idle' state events.
         */
        var _handleStateIdle = function(aEvent)
        {
            if(aEvent.type === 'keydown')
            {
                if(aEvent.which === 80)
                {
                    aEvent.preventDefault();
                    _setState(_STATE.POLYGON);
                }
                else if(aEvent.which === 82)
                {
                    aEvent.preventDefault();
                    _setState(_STATE.RECTANGLE);
                }
            }
            _inputPolygon = [];
            _clearKineticPolygon();
            _clearKineticLine();
            _render();
        };

        /**
         * Handle state polygon.
         */
        var _handleStatePolygon = function(aEvent)
        {
            if(aEvent.type === 'mouseup')
            {
                aEvent.preventDefault();
                _inputPolygon.push({x: aEvent.layerX, y: aEvent.layerY});
                _defineKineticPolygon();
            }
            else if(aEvent.type === 'keydown')
            {
                if(aEvent.which === 27)
                {
                    aEvent.preventDefault();
                    _clearKineticPolygon();
                    _clearKineticLine();
                    _setState(_STATE.IDLE);
                }
                else if(aEvent.which === 67)
                {
                    aEvent.preventDefault();
                    _clearKineticLine();
                    _setState(_STATE.GLYPH_COLOURING);
                }
            }
            else if(aEvent.type === 'mousemove' && _inputPolygon.length > 0)
            {
                _defineKineticLine(aEvent.layerX, aEvent.layerY);
            }
            _render();
        };

        /**
         * Handle state rectangle.
         */
        var _handleStateRectangle = function(aEvent)
        {
            if(aEvent.type === 'mouseup')
            {
                aEvent.preventDefault();
                if(_inputPolygon.length === 1)
                {
                    _inputPolygon.push({x: aEvent.layerX, y: _inputPolygon[0].y});
                    _inputPolygon.push({x: aEvent.layerX, y: aEvent.layerY});
                    _inputPolygon.push({x: _inputPolygon[0].x, y: aEvent.layerY});
                    _setState(_STATE.GLYPH_COLOURING);
                }
                else
                {
                    _inputPolygon.push({x: aEvent.layerX, y: aEvent.layerY});
                }
                _defineKineticPolygon();
            }
            else if(aEvent.type === 'keydown')
            {
                if(aEvent.which === 27)
                {
                    aEvent.preventDefault();
                    _clearKineticPolygon();
                    _clearKineticLine();
                    _setState(_STATE.IDLE);
                }
            }
            else if(aEvent.type === 'mousemove' && _inputPolygon.length > 0)
            {
                _defineKineticLine(aEvent.layerX, aEvent.layerY);
            }
            _render();
        };

        /**
         * Handle glyph coloring state.
         */
        var _handleStateGlyphColouring = function(aEvent)
        {
            if(aEvent.type === 'keydown')
            {
                if(aEvent.which === 78) // neume
                {
                    _glyphColouring = _settings.glyphs.neume;
                }
                else if(aEvent.which === 84) // text
                {
                    _glyphColouring = _settings.glyphs.text;
                }
                else if(aEvent.which === 69) // white/erase
                {
                    _glyphColouring = _settings.glyphs.white;
                }
                else if(aEvent.which === 32 && _glyphColouring !== null)
                {
                    aEvent.preventDefault();
                    _saveGeometry();
                    _colourGlyphs(_glyphColouring);
                    _clearKineticPolygon();
                    _clearKineticLine();
                    _setState(_STATE.IDLE);
                }
                else if(aEvent.which === 27)
                {
                    aEvent.preventDefault();
                    _clearKineticPolygon();
                    _clearKineticLine();
                    _setState(_STATE.IDLE);
                }
            }
            _render();
        };

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// DRAWING/RENDERINGß
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Rendering.
         */
        var _render = function()
        {
            _layerUISegmentation.batchDraw();
        };

        /**
         * Defines the polygon.
         */
        var _defineKineticPolygon = function()
        {
            _clearKineticPolygon();
            if(_inputPolygon.length > 0)
            {
                _kineticPolygon = new Kinetic.Shape(_settings.kinetic.shape);
                _kineticPolygon.x(_inputPolygon[0].x);
                _kineticPolygon.y(_inputPolygon[0].y);
                _layerUISegmentation.add(_kineticPolygon);
            }
        };

        /**
         * Defines Kinetic line.
         */
        var _defineKineticLine = function(aLayerMouseX, aLayerMouseY)
        {
            var index = _inputPolygon.length - 1;
            if(_kineticLine === null)
            {
                _kineticLine = new Kinetic.Line(_settings.kinetic.line);
                _layerUISegmentation.add(_kineticLine);
            }
            _kineticLine.points([_inputPolygon[index].x, _inputPolygon[index].y, aLayerMouseX, aLayerMouseY]);
        };

        /**
         * Clears the polygon.
         */
        var _clearKineticPolygon = function()
        {
            if(_kineticPolygon !== null)
            {
                _kineticPolygon.destroy();
            }
            _kineticPolygon = null;
        };

        /**
         * Clears the line.
         */
        var _clearKineticLine = function()
        {
            if(_kineticLine !== null)
            {
                _kineticLine.destroy();
            }
            _kineticLine = null;
        };

        /**
         * Basic draw method for polygon.
         */
        var _drawPolygon = function(aContext)
        {
            for(var i = 0; i < _inputPolygon.length; i++)
            {
                // Don't draw path if initial point or last point.
                if(i === 0)
                {
                    aContext.beginPath();
                    aContext.moveTo(0, 0);
                }
                else
                {
                    var nextX = _inputPolygon[i].x - _inputPolygon[0].x;
                    var nextY = _inputPolygon[i].y - _inputPolygon[0].y;
                    aContext.lineTo(nextX, nextY);
                    aContext.stroke();
                }
            }
            aContext.closePath();
            aContext.stroke();
            aContext.fillStrokeShape(this);
        };

        /**
         * Color image.
         */
        var _colourGlyphs = function(aGlyphSettings)
        {
            // Get bounding box.
            var upperLeftX = Number.MAX_VALUE;
            var upperLeftY = Number.MAX_VALUE;
            var lowerRightX = 0;
            var lowerRightY = 0;
            for(var i = 0; i < _inputPolygon.length; i++)
            {
                upperLeftX = _inputPolygon[i].x < upperLeftX ? _inputPolygon[i].x : upperLeftX;
                upperLeftY = _inputPolygon[i].y < upperLeftY ? _inputPolygon[i].y : upperLeftY;
                lowerRightX = _inputPolygon[i].x > lowerRightX ? _inputPolygon[i].x : lowerRightX;
                lowerRightY = _inputPolygon[i].y > lowerRightY ? _inputPolygon[i].y : lowerRightY;
            }

            // We need to check if this is a rectangle.  That means we don't have to do collision detection.
            var isRectangle = _inputPolygon.length === 4 && _inputPolygon[0].y === _inputPolygon[1].y && _inputPolygon[1].x === _inputPolygon[2].x &&
                              _inputPolygon[2].y === _inputPolygon[3].y && _inputPolygon[3].x === _inputPolygon[0].x;

            // Next, go through image at each of those points and hit-test against our shape.  If it hits, color that pixel on the image.
            var width = lowerRightX - upperLeftX;
            var height = lowerRightY - upperLeftY;
            var positionX = upperLeftX;
            var positionY = upperLeftY;
            var imageData = _imageContext.getImageData(upperLeftX, upperLeftY, width, height);
            for(i = 0; i < imageData.data.length; i += 4)
            {
                if(isRectangle || _kineticPolygon.intersects({x: positionX, y: positionY}))
                {
                    // Check if pixel falls in thresholds.
                    var decision = true;
                    for(var j = 0; j < 4; j++)
                    {
                        decision = decision && ((!aGlyphSettings.inverseThresholds[j] && imageData.data[i + j] >= aGlyphSettings.thresholds[j]) ||
                                                (aGlyphSettings.inverseThresholds[j] && imageData.data[i + j] <= aGlyphSettings.thresholds[j]));
                    }

                    // If in threshold, color.
                    if(decision)
                    {
                        imageData.data[i] = aGlyphSettings.colour[0];
                        imageData.data[i + 1] = aGlyphSettings.colour[1];
                        imageData.data[i + 2] = aGlyphSettings.colour[2];
                        imageData.data[i + 3] = aGlyphSettings.colour[3];
                    }
                }
                positionX++;
                if(positionX >= lowerRightX)
                {
                    positionX = upperLeftX;
                    positionY++;
                }
            }
            _correctionsContext.putImageData(imageData, upperLeftX, upperLeftY);
        };

        /**
         * Saves the current input polygon to geometries array.
         */
        var _saveGeometry = function()
        {
            var newGeometry = {colour: _glyphColouring.colour,
                               points: _inputPolygon,
                               workingWidth: _kineticImage.getWidth()};
            _geometries.push(newGeometry);
        };

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// STATE METHODS
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Sets state.
         */
        var _setState = function(aState)
        {
            _state = aState;
            _setUIStateInfo();
        };

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// LOADERS
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Image loading method.  It automatically resizes
         */
        var _loadImage = function(aImageURL)
        {
            var image = new Image();
            var layer = this;
            image.onload = function()
            {
                _kineticImage = new Kinetic.Image({x: 0, y: 0, image: this, width: this.width, height: this.height});
                layer.parent.width(_kineticImage.getWidth() + layer.x());
                layer.parent.height(_kineticImage.getHeight() + layer.y());
                layer.add(_kineticImage);
                _kineticImage.cache();
                layer.draw();
            };
            image.src = aImageURL;
        };

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// UI
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Sets UI image info.
         */
        var _setUIImageInfo = function()
        {
        };

        /**
         * Sets UI state info.
         */
        var _setUIStateInfo = function()
        {
            $('#state').text(_getStateText());
        };

        /**
         * Display state.
         */
        var _getStateText = function()
        {
            var stateTitle = null;
            switch(_state)
            {
                case _STATE.IDLE:
                    stateTitle = "Idle";
                    break;

                case _STATE.POLYGON:
                    stateTitle = "Defining polygon";
                    break;

                case _STATE.RECTANGLE:
                    stateTitle = "Defining rectangle";
                    break;

                case _STATE.GLYPH_COLOURING:
                    stateTitle = "Glyph colouring";
                    break;

                default:
                    break;
            }
            return stateTitle;
        };

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CONSOLE
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Outputs info to console on event.
         */
        var outputEvent = function(aEvent)
        {
            if(_settings.debug)
            {
                console.log("---");
                console.log("state: " + _state);
                console.log("polygon:");
                console.log(_inputPolygon);
                console.log("mouse (layer): " + aEvent.layerX + ", " + aEvent.layerY);
                console.log("mouse (page): " + aEvent.pageX + ", " + aEvent.pageY);
                console.log("geometries");
                console.log(_geometries);
            }
        };

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PRIVATE MEMBERS
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        var _STATE =
        {
            IDLE: 0,
            POLYGON: 2,
            RECTANGLE: 3,
            GLYPH_COLOURING: 4
        };

        // Default settings.
        var _defaults =
        {
            // Kinetic stage settings.
            kinetic:
            {
                stage:
                {
                    container: 'container',
                    width: 500,
                    height: 800
                },

                layers:
                {
                    image:
                    {
                        x: 0,
                        y: 0,
                        width: 200,
                        height: 500
                    }
                },

                shape:
                {
                    fillRed: 0,
                    fillGreen: 255,
                    fillBlue: 0,
                    fillAlpha: 0.2,
                    strokeWidth: 2,
                    strokeEnabled: true,
                    strokeRed: 0,
                    strokeGreen: 255,
                    strokeBlue: 0,
                    strokeAlpha: 1,
                    drawFunc: _drawPolygon
                },

                line:
                {
                    x: 0,
                    y: 0,
                    stroke: 'green',
                    tension: 1
                }
            },

            // Glyph coloring settings.
            glyphs:
            {
                text:
                {
                    colour: [255, 0, 0, 255],
                    thresholds: [220, 127, 220, 255],
                    inverseThresholds: [true, false, true, false]
                },

                neume:
                {
                    colour: [0, 255, 0, 255],
                    thresholds: [127, 220, 220, 255],
                    inverseThresholds: [false, true, true, false]
                },

                white: // erase
                {
                    colour: [255, 255, 255, 255],
                    thresholds: [0, 0, 0, 0],
                    inverseThresholds: [false, false, false, false]
                }
            },

            // Image settings.
            image:
            {
                source: null
            },

            // Debug.
            debug: true
        };

        // Settings.
        var _settings = $.extend({}, _defaults, aSettings);

        // Members.
        var _stage = null;
        var _layerImage = null;
        var _layerCorrections = null;
        var _layerUISegmentation = null;
        var _state = _STATE.IDLE;
        var _inputPolygon = [];
        var _kineticPolygon = null;
        var _kineticImage = null;
        var _imageContext = null;
        var _glyphColouring = null;
        var _correctionsContext = null;
        var _kineticLine = null;
        var _geometries = null;

        // Run.
        run();
    };


    $.fn.PixelSegmentation = function(aOptions)
    {
        return this.each(function()
        {
            var element = $(this);
            if (element.data('PixelSegmentation'))
            {
                return;
            }
            var instance = new PixelSegmentation(aOptions);
            element.data('PixelSegmentation', instance);
        });
    };
})(jQuery);
