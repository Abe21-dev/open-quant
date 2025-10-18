class BaseApiAdapter:
    def __init__(self, base_url, header: dict):
        self.base_url = base_url
        self.header = header
