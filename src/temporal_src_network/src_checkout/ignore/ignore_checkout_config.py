#!/usr/bin/env python3

from ..checkout_config import CheckoutConfig

LOG_TAG = "ignore_checkout_config"

class IgnoreCheckoutConfig(CheckoutConfig):
    "Ignore Checkout config."

    CHECKOUT_TYPE = "ignore"

    def __init__(self, *, _not_called_from_create=True):
        super().__init__(IgnoreCheckoutConfig.CHECKOUT_TYPE)

        if _not_called_from_create:
            raise RuntimeError("Object must be created with IgnoreCheckoutConfig.create()")

    @classmethod
    def create(cls):
        checkout_config = cls(_not_called_from_create=False)
        return (0, checkout_config)



    def to_string(self):
        return CheckoutConfig.to_string(self)
