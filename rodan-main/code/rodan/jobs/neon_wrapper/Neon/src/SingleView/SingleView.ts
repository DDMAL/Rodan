import { updateHighlight, setOpacityFromSlider } from '../DisplayPanel/DisplayControls';
import NeonView from '../NeonView';
import DisplayPanel from '../DisplayPanel/DisplayPanel';
import ZoomHandler from './Zoom';
import { ViewInterface, DisplayConstructable } from '../Interfaces';

import * as d3 from 'd3';

/**
 * A view module for displaying a single page of a manuscript.
 */
class SingleView implements ViewInterface {
  readonly neonView: NeonView;
  private container: HTMLElement;
  private updateCallbacks: Array<() => void>;
  private group: SVGSVGElement;
  private bg: SVGImageElement;
  private mei: SVGSVGElement;
  zoomHandler: ZoomHandler;
  private displayPanel: DisplayPanel;
  readonly pageURI: string;
  /**
   * Constructor for SingleView.
   * @param image - The URI to the background image for the page.
   */
  constructor (neonView: NeonView, panel: DisplayConstructable, image: string) {
    this.neonView = neonView;
    this.container = document.getElementById('container');
    this.updateCallbacks = new Array(0);
    // Group will contain the image and the rendered SVG
    this.group = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.group.id = 'svg_group';
    this.group.setAttribute('height', window.innerHeight.toString());
    this.group.setAttribute('width', '100%');

    this.bg = document.createElementNS('http://www.w3.org/2000/svg', 'image');
    this.bg.id = 'bgimg';
    this.bg.classList.add('background');
    this.bg.setAttribute('x', '0');
    this.bg.setAttribute('y', '0');

    const reader = new FileReader();
    fetch(image).then(result => {
      if (result.ok) {
        reader.addEventListener('load', () => {
          this.bg.setAttributeNS('http://www.w3.org/1999/xlink', 'href', reader.result.toString());
          const bbox = this.bg.getBBox();
          if (!this.group.hasAttribute('viewBox')) {
            this.group.setAttribute('viewBox', '0 0 ' + bbox.width.toString() + ' ' + bbox.height.toString());
          }
        });
        return result.blob();
      }
    }).then(blob => {
      reader.readAsDataURL(blob);
    });

    this.mei = document.createElementNS('http://www.w3.org/svg', 'svg') as SVGSVGElement;
    this.mei.id = 'mei_output';
    this.mei.classList.add('neon-container', 'active-page');

    this.group.appendChild(this.bg);
    this.group.appendChild(this.mei);
    this.container.appendChild(this.group);

    this.zoomHandler = new ZoomHandler();
    this.displayPanel = new panel(this, 'neon-container', 'background', this.zoomHandler);

    this.setViewEventHandlers();
    this.displayPanel.setDisplayListeners();

    this.pageURI = image;

    document.getElementById('loading').style.display = 'none';
  }

  /**
   * Update the SVG being displayed.
   * @param svg - New rendered SVG to use.
   */
  updateSVG (svg: SVGSVGElement): void {
    this.group.replaceChild(svg, this.mei);
    this.mei = svg;
    this.mei.id = 'mei_output';
    this.mei.classList.add('neon-container', 'active-page');
    const height = parseInt(this.mei.getAttribute('height'));
    const width = parseInt(this.mei.getAttribute('width'));

    this.bg.setAttribute('height', height.toString());
    this.bg.setAttribute('width', width.toString());
    this.group.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
    updateHighlight();
    this.resetTransformations();
    this.updateCallbacks.forEach(callback => callback());
  }

  /**
   * Change to a certain page
   * Since there is only one page, this is essentially a wrapper for updateSVG
   */
  async changePage (_page: number, _delay: boolean): Promise<void> {
    const svg = await this.neonView.getPageSVG(this.getCurrentPageURI());
    this.updateSVG(svg);
  }

  /**
   * Add a callback to the list of those be called when the page updates.
   * @param cb - The callback function.
   */
  addUpdateCallback (cb: () => void): void {
    this.updateCallbacks.push(cb);
  }

  /**
   * Remove a callback from the list of callbacks if it is part of the list.
   * @param cb - The callback function.
   */
  removeUpdateCallback (cb: () => void): void {
    const index = this.updateCallbacks.findIndex((elem) => {
      return elem === cb;
    });
    if (index !== -1) {
      this.updateCallbacks.splice(index, 1);
    }
  }

  /**
   * Reset the transformations that have been applied to the SVG upon update.
   */
  resetTransformations (): void {
    this.displayPanel.zoomHandler.restoreTransformation();
    setOpacityFromSlider();
  }

  /**
   * @returns The zero-indexed number of the current page. This will always be zero.
   */
  getCurrentPage (): number {
    return 0;
  }

  /**
   * @returns The URI of the page.
   */
  getCurrentPageURI (): string {
    return this.pageURI;
  }

  /**
   * Set event handlers for the view and display panel.
   */
  setViewEventHandlers (): void {
    document.body.addEventListener('keydown', (evt) => {
      switch (evt.key) {
        case 'Shift':
          d3.select('#svg_group').on('.drag', null);
          d3.select('#svg_group').call(
            d3.drag().on('start', this.displayPanel.zoomHandler.startDrag.bind(this.displayPanel.zoomHandler))
              .on('drag', this.displayPanel.zoomHandler.dragging.bind(this.displayPanel.zoomHandler))
          );
          break;
        case 'h':
          document.getElementById('mei_output').setAttribute('visibility', 'hidden');
          break;
        default: break;
      }
    });
    document.body.addEventListener('keyup', (evt) => {
      switch (evt.key) {
        case 'Shift':
          d3.select('#svg_group').on('.drag', null);
          if (this.neonView.getUserMode() !== 'viewer') {
            this.neonView.NeumeEdit.setSelectListeners();
          }
          break;
        case 'h':
          document.getElementById('mei_output').setAttribute('visibility', 'visible');
          break;
        default: break;
      }
    });

    d3.select('#container').on('touchstart', () => {
      if (d3.event.touches.length === 2) {
        this.displayPanel.zoomHandler.startDrag();
        d3.select('#container').on('touchmove', this.displayPanel.zoomHandler.dragging.bind(this.displayPanel.zoomHandler));
        d3.select('#container').on('touchend', () => {
          d3.select('#container').on('touchmove', null);
        });
      }
    });
    d3.select('#container').on('wheel', this.displayPanel.zoomHandler.scrollZoom.bind(this.displayPanel.zoomHandler), false);
    // Update height of container based on window
    window.onresize = (): void => {
      const newHeight = window.innerHeight;
      const container = document.getElementById('container');
      if (newHeight > Number(container.getAttribute('height'))) {
        container.setAttribute('height', newHeight.toString());
      }
    };
  }

  /**
   * @returns A human readable name for the page. Used for downloads.
   */
  getPageName (): string {
    return this.neonView.name;
  }
}

export { SingleView as default };
