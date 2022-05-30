import NeonView from '../NeonView';
import { EditorAction } from '../Types';
import * as d3 from 'd3';

class DragHandler {
  private dragStartCoords: Array<number>;
  private resetToAction: (selection: d3.Selection<d3.BaseType, {}, HTMLElement, any>, args: any[]) => void;
  readonly neonView: NeonView;
  private selector: string;
  private selection: Element[];
  private dx: number;
  private dy: number;

  /**
   * @param selector - CSS selector of element to apply drag handler to.
   */
  constructor (neonView: NeonView, selector: string) {
    this.neonView = neonView;
    this.selector = selector;
  }

  /**
   * Initialize the dragging action and handler for selected elements.
   */
  dragInit (): void {
    // Adding listeners
    const dragBehaviour = d3.drag()
      .on('start', dragStarted.bind(this))
      .on('drag', this.dragging.bind(this))
      .on('end', this.dragEnded.bind(this));

    const activeNc = d3.selectAll('.selected');
    const selection = Array.from(document.getElementsByClassName('selected'));
    this.selection = selection.concat(Array.from(document.getElementsByClassName('resizePoint')));

    this.dragStartCoords = new Array(activeNc.size());

    activeNc.call(dragBehaviour);

    // Drag effects
    function dragStarted (): void {
      this.dragStartCoords = [d3.event.x, d3.event.y];
      this.dx = 0;
      this.dy = 0;
      const target = d3.event.sourceEvent.target;
      if (target.classList.contains('staff')) {
        d3.select(this.selector).call(dragBehaviour);
      }
    }
  }

  dragging (): void {
    const relativeY = d3.event.y - this.dragStartCoords[1];
    const relativeX = d3.event.x - this.dragStartCoords[0];
    this.dx = d3.event.x - this.dragStartCoords[0];
    this.dy = d3.event.y - this.dragStartCoords[1];
    this.selection.forEach((el) => {
      d3.select(el).attr('transform', function () {
        return 'translate(' + [relativeX, relativeY] + ')';
      });
    });
    /*
     * if we're dragging a syllable (or neume etc) then there won't be a syl selected
     * then we don't want the bounding box (if it is displayed) to move when dragging the neumes
     * it will be a child of the element in selection, so it will get moved in the above loop
     * so we cancel that movement out here
     */
    if (this.selection.filter((element: HTMLElement) => element.classList.contains('syl')).length === 0) {
      d3.selectAll('.syllable.selected').selectAll('.sylTextRect-display').attr('transform', function () {
        return 'translate(' + [-1 * relativeX, -1 * relativeY] + ')';
      });
    }
  }

  dragEnded (): void {
    const paramArray = [];
    this.selection.filter((el: SVGElement) => !el.classList.contains('resizePoint')).forEach((el: SVGElement) => {
      const id = (el.tagName === 'rect') ? el.closest('.syl').id : el.id;
      const singleAction = { action: 'drag',
        param: { elementId: id,
          x: this.dx,
          y: (this.dy) * -1 }
      };
      paramArray.push(singleAction);
    });
    const editorAction: EditorAction = {
      'action': 'chain',
      'param': paramArray
    };

    const xDiff = Math.abs(this.dx);
    const yDiff = Math.abs(this.dy);

    if (xDiff > 5 || yDiff > 5) {
      this.neonView.edit(editorAction, this.neonView.view.getCurrentPageURI()).then(() => {
        this.neonView.updateForCurrentPage();
        this.endOptionsSelection();
        this.reset();
        this.dragInit();
      });
    } else {
      this.reset();
      this.dragInit();
    }
  }

  /** Set the d3 action to use for [[reset]]. */
  resetTo (reset: (selection: d3.Selection<d3.BaseType, {}, HTMLElement, any>, args: any[]) => void): void {
    this.resetToAction = reset;
  }

  /** Reset to a previous d3 action for [[this.selector]]. */
  reset (): void {
    if (this.resetToAction !== undefined) {
      d3.select(this.selector).call(this.resetToAction);
    }
  }

  endOptionsSelection (): void {
    try {
      document.getElementById('moreEdit').innerHTML = '';
      document.getElementById('moreEdit').classList.add('is-invisible');
    } catch (e) {}
  }
}

export { DragHandler as default };
