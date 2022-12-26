class ExportingException(Exception):
    """
    Raised when a exporting  encounters an error
    """
    
    message = ""
    

    def __init__(self, msg) -> None:
        self.message = msg
        
class SmsException(Exception):
    """Exception raised SMS encounters an error """
    message = ""

    def __init__(self, msg) -> None:
        self.message = msg