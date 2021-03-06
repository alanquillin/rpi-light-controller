class UserMessageError(Exception):
    def __init__(self, response_code, user_msg=None, server_msg=None):
        self.user_msg = user_msg or ""
        self.server_msg = server_msg or self.user_msg
        self.response_code = response_code
        super().__init__()


class ClientError(UserMessageError):
    def __init__(self, response_code=400, user_msg=None, **kwargs):
        if not user_msg:
            user_msg = "Invalid request"
        super().__init__(response_code, user_msg=user_msg, **kwargs)


class ServerError(UserMessageError):
    def __init__(self, response_code=500, user_msg=None, server_msg=None):
        user_msg = f"An error occurred while processing the request{f': {user_msg}' if user_msg else ''}"
        server_msg = f"Server-side error while processing request: {server_msg or user_msg}"
        super().__init__(response_code, user_msg=user_msg, server_msg=server_msg)


class NotFoundError(UserMessageError):
    def __init__(self, user_msg=None, **kwargs):
        if not user_msg:
            user_msg = "Requested resource not found"
        super().__init__(404, user_msg=user_msg, **kwargs)


class NotAuthorized(ClientError):
    def __init__(self, user_msg=None, **kwargs):
        if not user_msg:
            user_msg = "You are not authorized to access the requested resource."
        super().__init__(response_code=401, user_msg=user_msg, **kwargs)

class InvalidEnum(ValueError):
    pass
