class UserError(Exception):
    def __init__(self, message) -> None:
        self.__message=message
    
    def __str__(self) -> str:
        return f'{self.__message}'