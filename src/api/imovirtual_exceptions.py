class BuildIdNotFoundException(Exception):
    def __init__(self, message="Build ID not found"):
        self.message = message
        super().__init__(self.message)