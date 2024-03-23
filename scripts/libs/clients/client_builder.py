class IndentedWithSpacesString:
    """
    Represents a string indented with spaces.

    Attributes:
        _string (str): The original string.
        _indentations (int): The number of spaces for indentation.
    """
    def __init__(self, string: str, indentations: int):
        """
        Initializes an instance of IndentedWithSpacesString.

        Args:
            string (str): The original string.
            indentations (int): The number of spaces for indentation.
        """
        self._string = string
        self._indentations = indentations

    def __str__(self):
        """
        Returns the string representation of the object with the specified indentation.

        Returns:
            str: The string with indentation.
        """
        return ' ' * self._indentations + self._string


class ClientStrBuilder:
    """
    Builds a string representation of a client configuration.

    Methods:
        build(id: int) -> str: Builds the client configuration string.

    """
    def build(self, id: int) -> str:
        """
        Builds the client configuration string.

        Args:
            id (int): The client identifier.

        Returns:
            str: The string representation of the client configuration.
        """
        dynamic_lines = [
            IndentedWithSpacesString(f'client{id}:', 2),
            IndentedWithSpacesString(f'container_name: client{id}', 4),
            IndentedWithSpacesString('image: client:latest', 4),
            IndentedWithSpacesString('entrypoint: /client', 4),
            IndentedWithSpacesString('environment:', 4),
            IndentedWithSpacesString(f'- CLI_ID={id}', 6),
            IndentedWithSpacesString('- CLI_LOG_LEVEL=DEBUG', 6),
            IndentedWithSpacesString('networks:', 4),
            IndentedWithSpacesString('- testing_net', 6),
            IndentedWithSpacesString('depends_on:', 4),
            IndentedWithSpacesString('- server', 6)
        ]

        final_result = "\n".join(map(lambda x: str(x), dynamic_lines))
        return final_result
