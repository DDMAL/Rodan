import $, { event } from 'jquery';
import { drawGrid } from './Utilities/PaperUtilities';
import BaseItem from './Items/BaseItem';
import GUI_EVENTS from './Shared/Events';
import InputPortItem from './Items/InputPortItem';
import ItemController from './Controllers/ItemController';
import LayoutViewWorkflowBuilder from './Views/LayoutViewWorkflowBuilder';
import paper from 'paper';
import Radio from 'backbone.radio';
import Rodan from 'rodan';

/**
 * Main WorkflowBuilderGUI class.
 */
class WorkflowBuilderGUI
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor(options)
    {
        this._oldMouseEvent = window.MouseEvent; // FIX: paper.js stupidly redefines
        this._workflow = null;
        Radio.channel('rodan').on(Rodan.RODAN_EVENTS.EVENT__WORKFLOWBUILDER_SELECTED, (options) => this.initialize(options));
    }

    /**
     * Initialize the workspace.
     * The element associated with the canvas ID MUST be available at this time.
     */
    initialize(options)
    {
        this._initializeConfiguration();
        this._workflow = options.workflow;
        this._initializeView();
        this._initializeStateMachine();
        this._initializePaper('canvas-workspace');
        this._initializeRadio();
        this._initializeInterface();
        this._initializeGlobalTool();
        this._initializeGui();
        this._initializeLocalStorage();

        // We have to clear the updater.
        Radio.channel('rodan').request(Rodan.RODAN_EVENTS.REQUEST__UPDATER_CLEAR);
    }

    /**
     * Return workflow.
     */
    getWorkflow()
    {
        return this._workflow;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Initializers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Checks configuration loaded.
     */
    _initializeConfiguration()
    {
        var configuration =
        {
            "USER_AGENT": "rodan-standard",
            "GRID":
            {
                "DIMENSION": 20,
                "LINE_COLOR": "#606060",
                "LINE_WIDTH": 0.5
            },
            "ZOOM_MAX": 3.0,
            "ZOOM_MIN": 1.0,
            "ZOOM_RATE": 0.05,
            "ZOOM_INITIAL": 1.7,
            "WORKFLOWJOB_WIDTH": 20,
            "WORKFLOWJOB_HEIGHT": 22,
            "PORT_WIDTH": 8,
            "PORT_HEIGHT": 8,
            "OUTPUTPORT_COLOR": "#00ff00",
            "INPUTPORT_COLOR_SATISFIED": "#00ff00",
            "INPUTPORT_COLOR_UNSATISFIED": "#ff0000",
            "INPUTPORT_COLOR_CANDIDATE": "#00ff00",
            "STROKE_COLOR": "#000000",
            "FILL_COLOR": "#ccccff",
            "WORKFLOWJOBGROUP_FILL_COLOR": "#8888ff",
            "STROKE_WIDTH": 1,
            "FONT_SIZE": 10,
            "STROKE_COLOR_SELECTED": "#0000ff",
            "STROKE_WIDTH_SELECTED": 2,
            "CONNECTION_CIRCLE_RADIUS": 4,
            "HOVER_TIME": 1000,
            "LOCAL_STORAGE_ITEMS": ['scroll', 'zoom']
        }

        // Check if our entry exists.
        if (!Rodan.Configuration.PLUGINS['rodan-client-wfbgui'])
        {
            Rodan.Configuration.PLUGINS['rodan-client-wfbgui'] = {};
        }

        // Now fill in the gaps.
        var currentConfiguration = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'];
        $.extend(configuration, currentConfiguration);
        Rodan.Configuration.PLUGINS['rodan-client-wfbgui'] = configuration;
    }

    /**
     * Initialize view.
     */
    _initializeView()
    {
        var view = new LayoutViewWorkflowBuilder({model: this.getWorkflow()});
        Radio.channel('rodan').request(Rodan.RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: view});
        this._menuItems = [{label: 'Edit Name/Description', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOW_VIEW, options: {workflow: this.getWorkflow()}},
                           {label: 'Add Job', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_JOBCOLLECTION_VIEW, options: {workflow: this.getWorkflow()}},
                           {label: 'Import Workflow', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOWCOLLECTION_VIEW, options: {workflow: this.getWorkflow()}},
                           {label: 'Run', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_CREATE_WORKFLOWRUN, options: {workflow: this.getWorkflow()}}];
    }

    /**
     * Initialize GUI.
     */
    _initializeGui()
    {
        BaseItem.clearMap();
        this._multipleSelectionKey = Rodan.Environment.getMultipleSelectionKey();
        this._line = null;
        this._zoomRate = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_RATE;
        this._itemController = new ItemController();
        paper.handleMouseEvent = event => this._itemController.handleMouseEvent(event);

        // 
        window.addEventListener('keydown', (e) => {

            if(e.ctrlKey && e.key === '='){
                this._handleRequestZoomIn();
            }

            else if(e.ctrlKey && e.key === '-'){
                this._handleRequestZoomOut();
            }
            else if (e.ctrlKey && e.key == '0'){
                this._handleRequestZoomReset()
            }
        });
    }

    /**
     * Apply settings currently set in localStorage
     * and initialize event listeners for setting items.
     */
    _initializeLocalStorage()
    {
        this._applyLocalStorageSettings();
        this._initializeLocalStorageEvents();
    }

    /**
     * Initialize radio.
     */
    _initializeRadio()
    {
        this.rodanChannel = Radio.channel('rodan');
        this.rodanChannel.on(Rodan.RODAN_EVENTS.EVENT__MODEL_SYNC, options => this._handleEventModelSync(options));

        this.guiChannel = Radio.channel('rodan-client_gui');
        this.guiChannel.on(GUI_EVENTS.EVENT__WORKFLOWBUILDER_GUI_DESTROY, () => this._handleGuiDestroy());
        this.guiChannel.reply(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW, () => this.getWorkflow());
        this.guiChannel.reply(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_ZOOM_IN, () => this._handleRequestZoomIn());
        this.guiChannel.reply(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_ZOOM_OUT, () => this._handleRequestZoomOut());
        this.guiChannel.reply(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_ZOOM_RESET, () => this._handleRequestZoomReset());
    }

    /**
     * Initialize state machine.
     */
    _initializeStateMachine()
    {
        this._STATES = {
            IDLE: 0,
            MOUSE_DOWN: 1,
            MOUSE_UP: 2,
            DRAWING_LINE: 3
        };
        this._firstEntry = false;
        this._setState(this._STATES.IDLE);
    }

    /**
     * Initialize global tool.
     */
    _initializeGlobalTool()
    {
        this._lastToolEvent = null;
        paper.tool = new Tool();
        paper.tool.onMouseMove = event => this._handleEvent(event);
        paper.tool.onMouseUp = event => this._handleEvent(event);
        paper.tool.onMouseDown = event => this._handleEvent(event);
        paper.tool.onKeyDown = event => this._handleEventKeyDown(event);
        paper.tool.onKeyUp = event => this._handleEventKeyUp(event);
    }

    /**
     * Initialize global interface for GUI.
     */
    _initializeInterface()
    {
        var canvas = paper.view.element;
        canvas.oncontextmenu = function() {return false;};
    }

    /**
     * Initialize paper.
     */
    _initializePaper(canvasElementId)
    {
        paper.install(window);
        paper.setup(canvasElementId);
        paper.view.onFrame = (event) => this._handleFrame(event);
<<<<<<< Updated upstream
        paper.view.viewSize = [screen.width + 300, screen.height + 300];
=======
        paper.view.viewSize = [screen.width, screen.height];
>>>>>>> Stashed changes
        this.drawGrid = drawGrid;
        this.drawGrid(Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].GRID, paper);
        this._handleRequestZoomReset();
        
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Events and state machine
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle state. This is frame driven.
     */
    _handleFrame(event)
    {
        BaseItem.updateItems();
    }

    /**
     * Sets state.
     */
    _setState(state)
    {
        this._state = state;
        this._firstEntry = true;
    }

    /**
     * Handle ToolEvent.
     */
    _handleEvent(toolEvent)
    {
        switch (this._state)
        {
            case this._STATES.IDLE:
            {
                this._handleStateIdle(toolEvent);
                break;
            }

            case this._STATES.MOUSE_DOWN:
            {
                this._handleStateMouseDown(toolEvent);
                break;
            }

            case this._STATES.MOUSE_UP:
            {
                this._handleStateMouseUp(toolEvent);
                break;
            }

            case this._STATES.DRAWING_LINE:
            {
                this._handleStateDrawingLine(toolEvent);
                break;
            }

            default:
            {
                console.log('unknown state');
                break;
            }
        }
        this._lastToolEvent = toolEvent;
    }

    /**
     * Handle state idle.
     */
    _handleStateIdle(event)
    {
        if (this._firstEntry)
        {
            this._firstEntry = false;
        }

        if (event.type === 'mousedown')
        {
            this._setState(this._STATES.MOUSE_DOWN);
        }
    }

    /**
     * Handle state mouse down.
     */
    _handleStateMouseDown(event)
    {
        if (this._firstEntry)
        {
            this._firstEntry = false;
            if (!this._itemController.getMouseOverItem())
            {
                this._itemController.clearSelected();

                // If right-click, open context menu.
                if (event.event.button === 2)
                {
                    Radio.channel('rodan').request(Rodan.RODAN_EVENTS.REQUEST__CONTEXTMENU_SHOW,
                                              {items: this._menuItems, top: event.event.pageY, left: event.event.pageX});
                }
            }
        }

        if (event.type === 'mousemove')
        {
            if (this._itemController.getOutputPortItemForConnection() !== null)
            {
                this._setState(this._STATES.DRAWING_LINE);
            }
            else if (this._itemController.getSelectedCount() > 0)
            {
                this._itemController.moveSelectedItems(event.delta);
            }
            else
            {
                var deltaX = (event.event.screenX - this._lastToolEvent.event.screenX) / paper.view.zoom;
                var deltaY = (event.event.screenY - this._lastToolEvent.event.screenY) / paper.view.zoom;
                var delta = new Point(deltaX, deltaY);
                // paper.view.translate(delta);
                this._limitViewInThresholds(); // make sure we stay in bounds!
            }
        }
        else if (event.type === 'mouseup')
        {
            this._setState(this._STATES.MOUSE_UP);
            this._itemController.saveSelectedItemPositions();
        }
    }

    /**
     * Handle state mouse up.
     */
    _handleStateMouseUp(event)
    {
        if (this._firstEntry)
        {
            this._firstEntry = false;
            this._itemController.saveSelectedItemPositions();
        }
        this._setState(this._STATES.IDLE);
    }

    /**
     * Handle state drawing line.
     */
    _handleStateDrawingLine(event)
    {
        if (this._firstEntry)
        {
            this._firstEntry = false;

            // Create line.
            if (this._line === null)
            {
                var item = this._itemController.getOutputPortItemForConnection();
                var startPoint = new Point(item.position.x, item.bounds.bottom);
                this._line = this._itemController.createLineItem(startPoint);
            }

            // Get satisfiable InputPorts.
            var outputPortItem = this._itemController.getOutputPortItemForConnection();
            var candidateInputPortUrls = Radio.channel('rodan').request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_GET_SATISFYING_INPUTPORTS,
                                                                     {workflow: this._workflow, outputport: outputPortItem.getModel()});
            this._itemController.setInputPortCandidates(candidateInputPortUrls);
        }

        if (event.type === 'mousemove')
        {
            // Update end point to one pixel ABOVE the mouse pointer. This ensures that the next click event does NOT register
            // the line as the target.
            var adjustedPoint = new Point(event.point.x, event.point.y - 1);
            this._line.setEndPoint(adjustedPoint);
        }
        else if (event.type === 'mouseup')
        {
            var overItem = this._itemController.getMouseOverItem();
            if (overItem instanceof InputPortItem && !overItem.isSatisfied() && this._itemController.isInputPortCandidate(overItem))
            {
                var outputPortItem = this._itemController.getOutputPortItemForConnection();
                this._itemController.createConnection(outputPortItem, overItem, this.getWorkflow());
            }

            // Reset.
            this._state = this._STATES.IDLE;
            if (this._line)
            {
                this._line.remove();
                this._line.destroy();
                this._line = null;
            }
            this._itemController.clearSelected();
            this._itemController.clearInputPortCandidates();
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Input event handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle event key down.
     */
    _handleEventKeyDown(event)
    {
        if (event.event[this._multipleSelectionKey])
        {
            this._itemController.setSelectingMultiple(true);
        }
    }

    /**
     * Handle event key up.
     */
    _handleEventKeyUp(event)
    {
        if (!event.event[this._multipleSelectionKey])
        {
            this._itemController.setSelectingMultiple(false);
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Radio handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle GUI destroy.
     */
    _handleGuiDestroy()
    {
        BaseItem.clearMap();
        window.MouseEvent = this._oldMouseEvent;
    }

    /**
     * Handle event model sync.
     *
     * This guarantees that the WorkflowBuilder always has the latest version of the Workflow.
     */
    _handleEventModelSync(options)
    {
        if (options.model && options.model.constructor.name === 'Workflow')
        {
            this._workflow = options.model;
        }
    }

    /**
     * Handle zoom in.
     */
    _handleRequestZoomIn()
    {
        const zoom = paper.view.zoom + Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_RATE;
        const zoomToApply = zoom < Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MAX ? zoom : Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MAX;
        paper.view.zoom = zoomToApply;
        this._setLocalStorageItem('zoom', zoomToApply);
    }

    /**
     * Handle zoom out.
     */
    _handleRequestZoomOut()
    {
        var zoom = paper.view.zoom - Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_RATE;
        const zoomToApply = zoom > Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MIN ? zoom : Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MIN;
        paper.view.zoom = zoomToApply;
        this._setLocalStorageItem('zoom', zoomToApply);
        this._limitViewInThresholds(); // make sure we stay in bounds!
    }

    /**
     * Handle zoom reset.
     */
    _handleRequestZoomReset()
    {
        paper.view.zoom = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_INITIAL;
        this._setLocalStorageItem('zoom', paper.view.zoom);
        this._limitViewInThresholds(); // make sure we stay in bounds!
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns thresholds for given view zoom (xLeft, xRight, yTop, yBottom).
     */
    _getThresholds()
    {
        var halfWidth = paper.view.size.width / 2;
        var halfHeight = paper.view.size.height / 2;
        return {xLeft: halfWidth,
                xRight: halfWidth + paper.view.viewSize.width - paper.view.size.width,
                yTop: halfHeight,
                yBottom: halfHeight + paper.view.viewSize.height - paper.view.size.height};
    }

    /**
     * Limits view to the thresholds.
     */
    _limitViewInThresholds()
    {
        var thresholds = this._getThresholds();
        var newPoint = new Point(paper.view.center.x, paper.view.center.y);

        // x
        if (paper.view.center.x < thresholds.xLeft)
        {
            newPoint.x = thresholds.xLeft;
        }
        else if (paper.view.center.x > thresholds.xRight)
        {
            newPoint.x = thresholds.xRight;
        }

        // y
        if (paper.view.center.y < thresholds.yTop)
        {
            newPoint.y = thresholds.yTop;
        }
        else if (paper.view.center.y > thresholds.yBottom)
        {
            newPoint.y = thresholds.yBottom;
        }
        // paper.view.setCenter(newPoint);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Local Storage
///////////////////////////////////////////////////////////////////////////////////////

    /**
     * Initialize localStorage event listeners
     */
    _initializeLocalStorageEvents()
    {
        const canvasWrapper = document.querySelector('#canvas-wrap');

        // scrolling event listeners
        canvasWrapper.addEventListener('scroll', () => {
            this._handleScroll();
        });
    }

    /**
     * Handle user scrolling action.
     * Saves user's scroll position in localStorage.
     */
    _handleScroll() {
        const canvasWrapper = document.querySelector('#canvas-wrap');

        this._setLocalStorageItem({
            itemName: 'scroll',
            itemValue: [canvasWrapper.scrollLeft, canvasWrapper.scrollTop]
        })
    }

    /**
     * Retrieves desired workflow UI settings from localStorage and applies them.
     */
    _applyLocalStorageSettings() 
    {
        const localStorageObject = JSON.parse(window.localStorage.getItem('rodan-data'));

        if (localStorageObject && localStorageObject['workflow-builder-data']) {

            Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].LOCAL_STORAGE_ITEMS.forEach((item) => {
                if (localStorageObject['workflow-builder-data'][item]) {
                    this._applyLocalStorageItem(item);
                }
            });
        }
    }


    /**
     * Applies a particular item saved in localStorage to the workflow builder.
     */
    _applyLocalStorageItem(item) 
    {
        const localStorageObject = JSON.parse(window.localStorage.getItem('rodan-data'));
        const canvasWrapper = document.querySelector('#canvas-wrap');

        switch(item) {
            case 'scroll':
                const xPosition = localStorageObject['workflow-builder-data']['scroll'][0];
                const yPosition = localStorageObject['workflow-builder-data']['scroll'][1];
                canvasWrapper.scrollTo(xPosition, yPosition);
                break;
            
            case 'zoom':
                const zoom = localStorageObject['workflow-builder-data']['zoom'];
                let zoomToApply = zoom > Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MIN ? zoom : Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MIN;
                zoom < Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MAX ? zoom : Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MAX;
                this._limitViewInThresholds(); // make sure we stay in bounds!

                paper.view.zoom = zoomToApply;
                break;
        }
    }


    /**
     * Sets a workflfow-builder-related localStorage item
     */
    _setLocalStorageItem(name, value) 
    {
        let localStorageObject = JSON.parse(window.localStorage.getItem('rodan-data'));
        if (!localStorageObject) localStorageObject = {};
        if (!localStorageObject['workflow-builder-data']) localStorageObject['workflow-builder-data'] = {};

        localStorageObject['workflow-builder-data'][name] = value;
        window.localStorage.setItem('rodan-data', JSON.stringify(localStorageObject));
    }
}

var workspace = new WorkflowBuilderGUI();

export {workspace as default};
