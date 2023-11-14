#!/usr/bin/env python3

from .. import src_provider

from ...logger.logger_core import logger

LOG_TAG = "ignore_src_provider"

class IgnoreSrcProvider(src_provider.SrcProvider):
    "Provider for ignoring a checking out."

    def __init__(self, *, _not_called_from_create=True):
        if _not_called_from_create:
            raise RuntimeError("Object must be created with IgnoreSrcProvider.create()")

    @classmethod
    def create(cls):
        return (0, cls(_not_called_from_create=False))

    def checkout_src(self):
        logger.debug(LOG_TAG, "Ignoring checkout source")

        return 0
