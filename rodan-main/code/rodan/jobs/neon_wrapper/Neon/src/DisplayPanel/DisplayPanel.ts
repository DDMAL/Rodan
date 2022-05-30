import * as DisplayControls from './DisplayControls';
import ZoomHandler from '../SingleView/Zoom';
import { DisplayInterface, ViewInterface } from '../Interfaces';

/**
 * Return the HTML for the display panel.
 * @param {ZoomHandler} handleZoom - Includes zoom controls if defined.
 * @returns {string}
 */
function displayControlsPanel (handleZoom: ZoomHandler): string {
  let contents =
  '<p class=\'panel-heading\' id=\'displayHeader\'>Display' +
  '<svg class=\'icon is-pulled-right\'><use id=\'toggleDisplay\' xlink:href=\'' + __ASSET_PREFIX__ + 'assets/img/icons.svg' + '#dropdown-down\'></use></svg></p>' +
  '<div id=\'displayContents\'>';
  if (handleZoom !== undefined) {
    contents +=
    '<a class=\'panel-block has-text-centered\'><button class=\'button\' id=\'reset-zoom\'>Zoom</button>' +
    '<input aria-labelledby=\'reset-zoom\' class=\'slider is-fullwidth\' id=\'zoomSlider\' step=\'5\' min=\'25\' max=\'400\' value=\'100\' type=\'range\'/>' +
    '<output id=\'zoomOutput\' for=\'zoomSlider\'>100</output></a>';
  }
  contents +=
  '<a class=\'panel-block has-text-centered\'><button class=\'button\' id=\'reset-opacity\'>Glyph Opacity</button>' +
  '<input aria-labelledby=\'reset-opacity\' class=\'slider is-fullwidth\' id=\'opacitySlider\' step=\'5\' min=\'0\' max=\'100\' value=\'100\' type=\'range\'/>' +
  '<output id=\'opacityOutput\' for=\'opacitySlider\'>100</output></a>' +
  '<a class=\'panel-block has-text-centered\'><button class=\'button\' id=\'reset-bg-opacity\'>Image Opacity</button>' +
  '<input aria-labelledby=\'reset-bg-opacity\' class=\'slider is-fullwidth\' id=\'bgOpacitySlider\' step=\'5\' min=\'0\' max=\'100\' value=\'100\' type=\'range\'/>' +
  '<output id=\'bgOpacityOutput\' for=\'bgOpacitySlider\'>100</output></a>' +
  '<div class=\'panel-block\' id=\'extensible-block\'>' +
  '<div class=\'dropdown\' id=\'highlight-dropdown\'><div class=\'dropdown-trigger\'>' +
  '<button class=\'button\' id=\'highlight-button\' aria-haspopup=\'true\' aria-controls=\'highlight-menu\' style=\'width: auto\'>' +
  '<span>Highlight</span><span id=\'highlight-type\'>&nbsp;- Off</span>' +
  '<svg class=\'icon\'><use id=\'toggleDisplay\' xlink:href=\'' + __ASSET_PREFIX__ + 'assets/img/icons.svg' + '#dropdown-down\'></use>' +
  '</svg></button></div><div class=\'dropdown-menu\' id=\'highlight-menu\' role=\'menu\'>' +
  '<div class=\'dropdown-content\'><a aria-role=\'menuitem\' class=\'dropdown-item\' id=\'highlight-staff\'>Staff</a>' +
  '<a aria-role=\'menuitem\' class=\'dropdown-item\' id=\'highlight-syllable\'>Syllable</a>' +
  '<a aria-role=\'menuitem\' class=\'dropdown-item\' id=\'highlight-neume\'>Neume</a><hr class=\'dropdown-divider\'/>' +
  '<a aria-role=\'menuitem\' class=\'dropdown-item\' id=\'highlight-none\'>None</a></div></div></div></div></div>';
  return contents;
}

/**
 * A class that sets the content of the display panel to the right and
 * manages controls for viewing.
 */
class DisplayPanel implements DisplayInterface {
  view: ViewInterface;
  className: string;
  background: string;
  zoomHandler: ZoomHandler;

  /**
   * Constructor for DisplayPanel.
   * @param {SingleView | DivaView} view - The View parent.
   * @param {string} className - The class name for the rendered SVG object(s).
   * @param {string} background - The class name associated with the background.
   * @param {ZoomHandler} [zoomHandler] - The ZoomHandler object, if SingleView.
   */
  constructor (view: ViewInterface, className: string,
    background: string, zoomHandler: ZoomHandler = undefined) {
    this.view = view;
    this.className = className;
    this.background = background;
    this.zoomHandler = zoomHandler;

    const displayPanel = document.getElementById('display_controls');
    displayPanel.innerHTML = displayControlsPanel(this.zoomHandler);
    this.view.addUpdateCallback(this.updateVisualization.bind(this));
  }

  /**
   * Apply event listeners related to the DisplayPanel.
   */
  setDisplayListeners (): void {
    if (this.zoomHandler) {
      // Zoom handler stuff
      DisplayControls.setZoomControls(this.zoomHandler);
    }
    DisplayControls.initDisplayControls(this.className, this.background);
  }

  /**
   * Update SVG based on visualization settings
   */
  updateVisualization (): void {
    DisplayControls.setOpacityFromSlider(this.className);
    DisplayControls.updateHighlight();
  }
}

export { DisplayPanel as default };
