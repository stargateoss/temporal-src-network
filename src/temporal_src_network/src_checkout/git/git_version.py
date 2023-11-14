import re

from ...logger.logger_core import logger

LOG_TAG = "git_version"

class GitVersion:
    "The git command manager."

    REGEX_GIT_VERSION = r"(\d+)\.(\d+)(\.(\d+))?"

    def __init__(self, full, major, minor, patch, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with GitVersion.create()")

        self.full = full
        self.major = major
        self.minor = minor
        self.patch = patch

    @classmethod
    def create(cls, version):
        match = re.match("^" + GitVersion.REGEX_GIT_VERSION + "$", version)
        if not match:
            logger.error(LOG_TAG, "The version \"" + version + "\"" +
                " is not a valid git version matching '" + GitVersion.REGEX_GIT_VERSION + "'")
            return (1, None)

        git_version = cls(match.group(0), match.group(1), match.group(2), match.group(4), _not_called_from_create=False)

        return (0, git_version)

    def ensure_minimum(self, minimum):
        """
        Compares this instance against a minimum required version.

        @param minimum The minimum version
        """

        if not minimum or not isinstance(minimum, GitVersion):
            raise RuntimeError("The minimum object passed to GitVersion.check_minimum() must be an instance of GitVersion")

        # Major is insufficient
        if self.major < minimum.major:
            return False

        # Major is equal
        if self.major == minimum.major:
            # Minor is insufficient
            if self.minor < minimum.minor:
                return False

            # Minor is equal
            if self.minor == minimum.minor:
                # Patch is insufficient
                if self.patch and self.patch < (minimum.patch or 0):
                    return False

        return True
