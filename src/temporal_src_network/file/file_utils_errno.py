from . import file_constants

# Errors for invalid paths
ERRNO_NULL_PATH = "The {0} is null."
ERRNO_EMPTY_PATH = "The {0} is empty."
ERRNO_NON_STRING_PATH = "The {0} passed to \"{1}\" is not a string."
ERRNO_NULL_BYTE_CONTAINING_PATH = "The {0} is invalid since it contains null bytes.\npath: \"{1}\""
ERRNO_PATH_TOO_LONG = "The {0} is invalid since its length {1} is >= " + str(file_constants.PATH_MAX) + ".\npath: \"{2}\""
ERRNO_PATH_COMPONENT_TOO_LONG = "The {0} is invalid since the length {1} of component {2} \"{3}\" is" + \
    " > " + str(file_constants.NAME_MAX) + ".\npath: \"{4}\""
ERRNO_NON_ABSOLUTE_PATH = "The {0} is invalid since its not an absolute path.\npath: \"{1}\""
ERRNO_NON_CANONICAL_PATH = "The {0} is invalid since its not a canonical path.\npath: \"{1}\""


# Errors for invalid or not found files at path
ERRNO_FILE_NOT_FOUND_AT_PATH = "The {0} not found at path \"{1}\"."
ERRNO_NON_DIRECTORY_FILE_FOUND = "Non-directory file found at {0} path \"{1}\" with type \"{2}\"."
ERRNO_FILE_NOT_AN_ALLOWED_FILE_TYPE = \
    "The {0} found at path \"{1}\" of type \"{2}\" is not one of allowed file types \"{3}\"."
ERRNO_FILE_ALREADY_EXISTS_AT_PATH = "A file already exists at {0} path \"{1}\"."



# Errors for file creation
ERRNO_CREATING_FILE_FAILED = "Creating {0} at path \"{1}\" failed."
ERRNO_CREATING_FILE_FAILED_WITH_EXCEPTION = "Creating {0} at path \"{1}\" failed.\nException: {2}"

ERRNO_CANNOT_OVERWRITE_A_NON_SYMLINK_FILE_TYPE = \
    "Cannot overwrite {0} while creating symlink at \"{1}\" to \"{2}\" since destination is of file type \"{3}\" instead of a \"symlink\"."
ERRNO_CREATING_SYMLINK_FILE_FAILED_WITH_EXCEPTION = \
    "Creating {0} at path \"{1}\" to \"{2}\" {3} failed.\nException: {4}"
ERRNO_INVALID_SYMLINK_TARGET_NO_EXISTS_MODE = "The \"{0}\" target_no_exist_mode \"{1}\" passed to \"{2}\"" + \
    " must be one of ignore|allow|disallow."
ERRNO_INVALID_SYMLINK_DEST_ALREADY_EXISTS_MODE = "The \"{0}\" dest_already_exists_mode \"{1}\" passed to \"{2}\"" + \
    " must be one of ignore|overwrite|overwrite_only_if_symlink|disallow."



# Errors for file deletion
ERRNO_DELETING_FILE_FAILED_WITH_EXCEPTION = "Deleting {0} at path \"{1}\" failed.\nException: {2}"
ERRNO_CLEARING_DIRECTORY_FAILED_WITH_EXCEPTION = "Clearing {0} at path \"{1}\" failed.\nException: {2}"
ERRNO_FILE_STILL_EXISTS_AFTER_DELETING = "The {0} still exists after deleting it from \"{1}\"."
