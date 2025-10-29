import keyboard
import time
import msvcrt as kb
import os
# The `Control` class in Python provides a static method `select` that allows for selecting an item
# based on key inputs from a dictionary of selections.
class Control:
    
    @staticmethod
    def select(selections:dict) -> any:
        """
        This Python function takes a dictionary of selections, waits for a key press that matches one of
        the keys in the dictionary, and returns the corresponding value.
        
        :param selections: The `selections` parameter is a dictionary that contains key-value pairs
        where the keys represent the options or selections available to the user, and the values
        represent the corresponding actions or values associated with those options
        :type selections: dict
        :return: The `select` function returns the value associated with the key that was pressed from
        the `selections` dictionary.
        """
        # The code snippet `if not selections: raise ValueError("El diccionario 'selections' no puede
        # estar vacío")` is performing input validation.
        if not selections:
            raise ValueError("El diccionario 'selections' no puede estar vacío")
        
        buttons = [k.upper() for k in selections.keys()] # When we push a key the program read it as a upper key
        
        while True:
            key = keyboard.read_key().upper()
            time.sleep(0.2)
            
            if key in buttons:
                return selections[key]

    @staticmethod
    def clean_input_keys():
        """
        Clears all pressed keys.
        Used when you want to input.
        """
        
        # while a keypress is waiting to be read continue input, after clear the terminal
        while kb.kbhit(): input()
        os.system("cls")

if __name__ == '__main__':
   if Control.select({'W':'UP', 'S':'DOWN', 'A':'LEFT', 'ESC':'SALIR'}) == 'SALIR':
        print('Salir')
   else:
        print('Continuar')