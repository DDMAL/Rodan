import subprocess
import shutil
import os

from tempfile import mkstemp
from shutil import move
from os import remove, close


def execute(cmdArray, workingDir):
    stdout = ''
    stderr = ''
    try:
        try:
            process = subprocess.Popen(cmdArray, cwd=workingDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       bufsize=1)
        except OSError:
            return [False, '', 'ERROR : command(' + ' '.join(cmdArray) + ') could not get executed!']

        for line in iter(process.stdout.readline, b''):
            try:
                echoLine = line.decode("utf-8")
            except:
                echoLine = str(line)
            stdout += echoLine

        for line in iter(process.stderr.readline, b''):
            try:
                echoLine = line.decode("utf-8")
            except:
                echoLine = str(line)
            stderr += echoLine

    except (KeyboardInterrupt, SystemExit) as err:
        return [False, '', str(err)]

    process.stdout.close()

    returnCode = process.wait()
    if returnCode != 0 or stderr != '':
        return [False, stdout, stderr]
    else:
        return [True, stdout, stderr]


def copy_when_exists(src, dst):
    if dst is not None and os.path.isfile(src):
        shutil.copyfile(src, dst)


def parse_convert_from_config_file(config_file_path):
    convert_csv = False
    convert_arff = False
    with open(config_file_path) as config_file:
        for line in config_file:
            strip_line = line.strip()
            if strip_line == "convert_to_csv=true":
                convert_csv = True
            elif strip_line == "convert_to_arff=true":
                convert_arff = True
    return convert_csv, convert_arff


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    close(fh)
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)
