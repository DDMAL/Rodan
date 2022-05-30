import * as Color from './Color';
import { updateHighlight } from '../DisplayPanel/DisplayControls';
import * as Grouping from '../SquareEdit/Grouping';
import { resize } from './Resize';
import { Attributes } from '../Types';
import NeonView from '../NeonView';
import DragHandler from './DragHandler';
import * as SelectOptions from '../SquareEdit/SelectOptions';

import * as d3 from 'd3';
/**
 * @returns The selection mode chosen by the user.
 */
export function getSelectionType (): string {
  const element = document.getElementsByClassName('sel-by is-active');
  if (element.length !== 0) {
    return element[0].id;
  } else {
    return null;
  }
}

/**
 * Unselect all selected elements and run undo any extra
 * actions.
 */
export function unselect (): void {
  document.querySelectorAll('.selected').forEach((selected: SVGGElement) => {
    selected.classList.remove('selected');
    if (selected.classList.contains('staff')) {
      selected.removeAttribute('style');
      Color.unhighlight(selected);
    } else {
      selected.removeAttribute('style');
      selected.style.fill = '';
    }
  });
  Array.from(document.getElementsByClassName('text-select')).forEach((el: SVGElement) => {
    el.style.color = '';
    el.style.fontWeight = '';
    el.classList.remove('text-select');
  });
  Array.from(document.getElementsByClassName('sylTextRect-display')).forEach((sylRect: HTMLElement) => {
    sylRect.style.fill = 'blue';
  });

  Array.from(document.getElementsByClassName('syllable-highlighted')).forEach((syllable: HTMLElement) => {
    syllable.style.fill = '';
    syllable.classList.add('syllable');
    syllable.classList.remove('syllable-highlighted');
  });

  d3.selectAll('#resizeRect').remove();
  d3.selectAll('.resizePoint').remove();
  d3.selectAll('.rotatePoint').remove();

  if (!document.getElementById('selByStaff').classList.contains('is-active')) {
    Grouping.endGroupingSelection();
  } else {
    SelectOptions.endOptionsSelection();
  }
  document.getElementById('extraEdit').innerHTML = '';
  document.getElementById('extraEdit').classList.add('is-invisible');
  updateHighlight();
}

/**
 * Generic select function.
 * @param el - Element to select.
 * @param dragHandler - Only used for staves.
 */
export function select (el: SVGGraphicsElement, dragHandler?: DragHandler): void {
  if (el.classList.contains('staff')) {
    return selectStaff(el, dragHandler);
  }
  if (!el.classList.contains('selected') && !el.classList.contains('sylTextRect') &&
      !el.classList.contains('sylTextRect-display')) {
    el.classList.add('selected');
    el.style.fill = '#d00';
    if (el.querySelectorAll('.sylTextRect-display').length) {
      el.querySelectorAll('.sylTextRect-display').forEach((elem: HTMLElement) => {
        elem.style.fill = 'red';
      });
    }
    let sylId;
    if (el.classList.contains('syllable')) {
      sylId = el.id;
    } else if (el.closest('.syllable') !== null) {
      sylId = el.closest('.syllable').id;
    }
    if (sylId !== undefined) {
      const spans = document.querySelectorAll('span.' + sylId);
      spans.forEach((span: HTMLElement) => {
        span.style.color = '#d00';
        span.style.fontWeight = 'bold';
        span.classList.add('text-select');
      });
    }
  }
  updateHighlight();
}

/**
 * Select an nc.
 * @param el - The neume component.
 */
export async function selectNcs (el: SVGGraphicsElement, neonView: NeonView, dragHandler: DragHandler): Promise<void> {
  if (!el.parentElement.classList.contains('selected')) {
    const parent = el.parentElement as unknown as SVGGraphicsElement;
    unselect();
    select(parent);
    if (await isLigature(parent, neonView)) {
      const prevNc = parent.previousSibling as unknown as SVGGraphicsElement;
      if (await isLigature(prevNc, neonView)) {
        select(prevNc);
      } else {
        const nextNc = parent.nextSibling as unknown as SVGGraphicsElement;
        if (await isLigature(nextNc, neonView)) {
          select(nextNc);
        } else {
          console.warn('Error: Neither prev or next nc are ligatures');
        }
      }
      Grouping.triggerGrouping('ligature');
    } else if (parent.classList.contains('nc')) {
      SelectOptions.triggerNcActions(parent);
    } else {
      console.warn('No action triggered!');
    }
    dragHandler.dragInit();
  }
}

/**
 * @param nc - The neume component.
 * @param neonView - The [[NeonView]] for this instance.
 * @returns True if the neume component is part of a ligature.
 */
export async function isLigature (nc: SVGGraphicsElement, neonView: NeonView): Promise<boolean> {
  const attributes: Attributes = await neonView.getElementAttr(nc.id, neonView.view.getCurrentPageURI());
  return (attributes.ligated);
}

/**
 * @param elements - The elements to compare.
 * @returns True if the elements have the same parent up two levels, otherwise false.
 */
export function sharedSecondLevelParent (elements: SVGElement[]): boolean {
  const tempElements = Array.from(elements);
  const firstElement = tempElements.pop();
  const secondParent = firstElement.parentElement.parentElement;
  for (const element of tempElements) {
    const secPar = element.parentElement.parentElement;
    if (secPar.id !== secondParent.id) {
      return false;
    }
  }
  return true;
}

/**
 * Get the bounding box of a staff based on its staff lines.
 * Rotate is included in radians.
 */
export function getStaffBBox (staff: SVGGElement): {ulx: number; uly: number; lrx: number; lry: number; rotate: number} {
  let ulx, uly, lrx, lry, rotate;
  staff.querySelectorAll('path').forEach(path => {
    const coordinates: number[] = path.getAttribute('d')
      .match(/\d+/g)
      .map(element => Number(element));
    if (rotate === undefined) {
      rotate = Math.atan((coordinates[3] - coordinates[1]) /
        (coordinates[2] - coordinates[0]));
    }

    if (uly === undefined || Math.min(coordinates[1], coordinates[3]) < uly) {
      uly = Math.min(coordinates[1], coordinates[3]);
    }
    if (ulx === undefined || coordinates[0] < ulx) {
      ulx = coordinates[0];
    }
    if (lry === undefined || Math.max(coordinates[1], coordinates[3]) > lry) {
      lry = Math.max(coordinates[1], coordinates[3]);
    }
    if (lrx === undefined || coordinates[2] > lrx) {
      lrx = coordinates[2];
    }
  });
  return { 'ulx': ulx, 'uly': uly, 'lrx': lrx, 'lry': lry, 'rotate': rotate };
}

/**
 * select a boundingbox element
 * @param el - the bbox (sylTextRect) element in the DOM
 * @param dragHandler - the drag handler in use
 */
export function selectBBox (el: SVGGraphicsElement, dragHandler: DragHandler, neonView: NeonView): void {
  const bbox = el;
  const syl = bbox.closest('.syl');
  if (!syl.classList.contains('selected')) {
    syl.classList.add('selected');
    bbox.style.fill = '#d00';
    const closest = el.closest('.syllable') as HTMLElement;
    closest.style.fill = 'red';
    closest.classList.add('syllable-highlighted');
    if (neonView !== undefined ){
      resize(syl as SVGGraphicsElement, neonView, dragHandler);
    }
    if (dragHandler !== undefined) {
      dragHandler.dragInit();
    }
    const sylId = el.closest('.syllable').id;
    if (sylId !== undefined) {
      const span: HTMLSpanElement = document.querySelector('span.' + sylId);
      if (span) {
        span.style.color = '#d00';
        span.style.fontWeight = 'bold';
        span.classList.add('text-select');
      }
    }
  }
}

/**
 * Select not neume elements.
 * @param notNeumes - An array of not neumes elements.
 */
export function selectNn (notNeumes: SVGGraphicsElement[]): boolean {
  if (notNeumes.length > 0) {
    notNeumes.forEach(nn => { select(nn); });
    return false;
  } else {
    return true;
  }
}

/**
 * Select a staff element.
 * @param staff - The staff element in the DOM.
 * @param dragHandler - The drag handler in use.
 */
export function selectStaff (staff: SVGGElement, dragHandler: DragHandler): void {
  if (!staff.classList.contains('selected')) {
    staff.classList.add('selected');
    Color.unhighlight(staff);
    Color.highlight(staff, '#d00');
    dragHandler.dragInit();
  }
}

/**
 * Handle selecting an array of elements based on the selection type.
 */
export async function selectAll (elements: Array<SVGGraphicsElement>, neonView: NeonView, dragHandler: DragHandler): Promise<void> {
  const selectionType = getSelectionType();
  unselect();
  if (elements.length === 0) {
    return;
  }

  let selectionClass;
  let containsClefOrCustos = false;

  switch (selectionType) {
    case 'selBySyl':
      selectionClass = '.syllable';
      break;
    case 'selByNeume':
      selectionClass = '.neume';
      break;
    case 'selByNc':
      selectionClass = '.nc';
      break;
    case 'selByStaff':
      selectionClass = '.staff';
      break;
    case 'selByBBox':
      selectionClass = '.sylTextRect-display';
      break;
    default:
      console.error('Unknown selection type ' + selectionType);
      return;
  }

  // Get the groupings specified by selectionClass
  // that contain the provided elements to select.
  const groupsToSelect = new Set();
  for (const element of elements) {
    let grouping = element.closest(selectionClass);
    if (grouping === null) {
      // Check if we click-selected a clef or a custos
      grouping = element.closest('.clef, .custos');
      if (grouping === null) {
        console.warn('Element ' + element.id + ' is not part of specified group and is not a clef or custos.');
        continue;
      }
      containsClefOrCustos = containsClefOrCustos || true;
    }
    groupsToSelect.add(grouping);

    // Check for precedes/follows
    const follows = grouping.getAttribute('mei:follows');
    if (follows) {
      groupsToSelect.add(document.getElementById(follows.slice(1)));
    }
    const precedes = grouping.getAttribute('mei:precedes');
    if (precedes) {
      groupsToSelect.add(document.getElementById(precedes.slice(1)));
    }
  }

  // Select the elements
  groupsToSelect.forEach((group: SVGGraphicsElement) => { select(group, dragHandler); });

  /* Determine the context menu to display (if any) */

  const groups = Array.from(groupsToSelect.values()) as SVGGraphicsElement[];

  // Handle occurance of clef or custos
  if (containsClefOrCustos) {
    // A context menu will only be displayed if there is a single clef
    if (groupsToSelect.size === 1 && groups[0].classList.contains('clef')) {
      SelectOptions.triggerClefActions(groups[0]);
    } else if (groupsToSelect.size === 1 && groups[0].classList.contains('custos')) {
      SelectOptions.triggerCustosActions();
    } else {
      if (selectionType == 'selBySyl') {
        SelectOptions.triggerDefaultSylActions();
      } else {
        SelectOptions.triggerDefaultActions();
      }
    }
    return;
  }

  switch (selectionType) {
    case 'selByStaff':
      switch (groups.length) {
        case 1:
          SelectOptions.triggerSplitActions();
          resize(groups[0], neonView, dragHandler);
          break;
        default:
          SelectOptions.triggerStaffActions();
      }
      break;

    case 'selBySyl':
      switch (groups.length) {
        case 1:
          // TODO change context if it is only a neume/nc.
          SelectOptions.triggerSylActions();
          break;
        case 2:
          // Check if this is a linked syllable split by a staff break
          if ((groups[0].getAttribute('mei:follows') === '#' + groups[1].id) ||
          (groups[0].getAttribute('mei:precedes') === '#' + groups[1].id)) {
            Grouping.triggerGrouping('splitSyllable');
          } else if (sharedSecondLevelParent(groups)) {
            Grouping.triggerGrouping('syl');
          } else {
            // Check if this *could* be a selection with a single logical syllable split by a staff break.
            const staff0 = groups[0].closest('.staff');
            const staff1 = groups[1].closest('.staff');
            const staffChildren = Array.from(staff0.parentElement.children);
            // Check if these are adjacent staves (logically)
            if (Math.abs(staffChildren.indexOf(staff0) - staffChildren.indexOf(staff1)) === 1) {
              // Check if one syllable is the last in the first staff and the other is the first in the second.
              // Determine which staff is first.
              const firstStaff = (staffChildren.indexOf(staff0) < staffChildren.indexOf(staff1)) ? staff0 : staff1;
              const secondStaff = (firstStaff.id === staff0.id) ? staff1 : staff0;
              const firstLayer = firstStaff.querySelector('.layer');
              const secondLayer = secondStaff.querySelector('.layer');

              // Check that the first staff has either syllable as the last syllable
              const firstSyllableChildren = Array.from(firstLayer.children)
                .filter((elem: HTMLElement) => elem.classList.contains('syllable')) as HTMLElement[];
              const secondSyllableChildren = Array.from(secondLayer.children)
                .filter((elem: HTMLElement) => elem.classList.contains('syllable')) as HTMLElement[];
              const lastSyllable = firstSyllableChildren[firstSyllableChildren.length - 1];
              const firstSyllable = secondSyllableChildren[0];
              if (lastSyllable.id === groups[0].id && firstSyllable.id === groups[1].id) {
                Grouping.triggerGrouping('splitSyllable');
                break;
              } else if (lastSyllable.id === groups[1].id && firstSyllable.id === groups[0].id) {
                Grouping.triggerGrouping('splitSyllable');
                break;
              }
            }
            SelectOptions.triggerDefaultSylActions();
          }
          break;
        default:
          if (sharedSecondLevelParent(groups)) {
            Grouping.triggerGrouping('syl');
          } else {
            SelectOptions.triggerDefaultSylActions();
          }
      }
      break;

    case 'selByNeume':
      switch (groups.length) {
        case 1:
          // TODO change context if it is only a nc.
          SelectOptions.triggerNeumeActions();
          break;
        default:
          if (sharedSecondLevelParent(groups)) {
            Grouping.triggerGrouping('neume');
          } else {
            SelectOptions.triggerDefaultActions();
          }
      }
      break;

    case 'selByNc':
      switch (groups.length) {
        case 1:
          SelectOptions.triggerNcActions(groups[0]);
          break;
        case 2:
          if (sharedSecondLevelParent(groups)) {
            // Check if this selection is a ligature or can be a ligature
            // Check if these neume components are part of the same neume
            if (groups[0].parentElement === groups[1].parentElement) {
              const children = Array.from(groups[0].parentElement.children);
              // Check that neume components are adjacent
              if (Math.abs(children.indexOf(groups[0]) - children.indexOf(groups[1])) === 1) {
                // Check that second neume component is lower than first.
                // Note that the order in the list may not be the same as the
                // order by x-position.
                const orderFirstX = (groups[0].children[0] as SVGUseElement)
                  .x.baseVal.value;
                const orderSecondX = (groups[1].children[0] as SVGUseElement)
                  .x.baseVal.value;
                let posFirstY, posSecondY;

                if (orderFirstX < orderSecondX) {
                  posFirstY = (groups[0].children[0] as SVGUseElement)
                    .y.baseVal.value;
                  posSecondY = (groups[1].children[0] as SVGUseElement)
                    .y.baseVal.value;
                } else {
                  posFirstY = (groups[1].children[0] as SVGUseElement)
                    .y.baseVal.value;
                  posSecondY = (groups[0].children[0] as SVGUseElement)
                    .y.baseVal.value;
                }

                // Also ensure both components are marked or not marked as ligatures.
                const isFirstLigature = await isLigature(groups[0], neonView);
                const isSecondLigature = await isLigature(groups[1], neonView);
                if ((posSecondY > posFirstY) && !(isFirstLigature !== isSecondLigature)) {
                  Grouping.triggerGrouping('ligature');
                  break;
                }
              }
            }
            Grouping.triggerGrouping('nc');
          } else {
            SelectOptions.triggerDefaultActions();
          }
          break;
        default:
          if (sharedSecondLevelParent(groups)) {
            Grouping.triggerGrouping('nc');
          } else {
            SelectOptions.triggerDefaultActions();
          }
      }
      break;
    case 'selByBBox':
      switch (groups.length) {
        case 1:
          selectBBox(groups[0], dragHandler, neonView);
          SelectOptions.triggerDefaultActions();
          break;
        default:
          groups.forEach(g => selectBBox(g, dragHandler, undefined));
          break;
      }
      break;
    default:
      console.error('Unknown selection type. This should not have occurred.');
  }
}
