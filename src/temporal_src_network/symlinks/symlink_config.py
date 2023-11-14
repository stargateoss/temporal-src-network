import os

from . import symlinks_manager

from ..data import data_utils
from ..data.data_utils import log_value
from ..file import file_utils
from ..logger.logger_core import logger
from ..shell import shell_utils

LOG_TAG = "symlink_config"

class SymlinkConfig():
    "Symlink config."

    def __init__(self, symlink_name, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with SymlinkConfig.create()")

        self.symlink_name = symlink_name

        self.target = None
        self.target_expanded = None
        self.target_expansions = None

        self.dest = None
        self.dest_expanded = None
        self.dest_expansions = None

        self.target_is_directory = True
        self.target_no_exist_mode = "disallow"
        self.dest_already_exists_mode = "overwrite_only_if_symlink"

    @classmethod
    def create(cls, label, project_config, symlink_name, symlink_config_dict, symlink_placeholder_expansions):
        symlink_config = cls(symlink_name, _not_called_from_create=False)

        (return_value, symlink_config.target, symlink_config.target_expanded, symlink_config.target_expansions) = \
            cls.get_symlink_paths(label, symlink_name, symlink_config_dict, symlink_placeholder_expansions, "target")
        if str(return_value) != "0":
            return (return_value, None)

        (return_value, symlink_config.dest, symlink_config.dest_expanded, symlink_config.dest_expansions) = \
            cls.get_symlink_paths(label, symlink_name, symlink_config_dict, symlink_placeholder_expansions, "dest")
        if str(return_value) != "0":
            return (return_value, None)


        # If dest_expanded is not an absolute path, prefix it with project_root_dir
        if file_utils.is_path_absolute("dest symlink", symlink_config.dest_expanded) is not None:
            symlink_config.dest_expanded = os.path.join(project_config.project_root_dir, symlink_config.dest_expanded) # type: ignore


        symlink_config.target_is_directory = data_utils.get_bool_from_dict(
            symlink_config_dict, "target_is_directory", symlink_config.target_is_directory)

        target_no_exist_mode_string = data_utils.get_str_from_dict(
            symlink_config_dict, "target_no_exist_mode", symlink_config.target_no_exist_mode).upper()
        if target_no_exist_mode_string == "ALLOW":
            symlink_config.target_no_exist_mode = "allow"
        elif target_no_exist_mode_string == "DISALLOW":
            symlink_config.target_no_exist_mode = "disallow"
        elif target_no_exist_mode_string == "IGNORE":
            symlink_config.target_no_exist_mode = "ignore"

        symlink_config.dest_already_exists_mode = data_utils.get_str_from_dict(
            symlink_config_dict, "dest_already_exists_mode", symlink_config.dest_already_exists_mode)



        logger.vverbose(LOG_TAG, label + " symlink_config:\n" + symlink_config.to_string() + "\n")

        return (0, symlink_config)

    @classmethod
    def get_symlink_paths(cls, label, symlink_name, symlink_config_dict, symlink_placeholder_expansions, key):
        symlink_path = data_utils.get_str_from_dict(symlink_config_dict, key, None)
        symlink_expansions = data_utils.get_comma_separated_list_from_dict(
            symlink_config_dict, key + "_expansions", "env,placeholder", True)

        if symlink_path:
            symlink_path_expanded = symlink_path

            if "env" in symlink_expansions:
                symlink_path_expanded = shell_utils.expand_env_vars(symlink_path_expanded)

            if "placeholder" in symlink_expansions:
                symlink_path_expanded = symlinks_manager.SymlinksManager.expand_symlink(
                symlink_placeholder_expansions, symlink_path_expanded)

            if not symlink_path_expanded:
                logger.error(LOG_TAG, "The " + label + " symlink \"" + symlink_name + "\"" +
                         " " + key + " \"" + symlink_path + "\" not set after expansion")
                return (1, None, None, None)
        else:
            logger.error(LOG_TAG, "The " + label + " symlink \"" + symlink_name + "\"" +
                         " " + key + " not set")
            return (1, None, None, None)

        return (0, symlink_path, symlink_path_expanded, symlink_expansions)



    def to_string(self):
        return \
        "symlink_name: " + log_value(self.symlink_name) + \
        "\ntarget: " + log_value(self.target) + \
        "\ntarget_expanded: " + log_value(self.target_expanded) + \
        "\ntarget_expansions: " + log_value(self.target_expansions) + \
        "\ndest: " + log_value(self.dest) + \
        "\ndest_expanded: " + log_value(self.dest_expanded) + \
        "\ndest_expansions: " + log_value(self.dest_expansions) + \
        "\ntarget_is_directory: " + log_value(self.target_is_directory) + \
        "\ntarget_no_exist_mode: " + log_value(self.target_no_exist_mode) + \
        "\ndest_already_exists_mode: " + log_value(self.dest_already_exists_mode)
