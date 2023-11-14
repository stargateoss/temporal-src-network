import collections

from ..data import data_utils
from ..logger.logger_core import logger

LOG_TAG = "modules_config"

class ModulesConfig:
    "Modules config."

    def __init__(self, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with ModulesConfig.create()")

        self.src_checkout_dict = collections.OrderedDict()
        self.module_list = collections.OrderedDict()

    @classmethod
    def create(cls, modules_dict):
        modules_config = cls(_not_called_from_create=False)

        modules_config.src_checkout_dict = data_utils.get_ordered_dict_from_dict(
            modules_dict, "version_src_checkout", modules_config.src_checkout_dict)

        modules_config.module_list = data_utils.get_ordered_dict_from_dict(modules_dict, "list", None)
        if not modules_config.module_list:
            logger.error(LOG_TAG, "The 'project.modules.list' value is not set or not a dict")
            return (1, None)

        return (0, modules_config)
