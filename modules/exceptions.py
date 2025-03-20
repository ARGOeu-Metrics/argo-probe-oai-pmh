class MyException(Exception):
    def __init__(self, msg, title=None):
        self.msg = msg
        self.title = title


class XMLException(MyException):
    def __str__(self):
        return f"Error analysing XML content: {str(self.msg)}"


class RequestException(MyException):
    def __str__(self):
        return f"{str(self.msg)}"


class XMLRequestException(MyException):
    def __str__(self):
        return f"Error fetching XML {self.title}: {str(self.msg)}"


class XMLSchemaRequestException(MyException):
    def __str__(self):
        return f"Error reading XML schema: {str(self.msg)}"
