import os
from game.color import Color
from game.control import Control


# This Python class represents a menu with sections that can be navigated using keyboard controls.
class Menu:

    # The `CONTROL_SELECTIONS` dictionary in the `Menu` class is mapping keyboard controls to their
    # corresponding actions when navigating the menu.
    CONTROL_SELECTIONS = {"W": -1, "S": 1, "ENTER": "ENTER"}

    def __init__(self, sections: list, menu_name: str = "Menu") -> None:
        """
        This function initializes a menu object with a list of sections and a default menu name.

        :param sections: The `sections` parameter in the `__init__` method is a list that contains the
        menu sections for the menu. Each item in the list represents a section of the menu, such as
        appetizers, main courses, desserts, etc
        :type sections: list
        :param menu_name: The `menu_name` parameter is a string that represents the name of the menu. By
        default, it is set to 'Menu' if no value is provided when creating an instance of the class,
        defaults to Menu (optional)
        """
        self.menu_sections = sections
        self.menu_name = menu_name
        self.control = Control().select

    def select(self) -> int:
        """
        This Python function displays a menu with selectable options and allows the user to navigate and
        choose an option using keyboard inputs.
        :return: The `select` method is returning the position of the selected menu item when the user
        presses the 'ENTER' key.
        """
        os.system("cls")

        position = 0

        while True:
            print("" + "=" * 5 + f" {self.menu_name} " + "=" * 5)
            # This part of the code is iterating over the list of menu sections (`self.menu_sections`)
            # using a `for` loop. For each index `i` in the range of the length of
            # `self.menu_sections`, it checks if the current index `i` is equal to the `position`
            # variable.
            for i in range(len(self.menu_sections)):
                if i == position:
                    print(f"> {Color.BLUE}{self.menu_sections[i]}{Color.RESET} <")
                else:
                    print(self.menu_sections[i])

            print("Presiona una tecla [W][S][ENTER])")

            selected = self.control(self.CONTROL_SELECTIONS)
            if selected == "ENTER":
                return position
            else:
                position += selected
                if position < 0:
                    position = 0
                if position >= len(self.menu_sections):
                    position = len(self.menu_sections) - 1
            os.system("cls")


if __name__ == "__main__":
    pass
    b = Menu(["Jugar", "Opciones", "Salir"], menu_name="Numari")
    b.select()
