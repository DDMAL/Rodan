/*jshint esversion: 6 */
class PixelException
{
    constructor (message)
    {
        this.message = message;
    }
}

export class CannotDeleteLayerException extends PixelException {}

export class CannotSelectLayerException extends PixelException {}
