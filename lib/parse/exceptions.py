class HtmlParsingError(RuntimeError):
    def __init__(self, msg="The HTML could not be properly parsed"):
        super().__init__(msg)
