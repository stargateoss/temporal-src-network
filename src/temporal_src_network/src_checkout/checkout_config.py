import abc

from ..data.data_utils import log_value

class CheckoutConfig(metaclass=abc.ABCMeta):
    "Config for checking out a source."

    def __init__(self, checkout_type):
        self.checkout_type = checkout_type

    def to_string(self):
        return \
        "checkout_type: " + log_value(self.checkout_type)
