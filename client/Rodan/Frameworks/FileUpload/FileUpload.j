//
// FileUpload.j
// Editor
//
// Created by Francisco Tolmasky on 03/04/08.
// Copyright 2005 - 2008, 280 North, Inc. All rights reserved.
//

@import <Foundation/CPObject.j>
@import <Foundation/CPValue.j>
@import <Foundation/CPException.j>

@implementation UploadButton : CPButton
{
    DOMElement      _DOMIFrameElement;
    DOMElement      _fileUploadElement;
    DOMElement      _uploadForm;

    function        _mouseMovedCallback;
    function        _mouseUpCallback;

    id              _delegate;

    CPDictionary    _parameters;
    var             _isBrowser;

    CPString        _fileKey;
}

- (void)setup
{
            // Determine which browser is being used.

        _isBrowser = {
            IE:     !!(window.attachEvent && !window.opera),
            Opera:  !!window.opera,
            WebKit: navigator.userAgent.indexOf('AppleWebKit/') > -1,
            Gecko:  navigator.userAgent.indexOf('Gecko') > -1 && navigator.userAgent.indexOf('KHTML') == -1
        };

        _uploadForm = document.createElement("form");

        _uploadForm.method = "POST";
        _uploadForm.action = "#";

        if (_isBrowser.IE)
            _uploadForm.encoding = "multipart/form-data";
        else
            _uploadForm.enctype = "multipart/form-data";

        _fileUploadElement = document.createElement("input");

        _fileUploadElement.type = "file";
        _fileUploadElement.name = "file[]";

        _fileUploadElement.onmousedown = function(aDOMEvent)
        {
            aDOMEvent = aDOMEvent || window.event;

            var x = aDOMEvent.clientX,
                y = aDOMEvent.clientY,
                theWindow = [self window];

            [CPApp sendEvent:[CPEvent mouseEventWithType:CPLeftMouseDown location:[theWindow convertBridgeToBase:CGPointMake(x, y)]
                modifierFlags:0 timestamp:0 windowNumber:[theWindow windowNumber] context:nil eventNumber:-1 clickCount:1 pressure:0]];
            [[CPRunLoop currentRunLoop] limitDateForMode:CPDefaultRunLoopMode];

            if (document.addEventListener)
            {
                document.addEventListener(CPDOMEventMouseUp, _mouseUpCallback, NO);
                document.addEventListener(CPDOMEventMouseMoved, _mouseMovedCallback, NO);
            }
            else if (document.attachEvent)
            {
                document.attachEvent("on" + CPDOMEventMouseUp, _mouseUpCallback);
                document.attachEvent("on" + CPDOMEventMouseMoved, _mouseMovedCallback);
            }
        }

        _mouseUpCallback = function(aDOMEvent)
        {
            if (document.removeEventListener)
            {
                document.removeEventListener(CPDOMEventMouseUp, _mouseUpCallback, NO);
                document.removeEventListener(CPDOMEventMouseMoved, _mouseMovedCallback, NO);
            }
            else if (document.attachEvent)
            {
                document.detachEvent("on" + CPDOMEventMouseUp, _mouseUpCallback);
                document.detachEvent("on" + CPDOMEventMouseMoved, _mouseMovedCallback);
            }

            aDOMEvent = aDOMEvent || window.event;

            var x = aDOMEvent.clientX,
                y = aDOMEvent.clientY,
                theWindow = [self window];

            [CPApp sendEvent:[CPEvent mouseEventWithType:CPLeftMouseUp location:[theWindow convertBridgeToBase:CGPointMake(x, y)]
               modifierFlags:0 timestamp:0 windowNumber:[theWindow windowNumber] context:nil eventNumber:-1 clickCount:1 pressure:0]];
            [[CPRunLoop currentRunLoop] limitDateForMode:CPDefaultRunLoopMode];
        }

        _mouseMovedCallback = function(aDOMEvent)
        {
            aDOMEvent = aDOMEvent || window.event;

            var x = aDOMEvent.clientX,
                y = aDOMEvent.clientY,
                theWindow = [self window];

            [CPApp sendEvent:[CPEvent mouseEventWithType:CPLeftMouseDragged location:[theWindow convertBridgeToBase:CGPointMake(x, y)]
               modifierFlags:0 timestamp:0 windowNumber:[theWindow windowNumber] context:nil eventNumber:-1 clickCount:1 pressure:0]];
        }

        _uploadForm.style.position = "absolute";
        _uploadForm.style.top = "0px";
        _uploadForm.style.left = "0px";
        _uploadForm.style.zIndex = 1000;

        _fileUploadElement.style.opacity = "0";
        _fileUploadElement.style.filter = "alpha(opacity=0)";

        _uploadForm.style.width = "100%";
        _uploadForm.style.height = "100%";

        _fileUploadElement.style.fontSize = "1000px";

        if (_isBrowser.IE)
        {
            _fileUploadElement.style.position = "relative";
            _fileUploadElement.style.top = "-10px";
            _fileUploadElement.style.left = "-10px";
            _fileUploadElement.style.width = "1px";
        }
        else if (_isBrowser.Opera)
        {
            _fileUploadElement.style.position = "relative";
            _fileUploadElement.style.top = "0px";
            _fileUploadElement.style.left = "0px";
            _fileUploadElement.style.width = "100%";
            _fileUploadElement.style.height = "100%";
            _fileUploadElement.style.border = "none";
        }
        else
        {
            _fileUploadElement.style.cssFloat = "right";
        }

        _fileUploadElement.onchange = function()
        {
            [self uploadSelectionDidChange: [self selection]];
        };

        _uploadForm.appendChild(_fileUploadElement);

        _DOMElement.appendChild(_uploadForm);

        _parameters = [CPDictionary dictionary];

        [self setBordered:NO];

}
- (id)initWithCoder:(CPCoder)aCoder
{
    self = [super initWithCoder:aCoder];
    if (self)
    {
        [self setup];
    }
    return self;
}

- (id)initWithFrame:(CGRect)aFrame
{
    self = [super initWithFrame:aFrame];

    if (self)
    {
        [self setup];
    }

    return self;
}

// Override setEnabled.  Remove the _fileUploadElement when disabling, add it
// back in when enabling.
- (void)setEnabled:(BOOL)isEnabled
{
    if (! isEnabled)
    {
        if ([self isEnabled])
        {
            // Remove file upload element to disable.
            [self _removeUploadFormElements];
        }
    }
    else
    {
        if (! [self isEnabled])
        {
            // Add file upload element to enable.
            _uploadForm.appendChild(_fileUploadElement);
        }
    }

    [super setEnabled:isEnabled];
}


- (void)allowsMultipleFiles:(BOOL)allowsMultipleFiles
{
    _fileUploadElement.removeAttribute("multiple");  // Start as single file.

    if (allowsMultipleFiles)
    {
        _fileUploadElement.setAttribute("multiple", "true");
    }
}

- (void)setFileKey:(CPString)aKey
{
    _fileUploadElement.name = aKey;
}

- (void)setDelegate:(id)aDelegate
{
    _delegate = aDelegate;
}

- (id)delegate
{
    return _delegate;
}

- (void)setURL:(CPString)aURL
{
    _uploadForm.action = aURL;
}

- (void)uploadSelectionDidChange:(CPArray)selection
{
    if ([_delegate respondsToSelector:@selector(uploadButton:didChangeSelection:)])
        [_delegate uploadButton: self didChangeSelection: selection];
}

- (CPArray)selection
{
    var selection = [CPArray  array];

    if (_fileUploadElement.files)
    {
        var i = 0,
            length = _fileUploadElement.files.length,
            fileName;

        for (; i < length; i++)
        {
            fileName = _fileUploadElement.files.item(i).name
            if (! fileName && _fileUploadElement.files.item(i).fileName)
                fileName = _fileUploadElement.files.item(i).fileName

            [selection addObject:fileName];
        }
    }
    else
    {
        [selection addObject:_fileUploadElement.value];
    }

    return selection;
}

- (void)resetSelection
{
    _fileUploadElement.value = "";
}

- (void)uploadDidFinishWithResponse:(CPString)response
{
    if ([_delegate respondsToSelector:@selector(uploadButton:didFinishUploadWithData:)])
        [_delegate uploadButton: self didFinishUploadWithData: response];

}

- (void)uploadDidFailWithError:(CPString)anError
{
    if ([_delegate respondsToSelector:@selector(uploadButton:didFailWithError:)])
        [_delegate uploadButton: self didFailWithError: anError];
}

- (BOOL)setValue:(CPString)aValue forParameter:(CPString)aParam
{
    if (aParam == "file")
        return NO;

    [_parameters setObject:aValue forKey:aParam];

    return YES;
}

- (void)parameters
{
    return _parameters;
}

- (void)submit
{
    _uploadForm.target = "FRAME_"+(new Date());

    //remove existing parameters
    [self _removeUploadFormElements];

    //append the parameters to the form
    var keys = [_parameters allKeys];
    for (var i = 0, count = keys.length; i < count; i++)
    {
        var element = document.createElement("input");

        element.type = "hidden";
        element.name = keys[i];
        element.value = [_parameters objectForKey:keys[i]];

        _uploadForm.appendChild(element);
    }

    _uploadForm.appendChild(_fileUploadElement);

    if (_DOMIFrameElement)
    {
        document.body.removeChild(_DOMIFrameElement);
        _DOMIFrameElement.onload = nil;
        _DOMIFrameElement = nil;
    }

    if (_isBrowser.IE)
    {
        _DOMIFrameElement = document.createElement("<iframe id=\"" + _uploadForm.target + "\" name=\"" + _uploadForm.target + "\" />");

        if (window.location.href.toLowerCase().indexOf("https") === 0)
            _DOMIFrameElement.src = "javascript:false";
    }
    else
    {
        _DOMIFrameElement = document.createElement("iframe");
        _DOMIFrameElement.name = _uploadForm.target;
    }

    _DOMIFrameElement.style.width = "1px";
    _DOMIFrameElement.style.height = "1px";
    _DOMIFrameElement.style.zIndex = -1000;
    _DOMIFrameElement.style.opacity = "0";
    _DOMIFrameElement.style.filter = "alpha(opacity=0)";

    document.body.appendChild(_DOMIFrameElement);

    var _onloadHandler = function()
    {
        try
        {
            var responseText = _DOMIFrameElement.contentWindow.document.body ? _DOMIFrameElement.contentWindow.document.body.innerText :
                                                                               _DOMIFrameElement.contentWindow.document.documentElement.textContent;

            [self uploadDidFinishWithResponse: responseText];

            window.parent.setTimeout(function(){
                document.body.removeChild(_DOMIFrameElement);
                _DOMIFrameElement.onload = nil;
                _DOMIFrameElement = nil;
            }, 100);
        }
        catch (e)
        {
            [self uploadDidFailWithError:e];
        }
    }

    if (_isBrowser.IE)
    {
        _DOMIFrameElement.onreadystatechange = function()
        {
            if (this.readyState == "loaded" || this.readyState == "complete")
                _onloadHandler();
        }
    }

    _DOMIFrameElement.onload = _onloadHandler;

    _uploadForm.submit();

    if ([_delegate respondsToSelector:@selector(uploadButtonDidBeginUpload:)])
        [_delegate uploadButtonDidBeginUpload:self];
}

- (void)_removeUploadFormElements
{
    var index = _uploadForm.childNodes.length;
    while (index--)
        _uploadForm.removeChild(_uploadForm.childNodes[index]);
}

@end
