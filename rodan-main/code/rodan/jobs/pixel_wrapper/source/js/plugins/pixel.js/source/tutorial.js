/**
 * Created by zeyadsaleh on 2017-08-14.
 */
export class Tutorial
{
    constructor (pixelInstance)
    {
        this.pixelInstance = pixelInstance;
        this.currentTutorialPageIndex = 0;
        this.modalContent = document.createElement('div');
        this.createTutorial();
    }

    createTutorial ()
    {
        let overlay = document.createElement('div');
        overlay.setAttribute("id", "tutorial-div");

        let background = document.createElement('div');
        background.setAttribute("id", "tutorial-overlay");

        let modal = document.createElement('div');
        modal.setAttribute("id", "myModal");
        modal.setAttribute("class", "modal");

        this.modalContent.setAttribute("class", "modal-content");

        let modalHeader = document.createElement('div');
        modalHeader.setAttribute("class", "modal-header");

        let text = document.createTextNode("Tutorial");
        let h2 = document.createElement('h2');
        h2.appendChild(text);

        let closeModal = document.createElement('span');
        closeModal.setAttribute("class", "close");
        closeModal.innerHTML = "&times;";

        let modalBody = this.getModalBody(this.currentTutorialPageIndex);

        let modalFooter = document.createElement('div');
        modalFooter.setAttribute("class", "modal-footer");
        modalFooter.setAttribute("id", "modal-footer");

        let close = document.createElement('h2');
        close.innerHTML = "Got It!";

        modal.appendChild(this.modalContent);
        this.modalContent.appendChild(modalHeader);
        this.modalContent.appendChild(modalBody);
        this.modalContent.appendChild(modalFooter);
        modalHeader.appendChild(h2);
        modalHeader.appendChild(closeModal);
        modalFooter.appendChild(close);

        overlay.appendChild(background);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        modal.style.display = "block";

        modalFooter.addEventListener("click", () =>
        {
            overlay.parentNode.removeChild(overlay);
        });
    }

    getModalBody (tutorialPageIndex)
    {
        let modalBody = document.createElement('div');
        modalBody.setAttribute("class", "modal-body");
        modalBody.setAttribute("id", "modal-body");

        let tutorialP = document.createElement('p');
        let img = new Image();
        img.className = "tutorial-image";
        let next = document.createElement("button");
        next.innerHTML = "Next";
        let previous = document.createElement("button");
        previous.innerHTML = "Previous";
        let progress = document.createElement('p');
        progress.setAttribute("id", "tutorial-progress");
        progress.innerHTML = tutorialPageIndex + 1 + "/16";

        next.addEventListener("click", () =>
        {
            this.currentTutorialPageIndex++;
            this.getTutorialPage(this.currentTutorialPageIndex);
        });
        previous.addEventListener("click", () =>
        {
            this.currentTutorialPageIndex--;
            this.getTutorialPage(this.currentTutorialPageIndex);
        });

        switch (tutorialPageIndex)
        {
            case 0:
                tutorialP.innerHTML = "Navigate to the page you would like to edit and click the Pixel.js icon to open the toolboxes and layers view.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/01.gif";
                break;
            case 1:
                tutorialP.innerHTML = "Each layer has its own specific colour and represents a classification category. Create as many layers as needed. <br> A collection of keyboard shortcuts have been implemented. Each layer can be selected by its number (from <kbd>1</kbd> to <kbd>9</kbd>). Hover over the layers to receive a prompt.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/02.gif";
                break;
            case 2:
                tutorialP.innerHTML = "You can upload images to the currently selected layer. The image will be converted to the specified layer's colour. <br> In this example, we have uploaded the output images of a classification method in order to correct it.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/03.gif";
                break;
            case 3:
                tutorialP.innerHTML = "Double click on the layer's name to rename it.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/04.gif";
                break;
            case 4:
                tutorialP.innerHTML = "Use zoom along with the grab tool <kbd>g</kbd> to navigate a page.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/06.gif";
                break;
            case 5:
                tutorialP.innerHTML = "Use the select tool <kbd>s</kbd> to copy <kbd>Ctrl</kbd> + <kbd>c</kbd> or cut <kbd>Ctrl</kbd> + <kbd>x</kbd> and paste <kbd>Ctrl</kbd> + <kbd>v</kbd> rectangular regions of pixels from one layer to another.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/07.gif";
                break;
            case 6:
                tutorialP.innerHTML = "Right-click and drag right and left on the erase <kbd>e</kbd> and brush <kbd>b</kbd> tools to change the brush size.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/09.gif";
                break;
            case 7:
                tutorialP.innerHTML = "Press <kbd>Shift</kbd> and drag on the erase <kbd>e</kbd> and brush <kbd>b</kbd> tools to draw straight lines.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/10.gif";
                break;
            case 8:
                tutorialP.innerHTML = "Right-click and drag on rectangle tool <kbd>r</kbd> to erase rectangular regions, left-click to draw rectangle. Press <kbd>Shift</kbd> to draw squares.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/08.gif";
                break;
            case 9:
                tutorialP.innerHTML = "Use the Fullscreen mode <kbd>f</kbd> and the browser zoom to get more precision, when needed. <br> To exit Fullscreen mode, press on <kbd>f</kbd> again.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/fullscreen.gif";
                break;
            case 10:
                tutorialP.innerHTML = "You can bring a layer forward/backward by clicking and dragging them to their desired position.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/11.gif";
                break;
            case 11:
                tutorialP.innerHTML = "You can undo <kbd>Ctrl</kbd> + <kbd>z</kbd> and redo <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>z</kbd> an action.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/undo_redo.gif";
                break;
            case 12:
                tutorialP.innerHTML = "You can delete a layer by selecting it and then using <kbd>Ctrl</kbd> + <kbd>del</kbd>.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/delete_layer.gif";
                break;
            case 13:
                tutorialP.innerHTML = "You can mute (press <kbd>m</kbd> to toggle on/off) or hide (hold <kbd>h</kbd> to turn off, release to turn on) layers.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/12_layers_on_off.gif";
                break;
            case 14:
                tutorialP.innerHTML = "Change the opacity of a layer by displaying the layer options.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/05.gif";
                break;
            case 15:
                tutorialP.innerHTML = "Export layers as PNGs to save a specific layer as an image. See the " + '<a href="https://github.com/DDMAL/Pixel.js/wiki">wiki</a>' + " for details on the different export buttons and more information.";
                img.src = "https://github.com/DDMAL/Pixel.js/wiki/assets/21_export.gif";
                break;

            // let hotkeyGlossary = document.createElement('ul');
            // hotkeyGlossary.setAttribute("style", "list-style-type:none;");
            //
            // let LayerSelect = document.createElement('li');
            // LayerSelect.innerHTML = "<kbd>1</kbd> ... <kbd>9</kbd> layer select";
            //
            // let brushTool = document.createElement('li');
            // brushTool.innerHTML = "<kbd>b</kbd> brush tool";
            //
            // let rectangleTool = document.createElement('li');
            // rectangleTool.innerHTML = "<kbd>r</kbd> rectangle tool";
            //
            // let grabTool = document.createElement('li');
            // grabTool.innerHTML = "<kbd>g</kbd> grab tool";
            //
            // let eraserTool = document.createElement('li');
            // eraserTool.innerHTML = "<kbd>e</kbd> eraser tool";
            //
            // let shift = document.createElement('li');
            // shift.innerHTML = "<kbd>Shift</kbd>  force tools to paint in an exact way.";
            //
            // let undo = document.createElement('li');
            // undo.innerHTML = "<kbd>cmd</kbd> + <kbd>z</kbd> undo";
            //
            // let redo = document.createElement('li');
            // redo.innerHTML = "<kbd>cmd</kbd> + <kbd>Shift</kbd> + <kbd>z</kbd> redo";
        }

        modalBody.appendChild(img);
        modalBody.appendChild(tutorialP);
        if (this.currentTutorialPageIndex !== 0)
            modalBody.appendChild(previous);
        if (this.currentTutorialPageIndex !== 15)
            modalBody.appendChild(next);
        modalBody.appendChild(progress);

        return modalBody;
    }

    getTutorialPage (pageIndex)
    {
        let modalBody = document.getElementById("modal-body");
        modalBody.parentElement.removeChild(modalBody);

        this.modalContent.insertBefore(this.getModalBody(pageIndex), document.getElementById("modal-footer"));
    }
}
