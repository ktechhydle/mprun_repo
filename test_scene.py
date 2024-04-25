from graphics_framework import *

class MainWin(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('MPRUN Beta Test Scene')
        
        
        
if __name__ == '__main__':
    win = QApplication([])
    app = MainWin()
    app.show()
    sys.exit()