# pyright: reportInvalidStringEscapeSequence=false

import os
import subprocess

from ..logger.logger_core import logger

LOG_TAG = "shell_utils"

def run_shell_command(log_tag, command_array, capture, stdout=None, stderr=None,
    cwd=None, env=None, redirect_stderrr_to_stdout=False, timeout=None):
    "Run a shell command and get stdout, stderr and exit code."
    try:
        # If command_array is not set or of type list
        if not command_array or not isinstance(command_array, list):
            logger.error(LOG_TAG, "The command_array passed to run_shell_command function must be set and of type list")
            return (1, None, None)

        if capture:
            stderr = subprocess.STDOUT if redirect_stderrr_to_stdout else stderr

            if not stdout:
                stdout = subprocess.PIPE
            if not stderr:
                stderr = subprocess.PIPE

            process = subprocess.Popen(
                command_array, cwd=cwd, env=env, stdout=stdout, stderr=stderr, universal_newlines=True
            )
            stdout, stderr = process.communicate(timeout=timeout)
            return_value = process.returncode
            return (return_value, stdout, stderr)
        else:
            raise NotImplementedError("capture=False not supported")


    except subprocess.TimeoutExpired as err:
        logger.error(log_tag, "The " + str(command_array or [""]) + " shell command failed to complete even after " +
            str(timeout or "") + "s")
        return (1, err.stdout, err.stderr)
    except Exception as err:
        logger.error(log_tag, "Running " + str(command_array or [""]) + " shell command failed with err:\n" + str(err))
        return (1, None, None)
    finally:
        if not capture:
            close(stdout)
            close(stderr)

def close(obj):
    if obj and not isinstance(obj, int) and hasattr(obj, 'close') and callable(obj.close):
        obj.close()

class EnvironProxy:
    "Get str key value from dict_obj if it exists, otherwise default."

    __slots__ = ('_original_environ',)

    def __init__(self):
        self._original_environ = os.environ

    def __enter__(self):
        self._original_environ = os.environ
        os.environ = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.environ = self._original_environ

    def __getitem__(self, item):
        try:
            return self._original_environ[item]
        except KeyError:
            return ''

def expand_env_vars(path):
    # pylint: disable=anomalous-backslash-in-string
    """
    Expand environmental variables in path like bash does.

    - Substrings of the form `$NAME` or `${NAME}` are replaced by the value
      of the environmental variable name.
    - Substrings of the form `\$NAME` that have escaped `$` character
      are replaced with the literal value `$NAME` without expansion.
    - References to non-existing environmental variables are replaced
      with an empty string.

    Credit: https://stackoverflow.com/a/46879930
    """

    if not path:
        return path

    replacer = '\0'  # NUL shouldn't be in a file path anyways.
    while replacer in path:
        replacer *= 2

    path = path.replace('\\$', replacer)

    with EnvironProxy():
        return os.path.expandvars(path).replace(replacer, '$')
