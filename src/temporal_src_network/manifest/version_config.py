import collections
import os
import re

from ..data import data_utils
from ..data.data_utils import log_value
from ..file import file_utils
from ..logger.logger_core import logger

LOG_TAG = "version_config"

class VersionConfig:
    "Module version config."

    def __init__(self, module_config, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with VersionConfig.create()")

        self.module_config = module_config

        self.version_name = None

        self.version_root_sub_dir = None
        self.version_root_dir = None

        self.remove_version_root_dir_for_commands = set()

        self.src_checkout_dict = collections.OrderedDict()
        self.symlinks_dict = collections.OrderedDict()

    @classmethod
    def create(cls, project_config, module_config, version_name, version_config_dict):
        version_config = cls(module_config, _not_called_from_create=False)

        if not version_name or re.match('[' + os.sep + ']+', version_name) or \
            str(b'\x00') in version_name or re.match(r'^\.|\.\.$', version_name):
            logger.error(LOG_TAG, "The module \"" + module_config.module_name + "\"" +
                         " version_name \"" + version_name + "\" must be set and" +
                         " must not contain the path separator '" + os.sep + "'" +
                         " or null bytes or equal '.' or '..'")
            return (1, None)

        version_config.version_name = version_name



        version_config.remove_version_root_dir_for_commands = data_utils.get_comma_separated_list_from_dict(
            [version_config_dict, module_config.module_config_dict], "remove_version_root_dir_for_commands", "setup,remove", True)



        version_config.src_checkout_dict = data_utils.get_ordered_dict_from_dict(
            version_config_dict, "version_src_checkout", version_config.src_checkout_dict)

        # The src_checkout dict may not be set if user wants default branch
        # to be used and hasn't set src_checkout.ref
        if not version_config.src_checkout_dict:
            version_config.src_checkout_dict = collections.OrderedDict()


        version_config.symlinks_dict = data_utils.get_ordered_dict_from_dict(
            version_config_dict, "version_symlinks", version_config.symlinks_dict)

        module_root_dir = module_config.module_root_dir
        if not module_root_dir or not os.path.isabs(module_root_dir):
            logger.error(LOG_TAG, "The module \"" + module_config.module_name + "\"" +
                         " root_dir \"" + module_root_dir + "\" must be set" +
                         " and be an absolute path")
            return (1, None)

        # Create full path version root_dir
        if module_config.single_version:
            version_config.version_root_sub_dir = module_config.module_root_sub_dir
            version_config.version_root_dir = module_root_dir
            required_parent_dir_path = project_config.project_root_dir
            required_parent_dir_label = "project_root_dir \"" + project_config.project_root_dir + "\""
        else:
            version_config.version_root_sub_dir = os.path.join(module_config.module_root_sub_dir, version_name)
            version_config.version_root_dir = os.path.join(module_root_dir, version_name)
            required_parent_dir_path = module_root_dir
            required_parent_dir_label = "module_root_dir \"" + module_root_dir + "\""

        error = file_utils.is_path_valid("version_root_dir", version_config.version_root_dir)
        if error is not None:
            logger.error(LOG_TAG, error)
            return (1, None)

        # The version_root_dir will be deleted and so it must be under
        # the project_root_dir for single_version, otherwise under
        # module_root_dir so that important directories outside them
        # are not accidentally deleted, especially if project_root_dir
        # is set to the filesystem_root `/`.
        if not file_utils.is_path_in_dir_path(version_config.version_root_dir, required_parent_dir_path, True):
            logger.error(LOG_TAG, "The module \"" + module_config.module_name + "\"" +
                         " version \"" + version_name + "\" root_dir" +
                         " \"" + version_config.version_root_dir + "\" must be" +
                         " under " + required_parent_dir_label)
            return (1, None)




        logger.vverbose(LOG_TAG, "The module \"" + module_config.module_name + "\"" +
            " version_config:\n" + version_config.to_string() + "\n")

        return (0, version_config)



    def to_string(self):
        return \
        "version_name: " + log_value(self.version_name) + \
        "\nversion_root_sub_dir: " + log_value(self.version_root_sub_dir) + \
        "\nversion_root_dir: " + log_value(self.version_root_dir) + \
        "\nremove_version_root_dir_for_commands: " + log_value(self.remove_version_root_dir_for_commands)





def create_module_version_configs(project_config, module_config):
    versions_dict = module_config.versions_dict

    versions_list = data_utils.get_ordered_dict_from_dict(versions_dict, "list", None)
    if not versions_list:
        logger.error(LOG_TAG, "The 'versions.list' value not set or not a dict for module \"" + module_config.module_name + "\"")
        return (1, None)

    versions_count = len(versions_list)

    version_num = 1
    version_configs = []
    # For all version_name, version_config in versions_list
    for version_name, version_config_dict in versions_list.items():
        version_label = "module \"" + module_config.module_name + "\"" + \
                        " version " + str(version_num) + " \"" + version_name + "\""

        if data_utils.get_bool_from_dict(version_config_dict, "ignore", False):
            logger.verbose(LOG_TAG, "Ignoring version " + str(version_num) + " \"" + version_name + "\"")
            continue

        logger.verbose(LOG_TAG, "Creating version_config for version " + str(version_num) + " \"" + version_name + "\"")

        (return_value, version_config) = VersionConfig.create(
            project_config, module_config, version_name, version_config_dict)
        if str(return_value) != "0":
            return (return_value, None)
        if not version_config or not isinstance(version_config, VersionConfig):
            logger.error(LOG_TAG, "Failed to create version_config for " + version_label)
            return (1, None)

        version_configs.append(version_config)

        # Abort after processing the first version_config
        if module_config.single_version:
            if versions_count > 1:
                logger.debug(LOG_TAG, "Ignoring (" + str(versions_count - 1) + ")" +
                             " extra versions for module \"" + module_config.module_name + "\"" +
                             " since single_version is enabled")
            break

        version_num += 1

    return (0, version_configs)
