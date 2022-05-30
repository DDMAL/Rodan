import { bindInsertTabs, initInsertEditControls, initEditModeControls, initSelectionButtons } from './Controls';
import { setHighlightSelectionControls } from '../DisplayPanel/DisplayControls';
import * as Select from '../utils/Select';
import InsertHandler from './InsertHandler';
import NeonView from '../NeonView';
import * as SelectOptions from './SelectOptions';
import DragHandler from '../utils/DragHandler';
import { NeumeEditInterface } from '../Interfaces';

/**
 * An Edit Module for a single page of a manuscript.
 * Works with the SingleView module.
 */
class SingleEditMode implements NeumeEditInterface {
  neonView: NeonView;
  dragHandler: DragHandler;
  insertHandler: InsertHandler;
  /**
   * Constructor for an EditMode object.
   * @param {NeonView} neonView - The NeonView parent.
   */
  constructor (neonView: NeonView) {
    this.neonView = neonView;
    initEditModeControls(this);
  }

  /**
   * Initialize the start of edit mode when first leaving viewer mode.
   */
  initEditMode (): void {
    this.dragHandler = new DragHandler(this.neonView, '#svg_group');
    this.insertHandler = new InsertHandler(this.neonView, '#svg_group');
    bindInsertTabs(this.insertHandler);
    document.getElementById('primitiveTab').click();
    Select.setSelectHelperObjects(this.neonView, this.dragHandler);
    this.setSelectListeners();

    SelectOptions.initNeonView(this.neonView);
    initInsertEditControls();
    const editMenu = document.getElementById('editMenu');
    editMenu.style.backgroundColor = '#ffc7c7';
    editMenu.style.fontWeight = 'bold';

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
    Select.clickSelect('#svg_group, #svg_group use, #svg_group rect');
    Select.dragSelect('#svg_group');
  }
}

export { SingleEditMode as default };
