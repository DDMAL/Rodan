import { bindInsertTabs, initInsertEditControls, initEditModeControls, initSelectionButtons } from './Controls';
import * as Select from '../utils/Select';
import InsertHandler from './InsertHandler';
import NeonView from '../NeonView';
import * as SelectOptions from './SelectOptions';
import { setHighlightSelectionControls } from '../DisplayPanel/DisplayControls';
import DragHandler from '../utils/DragHandler';
import { NeumeEditInterface } from '../Interfaces';

class DivaEdit implements NeumeEditInterface {
  neonView: NeonView;
  dragHandler: DragHandler;
  insertHandler: InsertHandler;
  constructor (neonView: NeonView) {
    this.neonView = neonView;
    initEditModeControls(this);
  }

  initEditMode (): void {
    this.dragHandler = new DragHandler(this.neonView, '.active-page > svg');
    this.insertHandler = new InsertHandler(this.neonView, '.active-page > svg');
    bindInsertTabs(this.insertHandler);
    document.getElementById('primitiveTab').click();
    Select.setSelectHelperObjects(this.neonView, this.dragHandler);
    this.setSelectListeners();

    SelectOptions.initNeonView(this.neonView);
    initInsertEditControls();
    const editMenu = document.getElementById('editMenu');
    editMenu.style.backgroundColor = '#ffc7c7';
    editMenu.style.fontWeight = 'bold';

    Select.setSelectStrokeWidth(1);

    initSelectionButtons();

    setHighlightSelectionControls();

    this.neonView.view.addUpdateCallback(this.setSelectListeners.bind(this));
  }

  /**
   * Get the user mode that Neon is in. Either insert, edit, or viewer.
   * @returns {string}
   */
  getUserMode (): string {
    if (this.insertHandler !== undefined) {
      if (this.insertHandler.isInsertMode()) {
        return 'insert';
      }
      return 'edit';
    }
    return 'viewer';
  }

  setSelectListeners (): void {
    Select.clickSelect('.active-page > svg > svg, .active-page > svg > svg use, .active-page > svg > svg rect');
    Select.dragSelect('.active-page svg');
  }
}

export { DivaEdit as default };
