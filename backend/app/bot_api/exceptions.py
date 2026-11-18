class TelegramApiException(Exception):
    def __init__(self, error_code: int, description: str):
        super().__init__(description)
        self.error_code = error_code
        self.description = description
