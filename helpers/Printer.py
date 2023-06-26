import time
import itertools
import sys

ascii_art = """\033[32m
 ______  __  __  ______  ______  ______  ______  ______    
/\  ___\/\ \/\ \/\  ___\/\  ___\/\  ___\/\  ___\/\  ___\   
\ \___  \ \ \_\ \ \ \___\ \ \___\ \  __\\ \___  \ \___  \  
 \/\_____\ \_____\ \_____\ \_____\ \_____\/\_____\/\_____\ 
  \/_____/\/_____/\/_____/\/_____/\/_____/\/_____/\/_____/                                              
\033[0m
"""

help_text = """
------ Type these commands, then press Enter ------
---------------------------------------------------
    cmd : Prints a list of commands
    upsert <text> : Inserts Vector and Text into DB
    query <text> : Gets similar data based on text
    delete <id> : Removes data stored in DB by id
    exit : Exit the program
---------------------------------------------------
"""

def print_ascii():
    for char in ascii_art:
        print(char, end='', flush=True)
        time.sleep(0.008)

def type(text):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.006)
    print()

def print_help():
    print(help_text)

def waiting(msg, stop_event):
    # courtesy of some creative people online :)
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    print(f"\033[33m{msg} \033[34m", end='', flush=True)
    for _ in range(100):
        if stop_event.is_set():  # Check if the stop event is set
            break
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        sys.stdout.write('\b')
        time.sleep(0.05)
    sys.stdout.write('\r')
    
def error_response(err):
    print("\033[31mError:", err, "\033[0m")