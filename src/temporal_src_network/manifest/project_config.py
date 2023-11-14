import collections
import os

from ..data import data_utils
from ..data.data_utils import log_value
from ..file import file_utils
from ..logger.logger_core import logger
from ..shell import shell_utils

LOG_TAG = "project_config"

class ProjectConfig:
    "Project config."

    def __init__(self, manifest_label, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with ProjectConfig.create()")

        self.manifest_label = manifest_label

        self.project_root_dir = str("")
        self.remove_project_root_dir_for_commands = set()

        self.src_checkout_dict = collections.OrderedDict()
        self.symlinks_dict = collections.OrderedDict()

        self.modules_dict = collections.OrderedDict()

    @classmethod
    def create(cls, project_config_dict, manifest_label):
        project_config = cls(manifest_label, _not_called_from_create=False)

        original_project_root_dir = data_utils.get_str_from_dict(project_config_dict, "project_root_dir", None)
        # If project_root_dir key is set
        if original_project_root_dir:
            project_root_dir = shell_utils.expand_env_vars(original_project_root_dir)

            if not project_root_dir:
                logger.error(LOG_TAG, "The project_root_dir \"" + str(original_project_root_dir) + "\"" +
                             " is unset after environmental variable expansion")
                return (1, None)

            error = file_utils.is_path_valid("project_root_dir", project_root_dir, ensure_absolute=False)
            if error is not None:
                logger.error(LOG_TAG, error)
                return (1, None)

            project_root_dir = os.path.realpath(project_root_dir)
        # If project_root_dir key is not set
        elif original_project_root_dir is None:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                project_root_dir = os.environ.get("GITHUB_WORKSPACE")
                if not project_root_dir:
                    logger.error(LOG_TAG, "$GITHUB_WORKSPACE environmental variable not set")
                    return (1, None)
            else:
                # Default to current working directory
                project_root_dir = os.path.realpath(".")
        else:
            logger.error(LOG_TAG, "The project_root_dir must be set." +
                " original_project_root_dir: \"" + str(original_project_root_dir) + "\"")
            return (1, None)

        error = file_utils.is_path_valid("real project_root_dir", project_root_dir)
        if error is not None:
            logger.error(LOG_TAG, error)
            return (1, None)

        project_config.project_root_dir = project_root_dir



        project_config.remove_project_root_dir_for_commands = data_utils.get_comma_separated_list_from_dict(
            project_config_dict, "remove_project_root_dir_for_commands", None, True)

        # We must not accidentally delete the filesystem root.
        filesystem_root =  file_utils.get_filesystem_root()
        if project_config.remove_project_root_dir_for_commands and \
            project_config.project_root_dir == filesystem_root:
            logger.error(LOG_TAG, "The remove_project_root_dir_for_commands cannot be set" +
            " as project_root_dir \"" + str(project_config.project_root_dir) + "\"" +
            " is the filesystem_root \"" + str(filesystem_root) + "\"." +
            "\noriginal_project_root_dir: \"" + str(original_project_root_dir) + "\"" +
            "\nremove_project_root_dir_for_commands:" +
            " " + str(project_config.remove_project_root_dir_for_commands))
            return (1, None)



        project_config.src_checkout_dict = data_utils.get_ordered_dict_from_dict(
            project_config_dict, "project_src_checkout", project_config.src_checkout_dict)

        project_config.symlinks_dict = data_utils.get_ordered_dict_from_dict(
            project_config_dict, "project_symlinks", project_config.symlinks_dict)

        project_config.modules_dict = data_utils.get_ordered_dict_from_dict(
            project_config_dict, "modules", project_config.modules_dict)



        logger.vverbose(LOG_TAG, "project_config:\n" + project_config.to_string() + "\n")

        return (0, project_config)



    def to_string(self):
        return \
        "manifest_label: " + log_value(self.manifest_label) + \
        "\nproject_root_dir: " + log_value(self.project_root_dir) + \
        "\nremove_project_root_dir_for_commands: " + log_value(self.remove_project_root_dir_for_commands)
