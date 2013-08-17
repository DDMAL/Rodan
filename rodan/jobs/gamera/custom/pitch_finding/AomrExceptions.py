""" This file defines some exceptions for the AOMR Toolkit. """


class AomrError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class AomrFilePathNotSetError(AomrError):
    pass


class AomrStaffFinderNotFoundError(AomrError):
    pass


class AomrUnableToFindStavesError(AomrError):
    pass


# AOMR MEI errors
class AomrMeiFormNotFoundError(AomrError):
    pass


class AomrMeiPitchNotFoundError(AomrError):
    pass


class AomrMeiNoteIntervalMismatchError(AomrError):
    pass


# AOMR Aruspix Errors
class AomrNotAnAruspixFileError(AomrError):
    pass


class AomrAruspixPackageError(AomrError):
    pass

