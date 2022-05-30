import NeonView from './NeonView';
import DisplayPanel from './DisplayPanel/DisplayPanel';
import { DisplayConstructable, ViewInterface } from './Interfaces';
import ZoomHandler from './SingleView/Zoom';

import Diva from 'diva.js';

/**
 * View module that uses the diva.js viewer to render the pages of a IIIF manifests
 * and then display the rendered MEI files over the proper pages.
 */
class DivaView implements ViewInterface {
  readonly neonView: NeonView;
  /** Callbacks that run whenever the display updates. */
  private updateCallbacks: Array<() => void>;
  divaReady: boolean;
  /** The diva.js instance. */
  private diva: Diva;
  /** Map zero-index page numbers to the actual URI/IRI identifier. */
  private indexMap: Map<number, string>;
  private displayPanel: DisplayPanel;
  /** Time to wait after a page becomes active before loading it. In milliseconds. */
  private loadDelay: number;
  zoomHandler: ZoomHandler;

  /**
   * @param manifest - URI/IRI to the IIIF manifest.
   */
  constructor (neonView: NeonView, Display: DisplayConstructable, manifest: string) {
    this.neonView = neonView;
    this.updateCallbacks = [];
    this.divaReady = false;
    this.diva = new Diva('container', {
      objectData: manifest
    });
    document.getElementById('container').style.minHeight = '100%';
    this.indexMap = new Map();
    this.diva.disableDragScrollable();
    this.displayPanel = new Display(this, 'neon-container', 'diva-viewer-canvas');
    this.loadDelay = 500; // in milliseconds
    this.initDivaEvents();
    this.setViewEventHandlers();

    window.onresize = (): void => {
      const height = window.innerHeight;
      const width = window.innerWidth;

      window.setTimeout((): void => {
        if ((height === window.innerHeight) && (width === window.innerWidth)) {
          this.changePage(this.getCurrentPage(), false);
        }
      }, this.loadDelay);
    };
  }

  /**
   * Set the listeners for certain events internal to diva.js
   */
  initDivaEvents (): void {
    Diva.Events.subscribe('ManifestDidLoad', this.parseManifest.bind(this), this.diva.settings.ID);
    Diva.Events.subscribe('ObjectDidLoad', this.didLoad.bind(this), this.diva.settings.ID);
    Diva.Events.subscribe('ActivePageDidChange', this.changePage.bind(this), this.diva.settings.ID);
    Diva.Events.subscribe('ZoomLevelDidChange', this.adjustZoom.bind(this), this.diva.settings.ID);
  }

  /**
   * Called when the visible page changes in the diva.js viewer.
   * @param pageIndex - The zero-indexed page that is most visible.
   * @param delay - Whether to delay the loading of the page so that neon doesn't lag while scrolling.
   */
  async changePage (pageIndex: number, delay = true): Promise<void> {
    function checkAndLoad (page: number): void {
      if (page === this.getCurrentPage()) {
        const pageURI = this.indexMap.get(page);
        this.neonView.getPageSVG(pageURI).then((svg: SVGSVGElement) => {
          this.updateSVG(svg, page);
          const containerId = 'neon-container-' + page;
          const container = document.getElementById(containerId);
          if (container !== null) {
            container.classList.add('active-page');
          }
          this.updateCallbacks.forEach((callback: Function) => callback());
        }).catch((err: { name: string }) => {
          if (err.name !== 'not_found' && err.name !== 'missing_mei') {
            console.error(err);
          }
        });
      }
    }

    const pageIndexes = [pageIndex];
    Array.from(document.getElementsByClassName('active-page')).forEach(elem => {
      elem.classList.remove('active-page');
    });
    for (const page of pageIndexes) {
      if (delay) {
        window.setTimeout(checkAndLoad.bind(this), (this.loadDelay), page);
      } else {
        checkAndLoad.bind(this)(page);
      }
    }
  }

  /**
   * @returns Active zero-indexed page in the diva.js viewer.
   */
  getCurrentPage (): number {
    return this.diva.getActivePageIndex();
  }

  /**
   * @returns The active page URI in the diva.js viewer.
   */
  getCurrentPageURI (): string {
    return this.indexMap.get(this.getCurrentPage());
  }

  /**
   * Adjust the rendered SVG(s) to be the correct size after zooming.
   */
  adjustZoom (): void {
    (new Promise((resolve): void => {
      Array.from(document.getElementsByClassName('neon-container'))
        .forEach((elem: HTMLElement) => { elem.style.display = 'none'; });
      setTimeout(resolve, this.diva.settings.zoomDuration + 100);
    })).then(() => {
      this.changePage(this.diva.getActivePageIndex(), true);
      Array.from(document.getElementsByClassName('neon-container'))
        .forEach((elem: HTMLElement) => {
          const svg = elem.firstChild as SVGSVGElement;
          const pageNo = parseInt(elem.id.match(/\d+/)[0]);
          this.updateSVG(svg, pageNo);
          elem.style.display = '';
        });
    });
  }

  /**
   * Update the SVG being displayed for the specified page.
   * @param svg - The SVG of the page to update to.
   * @param pageNo - The zero-indexed page number.
   */
  updateSVG (svg: SVGSVGElement, pageNo: number): void {
    const inner = document.getElementById('diva-1-inner');
    const dimensions = this.diva.getPageDimensionsAtCurrentZoomLevel(pageNo);
    const offset = this.diva.settings.viewHandler._viewerCore.getPageRegion(pageNo, {
      includePadding: true,
      incorporateViewport: true
    });
    const marginLeft = window.getComputedStyle(inner, null)
      .getPropertyValue('margin-left');

    const containerId = 'neon-container-' + pageNo.toString();
    let container = document.getElementById(containerId);
    if (container === null) {
      container = document.createElement('div');
      container.id = containerId;
      container.classList.add('neon-container');
      inner.appendChild(container);
    }

    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }

    svg.setAttribute('width', dimensions.width.toString());
    svg.setAttribute('height', dimensions.height.toString());
    container.style.position = 'absolute';
    container.style.top = `${offset.top}px`;
    container.style.left = `${offset.left - parseInt(marginLeft)}px`;

    container.appendChild(svg);
  }

  /**
   * Function called when diva.js finishes loading.
   */
  didLoad (): void {
    this.divaReady = true;
    this.displayPanel.setDisplayListeners();
    document.getElementById('loading').style.display = 'none';
    console.log(this.diva);
  }

  /**
   * Add a callback function that will be run whenever an SVG is updated.
   * @param cb - The callback function.
   */
  addUpdateCallback (cb: () => void): void {
    this.updateCallbacks.push(cb);
  }

  /**
   * Remove a callback function previously added to the list of functions to call.
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
   * Set listeners on the body element for global events.
   */
  setViewEventHandlers (): void {
    document.body.addEventListener('keydown', (evt) => {
      switch (evt.key) {
        case 'h':
          for (const container of document.getElementsByClassName('neon-container') as HTMLCollectionOf<HTMLElement>) {
            container.style.visibility = 'hidden';
          }
          break;
        default: break;
      }
    });

    document.body.addEventListener('keyup', (evt) => {
      switch (evt.key) {
        case 'h':
          for (const container of document.getElementsByClassName('neon-container') as HTMLCollectionOf<HTMLElement>) {
            container.style.visibility = '';
          }
          break;
        default: break;
      }
    });
  }

  /**
   * Use the IIIF manifest to create a map between IIIF canvases and page indexes.
   * @param manifest - The IIIF manifest object.
   */
  parseManifest (manifest: { sequences: { canvases: object[] }[] }): void {
    this.indexMap.clear();
    for (const sequence of manifest.sequences) {
      for (const canvas of sequence.canvases) {
        this.indexMap.set(sequence.canvases.indexOf(canvas), canvas['@id']);
      }
    }
  }

  /**
   * @returns The name of the active page/canvas combined with the manuscript name.
   */
  getPageName (): string {
    const manuscriptName = this.diva.settings.manifest.itemTitle;
    const pageName = this.diva.settings.manifest.pages[this.getCurrentPage()].l;
    return manuscriptName + ' \u2014 ' + pageName;
  }
}

export { DivaView as default };
