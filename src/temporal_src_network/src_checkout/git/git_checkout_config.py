import re

from .git_version import GitVersion

from ..checkout_config import CheckoutConfig

from ...data import data_utils
from ...data.data_utils import log_value
from ...data.data_utils import log_private_value
from ...logger.logger_core import logger
from ...manifest.modules_config import ModulesConfig
from ...manifest.project_config import ProjectConfig
from ...manifest.version_config import VersionConfig

LOG_TAG = "git_checkout_config"

class GitCheckoutConfig(CheckoutConfig):
    "Git Checkout config."

    CHECKOUT_TYPE = "git"

    REGEX_SSH_GIT_REPO_URL = r'^git@([^:]+):(.*)$'


    MINIMUM_GIT_VERSION = "2.18"
    """
    Minimum required git version.

    - Auth header not supported before 2.9
    - Wire protocol v2 not supported before 2.18
    """

    MINIMUM_GIT_LFS_VERSION = "2.1"
    """
    Minimum required git-lfs version for lfs.

    - Auth header not supported before 2.1
    """

    MINIMUM_GIT_CONE_SPARSE_CHECKOUT_VERSION = "2.26"
    """
    Minimum required git version for cone mode sparse checkout.

    - sparse checkout support and `core.sparseCheckout` config
      were added in git v1.7 (2010/09/07)
      - https://git-scm.com/docs/git-read-tree#_sparse_checkout
      - https://github.com/git/git/blob/master/Documentation/RelNotes/1.7.0.txt

    - `git sparse-checkout` command and `core.spareCheckoutCone` config
      were added in git v2.25 (2020/01/13)
      - https://git-scm.com/docs/git-sparse-checkout/2.25.0

    - `git sparse-checkout set --cone` was added in git v2.26 (2020/03/23)
      - https://git-scm.com/docs/git-sparse-checkout/2.26.0

    - `git sparse-checkout set --no-cone` was added in git v2.35 (2022/01/24)
      - https://git-scm.com/docs/git-sparse-checkout/2.35.0

    - `git sparse-checkout --skip-checks` was added as hidden flag in git v2.36 (2022/04/18)
      For `--cone` mode, the following errors will be generated:
      - Directory is passed with a leading slash: `specify directories rather than patterns (no leading slash)`
      - Directory is passed with a leading exclamation mark: `specify directories rather than patterns.  If your directory starts with a '!', pass --skip-checks`
      - Directory is passed with a pattern match character: `specify directories rather than patterns.  If your directory really has any of '*?[]\' in it, pass --skip-checks`
      - A file path is passed instead of a directory: `'<file_path>' is not a directory; to treat it as a directory anyway, rerun with --skip-checks`
      For `--no-cone` mode, the following warning will be generated:
      - File path is passed without a leading slash: `pass a leading slash before paths such as '<file_pattern>' if you want a single file.`

      - https://git-scm.com/docs/git-sparse-checkout/2.36.0
      - https://github.com/git/git/commit/8dd7c4739bded62175bea1f7518d993b39b51f90
      - https://github.com/git/git/commit/4ce504360bc3b240e570281fabe00a85027532c3

    - `git sparse-checkout set --cone` was made default in git v2.37 (2022/06/27)
      - https://git-scm.com/docs/git-sparse-checkout/2.37.0

    - Exclude patterns may require manual entry
      - https://stackoverflow.com/a/59515426

    - sparse checkout support was added to action/checkout workflow in v3.5.3 (2023/06/09)
      - https://github.com/actions/checkout/commit/d106d4669b3bfcb17f11f83f98e1cab478e9f635
      - https://github.com/actions/checkout/pull/1369
      - https://github.com/actions/checkout/releases/tag/v3.5.3
    """

    MINIMUM_GIT_SPARSE_CHECKOUT_SKIP_CHECKS_VERSION = "2.36"
    """
    Minimum required git version for `git sparse-checkout --skip-checks`.

    See also {@link #MINIMUM_GIT_CONE_SPARSE_CHECKOUT_VERSION}
    """

    def __init__(self, *, _not_called_from_create=True):
        super().__init__(GitCheckoutConfig.CHECKOUT_TYPE)

        if _not_called_from_create:
            raise RuntimeError("Object must be created with GitCheckoutConfig.create()")

        self.src_url = None
        self.ref = None
        self.commit = None
        self.sparse_checkout = None
        self.sparse_checkout_cone_mode = True
        self.sparse_checkout_skip_checks = False
        self.sparse_checkout_level_mode = "add" # add|override
        self.fetch_depth = 1
        self.fetch_tags = False
        self.show_progress = False
        self.lfs = False
        self.submodules = False
        self.recursive_submodules = False
        self.git_auth_token = None
        self.ssh_strict = True
        self.persist_credentials = False
        self.set_safe_directory = "ignore" # add|add_and_remove|ignore

    @classmethod
    def create(cls, git, command_type, project_config=None, modules_config=None, version_config=None):
        checkout_config = cls(_not_called_from_create=False)

        if project_config and isinstance(project_config, ProjectConfig):
            is_project_checkout = True

            label = "project"

            modules_src_checkout = None
            module_src_checkout = None
            main_src_checkout = project_config.src_checkout_dict
        elif modules_config and isinstance(modules_config, ModulesConfig) and \
            version_config and isinstance(version_config, VersionConfig):
            is_project_checkout = False

            module_config = version_config.module_config

            label = "module \"" + module_config.module_name + "\"" + \
            " version \"" + version_config.version_name + "\""

            modules_src_checkout = modules_config.src_checkout_dict
            module_src_checkout = module_config.src_checkout_dict
            main_src_checkout = version_config.src_checkout_dict
        else:
            logger.error(LOG_TAG, "Either (project_config) or (modules_config and version_config)" +
                         " must be passed to CheckoutConfig.create()")
            return (1, None)

        checkout_config.src_url = data_utils.get_str_from_dict(
            [main_src_checkout, module_src_checkout],
            "src_url", checkout_config.src_url)



        checkout_config.fetch_depth = max(data_utils.get_int_from_dict(
            [main_src_checkout, module_src_checkout],
            "fetch_depth", checkout_config.fetch_depth), 0)

        checkout_config.fetch_tags = data_utils.get_bool_from_dict(
            [main_src_checkout, module_src_checkout],
            "fetch_tags", checkout_config.fetch_tags)

        checkout_config.show_progress = data_utils.get_bool_from_dict(
            [main_src_checkout, module_src_checkout],
            "show_progress", checkout_config.show_progress)

        checkout_config.lfs = data_utils.get_bool_from_dict(
            [main_src_checkout, module_src_checkout],
            "lfs", checkout_config.lfs)

        submodules_string = data_utils.get_str_from_dict(
            [main_src_checkout, module_src_checkout],
            "submodules", "DISABLE").upper()
        if submodules_string == "ENABLE":
            checkout_config.submodules = True
            checkout_config.recursive_submodules = False
        elif submodules_string == "RECURSIVE":
            checkout_config.submodules = True
            checkout_config.recursive_submodules = True



        ref = data_utils.get_str_from_dict(main_src_checkout, "ref", None)
        # If commit hash
        if ref and re.match('^[a-zA-Z0-9]{40}$', ref):
            checkout_config.commit = ref
        # Else `refs/heads/*` or `refs/tags/*`
        else:
            checkout_config.ref = ref


        checkout_config.sparse_checkout_cone_mode = data_utils.get_bool_from_dict(
            [main_src_checkout, module_src_checkout],
            "sparse_checkout_cone_mode", checkout_config.sparse_checkout_cone_mode)

        checkout_config.sparse_checkout_skip_checks = data_utils.get_bool_from_dict(
            [main_src_checkout, module_src_checkout],
            "sparse_checkout_skip_checks", checkout_config.sparse_checkout_skip_checks)

        if is_project_checkout:
            project_sparse_checkout = data_utils.get_str_from_dict(main_src_checkout, "sparse_checkout", None)
            if project_sparse_checkout:
                checkout_config.sparse_checkout = project_sparse_checkout.strip().splitlines()



            # Get git_auth_token from env var or key of main_src_checkout
            (found, git_auth_token) = data_utils.get_str_from_env_or_dict(
                main_src_checkout, "git_auth_token_var", "git_auth_token")
            if found and isinstance(git_auth_token, str):
                checkout_config.git_auth_token = git_auth_token
        else:
            sparse_checkout_level_mode = data_utils.get_str_from_dict(main_src_checkout, "sparse_checkout_level_mode", None)
            module_sparse_checkout = data_utils.get_str_from_dict(module_src_checkout, "sparse_checkout", None)
            version_sparse_checkout = data_utils.get_str_from_dict(main_src_checkout, "sparse_checkout", None)
            if not sparse_checkout_level_mode or sparse_checkout_level_mode == "add":
                sparse_checkout = []
                if module_sparse_checkout:
                    sparse_checkout.extend(module_sparse_checkout.strip().splitlines())
                if version_sparse_checkout:
                    sparse_checkout.extend(version_sparse_checkout.strip().splitlines())
                checkout_config.sparse_checkout = sparse_checkout
            elif sparse_checkout_level_mode == "override":
                if version_sparse_checkout:
                    checkout_config.sparse_checkout = version_sparse_checkout.strip().splitlines()
            else:
                logger.error(LOG_TAG, "The " + label + " sparse_checkout_level_mode" +
                             " \"" + sparse_checkout_level_mode + "\" must be 'add' or 'override'")
                return (1, None)




            # Get git_auth_token from env var or key of main_src_checkout
            (found, git_auth_token) = data_utils.get_str_from_env_or_dict(
                main_src_checkout, "git_auth_token_var", "git_auth_token")
            if found and isinstance(git_auth_token, str):
                checkout_config.git_auth_token = git_auth_token
            else:
                # Else get git_auth_token from env var or key of module_src_checkout
                (found, git_auth_token) = data_utils.get_str_from_env_or_dict(
                    module_src_checkout, "git_auth_token_var", "git_auth_token")
                if found and isinstance(git_auth_token, str):
                    checkout_config.git_auth_token = git_auth_token
                else:
                    # Else get git_auth_token from env var or key of modules_src_checkout
                    (found, git_auth_token) = data_utils.get_str_from_env_or_dict(
                        modules_src_checkout, "git_auth_token_var", "git_auth_token")
                    if found and isinstance(git_auth_token, str):
                        checkout_config.git_auth_token = git_auth_token



        # If token is set, like by workflow actions, then convert ssh
        # to https urls so that token can be used with
        # `http.<src_url>.extraheader` git config to fetch repos.
        # If token is not set, like by local builds, then ssh urls will
        # be used as is to fetch repos with the ssh keys configured by
        # user themselves in their `~/.ssh` directory.
        # actions/checkout does this replacement when ssh-key is
        # set instead.
        # We currently do not support `ssh-key` config.
        # For example `git@github.com:` to `https://github.com/`
        if checkout_config.git_auth_token and checkout_config.src_url and \
            re.match(GitCheckoutConfig.REGEX_SSH_GIT_REPO_URL, checkout_config.src_url):
            checkout_config.src_url = re.sub(pattern=GitCheckoutConfig.REGEX_SSH_GIT_REPO_URL,
                                              repl='https://\\1/\\2',
                                              string=checkout_config.src_url)



        checkout_config.ssh_strict = data_utils.get_bool_from_dict(
            [main_src_checkout, module_src_checkout],
            "ssh_strict", checkout_config.ssh_strict)
        git.set_ssh_strict(checkout_config.ssh_strict)

        checkout_config.persist_credentials = data_utils.get_bool_from_dict(
            [main_src_checkout, module_src_checkout],
            "persist_credentials", checkout_config.persist_credentials)



        checkout_config.set_safe_directory = data_utils.get_str_from_dict(
            [main_src_checkout, module_src_checkout],
            "set_safe_directory", checkout_config.set_safe_directory)
        if checkout_config.set_safe_directory not in ["add", "add_and_remove", "ignore"]:
            logger.error(LOG_TAG, "The " + label + " set_safe_directory" +
                " \"" + checkout_config.set_safe_directory + "\"" +
                " must be 'add', 'add_and_remove' or 'ignore'")
            return (1, None)



        logger.vverbose(LOG_TAG, label + " git_checkout_config:\n" + checkout_config.to_string() + "\n")



        # Ensure required git versions exist
        if command_type in ["setup"]:
            return_value = cls.ensure_required_git_versions(git, checkout_config)
            if str(return_value) != "0":
                return (return_value, None)



        # Ensure src_url is valid and exists
        if not checkout_config.src_url or not git.is_valid_repo_url(checkout_config.src_url):
            logger.error(LOG_TAG, "The " + label +
                         " src_url \"" + str(checkout_config.src_url) + "\"" +
                         " is not valid, does not exist or failed to connect to it")
            return (1, None)

        return (0, checkout_config)

    @classmethod
    def ensure_required_git_versions(cls, git, checkout_config):
         # Ensure minimum required git version is installed
        (return_value, minimum_git_version) = GitVersion.create(GitCheckoutConfig.MINIMUM_GIT_VERSION)
        if str(return_value) != "0":
            return return_value
        elif not minimum_git_version or not isinstance(minimum_git_version, GitVersion):
            logger.error(LOG_TAG, "Failed to get minimum_git_version")
            return 1

        if not git.git_version.ensure_minimum(minimum_git_version):
            logger.error(LOG_TAG, "The 'git' version must be '>= " + minimum_git_version.full + "'" +
                " but current version is '= " + git.git_version.full + "'")
            return 1


        # Ensure minimum required git-lfs version is installed for lfs
        if checkout_config.lfs:
            (return_value, git_lfs_version) = git.get_git_lfs_version()
            if str(return_value) != "0":
                return (return_value, None)
            elif not git_lfs_version or not isinstance(git_lfs_version, GitVersion):
                logger.error(LOG_TAG, "Failed to get git_lfs_version")
                return 1

            (return_value, minimum_git_lfs_version) = GitVersion.create(GitCheckoutConfig.MINIMUM_GIT_LFS_VERSION)
            if str(return_value) != "0":
                return (return_value, None)
            elif not minimum_git_lfs_version or not isinstance(minimum_git_lfs_version, GitVersion):
                logger.error(LOG_TAG, "Failed to get minimum_git_lfs_version")
                return 1

            if not git_lfs_version.ensure_minimum(minimum_git_lfs_version):
                logger.error(LOG_TAG, "The 'git-lfs' version must be '>= " + minimum_git_lfs_version.full + "'" +
                    " for lfs but current version is '= " + git_lfs_version.full + "'")
                return 1


        # Ensure minimum required git version is installed for cone mode sparse checkout
        # We don't need to check no-cone mode support added in `v1.7`, since it is already lower than MINIMUM_GIT_VERSION
        if checkout_config.sparse_checkout and checkout_config.sparse_checkout_cone_mode:
            (return_value, minimum_git_cone_sparse_checkout_version) = GitVersion.create(
                GitCheckoutConfig.MINIMUM_GIT_CONE_SPARSE_CHECKOUT_VERSION)
            if str(return_value) != "0":
                return (return_value, None)
            elif not minimum_git_cone_sparse_checkout_version or not isinstance(minimum_git_cone_sparse_checkout_version, GitVersion):
                logger.error(LOG_TAG, "Failed to get minimum_git_cone_sparse_checkout_version")
                return 1

            if not git.git_version.ensure_minimum(minimum_git_cone_sparse_checkout_version):
                logger.error(LOG_TAG, "The 'git' version must be '>= " + minimum_git_cone_sparse_checkout_version.full + "'" +
                    " for cone mode sparse checkout but current version is '= " + git.git_version.full + "'")
                return 1

        return 0



    def to_string(self):
        return CheckoutConfig.to_string(self) + \
        "\nsrc_url: " + log_value(self.src_url) + \
        "\nref: " + log_value(self.ref) + \
        "\ncommit: " + log_value(self.commit) + \
        "\nsparse_checkout: " + log_value(self.sparse_checkout) + \
        "\nsparse_checkout_cone_mode: " + log_value(self.sparse_checkout_cone_mode) + \
        "\nsparse_checkout_skip_checks: " + log_value(self.sparse_checkout_skip_checks) + \
        "\nsparse_checkout_level_mode: " + log_value(self.sparse_checkout_level_mode) + \
        "\nfetch_depth: " + log_value(self.fetch_depth) + \
        "\nfetch_tags: " + log_value(self.fetch_tags) + \
        "\nshow_progress: " + log_value(self.show_progress) + \
        "\nlfs: " + log_value(self.lfs) + \
        "\nsubmodules: " + log_value(self.submodules) + \
        "\nrecursive_submodules: " + log_value(self.recursive_submodules) + \
        "\ngit_auth_token: " + log_private_value(self.git_auth_token) + \
        "\nssh_strict: " + log_value(self.ssh_strict) + \
        "\npersist_credentials: " + log_value(self.persist_credentials) + \
        "\nset_safe_directory: " + log_value(self.set_safe_directory)
