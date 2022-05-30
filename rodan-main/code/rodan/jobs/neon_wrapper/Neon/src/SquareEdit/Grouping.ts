import * as Contents from './Contents';
import * as Warnings from '../Warnings';
import * as Notification from '../utils/Notification';
import NeonView from '../NeonView';
import { EditorAction } from '../Types';
import { unsetVirgaAction, unsetInclinatumAction, removeHandler, deleteButtonHandler } from './SelectOptions';

/**
 * The NeonView parent to access editor actions.
 */
let neonView: NeonView;

/**
 * Set the neonView member.
 */
export function initNeonView (view: NeonView): void {
  neonView = view;
}

/**
 * Trigger the grouping selection menu.
 * @param type - The grouping type: nc, neume, syl, ligatureNc, or ligature
 */
export function triggerGrouping (type: string): void {
  const moreEdit = document.getElementById('moreEdit');
  moreEdit.classList.remove('is-invisible');
  moreEdit.innerHTML += Contents.groupingMenu[type];
  initGroupingListeners();
}

/**
 * Remove the grouping selection menu.
 */
export function endGroupingSelection (): void {
  const moreEdit = document.getElementById('moreEdit');
  moreEdit.innerHTML = '';
  moreEdit.classList.add('is-invisible');
  document.body.removeEventListener('keydown', deleteButtonHandler);
}

/**
 * The grouping dropdown listener.
 */
export function initGroupingListeners (): void {
  const del = document.getElementById('delete');
  del.removeEventListener('click', removeHandler);
  del.addEventListener('click', removeHandler);
  document.body.addEventListener('keydown', deleteButtonHandler);
  try {
    document.getElementById('mergeSyls').addEventListener('click', () => {
      const elementIds = getChildrenIds().filter(e =>
        document.getElementById(e).classList.contains('neume')
      );
      groupingAction('group', 'neume', elementIds);
    });
  } catch (e) {}

  try {
    document.getElementById('groupNeumes').addEventListener('click', () => {
      const elementIds = getIds();
      groupingAction('group', 'neume', elementIds);
    });
  } catch (e) {}

  try {
    document.getElementById('groupNcs').addEventListener('click', () => {
      const elementIds = getIds();
      groupingAction('group', 'nc', elementIds);
    });
  } catch (e) {}

  try {
    document.getElementById('ungroupNeumes').addEventListener('click', () => {
      const elementIds = getChildrenIds();
      groupingAction('ungroup', 'neume', elementIds);
    });
  } catch (e) {}

  try {
    document.getElementById('ungroupNcs').addEventListener('click', () => {
      const elementIds = getChildrenIds();
      groupingAction('ungroup', 'nc', elementIds);
    });
  } catch (e) {}

  try {
    document.getElementById('toggle-ligature').addEventListener('click', async () => {
      const elementIds = getIds();
      let isLigature;
      const ligatureRegex = /#E99[016]/;
      if (!ligatureRegex.test(document.getElementById(elementIds[0]).children[0].getAttribute('xlink:href'))) { // SMUFL codes for ligature glyphs
        isLigature = true;
      } else {
        isLigature = false;
        const chainAction: EditorAction = { 'action': 'chain',
          'param': [
            unsetInclinatumAction(elementIds[0]), unsetVirgaAction(elementIds[0]),
            unsetInclinatumAction(elementIds[1]), unsetVirgaAction(elementIds[1])
          ] };
        await neonView.edit(chainAction, neonView.view.getCurrentPageURI());
      }

      const editorAction: EditorAction = {
        'action': 'toggleLigature',
        'param': {
          'elementIds': elementIds,
          'isLigature': isLigature.toString()
        }
      };
      neonView.edit(editorAction, neonView.view.getCurrentPageURI()).then((result) => {
        if (result) {
          Notification.queueNotification('Ligature Toggled');
        } else {
          Notification.queueNotification('Ligature Toggle Failed');
        }
        endGroupingSelection();
        neonView.updateForCurrentPage();
      });
    });
  } catch (e) {}

  try {
    document.getElementById('toggle-link').addEventListener('click', () => {
      const elementIds = getIds();
      const chainAction: EditorAction = {
        'action': 'chain',
        'param': []
      };
      const param = new Array<EditorAction>();
      if (document.getElementById(elementIds[0]).getAttribute('mei:precedes')) {
        param.push({
          'action': 'set',
          'param': {
            'elementId': elementIds[0],
            'attrType': 'precedes',
            'attrValue': ''
          }
        });
        param.push({
          'action': 'set',
          'param': {
            'elementId': elementIds[1],
            'attrType': 'follows',
            'attrValue': ''
          }
        });
        param.push({
          'action': 'setText',
          'param': {
            'elementId': elementIds[1],
            'text': ''
          }
        });
      } else if (document.getElementById(elementIds[0]).getAttribute('mei:follows')) {
        param.push({
          'action': 'set',
          'param': {
            'elementId': elementIds[0],
            'attrType': 'follows',
            'attrValue': ''
          }
        });
        param.push({
          'action': 'set',
          'param': {
            'elementId': elementIds[1],
            'attrType': 'precedes',
            'attrValue': ''
          }
        });
        param.push({
          'action': 'setText',
          'param': {
            'elementId': elementIds[0],
            'text': ''
          }
        });
      } else {
        // Associate syllables. Will need to find which is first. Use staves.
        const syllable0 = document.getElementById(elementIds[0]);
        const syllable1 = document.getElementById(elementIds[1]);
        const staff0 = syllable0.closest('.staff');
        const staff1 = syllable1.closest('.staff');
        const staffChildren = Array.from(staff0.parentElement.children).filter((elem: HTMLElement) => elem.classList.contains('staff'));

        let firstSyllable, secondSyllable;
        // Determine first syllable comes first by staff
        if (staffChildren.indexOf(staff0) < staffChildren.indexOf(staff1)) {
          firstSyllable = syllable0;
          secondSyllable = syllable1;
        } else {
          firstSyllable = syllable1;
          secondSyllable = syllable0;
        }

        param.push({
          'action': 'set',
          'param': {
            'elementId': firstSyllable.id,
            'attrType': 'precedes',
            'attrValue': '#' + secondSyllable.id
          }
        });
        param.push({
          'action': 'set',
          'param': {
            'elementId': secondSyllable.id,
            'attrType': 'follows',
            'attrValue': '#' + firstSyllable.id
          }
        });
        // Delete syl on second syllable
        const syl = secondSyllable.querySelector('.syl');
        if (syl !== null) {
          param.push({
            'action': 'remove',
            'param': {
              'elementId': syl.id
            }
          });
        }
      }
      chainAction.param = param;
      neonView.edit(chainAction, neonView.view.getCurrentPageURI()).then((result) => {
        if (result) {
          Notification.queueNotification('Toggled Syllable Link');
        } else {
          Notification.queueNotification('Failed to Toggle Syllable Link');
        }
        endGroupingSelection();
        neonView.updateForCurrentPage();
      });
    });
  } catch (e) {}
}

/**
 * Form and execute a group/ungroup action.
 * @param action - The action to execute. Either "group" or "ungroup".
 * @param groupType - The type of elements to group. Either "neume" or "nc".
 * @param elementIds - The IDs of the elements.
 */
function groupingAction (action: string, groupType: string, elementIds: string[]): void {
  const editorAction: EditorAction = {
    'action': action,
    'param': {
      'groupType': groupType,
      'elementIds': elementIds
    }
  };
  neonView.edit(editorAction, neonView.view.getCurrentPageURI()).then((result) => {
    if (result) {
      if (action === 'group') {
        Notification.queueNotification('Grouping Success');
      } else {
        Notification.queueNotification('Ungrouping Success');
      }
    } else {
      if (action === 'group') {
        Notification.queueNotification('Grouping Failed');
      } else {
        Notification.queueNotification('Ungrouping Failed');
      }
    }
    neonView.updateForCurrentPage();

    // Prompt user to confirm if Neon does not re cognize contour
    if (groupType === 'nc') {
      const neumeParent = document.getElementById(elementIds[0]).parentElement;
      const ncs = Array.from(neumeParent.children) as SVGGraphicsElement[];
      const contour = neonView.info.getContour(ncs);
      if (contour === undefined) {
        Warnings.groupingNotRecognized();
      }
    }
    endGroupingSelection();
  });
}

/**
 * @returns The IDs of selected elements.
 */
function getIds (): string[] {
  const ids = [];
  const elements = Array.from(document.getElementsByClassName('selected'));
  elements.forEach(el => {
    ids.push(el.id);
  });
  return ids;
}

/**
 * @returns The IDs of the selected elements' children.
 */
function getChildrenIds (): string[] {
  const childrenIds = [];
  const elements = Array.from(document.getElementsByClassName('selected'));
  elements.forEach(el => {
    const children = Array.from(el.children);
    children.forEach(ch => {
      childrenIds.push(ch.id);
    });
  });
  return childrenIds;
}
