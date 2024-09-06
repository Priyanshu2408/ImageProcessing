class DefaultException(Exception):
    def __init__(self, msg="", status_code = 400):
        message = {
            "error": {
                "message": msg,
                "code": 4070,
                "status_code": status_code,
                "developer_message": "Default Exception: " + msg
            },
            "success": False}

        self.message = message