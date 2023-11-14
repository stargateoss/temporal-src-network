import errno
import os
import re
import shutil
import stat
import sys

from . import file_constants
from . import file_types
from .file_types import FileTypes
from . import file_utils_errno
from ..logger.logger_core import logger


LOG_TAG = "file_utils"

FILESYSTEM_ENCODING = None



def is_path_set(label, path):
    """
    Check if `path` is not `None` or empty and is of type `str`.

    @param label The label for `path`.
    @param path The `path` to check.
    @return Returns an error if `path` is not set, otherwise `None`.
    """

    if path is None:
        return file_utils_errno.ERRNO_NULL_PATH.format(label)

    if not isinstance(path, str):
        return file_utils_errno.ERRNO_NON_STRING_PATH.format(label, "is_path_set")

    if not path:
        return file_utils_errno.ERRNO_EMPTY_PATH.format(label)

    return None

def is_path_valid(label, path,
                  ensure_no_null_bytes=True,
                  ensure_not_too_long=True,
                  ensure_component_not_too_long=True,
                  ensure_absolute=True,
                  ensure_canonical=False):
    """
    Check if `path` is valid.

    The `path` is considered invalid if:
    - If path is `None` or empty.
    - If path contains null bytes.
    - If any path component length is `> 255` ({@link file_constants#NAME_MAX}).
    - If `ensure_not_too_long` is `True` and path length is `>= 4096` {@link file_constants#PATH_MAX}.
    - If `ensure_absolute` is `True` and path is not an absolute path.
    - If `ensure_canonical` is `True` and path is not a canonical path. Canonicalization is not
      done and its only checked if path can be considered a result of canonicalization. The
      `ensureAbsolute` must be `True` if it should also be checked if path is absolute.

    See also
    - {@link #path_contains_null_byte()}.
    - {@link #is_path_too_long()}.
    - {@link #is_path_component_too_long()}.
    - {@link #is_path_absolute()}.
    - {@link #is_path_canonical()}.

    @param label The label for `path`.
    @param path The `path` to check.
    @param ensure_no_null_bytes[`True`] Ensure that the `path` does not contain any null bytes.
    @param ensure_not_too_long[`True`] Ensure that the `path` is not too long.
    @param ensure_component_not_too_long[`True`] Ensure that any `path` component is not too long.
    @param ensure_absolute[`True`] Ensure that the `path` is an absolute path.
    @param ensure_canonical[`False`] Ensure that the `path` is a canonical path.
    @return Returns an error if `path` is invalid, otherwise `None`.
    """

    if path is None:
        return file_utils_errno.ERRNO_NULL_PATH.format(label)

    if not isinstance(path, str):
        return file_utils_errno.ERRNO_NON_STRING_PATH.format(label, "is_path_valid")

    if not path:
        return file_utils_errno.ERRNO_EMPTY_PATH.format(label)

    if ensure_no_null_bytes:
        error = path_contains_null_byte(label, path)
        if error is not None:
            return error

    if ensure_not_too_long:
        error = is_path_too_long(label, path)
        if error is not None:
            return error

    if ensure_component_not_too_long:
        error = is_path_component_too_long(label, path)
        if error is not None:
            return error

    if ensure_canonical:
        return is_path_canonical(label, path, ensure_absolute=ensure_absolute)
    elif ensure_absolute:
        if not os.path.isabs(path):
            return file_utils_errno.ERRNO_NON_ABSOLUTE_PATH.format(label, path)

    return None

def path_contains_null_byte(label, path):
    """
    Check if `path` contains null bytes.

    @param label The label for `path`.
    @param path The `path` to check.
    @return Returns an error if `path` contains null bytes, otherwise `None`.
    """
    if path is None:
        return None
    elif not isinstance(path, str):
        return file_utils_errno.ERRNO_NON_STRING_PATH.format(label, "path_contains_null_byte")
    elif not path:
        return None

    if str(b'\x00') in path:
        return file_utils_errno.ERRNO_NULL_BYTE_CONTAINING_PATH.format(label, path)
    else:
        return None

def is_path_too_long(label, path):
    """
    Check if `path` length is `>= 4096` {@link file_constants#PATH_MAX}.

    @param label The label for `path`.
    @param path The `path` to check.
    @return Returns an error if `path` length is too long, otherwise `None`.
    """

    if path is None:
        return None
    elif not isinstance(path, str):
        return file_utils_errno.ERRNO_NON_STRING_PATH.format(label, "is_path_too_long")
    elif not path:
        return None

    path_bytes = bytes(path, get_filesystem_encoding())
    path_length = len(path_bytes)
    if path_length >= file_constants.PATH_MAX:
        return file_utils_errno.ERRNO_PATH_TOO_LONG.format(label, path_length, path)
    else:
        return None

def is_path_component_too_long(label, path):
    """
    Check if any `path` component length is `> 255` ({@link file_constants#NAME_MAX}).

    @param label The label for `path`.
    @param path The `path` to check.
    @return Returns an error if any `path` component length is too long, otherwise `None`.
    """

    if path is None:
        return None
    elif not isinstance(path, str):
        return file_utils_errno.ERRNO_NON_STRING_PATH.format(label, "is_path_component_too_long")
    elif not path:
        return None

    if path.startswith(os.sep):
        i = 0
    else:
        i = 1
    encoding = get_filesystem_encoding()
    for component in path.split(os.sep):
        component_bytes = bytes(component, encoding)
        component_length = len(component_bytes)
        if component_length > file_constants.NAME_MAX:
            return file_utils_errno.ERRNO_PATH_COMPONENT_TOO_LONG.format(
                label, component_length, i, component, path)
        i += 1

    return None

def is_path_absolute(label, path):
    """
    Check if `path` is an absolute path as per {@link #isPathAbsolute(String)}.

    @param label The label for `path`.
    @param path The `path` to check.
    @return Returns an error if `path` is not an absolute path, otherwise `None`.
    """

    if path is not None and not isinstance(path, str):
        return file_utils_errno.ERRNO_NON_STRING_PATH.format(label, "is_path_absolute")

    if not path or not os.path.isabs(path):
        return file_utils_errno.ERRNO_NON_ABSOLUTE_PATH.format(label, path)
    else:
        return None

def is_path_canonical(label, path, ensure_absolute=True):
    """
    Check if `path` is a canonical path. Canonicalization is not done and its only checked if
    path can be considered a result of canonicalization.

    The `path` is considered invalid if:
    - If path is `None` or empty.
    - If path contains single dots `.` path components.
    - If path contains double dots `..` path components.
    - If path contains consecutive duplicate path separators `/`.
    - If path contains trailing path separator `/`. unless `rootfs`.
    - If `ensure_absolute` is `True` and path is not an absolute path.

    See also
    - {@link #is_path_valid()}.

    @param label The label for `path`.
    @param path The `path` to check.
    @param ensure_absolute[`True`] Ensure path is absolute. Mainly for
                           internal use if absolute path check will be made
                           elsewhere since canonical path must always be
                           absolute or for checking relative paths.
    @return Returns an error if `path` is not an canonical path, otherwise `None`.
    """

    if path is not None and not isinstance(path, str):
        return file_utils_errno.ERRNO_NON_STRING_PATH.format(label, "is_path_canonical")

    s = os.sep
    if (
            not path or
            (s + ".." + s) in (s + path + s) or # "/../"
            (s + "." + s) in (s + path + s) or # "/./"
            (s + s) in path or # "//"
            (path != s and path[-1] == s) or
            (ensure_absolute and not os.path.isabs(path))
    ):
        return file_utils_errno.ERRNO_NON_CANONICAL_PATH.format(label, path)
    else:
        return None






def get_filesystem_root():
    """
    This will return `/` on unix systems and cwd drive root like `C:\\`
    on Windows as `os.path.abspath(path)` returns `normpath(join(os.getcwd(), path))`.
    Windows does not have a single root and also has server share paths
    starting with `\\`.
    - https://docs.python.org/3/library/os.path.html#os.path.abspath
    """
    return os.path.abspath(os.sep)

def get_filesystem_encoding():
    "Get the global variable FILESYSTEM_ENCODING."

    global FILESYSTEM_ENCODING

    if FILESYSTEM_ENCODING:
        return FILESYSTEM_ENCODING

    # Get filesystem encoding
    # It is the locale encoding on UNIX systems, will return None for python < 3.2
    FILESYSTEM_ENCODING = sys.getfilesystemencoding()

    # If FILESYSTEM_ENCODING is not set, then set it to "ascii" (LANG=C)
    # Python defaults to the same if not set for >= 3.2
    if not FILESYSTEM_ENCODING:
        logger.warn(LOG_TAG, "Force setting filesystem encoding to 'ascii' since its not set")
        FILESYSTEM_ENCODING = "ascii"

    return FILESYSTEM_ENCODING





def get_file_type(log_tag, path, follow_links):
    "Returns the one of the FileTypes for file at path. Will also return FileTypes.NO_EXIST if failed to find file type."

    try:
        if follow_links:
            mode = os.stat(path).st_mode
        else:
            mode = os.lstat(path).st_mode
    except OSError as err:
        if err.errno != errno.ENOENT:
            logger.error(log_tag, "Getting file type of file at path \"" + path + "\"" +
                         " failed with err:\n" + str(err))
        return FileTypes.NO_EXIST

    if stat.S_ISREG(mode):
        return FileTypes.REGULAR
    elif stat.S_ISDIR(mode):
        return FileTypes.DIRECTORY
    elif stat.S_ISLNK(mode):
        return FileTypes.SYMLINK
    elif stat.S_ISSOCK(mode):
        return FileTypes.SOCKET
    elif stat.S_ISCHR(mode):
        return FileTypes.CHARACTER
    elif stat.S_ISFIFO(mode):
        return FileTypes.FIFO
    elif stat.S_ISBLK(mode):
        return FileTypes.BLOCK
    elif stat.S_ISDOOR(mode):
        return FileTypes.DOOR
    elif stat.S_ISPORT(mode):
        return FileTypes.PORT
    elif stat.S_ISWHT(mode):
        return FileTypes.WHITEOUT
    else:
        return FileTypes.UNKNOWN






def normalize_path(path):
    "Returns normalized path."

    if os.sep == '/':
        # Normalize path first, then replace multiple "/" with single.
        # This is necessary since python does not remove "//" from the
        # start to maintain compatibility with windows
        return re.sub("[/]+", "/", os.path.normpath(str(path)))
    else:
        return os.path.normpath(str(path))





def is_path_in_dir_paths(path, dir_paths, ensure_under, canonicalize_path=True, canonicalize_dir_path=True):
    """
    Wrapper for {@link #get_if_path_in_dir_path()} that returns
    `true` if path is in one of the `dir_paths`, otherwise returns `false`.

    TODO: Update to be consistent with portal-io-file
    """

    if not dir_paths or not isinstance(dir_paths, list):
        return False

    for dir_path in dir_paths:
        if get_if_path_in_dir_path(path, dir_path, ensure_under,
                                   canonicalize_path=canonicalize_path,
                                   canonicalize_dir_path=canonicalize_dir_path) is not None:
            return True

    return False

def is_path_in_dir_path(path, dir_path, ensure_under, canonicalize_path=True, canonicalize_dir_path=True):
    """
    Wrapper for {@link #get_if_path_in_dir_path()} that returns `True` if
    path is in `dir_path`, otherwise returns `False`.
    """

    return get_if_path_in_dir_path(path, dir_path, ensure_under,
                                   canonicalize_path=canonicalize_path,
                                   canonicalize_dir_path=canonicalize_dir_path) is not None

def get_if_path_in_dir_path(path, dir_path, ensure_under, canonicalize_path=True, canonicalize_dir_path=True):
    """
    Check whether a path is in `dir_path`.

    @param path The `path` to check.
    @param dir_path The `directory path` to check in. This must be an absolute path.
    @param ensure_under If set to `True`, then it will be ensured that `path` is under the directory
                        and does not equal it. If set to `False`, it can either equal the directory
                        path or be under it.
    @param canonicalize_path[`True`] Set to `True` if `path` should be canonicalized, otherwise it will
                            be used as is.
    @param canonicalize_dir_path[`True`] Set to `True` if `dir_path` should be canonicalized in case it
                               may be a symlink, otherwise `dir_path` is just normalized.
    @return Returns the canonicalized or normalized `dir_path` if `path` is found in it, otherwise
    returns `None`.
    """

    if is_path_absolute("path", path) is not None or is_path_absolute("directory path", path) is not None:
        return False

    sep = os.sep

    if canonicalize_path:
        path = os.path.realpath(path)
    else:
        path = normalize_path(path)

    if canonicalize_dir_path:
        dir_path = os.path.realpath(dir_path)
    else:
        dir_path = normalize_path(dir_path)

    # If root "/", preserve it as is, otherwise append "/" to dir_path
    dir_sub_path = sep if dir_path == sep else dir_path + sep;
    if ensure_under:
        is_in_dir = path != dir_path and path.startswith(dir_sub_path)
    else:
        is_in_dir = path == dir_path or path.startswith(dir_sub_path)

    return dir_path if is_in_dir else None





def create_parent_directory_file(log_tag, label, file_path):
    """
    Create parent directory of file at path.

    This function is a wrapper for {@link #create_dir_file()}.

    @param label The optional label for the parent directory file. This can optionally be `None`.
    @param file_path The path for file whose parent needs to be created.
    @return Returns the error if parent path is not a directory file or failed to create it,
    otherwise `None`.
    """

    label_temp = "" if not label else str(label) + " "

    error = is_path_set(label_temp + "directory path", file_path)
    if error is not None:
        return error

    file_parent_path = get_dirname(file_path)

    if file_parent_path:
        return create_dir_file(log_tag, label, file_parent_path)
    else:
        return None

def create_dir_file(log_tag, label, file_path):
    """
    Create directory at path.

    @param label The optional label for the directory file. This can optionally be `None`.
    @param file_path The path for directory file to create.
    @return Returns the error if path is not a directory file or failed to create it,
    otherwise `None`.
    """

    label = "" if not label else str(label) + " "

    error = is_path_valid(label + "directory path", file_path)
    if error is not None:
        return error

    file_type = get_file_type(log_tag, file_path, False)

    # If file exists but not a directory file
    if file_type not in [FileTypes.NO_EXIST, FileTypes.DIRECTORY]:
        return file_utils_errno.ERRNO_NON_DIRECTORY_FILE_FOUND.format(
            label + "directory", file_path, file_type)

    if file_type == FileTypes.NO_EXIST:
        try:
            logger.verbose(log_tag, "Creating " + label + "directory file at path \"" + file_path + "\"")
            os.makedirs(file_path)
        except OSError as err:
            return file_utils_errno.ERRNO_CREATING_FILE_FAILED_WITH_EXCEPTION.format(label + "directory file", file_path, str(err))

    file_type = get_file_type(log_tag, file_path, False)
    if file_type != FileTypes.DIRECTORY:
        file_utils_errno.ERRNO_CREATING_FILE_FAILED.format(label + "directory file", file_path)

    return None





def delete_regular_file(log_tag, label, file_path, ignore_non_existent_file=True):
    """
    Delete regular file at path.

    This function is a wrapper for {@link #delete_file()}.

    @param label The optional label for file to delete. This can optionally be `None`.
    @param file_path The {@code path} for file to delete.
    @param ignore_non_existent_file[`True`] Whether it should be considered an
                                 error if file to deleted doesn't exist.
    @return Returns the error if deletion was not successful, otherwise `None`.
    """

    return delete_file(log_tag, label, file_path, FileTypes.REGULAR.value,
                       ignore_non_existent_file=ignore_non_existent_file)

def delete_directory_file(log_tag, label, file_path, ignore_non_existent_file=True):
    """
    Delete directory file at path.

    This function is a wrapper for {@link #delete_file()}.

    @param label The optional label for file to delete. This can optionally be `None`.
    @param file_path The {@code path} for file to delete.
    @param ignore_non_existent_file[`True`] Whether it should be considered an
                                 error if file to deleted doesn't exist.
    @return Returns the error if deletion was not successful, otherwise `None`.
    """

    return delete_file(log_tag, label, file_path,  FileTypes.DIRECTORY.value,
                       ignore_non_existent_file=ignore_non_existent_file)

def delete_symlink_file(log_tag, label, file_path, ignore_non_existent_file=True):
    """
    Delete symlink file at path.

    This function is a wrapper for {@link #delete_file()}.

    @param label The optional label for file to delete. This can optionally be `None`.
    @param file_path The {@code path} for file to delete.
    @param ignore_non_existent_file[`True`] Whether it should be considered an
                                 error if file to deleted doesn't exist.
    @return Returns the error if deletion was not successful, otherwise `None`.
    """

    return delete_file(log_tag, label, file_path, FileTypes.SYMLINK.value,
                       ignore_non_existent_file=ignore_non_existent_file)

def delete_normal_file(log_tag, label, file_path, ignore_non_existent_file=True):
    """
    Delete regular, directory or symlink file at path.

    This function is a wrapper for {@link #delete_file()}.

    @param label The optional label for file to delete. This can optionally be `None`.
    @param file_path The {@code path} for file to delete.
    @param ignore_non_existent_file[`True`] Whether it should be considered an
                                 error if file to deleted doesn't exist.
    @return Returns the error if deletion was not successful, otherwise `None`.
    """

    return delete_file(log_tag, label, file_path, file_types.FILE_TYPE_NORMAL_FLAGS,
                       ignore_non_existent_file=ignore_non_existent_file)

def delete_file(log_tag, label, file_path, allowed_file_type_flags, ignore_non_existent_file=True,
                ignore_wrong_file_type=False):
    """
    Delete file at path.

    The {@code file_path} must be the canonical path to the file to be deleted since symlinks will
    not be followed.
    If the {@code file_path} is a canonical path to a directory, then any symlink files found under
    the directory will be deleted, but not their targets.

    @param label The optional label for file to delete. This can optionally be `None`.
    @param file_path The {@code path} for file to delete.
    @param allowed_file_type_flags The flags that are matched against the file's {@link FileTypes} to
                                see if it should be deleted or not. This is a safety measure to
                                prevent accidental deletion of the wrong type of file, like a
                                directory instead of a regular file. You can pass
                                {@link file_types#FILE_TYPE_ANY_FLAGS} to allow deletion of any file type.
    @param ignore_non_existent_file[`True`] Whether it should be considered an
                                 error if file to deleted doesn't exist.
    @param ignore_wrong_file_type[`False`] Whether it should be considered an
                                 error if file type is not one from `allowed_file_type_flags`.
    @return Returns the error if deletion was not successful, otherwise `None`.
    """

    label = "" if not label else str(label) + " "

    error = is_path_valid(label + "file path", file_path)
    if error is not None:
        return error

    file_type = get_file_type(log_tag, file_path, False)

    logger.vverbose(log_tag, "Processing delete of " + label + "file at path" +
                    " \"" + file_path + "\" of type \"" + file_type.name + "\"")

    # If file does not exist
    if file_type == FileTypes.NO_EXIST:
        # If delete is to be ignored if file does not exist
        if ignore_non_existent_file:
            return None
            # Else return with error
        else:
            label += "file meant to be deleted"
            return file_utils_errno.ERRNO_FILE_NOT_FOUND_AT_PATH.format(
                label, file_path)

    # If the file type of the file does not exist in the allowed_file_type_flags
    if (allowed_file_type_flags & file_type.value) == 0:
        # If wrong file type is to be ignored
        if ignore_wrong_file_type:
            logger.verbose(log_tag, "Ignoring deletion of " + label +
                           "file at path \"" + file_path + "\" of type \"" + file_type.name +
                           "\" not matching allowed file types: " +
                           file_types.convert_file_type_flags_to_names_string(allowed_file_type_flags))
            return None

        # Else return with error
        return file_utils_errno.ERRNO_FILE_NOT_AN_ALLOWED_FILE_TYPE.format(
            label + "file meant to be deleted", file_path, file_type.name,
            file_types.convert_file_type_flags_to_names_string(allowed_file_type_flags))

    try:
        logger.verbose(log_tag, "Deleting " + label +
            ("directory" if file_type == FileTypes.DIRECTORY else "file") + " at path \"" + file_path + "\"")

        if file_type == FileTypes.DIRECTORY:
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
    except OSError as err:
        if err.errno != errno.ENOENT:
            return file_utils_errno.ERRNO_DELETING_FILE_FAILED_WITH_EXCEPTION.format(
                label + "file", file_path, str(err))

    # If file still exists after deleting it
    file_type = get_file_type(log_tag, file_path, False)
    if file_type != FileTypes.NO_EXIST:
        return file_utils_errno.ERRNO_FILE_STILL_EXISTS_AFTER_DELETING.format(
            label + "file meant to be deleted", file_path)

    return None





def create_symlink_file(log_tag, label, target_file_path, dest_file_path, target_is_directory,
                        target_no_exist_mode, dest_already_exists_mode):
    """
    Create a symlink file at path.

    ### target_is_directory

    The `target_is_directory` argument value to pass to [`os.symlink()`]
    so that symlink to [`target`](#target) is created as a directory.

    On Windows, a symlink represents either a file or a directory, and
    does not morph to the target dynamically. If the target is present,
    the type of the symlink will be created to match. Otherwise, the
    symlink will be created as a directory if `target_is_directory` is
    `true` (the default) or a file symlink otherwise.
    **On non-Windows platforms, `target_is_directory` is ignored.

    - [`os.symlink()`]: https://docs.python.org/3/library/os.html#os.symlink



    ### target_no_exist_mode

    The mode for what to do if symlink `target_file_path` does not exist.

    **Values:**

    The value for mode.

    - `ignore` - Ignore creating the symlink and do not exit with error.
    - `allow` - Create the (dangling) symlink.
    - `disallow` - Exit with error.



    ### dest_already_exists_mode

    The mode for what to do if symlink `dest_file_path` already exists.

    **Values:**

    The value for mode.

    - `ignore` - Ignore creating the symlink.
    - `overwrite` - Delete any existing file at destination path regardless of its file type and then create the symlink at the destination path.
    - `overwrite_only_if_symlink` - Delete any existing file at destination path but only if it is a `symlink` file and then create the symlink at the destination path.
    - `disallow` - Exit with error.

    @param label The optional label for the symlink file. This can optionally be {@code null}.
    @param target_file_path The `path` TO which the symlink file will be created.
    @param dest_file_path The `path` AT which the symlink file will be created.
    @param target_is_directory The `target_is_directory` argument value to pass to `os.symlink()`.
    @param target_no_exist_mode The mode for what to do if symlink `target_file_path` does not exist.
    @param dest_already_exists_mode The mode for what to do if symlink `dest_file_path` already exists.
    @return Returns the `error` if failed to create symlink file, otherwise `null`.
    """

    label = "" if not label else str(label) + " "

    error = is_path_valid(label + "symlink destination file path", dest_file_path)
    if error is not None:
        return error

    # Allow non absolute paths
    error = is_path_valid(label + "symlink target file path", target_file_path, ensure_absolute=False)
    if error is not None:
        return error

    symlink_type = "directory" if target_is_directory else "file"

    target_file_absolute_path = target_file_path
    # If target path is relative instead of absolute
    if not os.path.isabs(target_file_path):
        dest_file_parent_path = get_dirname(dest_file_path)
        if dest_file_parent_path:
            target_file_absolute_path = os.path.join(dest_file_parent_path, target_file_path)

    # Remove `/../` path components since in path `/a/b/c/../t` created
    # after appending the `../t` target, the `c` directory may not exist.
    target_file_absolute_path = normalize_path(target_file_absolute_path)

    target_file_type = get_file_type(log_tag, target_file_absolute_path, False)
    dest_file_type = get_file_type(log_tag, dest_file_path, False)

    # If target file does not exist
    if target_file_type == FileTypes.NO_EXIST:
        target_no_exist_mode = target_no_exist_mode.upper() if target_no_exist_mode else "DISALLOW"

        # If to ignore creating symlink if target does not exist
        if target_no_exist_mode == "IGNORE":
            logger.verbose(log_tag, "Ignoring creating " + label + "symlink file at path" +
                           " \"" + dest_file_path + "\" to \"" + target_file_path + "\" " +
                           symlink_type + " since target does not exist")
            return None
        # If dangling symlink should be allowed
        elif target_no_exist_mode == "ALLOW":
            pass
        # If dangling symlink should not be allowed, then return with error
        elif target_no_exist_mode == "DISALLOW":
            label += "symlink target file"
            return file_utils_errno.ERRNO_FILE_NOT_FOUND_AT_PATH.format(
                label, target_file_absolute_path)
        else:
            return file_utils_errno.ERRNO_INVALID_SYMLINK_TARGET_NO_EXISTS_MODE.format(
                label + "symlink file", target_no_exist_mode, "create_symlink_file")

    # If destination already exists
    if dest_file_type != FileTypes.NO_EXIST:
        dest_already_exists_mode = dest_already_exists_mode.upper() if dest_already_exists_mode else "DISALLOW"

        # If to ignore creating symlink
        if dest_already_exists_mode == "IGNORE":
            logger.verbose(log_tag, "Ignoring creating " + label + "symlink file at path" +
                           " \"" + dest_file_path + "\" to \"" + target_file_path + "\" " +
                           symlink_type + " since a " + dest_file_type.name +
                           " file already exists at destination")
            return None
        # If to overwrite destination regardless of file type
        elif dest_already_exists_mode == "OVERWRITE":
            pass
        # If to overwrite destination if it already exists and is a symlink
        elif dest_already_exists_mode == "OVERWRITE_ONLY_IF_SYMLINK":
            if dest_file_type != FileTypes.SYMLINK:
                return file_utils_errno.ERRNO_CANNOT_OVERWRITE_A_NON_SYMLINK_FILE_TYPE.format(
                    label + "file", dest_file_path, target_file_path, dest_file_type.name)
        # If symlink should not be created, then return with error
        elif dest_already_exists_mode == "DISALLOW":
            label += "symlink destination"
            return file_utils_errno.ERRNO_FILE_ALREADY_EXISTS_AT_PATH.format(
                label, dest_file_path)
        else:
            return file_utils_errno.ERRNO_INVALID_SYMLINK_DEST_ALREADY_EXISTS_MODE.format(
                label + "symlink file", dest_already_exists_mode, "create_symlink_file")

        # Delete the destination file
        error = delete_normal_file(log_tag, label + "symlink destination", dest_file_path)
        if error is not None:
            return error
    else:
        # Create the destination file parent directory
        error = create_parent_directory_file(log_tag, label + "symlink destination file parent", dest_file_path)
        if error is not None:
            return error

    try:
        # Create symlink from dest_file_path -> target_file_path
        logger.verbose(log_tag, "Creating " + label + "symlink file at path" +
                       " \"" + dest_file_path + "\" to \"" + target_file_path + "\" " + symlink_type)

        os.symlink(target_file_path, dest_file_path, target_is_directory=target_is_directory)

        return None
    except Exception as err:
        return file_utils_errno.ERRNO_CREATING_SYMLINK_FILE_FAILED_WITH_EXCEPTION.format(
            label + "symlink file", dest_file_path, target_file_path, symlink_type, str(err))






def get_dirname(path):
    """
    Get dirname of `path`

    - https://stackoverflow.com/a/25669963
    """

    return os.path.normpath(os.path.join(path, os.pardir)) if path else None
