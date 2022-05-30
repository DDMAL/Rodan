import NeonView from '../NeonView';
import { EditorAction } from '../Types';
import * as d3 from 'd3';

/**
 * Class that handles insert mode, events, and actions.
 */
class InsertHandler {
  type: string;
  firstClick = true;
  coord: DOMPoint;
  attributes: object;
  selector: string;
  neonView: NeonView;

  /**
   * @param neonView - NeonView parent.
   * @param sel - The CSS selector to apply insert listeners to.
   */
  constructor (neonView: NeonView, sel: string) {
    this.neonView = neonView;
    this.selector = sel;
  }

  /**
   * Called when an insert button is clicked.
   * Triggers the start of insert mode.
   * @param buttonId - The ID of the button that was clicked.
   */
  insertActive (buttonId: string): void {
    const alreadyInInsertMode = this.isInsertMode();
    switch (buttonId) {
      case 'punctum':
        this.type = 'nc';
        this.attributes = null;
        break;
      case 'diamond':
        this.type = 'nc';
        this.attributes = { 'tilt': 'se' };
        break;
      case 'virga':
        this.type = 'nc';
        this.attributes = { 'tilt': 'n' };
        break;
      case 'pes':
      case 'clivis':
      case 'scandicus':
      case 'climacus':
      case 'torculus':
      case 'porrectus':
      case 'pressus':
        const contour = this.neonView.info.getContourByValue(
          buttonId.charAt(0).toUpperCase() + buttonId.slice(1)
        );
        this.type = 'grouping';
        this.attributes = { 'contour': contour };
        break;
      case 'cClef':
      case 'fClef':
        this.type = 'clef';
        this.attributes = { 'shape': buttonId.charAt(0).toUpperCase() };
        break;
      case 'custos':
        this.type = 'custos';
        this.attributes = null;
        break;
      case 'staff':
        this.type = 'staff';
        this.attributes = null;
        break;
      default:
        this.type = '';
        this.attributes = null;
        console.error('Invalid button for insertion: ' + buttonId + '.');
        return;
    }

    this.removeInsertClickHandlers();
    if (this.type === 'staff') {
      document.querySelector(this.selector)
        .addEventListener('click', this.staffHandler);
    } else {
      document.querySelector(this.selector)
        .addEventListener('click', this.handler);
    }

    // Disable edit mode listeners
    document.body.addEventListener('keydown', this.keydownListener);
    document.body.addEventListener('keyup', this.resetInsertHandler);
    document.body.addEventListener('click', this.clickawayHandler);

    // Add 'return to edit mode' button
    if (!alreadyInInsertMode) {
      const editModeButton = document.createElement('button');
      editModeButton.id = 'returnToEditMode';
      editModeButton.classList.add('button');
      editModeButton.innerHTML = 'Return to Edit Mode';
      document.getElementById('redo').parentNode.appendChild(editModeButton);
      editModeButton.addEventListener('click', this.insertDisabled);
    }
    const editMenu = document.getElementById('editMenu');
    editMenu.style.backgroundColor = 'whitesmoke';
    editMenu.style.fontWeight = '';
    const insertMenu = document.getElementById('insertMenu');
    insertMenu.style.backgroundColor = '#ffc7c7';
    insertMenu.style.fontWeight = 'bold';
  }

  /**
   * Disable insert mode and remove event listeners.
   */
  insertDisabled = (function insertDisabled (): void {
    this.type = '';
    this.removeInsertClickHandlers();
    document.body.removeEventListener('keydown', this.keydownListener);
    document.body.removeEventListener('keyup', this.resetInsertHandler);
    document.body.removeEventListener('click', this.clickawayHandler);
    const selected = document.querySelector('.insertel.is-active');
    if (selected !== null) {
      selected.classList.remove('is-active');
    }
    this.firstClick = true;
    try {
      document.getElementById('returnToEditMode').remove();
    } catch (e) {
      // console.debug(e);
    }
    const editMenu = document.getElementById('editMenu');
    const insertMenu = document.getElementById('insertMenu');
    editMenu.style.backgroundColor = '#ffc7c7';
    editMenu.style.fontWeight = 'bold';
    insertMenu.style.backgroundColor = 'whitesmoke';
    insertMenu.style.fontWeight = '';
  }).bind(this);

  /**
   * Event handler to handle a user clicking away from the active page
   * causing insert mode to end.
   */
  clickawayHandler = (function clickawayHandler (evt: MouseEvent): void {
    const target = evt.target as HTMLElement;
    if (target.closest('.active-page') === null &&
      target.closest('#insert_controls') === null &&
      target.closest('#svg_group') === null) {
      this.insertDisabled();
      document.body.removeEventListener('keydown',
        this.staffHandler);
      document.body.removeEventListener('keydown',
        this.handler);
    }
  }).bind(this);

  /**
   * Resets an insert event listener after temporarily removing it.
   */
  resetInsertHandler = (function resetInsertHandler (evt: KeyboardEvent): void {
    if (evt.key === 'Shift') {
      document.querySelector(this.selector)
        .addEventListener('click', this.type === 'staff' ?
          this.staffHandler : this.handler);
    }
  }).bind(this);

  /**
   * Listens to key presses to either exit edit mode (if Escape) or
   * temporarily remove insert event listeners (if Shift).
   */
  keydownListener = (function keydownListener (evt: KeyboardEvent): void {
    if (evt.key === 'Escape') {
      this.insertDisabled();
      document.body.removeEventListener('keydown', this.staffHandler);
      document.body.removeEventListener('keydown', this.handler);
    } else if (evt.key === 'Shift') {
      this.removeInsertClickHandlers();
    }
  }).bind(this);

  /**
   * Event handler for clicking to insert any element except a staff.
   */
  handler = (function handler (evt: MouseEvent): void {
    evt.stopPropagation();
    const container = document.getElementsByClassName('active-page')[0].getElementsByClassName('definition-scale')[0] as SVGSVGElement;
    const pt = container.createSVGPoint();
    pt.x = evt.clientX;
    pt.y = evt.clientY;
    // Transform pt to SVG context
    const transformMatrix = (container.getElementsByClassName('system')[0] as SVGGraphicsElement).getScreenCTM();
    const cursorpt = pt.matrixTransform(transformMatrix.inverse());

    const editorAction: EditorAction = {
      'action': 'insert',
      'param': {
        'elementType': this.type,
        'staffId': 'auto',
        'ulx': cursorpt.x,
        'uly': cursorpt.y
      }
    };

    if (this.attributes !== null) {
      editorAction['param']['attributes'] = this.attributes;
      if (this.attributes['shape'] === 'F') {
        editorAction['param']['ulx'] -= 50;
      }
    }

    this.neonView.edit(editorAction, this.neonView.view.getCurrentPageURI()).then(() => {
      return this.neonView.updateForCurrentPage();
    }).then(() => {
      document.querySelector(this.selector).addEventListener('click', this.handler);
    });
  }).bind(this);

  /**
   * Event handler to insert a staff.
   */
  staffHandler = (function staffHandler (evt: MouseEvent): void {
    const container = document.getElementsByClassName('active-page')[0].getElementsByClassName('definition-scale')[0] as SVGSVGElement;
    const pt = container.createSVGPoint();
    pt.x = evt.clientX;
    pt.y = evt.clientY;
    const transformMatrix = (container.getElementsByClassName('system')[0] as SVGGraphicsElement).getScreenCTM();
    const cursorpt = pt.matrixTransform(transformMatrix.inverse());

    if (this.firstClick) {
      this.coord = cursorpt;
      d3.select(container).append('circle').attr('cx', cursorpt.x)
        .attr('cy', cursorpt.y)
        .attr('r', 10)
        .attr('id', 'staff-circle')
        .attr('fill', 'green');
      this.firstClick = false;
    } else {
      let ul, lr;
      if (cursorpt.x < this.coord.x || cursorpt.y < this.coord.y) { // second point is not lr
        ul = cursorpt;
        lr = this.coord;
      } else {
        ul = this.coord;
        lr = cursorpt;
      }
      document.getElementById('staff-circle').remove();
      const action: EditorAction = {
        'action': 'insert',
        'param': {
          'elementType': 'staff',
          'staffId': 'auto',
          'ulx': ul.x,
          'uly': ul.y,
          'lrx': lr.x,
          'lry': lr.y
        }
      };

      this.neonView.edit(action, this.neonView.view.getCurrentPageURI()).then(() => {
        this.neonView.updateForCurrentPage();
        this.firstClick = true;
      });
    }
  }).bind(this);

  /**
   * Remove the insert listeners while not leaving insert mode entirely.
   */
  removeInsertClickHandlers = (function removeInsertClickHandlers (): void {
    document.querySelector(this.selector).removeEventListener('click', this.staffHandler);
    document.querySelector(this.selector).removeEventListener('click', this.handler);
  }).bind(this);

  isInsertMode (): boolean {
    return (this.type !== '');
  }
}
export { InsertHandler as default };
