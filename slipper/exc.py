# coding=utf-8


class SlipperException(Exception):
    """Raises when model exception happens."""
    message = 'SlipperException %s.'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.msg = self.message % kwargs
        super(SlipperException, self).__init__(self.msg)

    def __str__(self):
        return self.msg
