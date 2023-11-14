import os

from . import git_auth_manager
from . import git_checkout_config
from . import git_command_manager
from . import git_ref_utils

from .. import src_provider

from ...file import file_utils
from ...logger.logger_core import logger

LOG_TAG = "git_src_provider"

class GitSrcProvider(src_provider.SrcProvider):
    "Provider for checking out a git source."

    def __init__(self, git, auth_manager, repo_root_dir, checkout_config, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with GitSrcProvider.create_*()")

        self.git = git
        self.auth_manager = auth_manager
        self.repo_root_dir = repo_root_dir
        self.checkout_config = checkout_config

    @classmethod
    def create_for_project(cls, command_type, project_config):
        (return_value, git) = git_command_manager.GitCommandManager.create(
            command_type, project_config.project_root_dir)
        if str(return_value) != "0":
            return (return_value, None)
        if not git:
            logger.error(LOG_TAG, "Failed to create git_command_manager for the project")
            return (1, None)

        (return_value, checkout_config) = git_checkout_config.GitCheckoutConfig.create(
            git, command_type, project_config=project_config)
        if str(return_value) != "0":
            return (return_value, None)
        if not checkout_config or not isinstance(checkout_config, git_checkout_config.GitCheckoutConfig):
            logger.error(LOG_TAG, "Failed to create checkout_config forthe project")
            return (1, None)

        (return_value, auth_manager) = git_auth_manager.GitAuthManager.create(git, checkout_config)
        if str(return_value) != "0":
            return (return_value, None)
        if not git:
            logger.error(LOG_TAG, "Failed to create git_auth_manager for the project")
            return (1, None)

        return (0, cls(git, auth_manager, project_config.project_root_dir, checkout_config, _not_called_from_create=False))

    @classmethod
    def create_for_version(cls, command_type, modules_config, version_config):
        label = "module" + " \"" + version_config.module_config.module_name + "\"" + \
                " version \"" + version_config.version_name + "\""

        (return_value, git) = git_command_manager.GitCommandManager.create(
            command_type, version_config.version_root_dir)
        if str(return_value) != "0":
            return (return_value, None)
        if not git:
            logger.error(LOG_TAG, "Failed to create git_command_manager for " + label)
            return (1, None)

        (return_value, checkout_config) = git_checkout_config.GitCheckoutConfig.create(
            git, command_type, modules_config=modules_config, version_config=version_config)
        if str(return_value) != "0":
            return (return_value, None)
        if not checkout_config or not isinstance(checkout_config, git_checkout_config.GitCheckoutConfig):
            logger.error(LOG_TAG, "Failed to create checkout_config for " + label)
            return (1, None)

        (return_value, auth_manager) = git_auth_manager.GitAuthManager.create(git, checkout_config)
        if str(return_value) != "0":
            return (return_value, None)
        if not git:
            logger.error(LOG_TAG, "Failed to create git_auth_manager for " + label)
            return (1, None)

        return (0, cls(git, auth_manager, version_config.version_root_dir, checkout_config, _not_called_from_create=False))



    # - https://github.com/actions/checkout/blob/v4.0.0/src/git-source-provider.ts#L15
    def checkout_src(self):
        checkout_config = self.checkout_config
        repo_root_dir = self.repo_root_dir
        auth_configured = False
        set_safe_directory_configured = False

        try:
            logger.debug(LOG_TAG, "Checkout source at " + checkout_config.src_url)
            logger.debug(LOG_TAG, "repo_root_dir: \"" + repo_root_dir + "\"")

            # Create repo_root_dir if it does not already exist
            error = file_utils.create_dir_file(LOG_TAG, "repo root", repo_root_dir)
            if error is not None:
                logger.error(LOG_TAG, error)
                return 1

            # repo_root_dir should have been deleted before this method is
            # called, so we do not need to do any cleanup.
            # https://github.com/actions/checkout/blob/v4.0.0/src/git-source-provider.ts#L63
            # https://github.com/actions/checkout/blob/v4.0.0/src/git-directory-helper.ts#L9



            if checkout_config.set_safe_directory in ["add", "add_and_remove"]:
                # Setup the repo root directory as a safe directory,
                # so if we pass this into a container job with a different
                # user it doesn't fail, Otherwise all git commands we
                # run in a container fail.

                # TODO: Configure temp global config

                logger.debug(LOG_TAG, "Adding repo root directory to the 'safe.directory' global git config")
                return_value = self.git.config_add_if_no_exist(True, "safe.directory", repo_root_dir, True)
                if str(return_value) != "0":
                    logger.error(LOG_TAG, "Failed to add repo root directory to the 'safe.directory' global git config")
                    return return_value
                set_safe_directory_configured = True



            # Determine the default branch
            # We always get default branch so that we can pass it to "git init"
            # to hide the "Using 'master'" branch verbose hint message.
            logger.verbose(LOG_TAG, "Determining the default branch")
            (return_value, default_branch) = self.git.get_default_branch(checkout_config.src_url)
            if str(return_value) != "0":
                return return_value

            if not checkout_config.ref and not checkout_config.commit:
                if not default_branch:
                    logger.error(LOG_TAG, "The default branch not set")
                    return 1

                logger.verbose(LOG_TAG, "Using default branch \"" + default_branch + "\" as ref")
                checkout_config.ref = default_branch


            # Initialize the repository
            if not os.path.isdir(os.path.join(repo_root_dir, ".git")):
                logger.verbose(LOG_TAG, "Initializing the repository: " + checkout_config.src_url)
                return_value = self.git.init(default_branch=default_branch)
                if str(return_value) != "0":
                    return return_value


                return_value = self.git.remote_add("origin", checkout_config.src_url)
                if str(return_value) != "0":
                    return return_value



            # Disable automatic garbage collection
            logger.verbose(LOG_TAG, "Disabling automatic garbage collection")
            if not self.git.disable_automatic_garbage_collection():
                logger.verbose(LOG_TAG, "IUnable to turn off git automatic garbage collection." +
                    " The git fetch operation may trigger garbage collection and cause a delay.")



            # Configure auth
            logger.verbose(LOG_TAG, "Configuring auth")
            return_value = self.auth_manager.configure_auth()
            if str(return_value) != "0":
                return return_value
            auth_configured = True



            # LFS install
            if checkout_config.lfs:
                logger.verbose(LOG_TAG, "Installing LFS config")
                return_value = self.git.lfs_install()
                if str(return_value) != "0":
                    return return_value



            # Fetch
            logger.verbose(LOG_TAG, "Fetching the repository")
            fetch_filter = None
            if checkout_config.sparse_checkout:
                fetch_filter = "blob:none"

            show_progress = checkout_config.show_progress

            if checkout_config.fetch_depth and checkout_config.fetch_depth <= 0:
                # Fetch all branches and tags
                ref_spec = git_ref_utils.get_ref_spec_for_all_history(
                    checkout_config.ref, checkout_config.commit)

                return_value = self.git.fetch(ref_spec,
                                              fetch_filter=fetch_filter,
                                              show_progress=show_progress)
                if str(return_value) != "0":
                    return return_value


                # When all history is fetched, the ref we're interested in may have moved to a different
                # commit (push or force push). If so, fetch again with a targeted refspec.
                (return_value, ref_exists) = git_ref_utils.test_ref(
                    self.git, checkout_config.ref, checkout_config.commit)
                if str(return_value) != "0":
                    return return_value
                if not ref_exists:
                    (return_value, ref_spec) = git_ref_utils.get_ref_spec(
                                            checkout_config.ref, checkout_config.commit)
                    if str(return_value) != "0":
                        return return_value

                    return_value = self.git.fetch(
                        ref_spec, fetch_filter=fetch_filter, show_progress=show_progress)
                    if str(return_value) != "0":
                        return return_value
            else:
                (return_value, ref_spec) = git_ref_utils.get_ref_spec(
                    checkout_config.ref, checkout_config.commit)
                if str(return_value) != "0":
                    return return_value

                return_value = self.git.fetch(ref_spec, fetch_filter=fetch_filter,
                                              fetch_depth=checkout_config.fetch_depth,
                                              fetch_tags=checkout_config.fetch_tags,
                                              show_progress=show_progress)
                if str(return_value) != "0":
                    return return_value



            # Checkout info
            logger.verbose(LOG_TAG, "Determining the checkout info")
            (return_value, checkout_ref, checkout_start_point) = git_ref_utils.get_checkout_info(
                self.git, checkout_config.ref, checkout_config.commit)
            if str(return_value) != "0":
                return return_value



            # LFS fetch
            # Explicit lfs-fetch to avoid slow checkout (fetches one lfs object at a time).
            # Explicit lfs fetch will fetch lfs objects in parallel.
            # For sparse checkouts, let `checkout` fetch the needed objects lazily.
            if checkout_config.lfs and not checkout_config.sparse_checkout:
                logger.verbose(LOG_TAG, "Fetching LFS objects")
                return_value = self.git.lfs_fetch(checkout_start_point if checkout_start_point else checkout_ref)
                if str(return_value) != "0":
                    return return_value



            # Sparse checkout
            if checkout_config.sparse_checkout:
                if checkout_config.sparse_checkout_cone_mode:
                    logger.verbose(LOG_TAG, "Setting up sparse checkout with cone mode")
                    return_value = self.git.sparse_checkout(checkout_config.sparse_checkout,
                        checkout_config.sparse_checkout_skip_checks)
                else:
                    logger.verbose(LOG_TAG, "Setting up sparse checkout with no-cone mode")
                    return_value = self.git.sparse_checkout_no_cone_mode(checkout_config.sparse_checkout)
                if str(return_value) != "0":
                    return return_value



            # Checkout
            logger.verbose(LOG_TAG, "Checking out the ref")
            return_value = self.git.checkout(checkout_ref, checkout_start_point,
                                             show_progress=show_progress)
            if str(return_value) != "0":
                return return_value



            # Submodules
            if checkout_config.submodules:
                # TODO: Temporarily override global config

                # Checkout submodules
                logger.verbose(LOG_TAG, "Fetching submodules")
                return_value = self.git.submodule_sync(
                    checkout_config.recursive_submodules)
                if str(return_value) != "0":
                    return return_value

                return_value = self.git.submodule_update(
                    checkout_config.fetch_depth,
                    checkout_config.recursive_submodules)
                if str(return_value) != "0":
                    return return_value

                return_value = self.git.submodule_for_each(
                    "git config --local gc.auto 0",
                    checkout_config.recursive_submodules)
                if str(return_value) != "0":
                    return return_value

                # TODO: Persist credentials



            # TODO: Get commit information

            # Log commit sha
            self.git.log1("--format='%H'")

            # TODO: Check for incorrect pull request merge commit

            return 0

        finally:
            if set_safe_directory_configured and checkout_config.set_safe_directory in ["add_and_remove"]:
                logger.debug(LOG_TAG, "Removing repo root directory from the 'safe.directory' global git config")
                return_value = self.git.config_unset_if_exist(True, "safe.directory", repo_root_dir, True)
                if str(return_value) != "0":
                    logger.error(LOG_TAG, "Failed to remove repo root directory from the 'safe.directory' global git config")

            if auth_configured and not checkout_config.persist_credentials:
                logger.verbose(LOG_TAG, "Removing auth")
                self.auth_manager.remove_auth()
