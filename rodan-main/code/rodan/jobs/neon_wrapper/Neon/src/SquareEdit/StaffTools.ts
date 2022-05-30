import * as Notification from '../utils/Notification';
import NeonView from '../NeonView';
import { EditorAction } from '../Types';
import { selectAll } from '../utils/SelectTools';
import DragHandler from '../utils/DragHandler';

/** Handle splitting a staff into two staves through Verovio. */
export class SplitHandler {
  readonly neonView: NeonView;
  readonly staff: SVGGElement;

  /**
   * @param staff - The staff that will be modified.
   */
  constructor (neonView: NeonView, staff: SVGGElement) {
    this.neonView = neonView;
    this.staff = staff;
  }

  /**
   * First part of the split action.
   */
  startSplit (): void {
    this.splitDisable();

    document.body.addEventListener('click', this.handler, { capture: true });

    // Handle keypresses
    document.body.addEventListener('keydown', this.keydownListener);
    document.body.addEventListener('keyup', this.resetHandler);
    document.body.addEventListener('click', this.clickawayHandler);

    Notification.queueNotification('Click Where to Split');
  }

  splitDisable (): void {
    document.body.removeEventListener('keydown', this.keydownListener);
    document.body.removeEventListener('keyup', this.resetHandler);
    document.body.removeEventListener('click', this.clickawayHandler);
    document.body.removeEventListener('click', this.handler, { capture: true });
  }

  /** Handle input to split a staff. */
  handler = ((evt: MouseEvent): void => {
    const id = this.staff.id;

    const container = this.staff.closest('.definition-scale') as SVGSVGElement;
    const pt = container.createSVGPoint();
    pt.x = evt.clientX;
    pt.y = evt.clientY;

    // Transform to SVG coordinate system.
    const transformMatrix = (container.getElementsByClassName('system')[0] as SVGGElement)
      .getScreenCTM().inverse();
    const cursorPt = pt.matrixTransform(transformMatrix);
    // Find staff point corresponds to if one exists
    // TODO

    const editorAction: EditorAction = {
      'action': 'split',
      'param': {
        'elementId': id,
        'x': cursorPt.x
      }
    };

    this.neonView.edit(editorAction, this.neonView.view.getCurrentPageURI()).then(async (result) => {
      if (result) {
        await this.neonView.updateForCurrentPage();
        Notification.queueNotification('Split action successful');
      }
      const dragHandler = new DragHandler(this.neonView, '.staff');
      this.splitDisable();
      selectAll([document.querySelector('#' + id) as SVGGElement], this.neonView, dragHandler);
      try {
        document.getElementById('moreEdit').innerHTML = '';
        document.getElementById('moreEdit').classList.add('is-invisible');
      } catch (e) {}
    });
  }).bind(this);

  /** Exits split on Escape press, disables on Shift. */
  keydownListener = ((evt: KeyboardEvent): void => {
    if (evt.key === 'Escape') {
      this.splitDisable();
    } else if (evt.key === 'Shift') {
      document.body.removeEventListener('click', this.handler, { capture: true });
    }
  }).bind(this);

  /** Exit split if user clicks off of active page. */
  clickawayHandler = ((evt: MouseEvent): void => {
    const target = evt.target as HTMLElement;
    if (target.closest('.active-page') === null) {
      this.splitDisable();
      document.body.removeEventListener('click', this.handler, { capture: true });
    }
  }).bind(this);

  /** Called to reapply the event listener if necessary. */
  resetHandler = ((evt: KeyboardEvent): void => {
    if (evt.key === 'Shift') {
      document.body.addEventListener('click', this.handler, { capture: true });
    }
  }).bind(this);
}
