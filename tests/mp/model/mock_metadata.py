from mp.model.metadata import Metadata


class MockMetadata(Metadata):
    def __init__(self, args):
        Metadata.__init__(self, args=args)

    def dict(self):
        return self._args
