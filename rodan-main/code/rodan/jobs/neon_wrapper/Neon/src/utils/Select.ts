/** @module utils/Select */

import {
  unselect, getStaffBBox, selectStaff, selectAll, getSelectionType
} from './SelectTools';
import { resize } from './Resize';
import NeonView from '../NeonView';
import DragHandler from './DragHandler';
import { InfoInterface } from '../Interfaces';
import ZoomHandler from '../SingleView/Zoom';

import * as d3 from 'd3';

let dragHandler: DragHandler, neonView: NeonView, info: InfoInterface, zoomHandler: ZoomHandler;
let strokeWidth = 7;

/**
 * Set stroke width on drag select box.
 * @param width - Stroke width in pixels.
 */
export function setSelectStrokeWidth (width: number): void {
  strokeWidth = width;
}

/**
 * Set the objects for this module.
 */
export function setSelectHelperObjects (nv: NeonView, dh: DragHandler): void {
  dragHandler = dh;
  neonView = nv;
  info = neonView.info;
  zoomHandler = neonView.view.zoomHandler;
}

function escapeKeyListener (evt: KeyboardEvent): void {
  if (evt.key === 'Escape') {
    if (document.getElementsByClassName('selected').length > 0) {
      info.infoListeners();
    }
    unselect();
  }
}

function isSelByBBox (): boolean {
  const selByBBox = document.getElementById('selByBBox');
  if (selByBBox) {
    return selByBBox.classList.contains('is-active');
  }
  return false;
}

function stopPropHandler (evt): void { evt.stopPropagation(); }

/**
 * Apply listeners for click selection.
 * @param selector - The CSS selector used to choose where listeners are applied.
 */
export function clickSelect (selector: string): void {
  document.querySelectorAll(selector).forEach(sel => {
    sel.removeEventListener('mousedown', clickHandler);
    sel.addEventListener('mousedown', clickHandler);
  });

  // Click away listeners
  document.body.removeEventListener('keydown', escapeKeyListener);
  document.body.addEventListener('keydown', escapeKeyListener);

  document.getElementById('container')
    .addEventListener('contextmenu', (evt) => { evt.preventDefault(); });

  document.querySelectorAll('use,rect,#moreEdit').forEach(sel => {
    sel.removeEventListener('click', stopPropHandler);
    sel.addEventListener('click', stopPropHandler);
  });
}

/**
 * Handle click events related to element selection.
 */
function clickHandler (evt: MouseEvent): void {
  if (!neonView) return;
  const mode = neonView.getUserMode();

  // If in insert mode or panning is active from shift key
  if (mode === 'insert' || evt.shiftKey) { return; }
  // Check if the element being clicked on is part of a drag Selection
  if (this.tagName === 'use' && getSelectionType() !== 'selByBBox') {
    if (this.closest('.selected') === null) {
      let selection = [this];
      // Check if this is part of a ligature and, if so, add all of it to the selection.
      const firstLigatureHalf = /E9B[45678]/;
      const secondLigatureHalf = /E9B[9ABC]/;
      if (this.getAttribute('xlink:href').match(secondLigatureHalf)) {
        // This is the second part of a ligature
        const nc = this.closest('.nc');
        const neume = this.closest('.neume');
        const ncIndex = Array.from(neume.children).indexOf(nc);
        const firstUse = neume.children[ncIndex - 1].children[0];
        console.assert(firstUse.getAttribute('xlink:href').match(firstLigatureHalf), 'First glyph of ligature unexpected!');
        if (firstUse.closest('.selected') === null) {
          selection.unshift(firstUse);
        }
      } else if (this.getAttribute('xlink:href').match(firstLigatureHalf)) {
        // This is the first part of a ligature
        const nc = this.closest('.nc');
        const neume = this.closest('.neume');
        const ncIndex = Array.from(neume.children).indexOf(nc);
        const secondUse = neume.children[ncIndex + 1].children[0];
        console.assert(secondUse.getAttribute('xlink:href').match(secondLigatureHalf), 'Second glyph of ligature unexpected!');
        if (secondUse.closest('.selected') === null) {
          selection.push(secondUse);
        }
      }
      if (window.navigator.userAgent.match(/Mac/) ? evt.metaKey : evt.ctrlKey) {
        selection = selection.concat(Array.from(document.getElementsByClassName('selected')));
      }
      selectAll(selection, neonView, dragHandler);
      if (dragHandler) {
        dragHandler.dragInit();
      }
    }
    else {
      let selection = [];
      if (window.navigator.userAgent.match(/Mac/) ? evt.metaKey : evt.ctrlKey) {
        // determine which selection mode we're in
        const temp = document.querySelector('.sel-by.is-active').id;
        let mode = '';
        switch (temp) {
          case 'selByStaff':
            mode = '.staff';
            break;
          case 'selByNeume':
            mode = '.neume';
            break;
          case 'selByNc':
            mode = '.nc';
            break;
          default:
            mode = '.syllable';
            break;
        }
        const remove = [this.closest(mode)];
        selection = Array.from(document.getElementsByClassName('selected'));
        selection = selection.filter( (el) => {
          return !remove.includes(el);
        });
        selectAll(selection, neonView, dragHandler);
        if (dragHandler) {
          dragHandler.dragInit();
        }
      }
    }
  } else if ((evt.target as HTMLElement).tagName === 'rect' && getSelectionType() === 'selByBBox') {
    if (this.closest('.selected') === null) {
      let selection = [evt.target] as SVGGElement[];
      if (window.navigator.userAgent.match(/Mac/) ? evt.metaKey : evt.ctrlKey) {
        selection = selection.concat(Array.from(document.getElementsByClassName('selected')) as SVGGElement[]);
        selection = selection.map( (el) => {
          if (el.tagName == 'rect') {
            return el;
          }
          return el.querySelector('.sylTextRect-Display');
        });
      }
      selectAll(selection, neonView, dragHandler);
      if (dragHandler) {
        dragHandler.dragInit();
      }
    } else {
      let selection = [];
      if (window.navigator.userAgent.match(/Mac/) ? evt.metaKey : evt.ctrlKey) {
        const remove = [this];
        selection = Array.from(document.getElementsByClassName('selected'));
        selection = selection.map( (el) => {
          if (el.tagName == 'rect') {
            return el;
          }
          return el.querySelector('.sylTextRect-Display');
        });
        selection = selection.filter( (el) => {
          return !remove.includes(el);
        });
        selectAll(selection, neonView, dragHandler);
        if (dragHandler) {
          dragHandler.dragInit();
        }
      }
    }
  } else {
    // Check if the point being clicked on is a staff selection (if applicable)
    if (getSelectionType() !== 'selByStaff') {
      info.infoListeners();
      return;
    }

    // Check if the point is in a staff.
    const container = document.getElementsByClassName('active-page')[0].getElementsByClassName('definition-scale')[0] as SVGSVGElement;
    let pt = container.createSVGPoint();
    pt.x = evt.clientX;
    pt.y = evt.clientY;
    const transformMatrix = (container.getElementsByClassName('system')[0] as SVGGraphicsElement).getScreenCTM();
    pt = pt.matrixTransform(transformMatrix.inverse());

    const selectedStaves = Array.from(document.getElementsByClassName('staff'))
      .filter((staff: SVGGElement) => {
        const bbox = getStaffBBox(staff);
        const ulx = bbox.ulx;
        const uly = bbox.uly;
        const lrx = bbox.lrx;
        const lry = bbox.lry;
        const rotate = bbox.rotate;

        return (pt.x > ulx && pt.x < lrx) &&
          (pt.y > (uly + (pt.x - ulx) * Math.tan(rotate))) &&
          (pt.y < (lry - (lrx - pt.x) * Math.tan(rotate)));
      });

    unselect();
    if (selectedStaves.length == 0) {
      return;
    }

    // Select a staff
    const staff = selectedStaves[0] as SVGGElement;
    if (!staff.classList.contains('selected')) {
      // Select previously unselected staff
      selectStaff(staff, dragHandler);
      resize(staff, neonView, dragHandler);
      if (dragHandler) {
        dragHandler.dragInit();
      }
    }
    // Trigger mousedown event on the staff
    staff.dispatchEvent(new MouseEvent('mousedown', {
      screenX: evt.screenX,
      screenY: evt.screenY,
      clientX: evt.clientX,
      clientY: evt.clientY,
      ctrlKey: evt.ctrlKey,
      shiftKey: evt.shiftKey,
      altKey: evt.altKey,
      metaKey: evt.metaKey,
      view: evt.view
    }));
  }
}

/**
 * Apply listeners for drag selection.
 * @param selector - The CSS selector used to choose where listeners are applied.
 */
export function dragSelect (selector: string): void {
  let initialX = 0;
  let initialY = 0;
  let panning = false;
  let dragSelecting = false;
  // var canvas = d3.select('#svg_group');
  d3.selectAll(selector.replace('.active-page', '').trim())
    .on('.drag', null);
  const canvas = d3.select(selector);
  const dragSelectAction = d3.drag()
    .on('start', selStart)
    .on('drag', selecting)
    .on('end', selEnd);
  canvas.call(dragSelectAction);
  if (dragHandler) {
    dragHandler.resetTo(dragSelectAction);
  }

  function selStart (): void {
    if (!neonView) return;
    const userMode = neonView.getUserMode();
    if (d3.event.sourceEvent.target.nodeName !== 'use' && userMode !== 'insert' && d3.event.sourceEvent.target.nodeName !== 'rect') {
      if (!d3.event.sourceEvent.shiftKey) { // If not holding down shift key to pan
        if (!document.getElementById('selByStaff').classList.contains('is-active') ||
          pointNotInStaff(d3.mouse(this))) {
          unselect();
          dragSelecting = true;
          const initialP = d3.mouse(this);
          initialX = initialP[0];
          initialY = initialP[1];
          initRect(initialX, initialY);
        }
      } else {
        panning = true;
        if (zoomHandler !== undefined) {
          zoomHandler.startDrag();
        }
      }
    } else if (d3.event.sourceEvent.shiftKey) {
      panning = true;
      if (zoomHandler !== undefined) {
        zoomHandler.startDrag();
      }
    }
  }

  /**
   * Check if a point is in the bounds of a staff element.
   * Rotate is not taken into account.
   */
  function pointNotInStaff (pt: number[]): boolean {
    const staves = Array.from(document.getElementsByClassName('staff'));
    const filtered = staves.filter((staff: SVGGElement) => {
      const bbox = getStaffBBox(staff);
      const ulx = bbox.ulx;
      const uly = bbox.uly;
      const lrx = bbox.lrx;
      const lry = bbox.lry;
      const rotate = bbox.rotate;

      return (pt[0] > ulx && pt[0] < lrx) &&
        (pt[1] > (uly + (pt[0] - ulx) * Math.tan(rotate))) &&
        (pt[1] < (lry - (lrx - pt[0]) * Math.tan(rotate)));
    });
    return (filtered.length === 0);
  }

  function selecting (): void {
    if (!panning && dragSelecting) {
      const currentPt = d3.mouse(this);
      const curX = currentPt[0];
      const curY = currentPt[1];

      const newX = curX < initialX ? curX : initialX;
      const newY = curY < initialY ? curY : initialY;
      const width = curX < initialX ? initialX - curX : curX - initialX;
      const height = curY < initialY ? initialY - curY : curY - initialY;

      updateRect(newX, newY, width, height);
    } else if (panning) {
      if (zoomHandler !== undefined) {
        zoomHandler.dragging();
      }
    }
  }

  function selEnd (): void {
    if (!panning && dragSelecting) {
      const rx = parseInt(document.getElementById('selectRect').getAttribute('x'));
      const ry = parseInt(document.getElementById('selectRect').getAttribute('y'));
      const lx = parseInt(document.getElementById('selectRect').getAttribute('x')) +
        parseInt(document.getElementById('selectRect').getAttribute('width'));
      const ly = parseInt(document.getElementById('selectRect').getAttribute('y')) +
        parseInt(document.getElementById('selectRect').getAttribute('height'));
      // Transform to the correct coordinate system
      const node = canvas.node() as SVGSVGElement;
      let ul = node.createSVGPoint();
      ul.x = rx;
      ul.y = ry;
      let lr = node.createSVGPoint();
      lr.x = lx;
      lr.y = ly;
      const transform = node.getScreenCTM().inverse()
        .multiply((canvas.select('.system').node() as SVGGraphicsElement)
          .getScreenCTM()).inverse();
      ul = ul.matrixTransform(transform);
      lr = lr.matrixTransform(transform);

      let nc;
      if (document.getElementById('selByStaff').classList.contains('is-active')) {
        nc = document.querySelectorAll(selector + ' use, ' + selector + ' .staff');
      } else if (isSelByBBox()) {
        nc = document.querySelectorAll(selector + ' .sylTextRect-display');
      } else {
        nc = document.querySelectorAll(selector + ' use');
      }
      const els = Array.from(nc);

      const elements = els.filter(function (d: SVGGraphicsElement): boolean {
        let ulx, uly, lrx, lry;
        if (isSelByBBox()) {
          ulx = Number(d.getAttribute('x'));
          uly = Number(d.getAttribute('y'));
          lrx = +ulx + +(d.getAttribute('width').slice(0, -2));
          lry = +uly + +(d.getAttribute('height').slice(0, -2));
          return !(((ul.x < ulx && lr.x < ulx) || (ul.x > lrx && lr.x > lrx)) || ((ul.y < uly && lr.y < uly) || (ul.y > lry && lr.y > lry)));
        } else if (d.tagName === 'use') {
          const box = (d.parentNode as SVGGElement).getBBox();
          ulx = box.x;
          uly = box.y;
          lrx = box.x + box.width;
          lry = box.y + box.height;
          return !(((ul.x < ulx && lr.x < ulx) || (ul.x > lrx && lr.x > lrx)) || ((ul.y < uly && lr.y < uly) || (ul.y > lry && lr.y > lry)));
        } else {
          const box = getStaffBBox(d);
          return !((ul.x < box.ulx && lr.x < box.ulx) ||
                  (ul.x > box.lrx && lr.x > box.lrx) ||
                  (ul.y < (box.uly + Math.abs(box.ulx - ul.x) * Math.tan(box.rotate)) &&
                    lr.y < (box.uly + Math.abs(box.ulx - ul.x) * Math.tan(box.rotate))) ||
                  (ul.y > (box.lry + Math.abs(box.lry - lr.y) * Math.tan(box.rotate)) &&
                    lr.y > (box.lry + Math.abs(box.lry - lr.y) * Math.tan(box.rotate))));
        }
      }) as SVGGraphicsElement[];

      // Get other halves of ligatures if only one is selected
      elements.forEach((element: SVGElement) => {
        if (element.tagName === 'use' && element.getAttribute('xlink:href').match(/E9B[456789ABC]/)) {
          const neume = element.closest('.neume');
          const ncIndex = Array.from(neume.children).indexOf(element.closest('.nc'));
          if (element.getAttribute('xlink:href').match(/E9B[45678]/)) {
            // Add second half of ligature to selected list if not already present
            const secondNc = neume.children[ncIndex + 1];
            const secondUse = secondNc.querySelector('use');
            if (elements.indexOf(secondUse) < 0) {
              elements.push(secondUse);
            }
          } else {
            // Add first half of ligature to selected list if not already present
            const firstNc = neume.children[ncIndex - 1];
            const firstUse = firstNc.querySelector('use');
            if (elements.indexOf(firstUse) < 0) {
              elements.push(firstUse);
            }
          }
        }
      });
      selectAll(elements, neonView, dragHandler);

      if (dragHandler) {
        dragHandler.dragInit();
      }
      d3.selectAll('#selectRect').remove();
      dragSelecting = false;
    }
    panning = false;
  }

  /**
     * Create an initial dragging rectangle.
     * @param ulx - The upper left x-position of the new rectangle.
     * @param uly - The upper left y-position of the new rectangle.
     */
  function initRect (ulx: number, uly: number): void {
    canvas.append('rect')
      .attr('x', ulx)
      .attr('y', uly)
      .attr('width', 0)
      .attr('height', 0)
      .attr('id', 'selectRect')
      .attr('stroke', 'black')
      .attr('stroke-width', strokeWidth)
      .attr('fill', 'none');
  }

  /**
     * Update the dragging rectangle.
     * @param newX - The new ulx.
     * @param newY - The new uly.
     * @param currentWidth - The width of the rectangle in pixels.
     * @param currentHeight - The height of the rectangle in pixels.
     */
  function updateRect (newX: number, newY: number, currentWidth: number, currentHeight: number): void {
    d3.select('#selectRect')
      .attr('x', newX)
      .attr('y', newY)
      .attr('width', currentWidth)
      .attr('height', currentHeight);
  }
}
