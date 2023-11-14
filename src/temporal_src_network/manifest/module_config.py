import collections
import os

from . import version_config

from ..data import data_utils
from ..data.data_utils import log_value
from ..file import file_utils
from ..logger.logger_core import logger
from ..shell import shell_utils

LOG_TAG = "module_config"

class ModuleConfig:
    "Module config."

    def __init__(self, module_config_dict, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with ModuleConfig.create()")

        self.module_config_dict = module_config_dict if module_config_dict else collections.OrderedDict()

        self.module_name = None

        self.module_root_sub_dir = None
        self.module_root_dir = None

        self.remove_module_root_dir_for_commands = set()

        self.src_checkout_dict = collections.OrderedDict()

        self.symlinks_dict = collections.OrderedDict()

        self.single_version = True
        self.versions_dict = collections.OrderedDict()

        self.version_configs = []

    @classmethod
    def create(cls, project_config, module_name, module_config_dict, existing_module_configs):
        module_config = cls(module_config_dict, _not_called_from_create=False)

        if not module_name:
            logger.error(LOG_TAG, "The module_name \"" + module_name + "\"  must be set")
            return (1, None)

        module_config.module_name = module_name



        original_module_root_dir = data_utils.get_str_from_dict(module_config_dict, "module_root_dir", None)
        module_root_dir = shell_utils.expand_env_vars(original_module_root_dir)
        if module_root_dir:
            module_root_dir = file_utils.normalize_path(module_root_dir)


        if not module_root_dir:
            logger.error(LOG_TAG, "The module \"" + module_name + "\" module_root_dir must be set." +
                " original_module_root_dir: \"" + str(original_module_root_dir) + "\"")
            return (1, None)

        # Ensure no null bytes or `.` or `..` path components
        error = file_utils.is_path_valid("module_root_dir", module_root_dir, ensure_absolute=False,
                  ensure_canonical=True)
        if error is not None:
            logger.error(LOG_TAG, error)
            return (1, None)

        # Create full path module_root_dir
        module_config.module_root_sub_dir = module_root_dir
        module_config.module_root_dir = os.path.join(project_config.project_root_dir, module_root_dir)

        error = file_utils.is_path_valid("real module_root_dir", module_config.module_root_dir)
        if error is not None:
            logger.error(LOG_TAG, error)
            return (1, None)

        # The module_root_dir will be deleted and so it must be under
        # the project_root_dir so that important directories outside it
        # are not accidentally deleted, especially if project_root_dir
        # is set to the filesystem_root `/`.
        if not file_utils.is_path_in_dir_path(module_config.module_root_dir, project_config.project_root_dir, True):
            logger.error(LOG_TAG, "The module \"" + module_name + "\"" +
                         " root_dir \"" + module_config.module_root_dir + "\"" +
                         " must be under project_root_dir \"" + project_config.project_root_dir + "\"")
            return (1, None)




        module_config.remove_module_root_dir_for_commands = data_utils.get_comma_separated_list_from_dict(
            module_config_dict, "remove_module_root_dir_for_commands", "remove", True)




        module_config.src_checkout_dict = data_utils.get_ordered_dict_from_dict(
            module_config_dict, "version_src_checkout", module_config.src_checkout_dict)
        module_config.symlinks_dict = data_utils.get_ordered_dict_from_dict(
            module_config_dict, "version_symlinks", module_config.symlinks_dict)



        module_config.versions_dict = data_utils.get_ordered_dict_from_dict(
            module_config_dict, "versions", module_config.versions_dict)
        if not module_config.versions_dict:
            logger.error(LOG_TAG, "The 'module.versions' value not set or not a dict for module \"" + module_config.module_name + "\"")
            return (1, None)



        module_config.single_version = data_utils.get_bool_from_dict(module_config.versions_dict,
            "single_version", module_config.single_version)



        for existing_module_config in existing_module_configs:
            # If module root_dir is the same or under another module's root_dir and either of them have single_version disabled
            # If `git` checkout is to be used, then two module versions shouldn't be allowed to shared directories either,
            # unless one uses `git` checkout and another a different compatible checkout like extracting a `zip` file.
            # These checks wouldn't work if bind mounts are used to point different paths to the same directory.
            if not module_config.single_version or not existing_module_config.single_version:
                if file_utils.is_path_in_dir_path(module_config.module_root_dir, existing_module_config.module_root_dir, False):
                    logger.error(LOG_TAG, "The module \"" + module_config.module_name + "\"" +
                                 " root_dir \"" + module_config.module_root_dir + "\"" +
                                 " is the same or under root_dir of another module \"" + existing_module_config.module_name + "\"." +
                                 " with root_dir \"" + existing_module_config.module_root_dir + "\"" +
                                 " Sharing same module root_dir is not allowed if either module has single_version disabled")
                    return (1, None)
                elif file_utils.is_path_in_dir_path(existing_module_config.module_root_dir, module_config.module_root_dir, False):
                    logger.error(LOG_TAG, "The module \"" + existing_module_config.module_name + "\"" +
                                 " root_dir \"" + existing_module_config.module_root_dir + "\"" +
                                 " is the same or under root_dir of current module \"" + module_config.module_name + "\"." +
                                 " with root_dir \"" + module_config.module_root_dir + "\"" +
                                 " Sharing same module root_dir is not allowed if either module has single_version disabled")
                    return (1, None)



        logger.vverbose(LOG_TAG, "module_config:\n" + module_config.to_string() + "\n")



        (return_value, version_configs) = version_config.create_module_version_configs(
            project_config, module_config)
        if str(return_value) != "0":
            return (return_value, None)
        # All versions may have been ignored
        if version_configs is None or not isinstance(version_configs, list):
            logger.error(LOG_TAG, "Failed to create version_configs for module \"" + module_name + "\"")
            return (1, None)

        module_config.version_configs = version_configs



        return (0, module_config)



    def to_string(self):
        return \
        "module_name: " + log_value(self.module_name) + \
        "\nmodule_root_sub_dir: " + log_value(self.module_root_sub_dir) + \
        "\nmodule_root_dir: " + log_value(self.module_root_dir) + \
        "\nremove_module_root_dir_for_commands: " + log_value(self.remove_module_root_dir_for_commands) + \
        "\nsingle_version: " + log_value(self.single_version)
