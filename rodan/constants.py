class task_status:
    """
    Descriptive backend task processing codes, for readability.
    """

    SCHEDULED = 0
    PROCESSING = 1
    FINISHED = 4
    FAILED = -1
    CANCELLED = 9

    EXPIRED = 8

    NOT_APPLICABLE = None
