import * as Contents from './Contents';
import * as Grouping from './Grouping';
import * as Notification from '../utils/Notification';
import NeonView from '../NeonView';
import { SplitHandler } from './StaffTools';
import { EditorAction } from '../Types';
import { getStaffBBox } from '../utils/SelectTools';

/**
 * The NeonView parent to call editor actions.
 */
let neonView: NeonView;

/**
 * Initialize NeonView.
 */
export function initNeonView (view: NeonView): void {
  neonView = view;
  Grouping.initNeonView(view);
}

/**
 * @param id - The id of the neume component.
 * @returns An action that unsets the inclinatum parameter of a neume component.
 */
export function unsetInclinatumAction (id: string): EditorAction {
  return {
    'action': 'set',
    'param': {
      'elementId': id,
      'attrType': 'tilt',
      'attrValue': ''
    }
  };
}

/**
 * @param id - The id of the neume component.
 * @returns An action that unsets the virga parameter of a neume component.
 */
export function unsetVirgaAction (id: string): EditorAction {
  return {
    'action': 'set',
    'param': {
      'elementId': id,
      'attrType': 'tilt',
      'attrValue': ''
    }
  };
}

/**
 * Function to handle removing elements
 */
export function removeHandler (): void {
  const toRemove = [];
  const selected = Array.from(document.getElementsByClassName('selected'));
  selected.forEach(elem => {
    if (elem.classList.contains('syl')) {
      elem = elem.closest('.syllable');
    }
    toRemove.push(
      {
        'action': 'remove',
        'param': {
          'elementId': elem.id
        }
      }
    );
  });
  const chainAction: EditorAction = {
    'action': 'chain',
    'param': toRemove
  };
  endOptionsSelection();
  neonView.edit(chainAction, neonView.view.getCurrentPageURI()).then(() => { neonView.updateForCurrentPage(); });
}

/**
 * Function to handle re-associating elements to the nearest staff
 */
export function changeStaffHandler(): void {
  const toChange: EditorAction[] = [];
  const selected = Array.from(document.getElementsByClassName('selected'));
  selected.forEach(elem => {
    toChange.push(
      {
        'action': 'changeStaff',
        'param': {
          'elementId': elem.id
        }
      }
    );
  });
  const chainAction: EditorAction = {
    'action': 'chain',
    'param': toChange
  };
  endOptionsSelection();
  neonView.edit(chainAction, neonView.view.getCurrentPageURI()).then(() => { neonView.updateForCurrentPage(); });
}

/**
 * Trigger the extra nc action menu for a selection.
 */
export function triggerNcActions (nc: SVGGraphicsElement): void {
  endOptionsSelection();
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.classList.remove('is-invisible');
    moreEdit.innerHTML = Contents.defaultActionContents;
  } catch (e) {}
  try {
    const extraEdit = document.getElementById('extraEdit');
    extraEdit.classList.remove('is-invisible');
    extraEdit.innerHTML = Contents.ncActionContents;
  } catch (e) {}
  document.querySelector('#Punctum.dropdown-item')
    .addEventListener('click', () => {
      const unsetInclinatum = unsetInclinatumAction(nc.id);
      const unsetVirga = unsetVirgaAction(nc.id);
      neonView.edit({ 'action': 'chain', 'param': [ unsetInclinatum, unsetVirga ] }, neonView.view.getCurrentPageURI()).then((result) => {
        if (result) {
          Notification.queueNotification('Shape Changed');
        } else {
          Notification.queueNotification('Shape Change Failed');
        }
        endOptionsSelection();
        neonView.updateForCurrentPage();
      });
    });

  document.querySelector('#Inclinatum.dropdown-item')
    .addEventListener('click', () => {
      const setInclinatum = {
        'action': 'set',
        'param': {
          'elementId': nc.id,
          'attrType': 'tilt',
          'attrValue': 'se'
        }
      };
      neonView.edit(setInclinatum, neonView.view.getCurrentPageURI()).then((result) => {
        if (result) {
          Notification.queueNotification('Shape Changed');
        } else {
          Notification.queueNotification('Shape Change Failed');
        }
        endOptionsSelection();
        neonView.updateForCurrentPage();
      });
    });

  document.querySelector('#Virga.dropdown-item')
    .addEventListener('click', () => {
      const unsetInclinatum = unsetInclinatumAction(nc.id);
      const setVirga = {
        'action': 'set',
        'param': {
          'elementId': nc.id,
          'attrType': 'tilt',
          'attrValue': 'n'
        }
      };
      neonView.edit({ 'action': 'chain', 'param': [ unsetInclinatum, setVirga ] }, neonView.view.getCurrentPageURI()).then((result) => {
        if (result) {
          Notification.queueNotification('Shape Changed');
        } else {
          Notification.queueNotification('Shape Change Failed');
        }
        endOptionsSelection();
        neonView.updateForCurrentPage();
      });
    });
  try {
    const del = document.getElementById('delete');
    del.removeEventListener('click', removeHandler);
    del.addEventListener('click', removeHandler);
  } catch (e) {}
  document.body.addEventListener('keydown', deleteButtonHandler);

  initOptionsListeners();
}

/**
 * Trigger extra neume actions.
 */
export function triggerNeumeActions (): void {
  endOptionsSelection();
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.classList.remove('is-invisible');
    moreEdit.innerHTML = Contents.defaultActionContents;
  } catch (e) {}
  try {
    const extraEdit = document.getElementById('extraEdit');
    extraEdit.classList.remove('is-invisible');
    extraEdit.innerHTML = Contents.neumeActionContents;
  } catch (e) {}
  const neume = document.querySelectorAll('.selected');
  if (neume.length !== 1) {
    console.warn('More than one neume selected! Cannot trigger Neume ClickSelect actions.');
    return;
  }

  document.querySelector('.grouping')
    .addEventListener('click', (e) => {
      const contour = neonView.info.getContourByValue((e.target as HTMLElement).id);
      triggerChangeGroup(contour);
    });

  function triggerChangeGroup (contour): void {
    const changeGroupingAction: EditorAction = {
      'action': 'changeGroup',
      'param': {
        'elementId': neume[0].id,
        'contour': contour
      }
    };
    neonView.edit(changeGroupingAction, neonView.view.getCurrentPageURI()).then((result) => {
      if (result) {
        Notification.queueNotification('Grouping Changed');
      } else {
        Notification.queueNotification('Grouping Failed');
      }
      endOptionsSelection();
      neonView.updateForCurrentPage();
    });
  }
  try {
    const del = document.getElementById('delete');
    del.removeEventListener('click', removeHandler);
    del.addEventListener('click', removeHandler);
  } catch (e) {}
  document.body.addEventListener('keydown', deleteButtonHandler);

  initOptionsListeners();
  Grouping.initGroupingListeners();
}

/**
 * Trigger extra syllable actions.
 */
export function triggerSylActions (): void {
  endOptionsSelection();
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.classList.remove('is-invisible');
    moreEdit.innerHTML =
      '<div><p class=\'control\'>' +
          '<button class=\'button\' id=\'ungroupNeumes\'>Ungroup</button></p></div>' +
      '<div><p class=\'control\'>' +
          '<button class=\'button\' id=\'delete\'>Delete</button></p></div>' +
      '<div><p class=\'control\'>' +
        '<button class=\'button\' id=\'changeStaff\'>Re-associate to nearest staff</button></p></div>';
    document.getElementById('changeStaff').addEventListener('click', changeStaffHandler);
  } catch (e) { console.debug(e); }
  try {
    const del = document.getElementById('delete');
    del.removeEventListener('click', removeHandler);
    del.addEventListener('click', removeHandler);
  } catch (e) {}
  document.body.addEventListener('keydown', deleteButtonHandler);

  Grouping.initGroupingListeners();
}

/**
 * Trigger extra clef actions for a specific clef.
 * @param clef - The clef on which to trigger additional actions.
 */
export function triggerClefActions (clef: SVGGraphicsElement): void {
  endOptionsSelection();
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.classList.remove('is-invisible');
    // custos contents is just the delete button
    moreEdit.innerHTML = Contents.custosActionContents;
  } catch (e) {}
  try {
    const extraEdit = document.getElementById('extraEdit');
    extraEdit.classList.remove('is-invisible');
    extraEdit.innerHTML = Contents.clefActionContents;
  } catch (e) {}
  document.querySelector('#CClef.dropdown-item')
    .addEventListener('click', () => {
      const setCClef: EditorAction = {
        'action': 'setClef',
        'param': {
          'elementId': clef.id,
          'shape': 'C'
        }
      };
      neonView.edit(setCClef, neonView.view.getCurrentPageURI()).then((result) => {
        if (result) {
          Notification.queueNotification('Shape Changed');
        } else {
          Notification.queueNotification('Shape Change Failed');
        }
        endOptionsSelection();
        neonView.updateForCurrentPage();
      });
    });
  document.querySelector('#FClef.dropdown-item')
    .addEventListener('click', () => {
      const setFClef: EditorAction = {
        'action': 'setClef',
        'param': {
          'elementId': clef.id,
          'shape': 'F'
        }
      };
      neonView.edit(setFClef, neonView.view.getCurrentPageURI()).then((result) => {
        if (result) {
          Notification.queueNotification('Shape Changed');
        } else {
          Notification.queueNotification('Shape Change Failed');
        }
        endOptionsSelection();
        neonView.updateForCurrentPage();
      });
    });

  try {
    const del = document.getElementById('delete');
    del.removeEventListener('click', removeHandler);
    del.addEventListener('click', removeHandler);
    document.getElementById('changeStaff').addEventListener('click', changeStaffHandler);
  } catch (e) {console.debug(e);}
  document.body.addEventListener('keydown', deleteButtonHandler);


  initOptionsListeners();
}

/**
 * Trigger extra custos actions.
 */
export function triggerCustosActions (): void {
  endOptionsSelection();
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.classList.remove('is-invisible');
    moreEdit.innerHTML += Contents.custosActionContents;
  } catch (e) {}

  try {
    document.getElementById('changeStaff')
      .addEventListener('click', changeStaffHandler);
  } catch (e) {console.debug(e);}

  try {
    const del = document.getElementById('delete');
    del.removeEventListener('click', removeHandler);
    del.addEventListener('click', removeHandler);
    document.body.addEventListener('keydown', deleteButtonHandler);
  } catch (e) {}
}

/**
 * Trigger extra staff actions.
 */
export function triggerStaffActions (): void {
  endOptionsSelection();
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.classList.remove('is-invisible');
    moreEdit.innerHTML = Contents.staffActionContents;
  } catch (e) {}

  document.getElementById('merge-systems')
    .addEventListener('click', () => {
      const systems = document.querySelectorAll('.staff.selected');
      const elementIds = [];
      systems.forEach(staff => {
        elementIds.push(staff.id);
      });
      const editorAction: EditorAction = {
        'action': 'merge',
        'param': {
          'elementIds': elementIds
        }
      };
      neonView.edit(editorAction, neonView.view.getCurrentPageURI()).then((result) => {
        if (result) {
          Notification.queueNotification('Staff Merged');
          endOptionsSelection();
          neonView.updateForCurrentPage();
        } else {
          Notification.queueNotification('Merge Failed');
        }
      });
    });

  try {
    const del = document.getElementById('delete');
    del.removeEventListener('click', removeHandler);
    del.addEventListener('click', removeHandler);
  } catch (e) {}
  document.body.addEventListener('keydown', deleteButtonHandler);
}

/**
 * Trigger split staff option
 */
export function triggerSplitActions (): void {
  endOptionsSelection();
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.classList.remove('is-invisible');
    moreEdit.innerHTML = Contents.splitActionContents;
  } catch (e) {}

  // TODO add trigger for split action
  document.getElementById('split-system')
    .addEventListener('click', () => {
      const staff = document.querySelector('.staff.selected') as SVGGElement;
      if (staff !== null) {
        const split = new SplitHandler(neonView, staff);
        split.startSplit();
        endOptionsSelection();
      } else {
        console.error('No staff was selected!');
        endOptionsSelection();
      }
    });

  document.getElementById('reset-rotate')
    .addEventListener('click', () => {
      const staff = document.querySelector('.staff.selected') as SVGElement;
      const rect = staff.querySelector('#resizeRect');
      const co = rect.getAttribute('points').split(' ');
      const dy = parseInt(co[0].split(',')[1]) - parseInt(co[1].split(',')[1]);
      let points = getStaffBBox(staff as SVGGElement);
      let y_change = Math.tan(points.rotate)*(points.lrx - points.ulx);
      if (staff !== null) {
        const editorAction: EditorAction = {
          'action': 'resizeRotate',
          'param': {
            'elementId': staff.id,
            "ulx": points.ulx,
            "uly": points.rotate > 0 ? points.uly + y_change/2 : points.uly - y_change/2,
            "lrx": points.lrx,
            "lry": points.rotate > 0 ? points.lry - y_change/2 : points.lry + y_change/2,
            "rotate": 0
          }
        };
        neonView.edit(editorAction, neonView.view.getCurrentPageURI()).then(async (result) => {
          if (result) {
            await neonView.updateForCurrentPage();
          }
        });
        endOptionsSelection();
      } else {
        console.error('No staff was selected');
        endOptionsSelection();
      }
    });

  try {
    const del = document.getElementById('delete');
    del.removeEventListener('click', removeHandler);
    del.addEventListener('click', removeHandler);
  } catch (e) {}
  document.body.addEventListener('keydown', deleteButtonHandler);
}

/**
 * Trigger default actions when selecting by syl
 */
export function triggerDefaultSylActions (): void {
  endOptionsSelection();
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.classList.remove('is-invisible');
    moreEdit.innerHTML = Contents.defaultSylActionContents;
  } catch (e) {}

  try {
    const del = document.getElementById('delete');
    del.removeEventListener('click', removeHandler);
    del.addEventListener('click', removeHandler);
  } catch (e) {}
  document.body.addEventListener('keydown', deleteButtonHandler);
  try {
    const changeStaff = document.getElementById('changeStaff');
    changeStaff.removeEventListener('click', changeStaffHandler);
    changeStaff.addEventListener('click', changeStaffHandler);
  } catch(e) {console.debug(e);}
}

/**
 * Trigger default selection option.
 */
export function triggerDefaultActions (): void {
  endOptionsSelection();
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.classList.remove('is-invisible');
    moreEdit.innerHTML = Contents.defaultActionContents;
  } catch (e) {}

  try {
    const del = document.getElementById('delete');
    del.removeEventListener('click', removeHandler);
    del.addEventListener('click', removeHandler);
  } catch (e) {}
  document.body.addEventListener('keydown', deleteButtonHandler);
}

/**
 * End the extra options menu.
 */
export function endOptionsSelection (): void {
  try {
    const moreEdit = document.getElementById('moreEdit');
    moreEdit.innerHTML = '';
    moreEdit.classList.add('is-invisible');
  } catch (e) {}
  document.body.removeEventListener('keydown', deleteButtonHandler);
}

/**
 * Initialize extra dropdown options.
 */
function initOptionsListeners (): void {
  document.getElementById('drop_select').addEventListener('click', function () {
    this.classList.toggle('is-active');
  });
}

/** Event handler for delete button press. */
export function deleteButtonHandler (evt: KeyboardEvent): void {
  if (evt.key === 'd' || evt.key === 'Backspace') { removeHandler(); evt.preventDefault(); }
}
