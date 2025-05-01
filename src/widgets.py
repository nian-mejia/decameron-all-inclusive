from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os

class BannerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Crear el banner
        self.banner_label = QLabel()
        self.banner_label.setMinimumHeight(150)  # Altura mínima para el banner
        self.banner_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.banner_label.setStyleSheet("""
            QLabel {
                background-color: #2c5282;
                padding: 0px;
                margin: 0px;
            }
        """)
        self.banner_label.setAlignment(Qt.AlignCenter)
        self.banner_label.setScaledContents(True)
        
        # Cargar el logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'decameron-logo.png')
        print(f"Intentando cargar logo desde: {logo_path}")
        print(f"El archivo existe: {os.path.exists(logo_path)}")
        
        self.logo_pixmap = QPixmap(logo_path)
        if not self.logo_pixmap.isNull():
            print(f"Logo cargado exitosamente. Tamaño: {self.logo_pixmap.width()}x{self.logo_pixmap.height()}")
            self.update_banner_pixmap()
        else:
            print("Error al cargar el logo")
            self.banner_label.setText("DECAMERON")
            self.banner_label.setStyleSheet("""
                QLabel {
                    background-color: #2c5282;
                    color: white;
                    font-size: 36px;
                    font-weight: bold;
                    font-family: 'Arial';
                    padding: 20px;
                }
            """)
        
        layout.addWidget(self.banner_label)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'logo_pixmap') and not self.logo_pixmap.isNull():
            self.update_banner_pixmap()

    def update_banner_pixmap(self):
        if self.banner_label.width() <= 0 or self.banner_label.height() <= 0:
            return
            
        # Escalar la imagen para llenar el banner manteniendo la proporción y expandiendo
        scaled_pixmap = self.logo_pixmap.scaled(
            self.banner_label.width(),
            self.banner_label.height(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        
        # Si la imagen escalada es más grande que el banner, recortarla al centro
        if scaled_pixmap.width() > self.banner_label.width() or scaled_pixmap.height() > self.banner_label.height():
            x = (scaled_pixmap.width() - self.banner_label.width()) // 2 if scaled_pixmap.width() > self.banner_label.width() else 0
            y = (scaled_pixmap.height() - self.banner_label.height()) // 2 if scaled_pixmap.height() > self.banner_label.height() else 0
            scaled_pixmap = scaled_pixmap.copy(
                x, y,
                min(scaled_pixmap.width(), self.banner_label.width()),
                min(scaled_pixmap.height(), self.banner_label.height())
            )
        
        self.banner_label.setPixmap(scaled_pixmap) 