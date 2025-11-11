import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

def create_overlay(png_path):
    app = QApplication(sys.argv)
    
    # Create window
    window = QLabel()
    
    # Load image
    pixmap = QPixmap(png_path)
    
    # Scale image to fit screen nicely
    screen = app.primaryScreen().size()
    # scaled_pixmap = pixmap.scaled(
    #     int(screen.width() * 0.8), 
    #     int(screen.height() * 0.8), 
    #     Qt.KeepAspectRatio, 
    #     Qt.SmoothTransformation
    # )
    
    # Set up window
    window.setPixmap(pixmap)
    window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    window.setAttribute(Qt.WA_TranslucentBackground)
    
    # Center window on screen
    window.resize(pixmap.size())
    window.move(
        (screen.width() - pixmap.width()) // 2,
        (screen.height() - pixmap.height()) // 2
    )
    
    # Close on click
    window.mousePressEvent = lambda event: app.quit()
    
    # Show and run
    window.show()
    app.exec_()

# Usage
create_overlay("temp\\overlay.png")