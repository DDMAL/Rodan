import os


def create_dirs(full_path):
    try:
        os.makedirs(os.path.dirname(full_path))
    except OSError:
        pass
