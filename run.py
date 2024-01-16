# run.py

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the main_menu function from main_menu.py
from main_menu import main_menu

# Run the main menu
if __name__ == "__main__":
    main_menu()
