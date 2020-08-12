class MockMetadata:
    def __init__(self, args):
        self._args = args

    def dict(self):
        return self._args
