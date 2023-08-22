import $ from 'jquery';
import { drawGrid } from './Utilities/PaperUtilities';
import BaseItem from './Items/BaseItem';
import GUI_EVENTS from './Shared/Events';
import InputPortItem from './Items/InputPortItem';
import ItemController from './Controllers/ItemController';
import LayoutViewWorkflowBuilder from './Views/LayoutViewWorkflowBuilder';
import paper from 'paper';
import Radio from 'backbone.radio';
import Rodan from 'rodan';
import _ from 'underscore';

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
        this._event = window.Event; // paper.js stupidly redefines Event and crashes the SAVE button in resources
        this._workflow = null;
        this._rightClickPosition = null;
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
        this._applyLocalStorageSettings();

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
                "LINE_COLOR": "#9e9e9ec7",
                "LINE_WIDTH": 0.5
            },
            "DATABASE_COORDINATES_MULTIPLIER": 1500, // Legacy workflows stored coordinates in the database differently. This is to maintain backwards compatibility.
            "WORKFLOW_PADDING": 50,
            "ZOOM_MAX": 3.0,
            "ZOOM_MIN": 1.0,
            "ZOOM_RATE": 0.1,
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
            "CONNECTION_PADDING": 5,
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
        this._menuItems = [
            { label: 'Edit Name/Description', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOW_VIEW, options: { workflow: this.getWorkflow() } },
            { label: 'Add Job', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_JOBCOLLECTION_VIEW, options: { workflow: this.getWorkflow() } },
            { label: 'Import Workflow', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOWCOLLECTION_VIEW, options: { workflow: this.getWorkflow() } },
            { label: 'Clear Assigned Resources', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_CLEAR_RESOURCEASSIGNMENTS, options: { workflow: this.getWorkflow() } },
            { label: 'Run', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_CREATE_WORKFLOWRUN, options: { workflow: this.getWorkflow() } }
        ];
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
        this._itemController = new ItemController({ workflow: this._workflow });
        paper.handleMouseEvent = event => this._itemController.handleMouseEvent(event);

        window.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === '=') {
                e.preventDefault();
                this._handleRequestZoomIn();
                e.preventDefault();
            } else if (e.ctrlKey && e.key === '-') {
                e.preventDefault();
                this._handleRequestZoomOut();
            } else if (e.ctrlKey && e.key === '0') {
                e.preventDefault();
                this._handleRequestZoomReset()
            }
        });

        const canvasWrapper = document.querySelector('#canvas-wrap');
        canvasWrapper.addEventListener('wheel', (event) => this._handleScroll(event));
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
        this.guiChannel.reply(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GET_NEW_JOB_POSITION, () => this._handleGetNewJobPosition());
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
        new paper.Layer({ name: 'connections' });
        new paper.Layer({ name: 'default' });
        paper.view.onFrame = (event) => this._handleFrame(event);
        this.drawGrid = drawGrid;
        this.drawGrid(Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].GRID, paper);
        
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Events and state machine
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle state. This is frame driven.
     */
    _handleFrame(event)
    {
        this.drawGrid(Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].GRID, paper);
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
                    this._rightClickPosition = event.point;
                    Radio.channel('rodan').request(Rodan.RODAN_EVENTS.REQUEST__CONTEXTMENU_SHOW, {items: this._menuItems, top: event.event.pageY, left: event.event.pageX});
                } else {
                    this._rightClickPosition = null;
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
                paper.view.translate(delta);
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
            this._saveToLocalStorage(); // Save the current zoom and position when the user stops dragging
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

    /**
     * Handle zooming in and out with the scroll-wheel.
     */
    _handleScroll(event)
    {
        const oldZoom = paper.view.zoom;
        const oldCenter = paper.view.center;
        
        const mousePosition = paper.view.viewToProject(new Point(event.offsetX, event.offsetY));

        const zoom = oldZoom * (1 + (event.deltaY < 0 ? 1 : -1) * Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_RATE);
        const newZoom = this._clampZoom(zoom);

        const offset = mousePosition.subtract(mousePosition.subtract(oldCenter).multiply(oldZoom / newZoom)).subtract(oldCenter);

        paper.view.zoom = newZoom;
        paper.view.center = paper.view.center.add(offset);
        this._saveToLocalStorage();
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
        window.Event = this._event;
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
        paper.view.zoom = this._clampZoom(zoom);
        this._saveToLocalStorage();
    }

    /**
     * Handle zoom out.
     */
    _handleRequestZoomOut()
    {
        var zoom = paper.view.zoom - Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_RATE;
        paper.view.zoom = this._clampZoom(zoom);
        this._saveToLocalStorage();
    }

    /**
     * Handle zoom reset.
     */
    _handleRequestZoomReset()
    {
        const boundingBox = this._getWorkflowBoundingBox();
        if (boundingBox) {
            const workflowCenter = this._getBoundingBoxCenter(boundingBox);
            paper.view.center = workflowCenter;
            const width = boundingBox.bottomRight.x - boundingBox.topLeft.x + 2 * Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].WORKFLOW_PADDING;
            const height = boundingBox.bottomRight.y - boundingBox.topLeft.y + 2 * Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].WORKFLOW_PADDING;
            const viewWidth = paper.view.viewSize.width;
            const viewHeight = paper.view.viewSize.height;
            const zoom = Math.min(viewWidth / width, viewHeight / height);
            paper.view.zoom = this._clampZoom(zoom);
        } else {
            paper.view.zoom = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_INITIAL;
        }
        this._saveToLocalStorage();
    }
    
    /**
     * Clamps the zoom to the min and max zoom values.
     * @param {number} zoom - The zoom value to clamp.
     * @returns {number} The clamped zoom value.
    */
    _clampZoom(zoom)
    {
        return Math.min(Math.max(zoom, Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MIN), Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].ZOOM_MAX);
    }

    /**
     * Calculates the bounding box given a list of workflow jobs.
     * @param {WorkflowJob[]} workflow_jobs - The workflow jobs to calculate the bounding box for.
     * @returns the bounding box of the workflow jobs or null if no workflow_jobs are provided.
     */
    _getBoundingBox(workflow_jobs)
    {
        if (!workflow_jobs) return null;
        let minX, maxX, minY, maxY;
        workflow_jobs.forEach(job => {
            const { x, y } = job.get('appearance');
            minX = minX === undefined || x < minX ? x : minX;
            maxX = maxX === undefined || x > maxX ? x : maxX;
            minY = minY === undefined || y < minY ? y : minY;
            maxY = maxY === undefined || y > maxY ? y : maxY;
        });
        const topLeft = { x: minX, y: minY };
        const bottomRight = { x: maxX, y: maxY };
        return { topLeft, bottomRight };
    }
    
    /**
     * Calculate the bounding box of the workflow in paper.js project coordinates.
     * @returns {{topLeft: {x: number, y: number}, bottomRight: {x: number, y: number}} | null} The bounds of the workflow in paper.js project coordinates or null if there are no jobs.
     */
    _getWorkflowBoundingBox()
    {
        if (this._workflow && this._workflow.get('workflow_jobs').length > 0) {
            const boundingBox = this._getBoundingBox(this._workflow.get('workflow_jobs'));
            const topLeft = BaseItem.appearanceToProject(boundingBox.topLeft);
            const bottomRight = BaseItem.appearanceToProject(boundingBox.bottomRight);
            return { topLeft, bottomRight };
        }
        return null;
    }

    /**
     * Calculates the center of a bounding box.
     * @param {{topLeft: {x: number, y: number}, bottomRight: {x: number, y: number}} | null} boundingBox The bounding box.
     * @return {{x: number, y: number} | null} The center of the bounding box or null if no bounding box is provided.
    */
    _getBoundingBoxCenter(boundingBox)
    {
        return boundingBox ? { x: (boundingBox.topLeft.x + boundingBox.bottomRight.x) / 2, y: (boundingBox.topLeft.y + boundingBox.bottomRight.y) / 2 } : null;
    }

    /**
     * Returns the database coordinates to create a new job. 
     * If the user right-clicked, use that position. Otherwise, use the center of the view.
     * @returns {{x: number, y: number}} The database coordinates to create a new job.
     */
    _handleGetNewJobPosition()
    {
        const position = this._rightClickPosition == null ? paper.view.center : this._rightClickPosition;
        return BaseItem.projectToAppearance(position);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Local Storage
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Saves the current zoom and position to `localStorage`.
    */
    _saveToLocalStorage()
    {
        this._setLocalStorageData({ zoom: paper.view.zoom, center: { x: paper.view.center.x, y: paper.view.center.y }});
    }

    /**
     * Serializes and sets the workflow builder data in `localStorage`.
     * @param {object} data - The data to store.
    */
    _setLocalStorageData(data)
    {
        localStorage.setItem(`workflow-builder-data#${this._workflow.id}`, JSON.stringify(data));
    }

    /**
     * Retrieves desired workflow UI settings from `localStorage` and applies them.
     */
    _applyLocalStorageSettings()
    {
        const data = localStorage.getItem(`workflow-builder-data#${this._workflow.id}`);
        if (!data) {
            return;
        }

        const { zoom, center } = JSON.parse(data);
        if (zoom) {
            paper.view.zoom = this._clampZoom(zoom);
        }
        if (center) {
            paper.view.center = new Point(center.x, center.y);
        }
    }
}

var workspace = new WorkflowBuilderGUI();

export {workspace as default};
