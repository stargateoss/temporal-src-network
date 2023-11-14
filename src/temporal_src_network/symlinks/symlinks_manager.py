import collections
import json

from ..manifest.project_config import ProjectConfig
from ..manifest.version_config import VersionConfig
from ..symlinks.symlink_config import SymlinkConfig

from ..data import data_utils
from ..file import file_utils
from ..logger.logger_core import logger

LOG_TAG = "symlinks_manager"

class SymlinksManager:
    "The symlinks manager."

    def __init__(self, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with SymlinksManager.create()")

        self.symlinks_list_level_mode = "add" # add|override
        self.symlink_configs = []
        self.symlink_placeholder_expansions = collections.OrderedDict()

    @classmethod
    def create(cls, project_config, version_config):
        symlinks_manager = cls(_not_called_from_create=False)

        symlinks_list = collections.OrderedDict()

        if not version_config and project_config and isinstance(project_config, ProjectConfig):
            label = "project"

            project_symlinks = project_config.symlinks_dict

            project_symlinks_list = data_utils.get_ordered_dict_from_dict(project_symlinks, "list", collections.OrderedDict())
            if project_symlinks_list:
                symlinks_list = project_symlinks_list

        elif version_config and isinstance(version_config, VersionConfig):
            module_config = version_config.module_config

            label = "module \"" + module_config.module_name + "\"" + \
            " version \"" + version_config.version_name + "\""

            module_symlinks = module_config.symlinks_dict
            version_symlinks = version_config.symlinks_dict

            symlinks_list_level_mode = data_utils.get_str_from_dict(version_symlinks, "symlinks_list_level_mode", None)
            module_symlinks_list = data_utils.get_ordered_dict_from_dict(module_symlinks, "list", collections.OrderedDict())
            version_symlinks_list = data_utils.get_ordered_dict_from_dict(version_symlinks, "list", collections.OrderedDict())
            if not symlinks_list_level_mode or symlinks_list_level_mode == "add":
                if module_symlinks_list and version_symlinks_list:
                    symlinks_list = collections.OrderedDict(
                        list(module_symlinks_list.items()) + list(version_symlinks_list.items()))
                elif module_symlinks_list:
                    symlinks_list = module_symlinks_list
                elif version_symlinks_list:
                    symlinks_list = version_symlinks_list
            elif symlinks_list_level_mode == "override":
                if version_symlinks_list:
                    symlinks_list = version_symlinks_list
            else:
                logger.error(LOG_TAG, "The module \"" + module_config.module_name + "\"" +
                             " version \"" + version_config.version_name + "\"" +
                             " symlinks_list_level_mode \"" + symlinks_list_level_mode + "\" must be 'add' or 'override'")
                return (1, None)
        else:
            logger.error(LOG_TAG, "Either (project_config) or version_config" +
                         " must be passed to CheckoutConfig.create()")
            return (1, None)

        if symlinks_list:
            logger.vverbose(LOG_TAG, "symlinks_list:\n" + json.dumps(symlinks_list, sort_keys=False, indent=4, default=str))



        symlinks_manager.symlink_placeholder_expansions = cls.get_symlink_placeholder_expansions_dict(
            project_config, version_config)
        logger.vverbose(LOG_TAG, "symlink_placeholder_expansions:\n" +
            json.dumps(symlinks_manager.symlink_placeholder_expansions, sort_keys=False, indent=4, default=str))



        i = 1
        symlink_configs = []
        # For all symlink_name, symlink_config_dict in symlinks_list
        for symlink_name, symlink_config_dict in symlinks_list.items():
            if data_utils.get_bool_from_dict(symlink_config_dict, "ignore", False):
                logger.verbose(LOG_TAG, "Ignoring symlink " + str(i) + " \"" + symlink_name + "\"")
                continue

            logger.verbose(LOG_TAG, "Creating symlink_config for symlink " + str(i) + " \"" + symlink_name + "\"")

            (return_value, symlink_config) = SymlinkConfig.create(
                label, project_config, symlink_name, symlink_config_dict, symlinks_manager.symlink_placeholder_expansions)
            if str(return_value) != "0":
                return (return_value, None)
            if not symlink_config:
                logger.error(LOG_TAG, "Failed to create symlink_config for symlink " + str(i) + " \"" + symlink_name + "\"")
                return (1, None)

            symlink_configs.append(symlink_config)

            i += 1

        symlinks_manager.symlink_configs = symlink_configs

        return (0, symlinks_manager)

    @classmethod
    def get_symlink_placeholder_expansions_dict(cls, project_config, version_config):
        expansions = collections.OrderedDict()

        expansions["PROJECT__ROOT_DIR"] = project_config.project_root_dir

        if version_config:
            module_config = version_config.module_config
            expansions["MODULE__NAME"] = module_config.module_name
            expansions["MODULE__ROOT_SUB_DIR"] = module_config.module_root_sub_dir
            expansions["MODULE__ROOT_DIR"] = module_config.module_root_dir

            expansions["VERSION__NAME"] = version_config.version_name
            expansions["VERSION__ROOT_SUB_DIR"] = version_config.version_root_sub_dir
            expansions["VERSION__ROOT_DIR"] = version_config.version_root_dir

        return expansions

    @staticmethod
    def expand_symlink(expansions, symlink):
        # Replace "@KEY_NAME@" placeholders with its real value
        for key, value in expansions.items():
            key_placeholder = "@" + key + "@"
            if key_placeholder in symlink:
                symlink = symlink.replace(key_placeholder, value)

        return symlink



    def create_symlinks(self):
        logger.debug(LOG_TAG, "Create symlinks")

        i = 1
        for symlink_config in self.symlink_configs:
            label = "(" + str(i) + ") " + symlink_config.symlink_name
            logger.verbose(LOG_TAG, "Processing creation of " + label + " symlink")
            error = file_utils.create_symlink_file(
                LOG_TAG,
                label,
                symlink_config.target_expanded, symlink_config.dest_expanded,
                symlink_config.target_is_directory, symlink_config.target_no_exist_mode,
                symlink_config.dest_already_exists_mode)
            if error is not None:
                logger.error(LOG_TAG, error)
                logger.error(LOG_TAG, "symlink_config:\n" + symlink_config.to_string())
                return 1

            i += 1

        return 0

    def remove_symlinks(self):
        logger.debug(LOG_TAG, "Remove symlinks")

        i = 1
        for symlink_config in self.symlink_configs:
            label = "(" + str(i) + ") " + symlink_config.symlink_name
            logger.verbose(LOG_TAG, "Processing removal of " + label + " symlink")
            error = file_utils.delete_symlink_file(
                LOG_TAG,
                label,
                symlink_config.dest_expanded,
                ignore_non_existent_file=True)
            if error is not None:
                logger.error(LOG_TAG, error)
                logger.error(LOG_TAG, "symlink_config:\n" + symlink_config.to_string())
                return 1

            i += 1

        return 0
