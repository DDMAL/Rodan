from django.db import models
from uuidfield import UUIDField


class InputPort(models.Model):
    class Meta:
        app_label = 'rodan'

    """
        An InputPort is simply a duple consisting of an optional label unique to the other InputPorts of
        the WorkflowJob and a reference to an InputPortType of the associated Job.

            * label (string): an optional name unique to the other InputPorts in the WorkflowJob (really only
              for the user) - the default label of an input_port is the name of its associated InputPortType
            * InputPortType (ref): reference to associated InputPortType

        Where an InputPortType defined what a Job CAN take, an input_port defines what a WorkflowJob
        WILL take when it is executed.

        Note: the number of InputPorts for a particular InputPortType must be within the associated
        InputPortType.minimum and InputPortType.maximum values.
    """

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_job = models.ForeignKey('rodan.WorkflowJob', null=True, blank=True)
    input_port_type = models.ForeignKey('rodan.InputPortType')
    label = models.CharField(max_length=255, null=True, blank=True, default=input_port_type.name)
