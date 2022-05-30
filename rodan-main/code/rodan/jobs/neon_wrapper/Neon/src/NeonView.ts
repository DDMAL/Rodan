import NeonCore from './NeonCore';

import { parseManifest } from './utils/NeonManifest';
import { prepareEditMode } from './utils/EditControls';
import setBody from './utils/template/Template';
import * as Types from './Types';
import * as Interfaces from './Interfaces';


/**
 * NeonView class. Manages the other modules of Neon and communicates with
 * NeonCore.
 */
class NeonView {
  /** The manifest describing what to load and where to find it. */
  manifest: Types.NeonManifest;
  /** Module that displays rendered MEI. */
  view: Interfaces.ViewInterface;
  /** Name of the document loaded. */
  name: string;
  /** Module that handles managing resources, rendering SVGs. */
  core: NeonCore;
  /** Module that provides additional information on musical elements. */
  info: Interfaces.InfoInterface;
  /** Module that allows editing of musical elements. */
  NeumeEdit: Interfaces.NeumeEditInterface;
  /** Module that allows viewing of syllable text. */
  textView: Interfaces.TextViewInterface;
  /** Module that allows editing of syllable text. */
  TextEdit: Interfaces.TextEditInterface;

  params: Interfaces.NeonViewParams;


  /**
   * Constructor for NeonView. Sets mode and passes constructors.
   */
  constructor (params: Interfaces.NeonViewParams) {
    if (!parseManifest(params.manifest)) {
      console.error('Unable to parse the manifest');
    }

    this.params = params;
    this.manifest = params.manifest;
  }

  /**
   * Set up Neon for any provided editing modules.
   */
  setupEdit(params: Interfaces.NeonViewParams): void {
    if (params.NeumeEdit !== undefined || (params.TextEdit !== undefined && params.TextView !== undefined)) {
      // Set up display for edit button
      prepareEditMode(this);
    }

    if (params.NeumeEdit !== undefined) {
      this.NeumeEdit = new params.NeumeEdit(this);
    }
    if (params.TextView !== undefined) {
      this.textView = new params.TextView(this);
      if (params.TextEdit !== undefined) {
        this.TextEdit = new params.TextEdit(this);
      }
    }
  }

  /**
   * Start Neon
   */
  start (): void {
    /* this.core.db.info().then((info) => {
      if (info.doc_count === 0) {
        this.core.initDb().then(() => { this.updateForCurrentPage(); });
      } else {
        Notification.queueNotification('Existing database found. Revert to start from the beginning.');
        this.updateForCurrentPage();
      }
    }); */
    setBody().then(() => {
      this.view = new this.params.View(this, this.params.Display, this.manifest.image);
      this.name = this.manifest.title;

      this.core = new NeonCore(this.manifest);
      this.info = new this.params.Info(this);

      window.setTimeout(this.setupEdit.bind(this), 2000, this.params);
      return this.core.initDb();
    }).then(() => {
      this.updateForCurrentPage(true);
    });
  }

  /**
   * Get the current page from the loaded view and then display the
   * most up to date SVG.
   */
  updateForCurrentPage (delay = false): Promise<void> {
    const pageNo = this.view.getCurrentPage();
    return this.view.changePage(pageNo, delay);
  }

  /**
   * Redo an action performed on the current page (if there is one).
   */
  redo (): Promise<boolean> {
    return this.core.redo(this.view.getCurrentPageURI());
  }

  /**
   * Undo the last action performed on the current page (if there is one).
   */
  undo (): Promise<boolean> {
    return this.core.undo(this.view.getCurrentPageURI());
  }

  /**
   * Get the mode Neon is in.
   * @returns Value is "viewer", "insert", or "edit".
   */
  getUserMode (): string {
    if (this.NeumeEdit !== undefined) {
      return this.NeumeEdit.getUserMode();
    } else if (this.TextEdit !== undefined) {
      return 'edit';
    } else {
      return 'viewer';
    }
  }

  /**
   * Attempt to perform an editor action.
   * @param action - The editor toolkit action object.
   * @param pageURI - The URI of the page to perform the action on
   */
  edit (action: Types.EditorAction, pageURI: string): Promise<boolean> {
    return this.core.edit(action, pageURI);
  }

  /**
   * Get the attributes for a specific musical element.
   * @param elementId - The unique ID of the musical element.
   * @param pageURI - The URI of the page the element is found on.
   */
  getElementAttr (elementID: string, pageURI: string): Promise<Types.Attributes> {
    return this.core.getElementAttr(elementID, pageURI);
  }

  /**
   * Updates browser database and creates JSON-LD save file.
   * @returns The contents of this file.
   */
  export (): Promise<string | ArrayBuffer> {
    return (new Promise((resolve, reject): void => {
      this.core.updateDatabase().then(() => {
        this.manifest['mei_annotations'] = this.core.getAnnotations();
        this.manifest.timestamp = (new Date()).toISOString();
        const data = new window.Blob([JSON.stringify(this.manifest, null, 2)], { type: 'application/ld+json' });
        const reader = new FileReader();
        reader.addEventListener('load', () => {
          resolve(reader.result);
        });
        reader.readAsDataURL(data);
      }).catch(err => { reject(err); });
    }));
  }

  /**
   * Save the current state to the browser database.
   */
  save (): Promise<void> {
    return this.core.updateDatabase();
  }

  /**
   * Deletes the local database of the loaded MEI file(s).
   */
  deleteDb (): Promise<{}[]> {
    return this.core.deleteDb();
  }

  /**
   * Get the page's MEI file encoded as a data URI.
   * @param pageNo - The URI specifying the page.
   * @returns A [Data URI](https://en.wikipedia.org/wiki/Data_URI_scheme).
   */
  getPageURI (pageNo?: string): Promise<string> {
    if (pageNo === undefined) {
      pageNo = this.view.getCurrentPageURI();
    }
    return new Promise((resolve): void => {
      this.core.getMEI(pageNo).then((mei) => {
        resolve('data:application/mei+xml;charset=utf-8,' + encodeURIComponent(mei));
      });
    });
  }

  /**
   * Get the page's MEI file as a string.
   * @param pageNo - The identifying URI of the page.
   */
  getPageMEI (pageNo: string): Promise<string> {
    return this.core.getMEI(pageNo);
  }

  /**
   * Get the page's SVG.
   * @param pageNo - The identifying URI of the page.
   */
  getPageSVG (pageNo: string): Promise<SVGSVGElement> {
    return this.core.getSVG(pageNo);
  }
}

export { NeonView as default };
