import abc

class SrcProvider(metaclass=abc.ABCMeta):
    "Provider for checking out a source."

    @abc.abstractmethod
    def checkout_src(self):
        raise NotImplementedError("Extended class must define 'SrcProvider.checkout_src()' method")
