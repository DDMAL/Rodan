import BaseModel from 'js/Models/BaseModel';
import Configuration from 'js/Configuration';
import Environment from 'js/Shared/Environment';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import WorkflowBuilderGUI from 'js/WorkflowBuilderGUI';

const Rodan =
{
	BaseModel: BaseModel,
	Configuration: Configuration,
	Environment: Environment,
	RODAN_EVENTS: RODAN_EVENTS,
	WorkflowBuilderGUI: WorkflowBuilderGUI
};

export default Rodan;
