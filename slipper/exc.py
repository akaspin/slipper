# coding=utf-8


class SlipperException(Exception):
    """Raises when slipper exception happens."""
    message = 'SlipperException %s.'

    def __init__(self, **kwargs):

        #: Exception kwargs.
        self.kwargs = kwargs

        #: Backed message
        self.msg = self.message % kwargs
        super(SlipperException, self).__init__(self.msg)

    def __str__(self):
        return self.msg
