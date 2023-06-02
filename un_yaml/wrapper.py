class Wrapper:
    """Wrap resource methods"""

    def __init__(self, data = None):
        self.data = data

    async def execute(self, cmd: str, argv: dict):
        return [cmd, argv]