from django.db import models
from rodan.models import OutputPortType
import uuid


class Output(models.Model):
    """
    An `Output` is the result of performing a job on the specific input `Resource`s.
    There must be one `Output` for each `OutputPort` in the `RunJob`'s associated
    `WorkflowJob`.

    **Fields**

    - `uuid`
    - `output_port` -- a reference to an `OutputPort`. It should be set to None when the
      original `OutputPort` is deleted.
    - `output_port_type_name` -- a string containing the name of the `OutputPortType`.
    - `run_job` -- a reference to the `RunJob` associated with this `Output`.
    - `resource` -- the precise `Resource` that is output by the `RunJob` at
      the above-referenced `OutputPort`.
    - `resource_list` -- the precise `ResourceList` that is output by the `RunJob` at
      the above-referenced `OutputPort`.

    **Properties**

    - `output_port_type` -- the corresponding `OutputPortType` object.
    """

    class Meta:
        app_label = "rodan"
        permissions = (("view_output", "View Output"),)

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    output_port = models.ForeignKey(
        "rodan.OutputPort",
        related_name="outputs",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    output_port_type_name = models.CharField(max_length=255, db_index=True)
    run_job = models.ForeignKey(
        "rodan.RunJob", related_name="outputs", on_delete=models.CASCADE, db_index=True
    )
    resource = models.ForeignKey(
        "rodan.Resource",
        related_name="outputs",
        on_delete=models.PROTECT,
        db_index=True,
        null=True,
        blank=True,
    )
    resource_list = models.ForeignKey(
        "rodan.ResourceList",
        related_name="outputs",
        on_delete=models.PROTECT,
        db_index=True,
        null=True,
        blank=True,
    )

    def __str__(self):
        return "<Output {0}>".format(str(self.uuid))

    @property
    def output_port_type(self):
        try:
            return OutputPortType.objects.get(
                job__name=self.run_job.job_name, name=self.output_port_type_name
            )
        except OutputPortType.DoesNotExist:
            return None
