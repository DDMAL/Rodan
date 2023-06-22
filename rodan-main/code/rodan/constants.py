from django.utils.translation import gettext_lazy as _
from djoser.constants import Messages as DjoserMessages


class task_status:
    """
    Descriptive backend task processing codes, for readability.
    """

    SCHEDULED = 0
    PROCESSING = 1
    FINISHED = 4
    FAILED = -1
    CANCELLED = 9

    EXPIRED = 8  # only for ResultsPackage
    WAITING_FOR_INPUT = 2  # only for RunJob
    RETRYING = 11  # only for WorkflowRun
    REQUEST_PROCESSING = 21  # only for WorkflowRun
    REQUEST_CANCELLING = 29  # only for WorkflowRun
    REQUEST_RETRYING = 31  # only for WorkflowRun

    NOT_APPLICABLE = None

class Messages(DjoserMessages):
    """
    Custom messages for Djoser.
    """
    USERNAME_NOT_FOUND = _("User with given username does not exist.")