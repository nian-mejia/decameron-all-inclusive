import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt

from widgets import BannerWidget
from shared_state import SharedState
from todo_incluido_tab import TodoIncluidoTab
from decas_tab import DecasTab

class HotelSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selector de Hoteles Decameron")
        self.setMinimumSize(800, 600)
        
        # Cargar estilos desde el archivo CSS
        self.load_styles()
        
        # Crear widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Agregar el banner
        banner = BannerWidget()
        main_layout.addWidget(banner)
        
        # Crear el estado compartido
        self.shared_state = SharedState()
        
        # Crear el widget de pestañas
        self.tabs = QTabWidget()
        
        # Crear las pestañas
        self.todo_incluido_tab = TodoIncluidoTab(self.shared_state)
        self.decas_tab = DecasTab(self.shared_state)
        
        # Agregar las pestañas
        self.tabs.addTab(self.decas_tab, "Decas")
        self.tabs.addTab(self.todo_incluido_tab, "Todo Incluido")
        
        # Agregar tabs al layout principal
        main_layout.addWidget(self.tabs)
        
    def load_styles(self):
        try:
            style_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles', 'styles.css')
            print(f"Intentando cargar estilos desde: {style_path}")
            print(f"El archivo existe: {os.path.exists(style_path)}")
            with open(style_path, 'r') as f:
                styles = f.read()
                QApplication.instance().setStyleSheet(styles)
                print("Estilos cargados exitosamente")
        except Exception as e:
            print(f"Error loading styles: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HotelSelector()
    window.show()
    sys.exit(app.exec()) 