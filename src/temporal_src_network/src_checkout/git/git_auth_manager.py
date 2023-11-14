import base64
import os
from urllib.parse import urlparse

from ...logger.logger_core import logger

LOG_TAG = "git_auth_manager"

class GitAuthManager:
    "The git auth manager."

    def __init__(self, git, checkout_config, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with GitAuthManager.create()")

        self.git = git
        self.checkout_config = checkout_config

        self.token_config_key = None
        self.basic_credential = None
        self.token_placeholder_config_value = None
        self.token_config_value = None

    @classmethod
    def create(cls, git, checkout_config):
        auth_manager = cls(git, checkout_config, _not_called_from_create=False)

        if not checkout_config.src_url:
            logger.error(LOG_TAG, "The src_url \"" + checkout_config.src_url + "\" passed to git_auth_manager is not set")
            return (1, None)

        src_url = urlparse(checkout_config.src_url)

        # Token auth header
        if checkout_config.git_auth_token:
            # scheme and netloc are SCHEME://HOSTNAME[:PORT]
            # For a github url, it will be "http.https://github.com/.extraheader"
            auth_manager.token_config_key = "http." + src_url.scheme + "://" + src_url.netloc + "/.extraheader"

            auth_manager.basic_credential = base64.b64encode(bytes(
                "x-access-token:" + checkout_config.git_auth_token, "utf-8")).decode('ascii')

            auth_manager.token_placeholder_config_value = "AUTHORIZATION: basic ***"
            auth_manager.token_config_value = "AUTHORIZATION: basic " + auth_manager.basic_credential

        return (0, auth_manager)



    def configure_auth(self):
        # Remove possible previous values
        return_value = self.remove_auth()
        if str(return_value) != "0":
            return return_value

        # TODO: Configure ssh

        # Configure token
        if self.checkout_config.git_auth_token:
            return self.configure_token()

        return 0

    def configure_token(self, config_path=None, global_config=False):
        logger.debug(LOG_TAG, "Configuring token")

        if not ((config_path and global_config) or (not config_path and not global_config)):
            logger.error(LOG_TAG, "Unexpected config_path and global_config parameter combinations")
            return 1

        # Validate token_config_key
        if not self.token_config_key or not isinstance(self.token_config_key, str) or \
            not self.token_config_key.startswith("http.") or \
            not self.token_config_key.endswith(".extraheader"):
            logger.error(LOG_TAG, "The token_config_key \"" + str(self.token_config_key or "") + "\" is not valid")
            return 1

        # Validate token_placeholder_config_value
        if not self.token_placeholder_config_value or \
            not isinstance(self.token_placeholder_config_value, str) or \
            not self.token_placeholder_config_value.startswith("AUTHORIZATION:"):
            logger.error(LOG_TAG, "The token_placeholder_config_value \"" + str(self.token_placeholder_config_value or "") + "\" is not valid")
            return 1

        # Default config path
        if (not config_path and not global_config):
            config_path = os.path.join(self.git.repo_root_dir, ".git", "config")

        # Configure a placeholder value. This approach avoids the credential being captured
        # by process creation audit events, which are commonly logged. For more information,
        # refer to https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/command-line-process-auditing
        return_value = self.git.config(global_config, self.token_config_key, self.token_placeholder_config_value)
        if str(return_value) != "0":
            return return_value

        # Replace the placeholder
        if config_path:
            self.replace_token_placeholder(config_path)

        return 0

    def replace_token_placeholder(self, config_path):
        "Replace token_placeholder_config_value from git config file."

        # Validate token_config_value
        if not self.token_config_value or \
            not isinstance(self.token_config_value, str) or \
            not self.token_config_value.startswith("AUTHORIZATION:"):
            # Never log token_config_value
            logger.error(LOG_TAG, "The token_config_value is not valid")
            return 1

        # Validate token_placeholder_config_value
        if not self.token_placeholder_config_value or \
            not isinstance(self.token_placeholder_config_value, str) or \
            not self.token_placeholder_config_value.startswith("AUTHORIZATION:"):
            logger.error(LOG_TAG, "The token_placeholder_config_value \"" + str(self.token_placeholder_config_value or "") + "\" is not valid")
            return 1

        try:
            # Open file at config_path and read it to "lines" variable.
            # The file must not contain non "utf-8" characters, otherwise
            # an exception will be raised.
            with open(config_path, encoding="utf-8", errors="strict") as fin:
                lines = fin.readlines()

            # If lines is set
            if lines:
                for i in range(len(lines)):  # pylint: disable=consider-using-enumerate
                    # If line contains token_placeholder_config_value, then replace only one
                    # instance of it in line with token_config_value
                    if self.token_placeholder_config_value in lines[i]:
                        # logger.debug(LOG_TAG, "Replacing token placeholder in \"" + lines[i] + "\" entry in git config")
                        lines[i] = lines[i].replace(self.token_placeholder_config_value, self.token_config_value, 1)
                        # logger.debug(LOG_TAG, "update_entry \"" + lines[i] + "\"")

            # Open file at config_path in write mode and write all lines in "lines" list to it.
            with open(config_path, "w", encoding="utf-8") as fout:
                for line in lines:
                    fout.write(line)

            return 0
        except Exception as err:
            logger.error(LOG_TAG, "Replacing token placeholder \"" + self.token_placeholder_config_value + "\"" +
                         " with actual value in git config file at \"" + str(config_path or "") + "\"" +
                         " failed with err:\n" + str(err))
            return 1



    def remove_auth(self):
        # TODO: Remove ssh

        # Remove token
        if self.checkout_config.git_auth_token:
            return self.remove_token()

        return 0

    def remove_token(self):
        return self.git.config_unset_if_exist(False, self.token_config_key)
