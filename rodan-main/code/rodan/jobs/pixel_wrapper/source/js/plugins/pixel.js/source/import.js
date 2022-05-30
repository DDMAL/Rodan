/*jshint esversion: 6 */

export class Import {
    constructor(pixelInstance, layers, pageIndex, zoomLevel, uiManager) {
        this.pixelInstance = pixelInstance;
        this.layers = layers;
        this.exportInterrupted = false;
        this.pageIndex = pageIndex;
        this.zoomLevel = zoomLevel;
        this.matrix = null;
        this.uiManager = uiManager;
    }

    /**
     * Allows a user to upload an image from their local machine to a layer as its background image.
     * @param layer
     * @param e
     */
    uploadLocalImageToLayer(layer, e)
    {
        let reader = new FileReader();

        reader.onload = (event) =>
        {
            this.importFromImageURLToLayer(layer, event.target.result);
        };

        reader.readAsDataURL(e.target.files[0]);
    }

    /**
     * Imports an image from a url to canvas and converts the RGB values of the image to the layer's RGB colours
     * Transparent pixels will stay transparent
     * @param layer
     * @param url: Data URLs are fully supported but file urls can cause the canvas to be "tainted" according to CORS
     * specifications since it comes from a different origin
     */
    importFromImageURLToLayer (layer, url)
    {
        let imageCanvas = document.createElement("canvas");
        imageCanvas.width = layer.getCanvas().width;
        imageCanvas.height = layer.getCanvas().height;

        let ctx = imageCanvas.getContext("2d");
        let img = new Image();
        img.src = url;

        img.onload = () =>
        {
            ctx.drawImage(img,0,0);

            let imageData = ctx.getImageData(0, 0, layer.getCanvas().width, layer.getCanvas().height),
                data = imageData.data;

            // Convert the colour of the image to the layer's colour
            for(let i = 0; i < data.length; i += 4)
            {
                data[i] = layer.colour.red;             // red
                data[i + 1] = layer.colour.green;       // green
                data[i + 2] = layer.colour.blue;        // blue
            }
            // overwrite original image
            ctx.putImageData(imageData, 0, 0);

            // Set this as the background image of the canvas
            layer.setBackgroundImageCanvas(imageCanvas);
            layer.drawLayer(this.pixelInstance.core.getSettings().maxZoomLevel, layer.getCanvas());
        };
    }
}