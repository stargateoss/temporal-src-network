# pylint: disable=unused-variable
# pyright: reportUnusedVariable=false

import os
import re

from . import git_ref_utils
from .git_checkout_config import GitCheckoutConfig
from .git_version import GitVersion

from ...data import data_utils
from ...logger.logger_core import logger
from ...shell import shell_utils

LOG_TAG = "git_command_manager"

class GitCommandManager:
    "The git command manager."

    def __init__(self, repo_root_dir, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with GitCommandManager.create()")

        self.git_version = None
        self.repo_root_dir = repo_root_dir
        self.ssh_strict = True

    @classmethod
    def create(cls, command_type, repo_root_dir):
        git = cls(repo_root_dir, _not_called_from_create=False)

        # git_checkout_config only uses git_version for setup command
        if command_type in ["setup"]:
            (return_value, git_version) = git.get_git_version()
            if str(return_value) != "0":
                return (return_value, None)
            elif not git_version or not isinstance(git_version, GitVersion):
                logger.error(LOG_TAG, "Failed to get git_version")
                return (1, None)

            git.git_version = git_version

        return (0, git)

    def set_ssh_strict(self, ssh_strict):
        if ssh_strict is not None and isinstance(ssh_strict, bool):
            self.ssh_strict = ssh_strict



    def get_git_ssh_command(self):
        command = "ssh"

        if self.ssh_strict:
            # Do not show authenticity prompt if ssh keys are not
            # configured in `known_hosts`, otherwise command will hang
            # forever until input is provided, and timeout will not work
            # either since ssh will be a child process.
            # `The authenticity of host 'github.com (ip)' can't be established.
            #  Are you sure you want to continue connecting (yes/no)?`
            # - https://man7.org/linux/man-pages/man5/ssh_config.5.html
            command += " -o StrictHostKeyChecking=yes"

            # actions/checkout also adds `CheckHostIP=no` if `ssh-strict` is `true` (default).
            # Currently, not sure whether we should.
            # https://github.com/actions/checkout/blob/v4.1.0/src/git-auth-helper.ts#L261
            # command += " -o CheckHostIP=no"

        return command


    def exec(self, args, capture, cwd=None, timeout=None, silent=False, allow_all_exit_codes=False, redirect_stderrr_to_stdout=True):
        git_command_array = []

        if timeout:
            # Add "--foreground" so that stdin prompts like authenticity
            # prompt (if not disabled like below) are still shown, but
            # since only parent process is sent the kill signal, and
            # not the children, the command will hang forever if no
            # input is provided for children to exit.
            # TODO: Popen.communicate() and Popen.wait() have their own timeout argument.
            # Use TimeoutExpired exception to kill all child processes.
            # https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate
            # https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait
            git_command_array.extend(["timeout", "--foreground", "--kill-after=0", "--signal=KILL", timeout])

        git_command_array.append("git")
        git_command_array.extend(args)

        if not cwd:
            cwd = self.repo_root_dir

        git_env = os.environ.copy()
        git_env["GIT_SSH_COMMAND"] = self.get_git_ssh_command()

        # FIXME: Force enable capture for all commands until run_shell_command()
        # adds support for it.
        # Also enable redirect_stderrr_to_stdout by default so that commands
        # that are not meant to be captured, their stdout/stderr is logged
        # in sync.
        capture = True
        stdout = None
        stderr = None

        (return_value, stdout, stderr) = shell_utils.run_shell_command(
            LOG_TAG,
            git_command_array,
            capture,
            stdout=stdout,
            stderr=stderr,
            cwd=cwd,
            env=git_env,
            # timeout=timeout,
            redirect_stderrr_to_stdout=redirect_stderrr_to_stdout)

        force_log = not allow_all_exit_codes and str(return_value) != "0"

        if capture:
            if not silent or force_log:
                if stdout and not stdout.isspace():
                    if str(return_value) != "0":
                        logger.error(LOG_TAG, str(stdout))
                    else:
                        logger.verbose(LOG_TAG, str(stdout))
                if stderr and not stderr.isspace():
                    logger.error(LOG_TAG, str(stderr))

        if force_log:
            logger.error(LOG_TAG, "git command failed:")
            logger.error(LOG_TAG, data_utils.get_list_string(git_command_array))

        return (return_value, stdout, stderr)



    def get_git_version(self):
        (return_value, stdout, stderr) = self.exec(["--version"], True,
            cwd=".", # repo_root_dir may not exist
        )
        if str(return_value) != "0":
            logger.error(LOG_TAG, "Failed to get current git version. Is 'git' installed in $PATH?")
            return (return_value, None)

        return GitCommandManager.extract_git_version("git --version", stdout)

    def get_git_lfs_version(self):
        (return_value, stdout, stderr) = self.exec(["lfs", "--version"], True,
            cwd=".", # repo_root_dir may not exist
        )
        if str(return_value) != "0":
            logger.error(LOG_TAG, "Failed to get current git lfs version. Is 'git-lfs' installed in $PATH?")
            return (return_value, None)

        return GitCommandManager.extract_git_version("git-lfs --version", stdout)

    @staticmethod
    def extract_git_version(label, version):
        if version:
            version = version.strip()
            if "\n" not in version:
                match = re.search(GitVersion.REGEX_GIT_VERSION, version)
                if not match:
                    logger.error(LOG_TAG, "The version \"" + version + "\"" +
                        " returned by '" + label + "' command does not match '" + GitVersion.REGEX_GIT_VERSION + "'")
                    return (1, None)

                return GitVersion.create(match.group(0))
            else:
                logger.error(LOG_TAG, "Unexpected newline in '" + label + "' output:\n" + version + "'")
                return (1, None)
        else:
            logger.error(LOG_TAG, "The '" + label + "' output not set")
            return (1, None)



    def init(self, default_branch=None):
        args = ["init"]

        # Hide the "Using 'master'" branch verbose hint message
        #  hint: Using 'master' as the name for the initial branch. This default branch name is subject to change
        if default_branch:
            args.append("--initial-branch=" + default_branch)

        (return_value, stdout, stderr) = self.exec(args, False)
        return return_value



    def remote_add(self, remote_name, remote_url):
        (return_value, stdout, stderr) = self.exec(["remote", "add", remote_name, remote_url], False)
        return return_value



    def get_default_branch(self, repo_url):
        # Pass "HEAD" as patterns arg so that only matching lines need
        # to be checked below instead of all refs.
        args = ["ls-remote", "--quiet", "--exit-code", "--symref", repo_url, "HEAD"]

        (return_value, stdout, stderr) = self.exec(args, True,
                                                   cwd=".", # repo_root_dir may not exist
                                                   silent=True,
                                                   redirect_stderrr_to_stdout=False)
        if str(return_value) != "0":
            return (return_value, None)

        if stdout:
            for line in stdout.strip().splitlines():
                line = line.strip()
                # Example: "ref: refs/heads/master  HEAD"
                if line.startswith("ref:") or line.endswith("HEAD"):
                    return (0,
                            line[len("ref:") : len("ref:") + len(line) - len("ref:") - len("HEAD")].strip())

        logger.error(LOG_TAG, "Failed to find default branch for repo \"" + repo_url + "\"")
        return (1, None)



    def fetch(self, ref_spec, fetch_filter=None, fetch_depth=None, fetch_tags=None, show_progress=False):
        args = ["-c", "protocol.version=2", "fetch"]
        if not git_ref_utils.TAGS_REF_SPEC in ref_spec and not fetch_tags:
            args.append("--no-tags")

        args.extend(["--prune", "--no-recurse-submodules"])
        if show_progress:
            args.append("--progress")

        if fetch_filter:
            args.append("--filter=" + fetch_filter)

        if fetch_depth and fetch_depth > 0:
            args.append("--depth=" + str(fetch_depth))
        elif os.path.isfile(os.path.join(self.repo_root_dir, ".git", "shallow")):
            args.append("--unshallow")

        args.append("origin")

        if ref_spec:
            args.extend(ref_spec)

        (return_value, stdout, stderr) = self.exec(args, False)
        return return_value



    def checkout(self, ref, start_point, show_progress=False):
        # Disable "You are in 'detached HEAD' state" message
        args = ["-c", "advice.detachedHead=false", "checkout", "--force"]

        if show_progress:
            args.append("--progress")

        if start_point:
            args.extend(["-B", ref, start_point])
        else:
            args.append(ref)

        (return_value, stdout, stderr) = self.exec(args, False)
        return return_value



    def sparse_checkout(self, sparse_checkout, skip_checks):
        args = ["sparse-checkout", "set", "--cone"]

        if skip_checks:
            (return_value, minimum_git_sparse_checkout_skip_checks_version) = GitVersion.create(
                GitCheckoutConfig.MINIMUM_GIT_SPARSE_CHECKOUT_SKIP_CHECKS_VERSION)
            if str(return_value) != "0":
                return (return_value, None)
            elif not minimum_git_sparse_checkout_skip_checks_version or not isinstance(minimum_git_sparse_checkout_skip_checks_version, GitVersion):
                logger.error(LOG_TAG, "Failed to get minimum_git_sparse_checkout_skip_checks_version")
                return 1

            if self.git_version and isinstance(self.git_version, GitVersion):
                if self.git_version.ensure_minimum(minimum_git_sparse_checkout_skip_checks_version):
                    args.append("--skip-checks")
            else:
                logger.error(LOG_TAG, "The git_version is not set")
                return 1

        args.extend(sparse_checkout)

        (return_value, stdout, stderr) = self.exec(args, False)
        return return_value

    def sparse_checkout_no_cone_mode(self, sparse_checkout):
        (return_value, stdout, stderr) = self.exec(["config", "core.sparseCheckout", "true"], False)
        if str(return_value) != "0":
            return return_value

        (return_value, stdout, stderr) = self.exec(["config", "core.sparseCheckoutCone", "false"], False)
        if str(return_value) != "0":
            return return_value

        (return_value, stdout, stderr) = self.exec(["rev-parse", "--git-path", "info/sparse-checkout"], True)
        if str(return_value) != "0":
            return return_value

        if not stdout:
            logger.error(LOG_TAG, "Failed to get sparse checkout file")
            return 1

        sparse_checkout_path = os.path.join(self.repo_root_dir, stdout.rstrip())

        try:
            # Open file at sparse_checkout_path in write mode and write
            # all lines in "sparse_checkout" list to it.
            # The file must not contain non "utf-8" characters, otherwise
            # an exception will be raised.
            with open(sparse_checkout_path, "w", encoding="utf-8", errors="strict") as fout:
                fout.write("\n" + "\n".join(sparse_checkout) + "\n")

            return 0
        except Exception as err:
            logger.error(LOG_TAG, "Writing sparse checkout patterns to sparse checkout" +
                         " file at \"" + sparse_checkout_path + "\" failed with err:\n" + str(err))
            return 1



    def lfs_install(self):
        (return_value, stdout, stderr) = self.exec(["lfs", "install", "--local"], False)
        return return_value

    def lfs_fetch(self, ref):
        (return_value, stdout, stderr) = self.exec(["lfs", "fetch", "origin", ref], False)
        return return_value



    def submodule_sync(self, recursive_submodules):
        args = ["submodule", "sync"]

        if recursive_submodules:
            args.append("--recursive")

        (return_value, stdout, stderr) = self.exec(args, False)
        return return_value

    def submodule_update(self, fetch_depth, recursive_submodules):
        args = ["-c", "protocol.version=2"]
        args.extend(["submodule", "update", "--init", "--force"])

        if fetch_depth > 0:
            args.append("--depth=" + str(fetch_depth))

        if recursive_submodules:
            args.append("--recursive")

        (return_value, stdout, stderr) = self.exec(args, False)
        return return_value

    def submodule_for_each(self, command, recursive_submodules):
        args = ["submodule", "foreach"]

        if recursive_submodules:
            args.append("--recursive")

        args.append(command)

        (return_value, stdout, stderr) = self.exec(args, False)
        return return_value



    def branch_exists(self, remote, pattern):
        args = ["branch", "--list"]
        if remote:
            args.append("--remote")
        args.append(pattern)

        (return_value, stdout, stderr) = self.exec(args, True, silent=True, redirect_stderrr_to_stdout=False)
        return str(return_value) == "0" and stdout and stdout.strip()

    def tag_exists(self, pattern):
        args = ["tag", "--list", pattern]
        (return_value, stdout, stderr) = self.exec(args, True, silent=True, redirect_stderrr_to_stdout=False)
        return str(return_value) == "0" and stdout and stdout.strip()

    def sha_exists(self, sha):
        args = ["rev-parse", "--verify", "--quiet", sha + "^{object}"]
        (return_value, stdout, stderr) = self.exec(args, True, silent=True, redirect_stderrr_to_stdout=False)
        return str(return_value) == "0"

    def rev_parse(self, ref):
        """
        Resolves a ref to a SHA. For a branch or lightweight tag, the commit SHA is returned.
        For an annotated tag, the tag SHA is returned.
        @param {string} ref  For example: "refs/heads/main" or "/refs/tags/v1"
        @returns sha
        """

        args = ["rev-parse", ref]
        (return_value, stdout, stderr) = self.exec(args, True, silent=True, redirect_stderrr_to_stdout=False)
        return str(return_value) == "0" and stdout and stdout.strip()



    def log1(self, format_string):
        args = ['log', '-1', format_string] if format_string else ['log', '-1']
        silent = not format_string

        (return_value, stdout, stderr) = self.exec(args, True, silent=silent, redirect_stderrr_to_stdout=False)
        return (return_value, stdout)



    def config(self, global_config, config_key, config_value, add=False):
        args = ["config"]

        args.append("--global" if global_config else "--local")

        if add:
            args.append("--add")

        args.extend([config_key, config_value])

        (return_value, stdout, stderr) = self.exec(args, False,
                                                   cwd=("." if global_config else None)) # repo_root_dir may not exist))
        return return_value

    def config_add_if_no_exist(self, global_config, config_key, config_value, fixed_value):
        if not self.config_exists(global_config, config_key,
            config_value=config_value, fixed_value=fixed_value):
            return self.config(global_config, config_key, config_value, add=True)
        else:
            return 0

    def config_exists(self, global_config, config_key, config_value=None, fixed_value=True):
        # Escape all the characters in the key except ASCII letters,
        # numbers and '_' with a backslash `\` so that it is considered
        # as a literal match.
        pattern = re.escape(config_key)

        args = ["config"]

        args.append("--global" if global_config else "--local")

        if config_value and fixed_value:
            args.append("--fixed-value")

        args.extend(["--name-only", "--get-regexp", pattern])

        if config_value:
            args.append(config_value)

        (return_value, stdout, stderr) = self.exec(args, True,
                                                   silent=True,
                                                   redirect_stderrr_to_stdout=False,
                                                   allow_all_exit_codes=True,
                                                   cwd=("." if global_config else None)) # repo_root_dir may not exist)
        return str(return_value) == "0"

    def config_unset(self, global_config, config_key, config_value=None, fixed_value=True):
        args = ["config"]

        args.append("--global" if global_config else "--local")

        if config_value and fixed_value:
            args.append("--fixed-value")

        args.extend(["--unset-all", config_key])

        if config_value:
            args.append(config_value)

        (return_value, stdout, stderr) = self.exec(args, False,
                                                   cwd=("." if global_config else None)) # repo_root_dir may not exist)
        return str(return_value) == "0"

    def config_unset_if_exist(self, global_config, config_key, config_value=None, fixed_value=True):
        if self.config_exists(global_config, config_key,
            config_value=config_value, fixed_value=fixed_value):

            if not self.config_unset(global_config, config_key,
                                     config_value=config_value, fixed_value=fixed_value):
                logger.error(LOG_TAG, "Failed to remove the \"" + config_key + "\"" +
                             " key from the " + ("global" if global_config else "local") + " git config")
                return 1

        return 0



    def disable_automatic_garbage_collection(self):
        args = ["config", "--local", "gc.auto", "0"]

        (return_value, stdout, stderr) = self.exec(args, False)
        return str(return_value) == "0"



    def is_valid_repo_url(self, repo_url, log_on_error=True):
        "Check if repo url is valid and exists."
        if not repo_url:
            return 1

        # The "--tags" arg is passed for faster response, since otherwise
        # ls-remote command takes many seconds to complete.
        # - https://stackoverflow.com/questions/73297514/fastest-way-to-check-if-a-git-server-is-available
        (return_value, stdout, stderr) = self.exec(["ls-remote", "--tags", repo_url], True,
                                                   cwd=".", # repo_root_dir may not exist
                                                   timeout="30s",
                                                   silent=True,
                                                   redirect_stderrr_to_stdout=True,
                                                   allow_all_exit_codes=True)

        if log_on_error and str(return_value) != "0" and stdout and not stdout.isspace():
            logger.error(LOG_TAG, "Check if \"" + repo_url + "\" repo exists faled:\n" + str(stdout))

        return str(return_value) == "0"
