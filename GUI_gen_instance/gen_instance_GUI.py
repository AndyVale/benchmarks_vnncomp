import sys
from PyQt6.QtWidgets import QApplication

from .main_gui import GUI
from .logic import logic

def main():
    application = QApplication(sys.argv)
    logic_instance = logic()
    window = GUI(logic_instance)
    window.show()
    sys.exit(application.exec())
    
if __name__ == "__main__":
    main()
