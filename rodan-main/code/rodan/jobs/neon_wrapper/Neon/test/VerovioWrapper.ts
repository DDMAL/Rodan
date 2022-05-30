import { VerovioMessage, VerovioResponse } from '../src/Types';
import * as verovio from 'verovio-dev';

/**
 * Wrapper to be used during tests when Web Workers are not available.
 */
export default class VerovioWrapper {
  toolkit;
  handler: (evt: MessageEvent) => void;
  constructor () {
    this.toolkit = new verovio.toolkit();
    this.toolkit.setOptions({
      from: 'mei',
      footer: 'none',
      header: 'none',
      pageMarginLeft: 0,
      pageMarginTop: 0,
      font: 'Bravura',
      useFacsimile: true,
    });
  }

  /**
   * Fake adding an event handler, just save the handler.
   * @param {string} type - The event to listen to, which is ignored.
   * @param {function} handler - The handler that will be saved.
   */
  addEventListener (_type: string, handler: (MessageEvent) => void): void {
    this.handler = handler;
  }

  /**
   * Fake sending a message and call the handler with the message here.
   * @param {object} message
   */
  postMessage (message: VerovioMessage): void {
    const data = this.handleNeonEvent(message);
    const evt = {
      data: data,
      target: {
        removeEventListener: (): void => {}
      }
    };

    this.handler(evt as unknown as MessageEvent);
  }

  /**
   * Handler for the different messages that could be sent.
   * @param {object} data - The content of the message.
   * @returns {object}
   */
  handleNeonEvent (data: VerovioMessage): VerovioResponse {
    const result: VerovioResponse = {
      id: data.id
    };

    switch (data.action) {
      case 'renderData':
        result.svg = this.toolkit.renderData(data.mei, {});
        break;
      case 'getElementAttr':
        result.attributes = this.toolkit.getElementAttr(data.elementId);
        break;
      case 'edit':
        result.result = this.toolkit.edit(data.editorAction);
        break;
      case 'getMEI':
        result.mei = this.toolkit.getMEI({
          pageNo: 0,
          scoreBased: true
        });
        break;
      case 'editInfo':
        result.info = this.toolkit.editInfo();
        break;
      case 'renderToSVG':
        result.svg = this.toolkit.renderToSVG(1);
        break;
      default:
        break;
    }

    return result;
  }
}
