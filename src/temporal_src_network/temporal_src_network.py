#!/usr/bin/env python3
"""
Title:           temporal-src-network
Description:     Utility to build temporal sources network
Usage:           Run "temporal-src-network --help"
Python version:  3 or higher
License:         MIT
"""

import argparse
import collections
import json
import os
import re
import select
import sys

from .data import data_utils
from .file import file_utils
from .logger.logger_core import logger
from .manifest.module_config import ModuleConfig
from .manifest.modules_config import ModulesConfig
from .manifest.project_config import ProjectConfig
from .src_checkout import src_provider as src_provider_lib
from .src_checkout.git.git_checkout_config import GitCheckoutConfig
from .src_checkout.git.git_src_provider import GitSrcProvider
from .src_checkout.ignore.ignore_checkout_config import IgnoreCheckoutConfig
from .src_checkout.ignore.ignore_src_provider import IgnoreSrcProvider
from .symlinks.symlinks_manager import SymlinksManager

import importlib.util # pylint: disable=wrong-import-order
YAML_SUPPORTED = False
try:
    if importlib.util.find_spec("ruamel.yaml") is not None:
        import ruamel.yaml # type: ignore # pylint: disable=import-error
        YAML_SUPPORTED = True
except Exception:
    pass

VERSION = "0.1.0"

LOG_TAG = "temporal_src_network"

PRIVATE_FIELDS_LIST = ["git_auth_token"]

RUAMEL_YAML_INSTALL_INSTRUCTIONS = \
"""Install ruamel.yaml by running following commands.
android/termux: "pip install ruamel.yaml"
debian/ubuntu: "sudo apt install python3-pip; sudo pip3 install ruamel.yaml"
For more info, check https://yaml.readthedocs.io/en/latest/install.html."""



def process_project(command_type, project_config):
    "Process project."

    if command_type not in ["setup", "remove"]:
        logger.error(LOG_TAG, "The project command_type \"" + command_type + "\" is not supported")
        return 1

    logger.info(LOG_TAG, "Processing project")

    project_root_dir = project_config.project_root_dir
    if not project_root_dir or not os.path.isabs(project_root_dir):
        logger.error(LOG_TAG, "The project root_dir \"" + project_root_dir + "\" must be set and be an" +
                     " absolute path")
        return 1


    if project_config.src_checkout_dict:
        (return_value, src_provider) = get_project_src_provider(command_type, project_config)
        if str(return_value) != "0":
            return return_value
        if not src_provider or not isinstance(src_provider, src_provider_lib.SrcProvider):
            logger.error(LOG_TAG, "Failed to create src_provider for project")
            return 1
    else:
        src_provider = None


    if project_config.symlinks_dict:
        (return_value, symlinks_manager) = SymlinksManager.create(project_config, None)
        if str(return_value) != "0":
            return return_value
        if not symlinks_manager or not isinstance(symlinks_manager, SymlinksManager):
            logger.error(LOG_TAG, "Failed to create symlinks_manager for project")
            return 1
    else:
        symlinks_manager = None


    if command_type == "setup":
        return_value = setup_project(project_config, src_provider, symlinks_manager)
    elif command_type == "remove":
        return_value = remove_project(project_config, symlinks_manager)
    else:
        logger.error(LOG_TAG, "The project command_type \"" + command_type + "\" is not handled")
        return 1

    return return_value

def setup_project(project_config, src_provider, symlinks_manager):
    "Run setup command for the project."

    project_root_dir = project_config.project_root_dir

    if "setup" in project_config.remove_project_root_dir_for_commands:
        # Remove project_root_dir if it already exists
        error = file_utils.delete_normal_file(LOG_TAG, "project root", project_root_dir)
        if error is not None:
            logger.error(LOG_TAG, error)
            return 1

    if src_provider:
        logger.log_verbose_no_format("")
        return_value = src_provider.checkout_src()
        if str(return_value) != "0":
            logger.error(LOG_TAG, "Failed to checkout source for project")
            return return_value

    # If project_root_dir does not exist
    if not os.path.isdir(project_root_dir):
        logger.error(LOG_TAG, "Failed to find project_root_dir at \"" + project_root_dir + "\"")
        return 1

    if symlinks_manager and symlinks_manager.symlink_configs:
        logger.log_verbose_no_format("")
        return_value = symlinks_manager.create_symlinks()
        if str(return_value) != "0":
            logger.error(LOG_TAG, "Failed to create symlinks for project")
            return return_value

    return 0

def remove_project(project_config, symlinks_manager):
    "Run remove command for the project."

    project_root_dir = project_config.project_root_dir

    if symlinks_manager and symlinks_manager.symlink_configs:
        logger.log_verbose_no_format("")
        return_value = symlinks_manager.remove_symlinks()
        if str(return_value) != "0":
            logger.error(LOG_TAG, "Failed to remove symlinks for the project")
            return return_value

    if "remove" in project_config.remove_project_root_dir_for_commands:
        logger.log_verbose_no_format("")
        # Remove project_root_dir if it already exists
        error = file_utils.delete_normal_file(LOG_TAG, "project root", project_root_dir)
        if error is not None:
            logger.error(LOG_TAG, error)
            return 1

    return 0



def process_module(module_num, command_type, project_config, modules_config, module_config):
    "Process module."

    if command_type not in ["setup", "remove"]:
        logger.error(LOG_TAG, "The module command_type \"" + command_type + "\" is not supported")
        return 1

    if command_type == "setup":
        # Create module_root_dir if it does not already exist
        error = file_utils.create_dir_file(LOG_TAG, "module root", module_config.module_root_dir)
        if error is not None:
            logger.error(LOG_TAG, error)
            return 1

    version_num = 1
    # For all version_config in version_configs
    for version_config in module_config.version_configs:
        version_label = "module " + str(module_num) + " \"" + module_config.module_name + "\"" + \
                        " version " + str(version_num) + " \"" + version_config.version_name + "\""

        if version_num > 1:
            logger.log_debug_no_format("\n")
        else:
            logger.log_debug_no_format("")

        logger.info(LOG_TAG, "Processing " + version_label)

        version_root_dir = version_config.version_root_dir
        if not version_root_dir or not os.path.isabs(version_root_dir) or \
            not file_utils.is_path_in_dir_path(version_root_dir, project_config.project_root_dir, True):
            logger.error(LOG_TAG, "The " + version_label +
                         " root_dir \"" + version_root_dir + "\" must be set and be an" +
                         " absolute path that is under project_root_dir \"" + project_config.project_root_dir + "\"")
            return 1

        logger.debug(LOG_TAG, "version_root_dir: \"" + version_root_dir + "\"")

        if command_type == "setup":
            (return_value, src_provider) = get_version_src_provider(
                command_type, modules_config, module_config, version_config)
            if str(return_value) != "0":
                return return_value
            if not src_provider or not isinstance(src_provider, src_provider_lib.SrcProvider):
                logger.error(LOG_TAG, "Failed to create src_provider for " + version_label)
                return 1
        else:
            src_provider = None

        (return_value, symlinks_manager) = SymlinksManager.create(project_config, version_config)
        if str(return_value) != "0":
            return return_value
        if not symlinks_manager or not isinstance(symlinks_manager, SymlinksManager):
            logger.error(LOG_TAG, "Failed to create symlinks_manager for " + version_label)
            return 1

        if command_type == "setup":
            return_value = setup_version(version_label, version_config, src_provider, symlinks_manager)
        elif command_type == "remove":
            return_value = remove_version(version_label, version_config, symlinks_manager)
        else:
            logger.error(LOG_TAG, "The module command_type \"" + command_type + "\" is not handled")
            return 1

        if str(return_value) != "0":
            return return_value

        version_num += 1

    if command_type == "remove":
        return_value = remove_module(module_config)
    else:
        return_value = 0

    return return_value

def setup_version(version_label, version_config, src_provider, symlinks_manager):
    "Run setup command for a version."

    if "setup" in version_config.remove_version_root_dir_for_commands:
        # Remove version_root_dir if it already exists
        error = file_utils.delete_normal_file(LOG_TAG, "version root", version_config.version_root_dir)
        if error is not None:
            logger.error(LOG_TAG, error)
            return 1

    logger.log_verbose_no_format("")
    return_value = src_provider.checkout_src()
    if str(return_value) != "0":
        logger.error(LOG_TAG, "Failed to checkout source for " + version_label)
        return return_value

    if symlinks_manager and symlinks_manager.symlink_configs:
        logger.log_verbose_no_format("")
        return_value = symlinks_manager.create_symlinks()
        if str(return_value) != "0":
            logger.error(LOG_TAG, "Failed to create symlinks for " + version_label)
            return return_value

    return 0

def remove_version(version_label, version_config, symlinks_manager):
    "Run remove command for a version."

    if symlinks_manager and symlinks_manager.symlink_configs:
        logger.log_verbose_no_format("")
        return_value = symlinks_manager.remove_symlinks()
        if str(return_value) != "0":
            logger.error(LOG_TAG, "Failed to remove symlinks for " + version_label)
            return return_value

    if "remove" in version_config.remove_version_root_dir_for_commands:
        logger.log_verbose_no_format("")

        # Remove version_root_dir if it already exists
        error = file_utils.delete_normal_file(LOG_TAG, "version root", version_config.version_root_dir)
        if error is not None:
            logger.error(LOG_TAG, error)
            return 1

    return 0

def remove_module(module_config):
    "Run remove command for a module."

    if "remove" in module_config.remove_module_root_dir_for_commands:
        logger.log_debug_no_format("")

        # Remove module_root_dir if it already exists
        error = file_utils.delete_normal_file(LOG_TAG, "module root", module_config.module_root_dir)
        if error is not None:
            logger.error(LOG_TAG, error)
            return 1

    return 0



def get_project_src_provider(command_type, project_config):
    checkout_type = data_utils.get_str_from_dict(
        project_config.src_checkout_dict, "checkout_type", None)

    if not checkout_type or checkout_type == GitCheckoutConfig.CHECKOUT_TYPE:
        return GitSrcProvider.create_for_project(command_type, project_config)
    elif checkout_type == IgnoreCheckoutConfig.CHECKOUT_TYPE:
        return IgnoreSrcProvider.create()
    else:
        logger.error(LOG_TAG, "The project checkout_type \"" + checkout_type + "\"" +
                     " is not supported")
        return (1, None)

def get_version_src_provider(command_type, modules_config, module_config, version_config):
    # Prioritize version_config over module_config
    checkout_type = data_utils.get_str_from_dict(
        [version_config.src_checkout_dict, module_config.src_checkout_dict],
        "checkout_type", None)

    if not checkout_type or checkout_type == GitCheckoutConfig.CHECKOUT_TYPE:
        return GitSrcProvider.create_for_version(command_type, modules_config, version_config)
    elif checkout_type == IgnoreCheckoutConfig.CHECKOUT_TYPE:
        return IgnoreSrcProvider.create()
    else:
        logger.error(LOG_TAG, "The module \"" + version_config.module_config.module_name + "\"" +
                     " version \"" + version_config.version_name + "\"" +
                     " checkout_type \"" + checkout_type + "\"" +
                     " is not supported")
        return (1, None)



def pre_process_manifest(manifest_label, manifest):
    "Pre-process manifest."

    # Sanitize illegal characters in manifest
    manifest = data_utils.sanitize_illegal_chars_from_dict(manifest)
    # logger.vverbose(LOG_TAG, manifest_label + "=\n\"\n" + json.dumps(manifest, indent=4) + "\n\"")
    return manifest

def read_manifests_from_file(manifest_file_label, manifest_file_path, manifests_format):
    "Read manifests from file."

    regex_file_fd = '^((/proc/self)|(/dev))/fd/[0-9]+$'
    regex_io_fd = '^((/proc/self)|(/dev))/fd/[0-2]$'

    # If manifest file does not exist at manifest_file_path and is not
    # path to a file descriptor, like passed via process substitution.
    if not os.path.isfile(manifest_file_path) and \
            not re.match(regex_file_fd, manifest_file_path):
        logger.error(LOG_TAG, "Failed to find " + manifest_file_label)
        return (1, None)

    try:
        if re.match(regex_file_fd, manifest_file_path):
            if re.match(regex_io_fd, manifest_file_path):
                logger.error(LOG_TAG, "The " + manifest_file_label + " cannot be for stdout, stderr or stdin fd.")
                return (1, None)

            # Check if data can be read from the file descriptor.
            # https://docs.python.org/3/library/select.html#select.select
            manifest_file_fd = os.open(manifest_file_path, os.O_RDONLY | os.O_NONBLOCK)
            rlist, _, _ = select.select([manifest_file_fd], [], [], 0)
            if not rlist:
                logger.error(LOG_TAG, "The " + manifest_file_label + " is not a readable fd.")
                return (1, None)

            # Default to yaml format
            if not manifests_format:
                manifests_format = "yaml"

        # Open file at manifest_file_path.
        # The file must not contain non "utf-8" characters, otherwise
        # an exception will be raised.
        all_manifests = []
        with open(manifest_file_path, "r", encoding="utf-8", errors="strict") as manifest_file:
            try:
                if manifests_format == "yaml" or manifests_format == "yml" or \
                        manifest_file_path.endswith(".yml") or \
                        manifest_file_path.endswith(".yaml"):
                    if not YAML_SUPPORTED:
                        logger.error(LOG_TAG, "Loading yaml from " + manifest_file_label +
                                     " requires ruamel.yaml.\n\n" +
                                     RUAMEL_YAML_INSTALL_INSTRUCTIONS + "\n")
                        return (1, None)

                    yaml = ruamel.yaml.YAML(typ='safe', pure=True) # type: ignore pylint: disable=used-before-assignment

                    # Load multiple manifests in same yaml file if they exist separated by `\n...\n---\n`
                    # https://yaml.readthedocs.io/en/latest/api/#dumping-a-multi-document-yaml-stream
                    # https://yaml.org/spec/1.2.2/#912-document-markers
                    manifests = list(yaml.load_all(manifest_file))
                    manifest_number = 1
                    for manifest in manifests:
                        manifest_label = ("manifest " + (str(manifest_number) + " "
                            if len(manifests) > 1 else "") + "in ") + manifest_file_label

                        all_manifests.append(pre_process_manifest(manifest_label,
                            collections.OrderedDict(manifest)))
                        manifest_number += 1

                elif manifests_format == "json" or \
                        manifest_file_path.endswith(".json"):
                    # Load json data from manifest file as a python dict
                    all_manifests.append(pre_process_manifest(manifest_file_label,
                        json.load(manifest_file, object_pairs_hook=collections.OrderedDict)))
                else:
                    logger.error(LOG_TAG, "The --manifests-format arg or " + manifest_file_label +
                        " file format/extension must equal 'yaml', 'yml' or 'json'.")
                    return (1, None)

                return (0, all_manifests)

            except ValueError as err:
                logger.error(LOG_TAG, "Loading json from " + manifest_file_label +
                             " failed with err:\n" + str(err))
                return (1, None)
    except Exception as err:
        logger.error(LOG_TAG, "Opening " + manifest_file_label + " failed with err:\n" + str(err))
        return (1, None)

def process_manifest(command_type, manifest_label, manifest):
    "Process manifest."

    if not manifest or not isinstance(manifest, dict):
        logger.error(LOG_TAG, "The manifest object created for " + manifest_label + " is not a dict")
        return 1

    safe_manifest = data_utils.delete_keys_from_dict(manifest, PRIVATE_FIELDS_LIST, [None, "***"])
    logger.vverbose(LOG_TAG, manifest_label + ":\n" + json.dumps(safe_manifest, sort_keys=False, indent=4, default=str))

    project_config_dict = data_utils.get_ordered_dict_from_dict(manifest, "project", None)
    if not project_config_dict:
        logger.error(LOG_TAG, "The 'project' value is not set or not a dict")
        return 1

    (return_value, project_config) = ProjectConfig.create(project_config_dict, manifest_label)
    if str(return_value) != "0":
        return return_value
    if not project_config or not isinstance(project_config, ProjectConfig):
        logger.error(LOG_TAG, "Failed to create project_config")
        return 1

    project_root_dir = project_config.project_root_dir
    logger.debug(LOG_TAG, "project_root_dir: \"" + str(project_root_dir) + "\"")



    module_configs = []
    if project_config.modules_dict:
        logger.log_debug_no_format("")

        (return_value, modules_config) = ModulesConfig.create(project_config.modules_dict)
        if str(return_value) != "0":
            return return_value
        if not modules_config or not isinstance(modules_config, ModulesConfig):
            logger.error(LOG_TAG, "Failed to create all_modules_config")
            return 1

        i = 1
        # For all module_name, module_config in all_modules_config.module_list
        for module_name, module_config_dict in modules_config.module_list.items():
            if i > 1:
                logger.log_verbose_no_format("")

            if data_utils.get_bool_from_dict(module_config_dict, "ignore", False):
                logger.debug(LOG_TAG, "Ignoring module " + str(i) + " \"" + module_name + "\"")
                continue

            logger.debug(LOG_TAG, "Creating module_config for module " + str(i) + " \"" + module_name + "\"")

            (return_value, module_config) = ModuleConfig.create(
                project_config, module_name, module_config_dict, module_configs)
            if str(return_value) != "0":
                return return_value
            if not module_config or not isinstance(module_config, ModuleConfig):
                logger.error(LOG_TAG, "Failed to create module_config for module " + str(i) + " \"" + module_name + "\"")
                return 1

            module_configs.append(module_config)
            i += 1

        logger.log_debug_no_format("")



    # The project must be setup before setting up modules
    if command_type == "setup":
        return_value = process_project(command_type, project_config)
        if str(return_value) != "0":
            logger.error(LOG_TAG, command_type + " project failed")
            return return_value
    elif command_type == "remove":
        # If project_root_dir does not exist
        if not os.path.isdir(project_root_dir):
            logger.error(LOG_TAG, "Nothing to remove since project_root_dir" +
                " does not exist at \"" + project_root_dir + "\"")
            return 0



    if module_configs:
        logger.log_debug_no_format("\n\n")
        logger.info(LOG_TAG, "Processing modules")

        module_num = 1
        # For all module_config in module_configs
        for module_config in module_configs:
            if module_num > 1:
                logger.log_debug_no_format("\n\n")

            logger.info(LOG_TAG, "Processing module " + str(module_num) + " \"" + module_config.module_name + "\"")

            return_value = process_module(module_num, command_type, project_config, modules_config, module_config)
            if str(return_value) != "0":
                logger.error(LOG_TAG, command_type + " module " + str(module_num) + " \"" + module_config.module_name + "\" failed")
                return return_value

            module_num += 1

        logger.log_debug_no_format("")
        logger.info(LOG_TAG, "All modules processed")



    # The project must be removed after removing modules
    if command_type == "remove":
        if project_config.modules_dict:
            logger.log_debug_no_format("\n\n")
        return_value = process_project(command_type, project_config)
        if str(return_value) != "0":
            logger.error(LOG_TAG, command_type + " project failed")
            return return_value

    return 0



DESCRIPTION = """
temporal-src-network command is used to build temporal sources network.

Usage:
  temporal-src-network [options] command_type manifests...
"""

EPILOG = """
The 'command_type' and 'manifests' arguments must be passed.

The manifests must either be in yaml or json format with the respective file extension,
unless the '--manifests-format' argument is passed. If manifest is a
fd path, then it will be assumed to be in yaml format unless '--manifests-format'
argument is passed.
"""

DESCRIPTION_EXTRA = """
Example YAML manifest:

```yaml

```
"""


class ShowHelpExtraAction(argparse.Action):
    "Show temporal-src-network extra help"

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        print("\n" + DESCRIPTION_EXTRA)
        sys.exit(0)


def main(argv):
    "temporal-src-network main."
    # pylint: disable=unused-variable

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawTextHelpFormatter)

    # Add supported arguments to parser
    # parser.add_argument("--help-extra", help="show extra help message and exit", nargs=0, action=ShowHelpExtraAction)

    parser.add_argument("--version", action="version", version=VERSION)

    parser.add_argument("-v", help="""increase log level,
pass one or more times for 'debug', 'verbose' or `vverbose',
(default: 'normal')""", dest="log_level", action="append_const", const=1)

    parser.add_argument("-q", "--quiet", action="store_true", help="""set log level to 'off',
(default: false)""")

    parser.add_argument("--manifests-format", help="""force consider manifest to be in desired format,
(default: use file extension, values: 'yaml', 'yml' or 'json')""")

    parser.add_argument("command_type", help="""command type to run:
  'setup' - setup project and modules
  'remove' - remove project and modules""")

    #subparsers = parser.add_subparsers(title="command_types", dest="command_type", required=True)

    #parser_setup = subparsers.add_parser("setup", help="setup project and modules") # type: ignore
    #parser_remove = subparsers.add_parser("remove", help="remove project and modules") # type: ignore

    parser.add_argument("manifests", nargs='+', help="one or more paths to manifest file(s)")


    # If no args passed, then show help and exit
    if len(argv) == 0:
        parser.print_help()
        return 1

    # Parse args
    args = parser.parse_args(argv)

    # Set args to local variables
    manifests_format = str(args.manifests_format or "")
    manifest_file_paths_list = args.manifests



    # Setup logger
    if args.quiet:
        log_level = logger.LOG_LEVEL_OFF
    else:
        log_level_index = logger.LOG_LEVELS.index(logger.DEFAULT_LOG_LEVEL)

        # For each "-v" flag, adjust the LOG_LEVEL between 0 and len(LOG_LEVELS) - 1
        for adjustment in args.log_level or ():
            log_level_index = min(len(logger.LOG_LEVELS) - 1, max(log_level_index + adjustment, 0))

        log_level = logger.LOG_LEVELS[log_level_index]

    logger.setup_logger(logger_log_level=log_level)



    logger.info(LOG_TAG, "Starting temporal_src_network")

    command_type = args.command_type
    if not command_type or command_type not in ["setup", "remove"]:
        logger.error(LOG_TAG, "The command_type \"" + command_type + "\" passed is not supported")
        return 1

    # For all manifests in manifest_file_paths_list
    return_value = "1"
    manifest_file_number = 1
    for manifest_file_path in manifest_file_paths_list:
        if len(manifest_file_paths_list) == 1:
            manifest_file_label = "manifest file at \"" + str(manifest_file_path or "") + "\""
        else:
            manifest_file_label = "manifest file " + str(manifest_file_number) + \
            " at \"" + str(manifest_file_path or "") + "\""

        if manifest_file_number > 1:
            logger.log_debug_no_format("\n\n\n")
        logger.info(LOG_TAG, "Processing " + command_type + " command for " + manifest_file_label)

        # Process manifest
        (return_value, manifests) = read_manifests_from_file(
            manifest_file_label, manifest_file_path, manifests_format)
        if str(return_value) != "0":
            break
        if not manifests or not isinstance(manifests, list):
            logger.error(LOG_TAG, "Failed to read manifest(s) from " + manifest_file_label)
            return_value = 1
            break

        manifest_number = 1
        manifests_count = len(manifests)
        for manifest in manifests:
            # Process manifest
            manifest_label = ("manifest " + (str(manifest_number) + " "
                if len(manifests) > 1 else "") + "in ") + manifest_file_label

            if manifest_number > 1:
                logger.log_debug_no_format("\n\n\n")
            if manifests_count > 1:
                logger.info(LOG_TAG, "Processing " + command_type + " command for " + manifest_label)

            return_value = process_manifest(command_type, manifest_label, manifest)
            if str(return_value) != "0":
                logger.error(LOG_TAG, "Processing " + command_type + " command for " +
                    manifest_label + " failed with exit code \"" + str(return_value) + "\"")
                break

            if manifests_count > 1:
                logger.info(LOG_TAG, "The " + command_type + " command for " + manifest_label + " complete")

            manifest_number += 1

        if str(return_value) != "0":
            break

        logger.info(LOG_TAG, "The " + command_type + " command for " + manifest_file_label + " complete")

        manifest_file_number += 1

    if not str(return_value).isdigit() or int(str(return_value)) < 0 or int(str(return_value)) > 255:
        return_value = 255

    return int(str(return_value))


#if __name__ == "__main__":
    #sys.exit(main(sys.argv[1:]))
