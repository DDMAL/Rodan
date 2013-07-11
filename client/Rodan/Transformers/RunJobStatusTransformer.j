@import "../Models/RunJob.j"

@global RUNJOB_STATUS_FAILED
@global RUNJOB_STATUS_NOTRUNNING
@global RUNJOB_STATUS_RUNNING
@global RUNJOB_STATUS_WAITINGFORINPUT
@global RUNJOB_STATUS_RUNONCEWAITING
@global RUNJOB_STATUS_HASFINISHED
@global RUNJOB_STATUS_CANCELLED

@implementation RunJobStatusTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return YES;
}

- (id)transformedValue:(id)value
{
    return [RunJobStatusTransformer mapStringToValue:value];
}

+ (id)mapStringToValue:(id)value
{
    switch (value)
    {
        case RUNJOB_STATUS_FAILED:
            return "Failed";
            break

        case RUNJOB_STATUS_NOTRUNNING:
            return "Not running";
            break

        case RUNJOB_STATUS_RUNNING:
            return "Running";
            break;

        case RUNJOB_STATUS_WAITINGFORINPUT:
            return "Waiting for input";
            break;

        case RUNJOB_STATUS_RUNONCEWAITING:
            return "Run once waiting";
            break;

        case RUNJOB_STATUS_HASFINISHED:
            return "Has finished";
            break;

        case RUNJOB_STATUS_CANCELLED:
            return "Cancelled";
            break;

        default:
            return "Unknown";
            break;
    }
}
@end
