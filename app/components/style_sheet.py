class StyleSheet:
    """ Style sheet  """

    def __init__(self, path: str):
        self.path = path
        self.style_sheet = self.__read_stylesheet()

    def __read_stylesheet(self) -> str:
        with open(self.path, "r") as f:
            return f.read()

    def __str__(self) -> str:
        return self.style_sheet

    def __repr__(self) -> str:
        return self.style_sheet
