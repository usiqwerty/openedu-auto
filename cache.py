class CacheContext:
    callbacks: list

    def __init__(self, callbacks: list):
        self.callbacks = callbacks

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        for callback in self.callbacks:
            callback()