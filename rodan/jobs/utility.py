import os

def create_result_output_dirs(full_output_path):
    output_dir = os.path.dirname(full_output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)