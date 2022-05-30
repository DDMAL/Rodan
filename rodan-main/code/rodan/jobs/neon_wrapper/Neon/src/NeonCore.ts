import { convertSbToStaff } from './utils/ConvertMei';
import * as Validation from './Validation';
import VerovioWrapper from './VerovioWrapper';
import { WebAnnotation, Attributes, EditorAction, NeonManifest, VerovioMessage } from './Types';
import { uuidv4 } from './utils/random';

import PouchDB from 'pouchdb';

/**
 * A cache is used to keep track of what has happened
 * across multiple pages in a manuscript without having
 * to make many calls to the PouchhDb database.
 */
interface CacheEntry {
  dirty: boolean;
  mei: string;
  svg: SVGSVGElement;
}

/**
 * The core component of Neon. This manages the database,
 * the verovio toolkit, the cache, and undo/redo stacks.
 */
class NeonCore {
  /** Wrapper for the Verovio WebWorker. */
  private verovioWrapper: VerovioWrapper;
  /** Stacks of actions that can be undone per page. */
  private undoStacks: Map<string, string[]>;
  /** Stacks of actions that can be redone per page. */
  private redoStacks: Map<string, string[]>;
  /** Cache containing entries for each page. */
  private neonCache: Map<string, CacheEntry>;
  private db: PouchDB.Database;
  private parser: DOMParser;
  /** Pages known not to have any associated MEI. */
  private blankPages: Array<string>;
  /** A collection of W3 Web Annotations. */
  private annotations: WebAnnotation[];
  private manifest: NeonManifest;
  private lastPageLoaded: string;

  getAnnotations (): WebAnnotation[] { return this.annotations; }

  /**
   * Constructor for NeonCore
   */
  constructor (manifest: NeonManifest) {
    this.verovioWrapper = new VerovioWrapper();
    Validation.init();

    /**
     * Stacks of previous MEI files representing actions that can be undone for each page.
     * @type {Map.<string, Array.<string>>}
     */
    this.undoStacks = new Map<string, string[]>();

    /**
     * Stacks of previous MEI files representing actions that can be redone for each page.
     * @type {Map.<string, Array.<string>>}
     */
    this.redoStacks = new Map();

    this.neonCache = new Map();

    this.parser = new DOMParser();

    this.db = new PouchDB('Neon');

    this.blankPages = [];

    // Add each MEI to the database
    this.manifest = manifest;
    this.annotations = manifest.mei_annotations;
    this.lastPageLoaded = '';
  }

  /**
   * Initialize the PouchDb database based on the provided manifest.
   * If a newer version already exists in the database, this will
   * not update the database unless forced.
   * @param force - If a database update should be forced.
   */
  async initDb (force = false): Promise<{}> {
    // Check for existing manifest
    type DbAnnotation = PouchDB.Core.IdMeta & PouchDB.Core.GetMeta & WebAnnotation;
    type Doc = PouchDB.Core.IdMeta & PouchDB.Core.GetMeta & { timestamp: string; annotations: string[]};
    const response = await new Promise<{}>((resolve, reject): void => {
      this.db.get(this.manifest['@id']).catch(err => {
        if (err.name === 'not_found') {
          // This is a new document.
          const doc = {
            _id: this.manifest['@id'],
            timestamp: this.manifest.timestamp,
            image: this.manifest.image,
            title: this.manifest.title,
            annotations: []
          };
          this.annotations.forEach(annotation => {
            doc.annotations.push(annotation.id);
          });
          return doc;
        } else {
          console.error(err);
          return reject(err);
        }
      }).then(async (doc: Doc) => {
        // Check if doc timestamp is newer than manifest
        const docTime = (new Date(doc.timestamp)).getTime();
        // Format timestamp to specific ISO 8601 variant because
        // Safari requires timezone offsets to be +/-HH:MM and fails on
        // the equally valid +/-HHMM. This doesn't need to be applied to
        // the browser generated timestamp since that always generates a
        // timestamp in UTC with the Z ending.
        const timeZoneRegexp = /(.+[-+\u2212]\d\d)(\d\d)$/;
        const manTime = (timeZoneRegexp.test(this.manifest.timestamp)) ?
          (new Date(this.manifest.timestamp.replace(timeZoneRegexp, '$1:$2'))).getTime()
          : (new Date(this.manifest.timestamp)).getTime();
        if (docTime > manTime) {
          if (!force) {
            // Fill annotations list with db annotations
            this.annotations = [];
            const promises = doc.annotations.map((id: string) => {
              return new Promise((res) => {
                this.db.get(id).then((annotation: DbAnnotation) => {
                  this.annotations.push({
                    id: annotation._id,
                    type: 'Annotation',
                    body: annotation.body,
                    target: annotation.target
                  });
                  res();
                }).catch(err => {
                  console.error(err);
                  res();
                });
              });
            });
            await Promise.all(promises);
            return resolve(false);
          }
        }
        for (const annotation of this.annotations) {
          // Add annotations to database
          await this.db.get(annotation.id).catch(err => {
            if (err.name === 'not_found') {
              return {
                _id: annotation.id
              };
            } else {
              console.error(err);
              return reject(err);
            }
          }).then((newAnnotation: DbAnnotation) => {
            newAnnotation.body = annotation.body;
            newAnnotation.target = annotation.target;
            return this.db.put(newAnnotation);
          }).catch(err => {
            reject(err);
            console.error(err);
          });
        }
        return this.db.put(doc);
      }).then(() => {
        return resolve(true);
      }).catch(err => {
        reject(err);
        console.error(err);
      });
    });

    return response;
  }

  /**
   * Load a page into the verovio toolkit. This will fetch the
   * page from the cache or from the database.
   * @param pageURI - The URI of the selected page.
   */
  loadPage (pageURI: string): Promise<CacheEntry> {
    return new Promise((resolve, reject): void => {
      // Was this already the loaded page?
      if (this.lastPageLoaded === pageURI && this.neonCache.has(pageURI)) {
        resolve(this.neonCache.get(pageURI));
      } else if (this.neonCache.has(pageURI)) {
        this.loadData(pageURI, this.neonCache.get(pageURI).mei).then(() => {
          resolve(this.neonCache.get(pageURI));
        });
      // Do we know this page has no MEI content?
      } else if (this.blankPages.includes(pageURI)) {
        Validation.blankPage();
        const e = new Error('No MEI file for page ' + pageURI);
        e.name = 'missing_mei';
        reject(e);
      } else {
        // Find annotation
        const annotation = this.annotations.find(elem => {
          return elem.target === pageURI;
        });
        if (annotation) {
          window.fetch(annotation.body).then(response => {
            if (response.ok) {
              return response.text();
            } else {
              throw new Error(response.statusText);
            }
          }).then(data => {
            // Check if the MEI file is sb-based. If so, convert to staff-based.
            if (data.match(/<sb .+>/)) {
              data = convertSbToStaff(data);
            }
            this.loadData(pageURI, data).then(() => {
              resolve(this.neonCache.get(pageURI));
            });
          }).catch(err => {
            reject(err);
          });
        } else {
          // If no annotation was found treat the page as
          // being blank
          Validation.blankPage();
          this.blankPages.push(pageURI);
        }
      }
    });
  }

  /**
   * Load data into the verovio toolkit and update the cache.
   * @param pageURI - The URI of the selected page.
   * @param data - The MEI of the page as a string.
   * @param dirty - If the cache entry should be marked as dirty.
   */
  loadData (pageURI: string, data: string, dirty = false): Promise<void> {
    Validation.sendForValidation(data);
    this.lastPageLoaded = pageURI;
    /* A promise is returned that will resolve to the result of the action.
     * However the value that is must return comes from the Web Worker and
     * information passed between the worker and main context much be in a
     * message. So an event handler is put on verovioWrapper for when a message
     * is receieved from the worker. Then a message is sent to the worker to
     * take an action. A response is sent back and the previously mentioned
     * event handler handles the response. Since it is defined within the
     * promise it has access to the necessary resolve function.
     */
    return new Promise((resolve): void => {
      const message: VerovioMessage = {
        id: uuidv4(),
        action: 'renderData',
        mei: data
      };
      function handle (evt: MessageEvent): void {
        if (evt.data.id === message.id) {
          const svg = this.parser.parseFromString(
            evt.data.svg,
            'image/svg+xml'
          ).documentElement;
          this.neonCache.set(pageURI, {
            svg: svg,
            mei: data,
            dirty: dirty
          });
          evt.target.removeEventListener('message', handle);
          resolve();
        }
      }
      this.verovioWrapper.addEventListener('message', handle.bind(this));
      this.verovioWrapper.postMessage(message);
    });
  }

  /**
   * Get the SVG for a specific page.
   * @param pageURI - The URI of the selected page.
   */
  getSVG (pageURI: string): Promise<SVGSVGElement> {
    return new Promise((resolve, reject): void => {
      this.loadPage(pageURI).then((entry) => {
        resolve(entry.svg);
      }).catch((err) => { reject(err); });
    });
  }

  /**
   * Get the MEI for a specific page.
   * @param pageURI - The URI of the selected page.
   */
  getMEI (pageURI: string): Promise<string> {
    return new Promise((resolve, reject): void => {
      this.loadPage(pageURI).then((entry) => {
        resolve(entry.mei);
      }).catch((err) => { reject(err); });
    });
  }

  /**
   * Get musical element attributes from the verovio toolkit.
   * @param elementId - The unique ID of the musical element.
   * @param pageURI - The URI of the selected page.
   */
  getElementAttr (elementId: string, pageURI: string): Promise<Attributes> {
    return new Promise((resolve): void => {
      this.loadPage(pageURI).then(() => {
        const message: VerovioMessage = {
          id: uuidv4(),
          action: 'getElementAttr',
          elementId: elementId
        };
        this.verovioWrapper.addEventListener('message', function handle (evt: MessageEvent) {
          if (evt.data.id === message.id) {
            evt.target.removeEventListener('message', handle);
            resolve(evt.data.attributes);
          }
        });
        this.verovioWrapper.postMessage(message);
      });
    });
  }

  /**
   * Perform an editor action on a specific page.
   * @param action - The editor toolkit action object.
   * @param pageURI - The URI of the selected page.
   */
  edit (editorAction: EditorAction, pageURI: string): Promise<boolean> {
    let promise: Promise<CacheEntry>;
    if (this.lastPageLoaded === pageURI) {
      promise = Promise.resolve(this.neonCache.get(pageURI));
    } else {
      promise = this.loadPage(pageURI);
    }
    return new Promise((resolve): void => {
      promise.then(entry => {
        const currentMEI = entry.mei;
        const message: VerovioMessage = {
          id: uuidv4(),
          action: 'edit',
          editorAction: editorAction
        };
        function handle (evt: MessageEvent): void {
          if (evt.data.id === message.id) {
            if (evt.data.result) {
              if (!this.undoStacks.has(pageURI)) {
                this.undoStacks.set(pageURI, []);
              }
              this.undoStacks.get(pageURI).push(currentMEI);
              this.redoStacks.set(pageURI, []);
            }
            evt.target.removeEventListener('message', handle);
            this.updateCache(pageURI, true).then(() => { resolve(evt.data.result); });
          }
        }
        this.verovioWrapper.addEventListener('message', handle.bind(this));
        this.verovioWrapper.postMessage(message);
      });
    });
  }

  /**
   * Update contents of the cache using information in verovio toolkit.
   * @param pageURI - Page to be updated in cache.
   * @param dirty - If the entry should be marked as dirty
   */
  updateCache (pageURI: string, dirty: boolean): Promise<void> {
    return new Promise((resolve): void => {
      // Must get MEI and then get SVG then finish.
      let mei: string, svgText: string;
      const meiPromise = new Promise((resolve): void => {
        const message: VerovioMessage = {
          id: uuidv4(),
          action: 'getMEI'
        };
        this.verovioWrapper.addEventListener('message', function handle (evt: MessageEvent) {
          if (evt.data.id === message.id) {
            mei = evt.data.mei;
            evt.target.removeEventListener('message', handle);
            Validation.sendForValidation(mei);
            resolve();
          }
        });
        this.verovioWrapper.postMessage(message);
      });
      const svgPromise = new Promise((resolve): void => {
        const message: VerovioMessage = {
          id: uuidv4(),
          action: 'renderToSVG'
        };
        this.verovioWrapper.addEventListener('message', function handle (evt: MessageEvent) {
          if (evt.data.id === message.id) {
            svgText = evt.data.svg;
            evt.target.removeEventListener('message', handle);
            resolve();
          }
        });
        this.verovioWrapper.postMessage(message);
      });

      meiPromise.then(() => { return svgPromise; }).then(() => {
        const svg = this.parser.parseFromString(
          svgText,
          'image/svg+xml'
        ).documentElement as unknown as SVGSVGElement;
        this.neonCache.set(pageURI, {
          mei: mei,
          svg: svg,
          dirty: dirty
        });
        resolve();
      });
    });
  }

  /**
   * Get the edit info string from the verovio toolkit.
   * @param pageURI - The URI of the page to get the edit info string from.
   */
  info (pageURI: string): Promise<string> {
    let promise: Promise<CacheEntry | void>;
    if (this.lastPageLoaded === pageURI) {
      promise = Promise.resolve();
    } else {
      promise = this.loadPage(pageURI);
    }
    return new Promise((resolve): void => {
      promise.then(() => {
        const message: VerovioMessage = {
          id: uuidv4(),
          action: 'editInfo'
        };
        this.verovioWrapper.addEventListener('message', function handle (evt: MessageEvent) {
          if (evt.data.id === message.id) {
            evt.target.removeEventListener('message', handle);
            resolve(evt.data.info);
          }
        });
        this.verovioWrapper.postMessage(message);
      });
    });
  }

  /**
   * Undo the last action performed on a specific page.
   * @param pageURI - The URI of the selected page.
   * @returns If the action was undone.
   */
  undo (pageURI: string): Promise<boolean> {
    return new Promise((resolve): void => {
      if (this.undoStacks.has(pageURI)) {
        const state = this.undoStacks.get(pageURI).pop();
        if (state !== undefined) {
          this.getMEI(pageURI).then(mei => {
            this.redoStacks.get(pageURI).push(mei);
            return this.loadData(pageURI, state, true);
          }).then(() => {
            resolve(true);
          });
          return;
        }
      }
      resolve(false);
    });
  }

  /**
   * Redo the last action performed on a page.
   * @param pageURI - The page URI.
   * @returns If the action was redone.
   */
  redo (pageURI: string): Promise<boolean> {
    return new Promise((resolve): void => {
      if (this.redoStacks.has(pageURI)) {
        const state = this.redoStacks.get(pageURI).pop();
        if (state !== undefined) {
          this.getMEI(pageURI).then((mei) => {
            this.undoStacks.get(pageURI).push(mei);
            return this.loadData(pageURI, state, true);
          }).then(() => {
            resolve(true);
          });
          return;
        }
      }
      resolve(false);
    });
  }

  /**
   * Update the PouchDb database stored in the browser.
   * This is based on the data stored in the cache. To save time,
   * only entries marked as dirty will be updated.
   */
  async updateDatabase (): Promise<void> {
    type Doc = PouchDB.Core.GetMeta & PouchDB.Core.IdMeta & { body: string; timestamp: string };
    let updateTimestamp = false;
    for (const pair of this.neonCache) {
      const key = pair[0];
      const value = pair[1];
      if (value.dirty) {
        updateTimestamp = true;
        const index = this.annotations.findIndex(elem => { return elem.target === key; });
        // try to update server with PUT request (if applicable)
        // this is simpler than expecting a specific API on the server
        // and using POST requests, although that would be better if there
        // is ever a dedicated public server for Neon! At time of writing,
        // only dev/testing server accepts PUT requests.
        // only attempt if not a data URI
        let uri: string;
        if (!this.annotations[index].body.match(/^data:/)) {
          await window.fetch(this.annotations[index].body,
            {
              method: 'PUT',
              headers: { 'Content-Type': 'application/mei+xml' },
              body: value.mei
            }
          ).then(response => {
            if (response.ok) {
              uri = this.annotations[index].body;
            } else {
              uri = 'data:application/mei+xml;base64,' + window.btoa(value.mei);
            }
          }).catch(err => {
            console.error(err);
            console.warn('Falling back to data URI');
            uri = 'data:application/mei+xml;base64,' + window.btoa(value.mei);
          });
        } else {
          uri = 'data:application/mei+xml;base64,' + window.btoa(value.mei);
        }
        // Update URI in annotations, database
        this.annotations[index].body = uri;
        await this.db.get(this.annotations[index].id).then((doc: Doc) => {
          doc.body = uri;
          return this.db.put(doc);
        }).then(() => {
          value.dirty = false;
        }).catch(err => {
          console.error(err);
        });
      }
    }

    if (updateTimestamp) {
      await this.db.get(this.manifest['@id']).then((doc: Doc) => {
        doc.timestamp = (new Date()).toISOString();
        return this.db.put(doc);
      }).catch(err => {
        console.error(err);
      });
    }
  }

  /** Completely remove the database. */
  async deleteDb (): Promise<{}[]> {
    type Doc = PouchDB.Core.IdMeta & PouchDB.Core.GetMeta & { timestamp: string; annotations: string[]};
    const annotations = await this.db.get(this.manifest['@id'])
      .then((doc: Doc) => { return doc.annotations; } );
    annotations.push(this.manifest['@id']);

    const promises = annotations.map((id) => {
      return new Promise(res => {
        this.db.get(id)
          .then(doc => { return this.db.remove(doc); })
          .then(() => res());
      });
    });
    return Promise.all(promises);
  }
}

export { NeonCore as default };
