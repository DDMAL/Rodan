class task_status:
    """
    Descriptive backend task processing codes, for readability.
    """

    SCHEDULED = 0
    PROCESSING = 1
    FINISHED = 4
    FAILED = -1
    CANCELLED = 9

    EXPIRED = 8    # only for ResultsPackage
    WAITING_FOR_INPUT = 2    # only for RunJob
    RETRYING = 11  # only for WorkflowRun

    NOT_APPLICABLE = None
