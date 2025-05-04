import os
import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QSpinBox, QGroupBox, QCalendarWidget,
                              QPushButton, QLineEdit, QScrollArea, QCompleter, QApplication)
from PySide6.QtCore import QDate, Qt
from decameron_styles import GROUPBOX_STYLE, COMBOBOX_STYLE, LABEL_STYLE

class DateInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMinimumWidth(120)
        self.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:hover {
                border: 1px solid #999;
            }
        """)

class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()  # Ignora el scroll para evitar cambiar la selección

class DecasTab(QWidget):
    def __init__(self, shared_state, parent=None):
        super().__init__(parent)
        self.shared_state = shared_state
        self.shared_state.add_observer(self)
        
        self.df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'data', 'conversion_decas.csv'))
        
        # Usar fechas del shared_state
        self.check_in_date = self.shared_state.check_in
        self.check_out_date = self.shared_state.check_out
        
        self.setup_ui()
        self.setup_connections()
        
        # Inicializar los combos
        self.hotel_combo.addItems(sorted(self.df['Hotel'].unique()))
        self.season_combo.addItems(["Baja", "Media", "Alta"])
        
        # Establecer valores iniciales desde shared_state
        if self.shared_state.hotel:
            self.hotel_combo.setCurrentText(self.shared_state.hotel)
        else:
            # Si no hay hotel seleccionado, establecer Isleño como default
            isleno_index = self.hotel_combo.findText("Isleño")
            if isleno_index >= 0:
                self.hotel_combo.setCurrentText("Isleño")
                self.shared_state.hotel = "Isleño"
        
        self.season_combo.setCurrentText(self.shared_state.season)
        
        # Calcular total inicial
        self.calculate_total()
        
    def setup_ui(self):
        # Contenedor principal con scroll
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)  # Espacio entre grupos
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = QScrollArea()
        scroll.setWidget(main_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        # Grupo de selección de hotel
        hotel_group = QGroupBox("Selección de Hotel")
        hotel_group.setStyleSheet(GROUPBOX_STYLE)
        hotel_layout = QVBoxLayout()
        hotel_layout.setSpacing(10)
        hotel_layout.setContentsMargins(15, 15, 15, 15)
        
        # Crear los widgets
        hotel_label = QLabel("Hotel:")
        hotel_label.setStyleSheet(LABEL_STYLE)
        self.hotel_combo = NoScrollComboBox()
        self.hotel_combo.setEditable(True)
        self.hotel_combo.setInsertPolicy(QComboBox.NoInsert)
        self.hotel_combo.setMinimumWidth(300)
        self.hotel_combo.setStyleSheet(COMBOBOX_STYLE)
        completer = QCompleter(self.hotel_combo.model(), self.hotel_combo)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.hotel_combo.setCompleter(completer)
        
        season_label = QLabel("Temporada:")
        season_label.setStyleSheet(LABEL_STYLE)
        self.season_combo = QComboBox()
        self.season_combo.setMinimumWidth(300)
        self.season_combo.setStyleSheet(COMBOBOX_STYLE)
        
        hotel_layout.addWidget(hotel_label)
        hotel_layout.addWidget(self.hotel_combo)
        hotel_layout.addSpacing(8)  # Espacio entre hotel y temporada
        hotel_layout.addWidget(season_label)
        hotel_layout.addWidget(self.season_combo)
        
        hotel_group.setLayout(hotel_layout)
        main_layout.addWidget(hotel_group)
        
        # Grupo de fechas
        dates_group = QGroupBox("Selección de Fechas")
        dates_group.setStyleSheet(GROUPBOX_STYLE)
        dates_layout = QVBoxLayout()
        dates_layout.setSpacing(12)
        dates_layout.setContentsMargins(15, 15, 15, 15)
        
        # Contenedor de fechas
        dates_container = QHBoxLayout()
        dates_container.setSpacing(12)
        
        # Fecha de entrada
        self.check_in_input = DateInput()
        self.check_in_input.setText(self.check_in_date.toString("dd/MM/yyyy"))
        self.check_in_input.mousePressEvent = lambda e: self.show_calendar("check_in")
        
        # Fecha de salida
        self.check_out_input = DateInput()
        self.check_out_input.setText(self.check_out_date.toString("dd/MM/yyyy"))
        self.check_out_input.mousePressEvent = lambda e: self.show_calendar("check_out")
        
        # Agregar campos de fecha al contenedor
        dates_container.addWidget(QLabel("Entrada:"))
        dates_container.addWidget(self.check_in_input)
        dates_container.addWidget(QLabel("a"))
        dates_container.addWidget(self.check_out_input)
        dates_container.addStretch()
        
        dates_layout.addLayout(dates_container)
        
        # Calendario popup (inicialmente oculto)
        self.calendar = QCalendarWidget()
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton {
                color: black;
                border: none;
                background-color: transparent;
                padding: 6px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QCalendarWidget QSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                padding: 3px;
            }
            QCalendarWidget QTableView {
                border: none;
                background-color: white;
                selection-background-color: #0078D4;
                selection-color: white;
            }
            QCalendarWidget QTableView::item:hover {
                background-color: #e5f3ff;
            }
            QCalendarWidget QTableView::item:selected {
                background-color: #0078D4;
                color: white;
            }
        """)
        self.calendar.hide()
        self.calendar.clicked.connect(self.on_date_selected)
        dates_layout.addWidget(self.calendar)
        
        dates_group.setLayout(dates_layout)
        main_layout.addWidget(dates_group)
        
        # Frame para selección de habitaciones
        rooms_group = QGroupBox("Selección de Habitaciones")
        rooms_group.setStyleSheet(GROUPBOX_STYLE)
        rooms_layout = QVBoxLayout()
        rooms_layout.setSpacing(12)
        rooms_layout.setContentsMargins(15, 15, 15, 15)
        
        # Tipos de habitaciones con spinners
        self.room_spinners = {}
        tipos_hab = [('Doble', 'Habitaciones Dobles:'), 
                    ('Triple', 'Habitaciones Triples:'), 
                    ('Cuádruple', 'Habitaciones Cuádruples:')]
        
        for tipo, label in tipos_hab:
            room_layout = QHBoxLayout()
            room_layout.setSpacing(12)
            
            # Label
            tipo_label = QLabel(label)
            
            # Spinner
            spinner = QSpinBox()
            spinner.setMinimum(0)
            spinner.setMaximum(10)
            spinner.setValue(0)
            spinner.setMinimumWidth(100)
            spinner.setButtonSymbols(QSpinBox.UpDownArrows)
            spinner.wheelEvent = lambda event: custom_wheel_event(spinner, event)
            spinner.setFocusPolicy(Qt.ClickFocus)
            spinner.setStyleSheet("""
                QSpinBox {
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background: white;
                    min-height: 20px;
                    font-size: 14px;
                }
                QSpinBox:hover {
                    border: 1px solid #999;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 20px;
                    border: none;
                    background: #f0f0f0;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background: #e0e0e0;
                }
            """)
            spinner.valueChanged.connect(self.calculate_total)
            
            self.room_spinners[tipo] = spinner
            
            room_layout.addWidget(tipo_label)
            room_layout.addWidget(spinner)
            room_layout.addStretch()
            rooms_layout.addLayout(room_layout)
        
        rooms_group.setLayout(rooms_layout)
        main_layout.addWidget(rooms_group)
        
        # Resultadoss
        result_group = QGroupBox("Resumen de Precios")
        result_group.setStyleSheet(GROUPBOX_STYLE)
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(15, 15, 15, 15)
        
        # Scroll area para los resultados
        result_scroll = QScrollArea()
        result_scroll.setWidgetResizable(True)
        result_scroll.setFrameShape(QScrollArea.NoFrame)
        result_scroll.setMinimumHeight(200)  # Altura mínima para mostrar varios resultados
        result_scroll.setMaximumHeight(400)  # Altura máxima para no ocupar demasiado espacio
        
        result_content = QWidget()
        result_content_layout = QVBoxLayout(result_content)
        
        self.result_label = QLabel()
        self.result_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 4px;
            }
        """)
        self.result_label.setWordWrap(True)
        result_content_layout.addWidget(self.result_label)
        result_content_layout.addStretch()
        
        result_scroll.setWidget(result_content)
        result_layout.addWidget(result_scroll)
        
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)
        
        main_layout.addStretch()

    def setup_connections(self):
        self.hotel_combo.currentTextChanged.connect(self._on_hotel_changed)
        self.season_combo.currentTextChanged.connect(self._on_season_changed)

    def show_calendar(self, mode):
        self.calendar_mode = mode
        
        # Posicionar el calendario como popup
        if mode == "check_in":
            input_widget = self.check_in_input
        else:
            input_widget = self.check_out_input
            
        # Obtener la posición global del input
        pos = input_widget.mapToGlobal(input_widget.rect().bottomLeft())
        
        # Ajustar la posición para que sea visible
        calendar_size = self.calendar.sizeHint()
        screen = self.screen()
        screen_geometry = screen.geometry()
        
        # Asegurar que el calendario no se salga de la pantalla
        if pos.x() + calendar_size.width() > screen_geometry.right():
            pos.setX(screen_geometry.right() - calendar_size.width())
        if pos.y() + calendar_size.height() > screen_geometry.bottom():
            pos.setY(input_widget.mapToGlobal(input_widget.rect().topLeft()).y() - calendar_size.height())
            
        self.calendar.move(pos)
        self.calendar.setWindowFlags(Qt.Popup)
        self.calendar.show()
        
        if mode == "check_in":
            self.calendar.setSelectedDate(self.check_in_date)
        else:
            self.calendar.setSelectedDate(self.check_out_date)

    def on_date_selected(self, date):
        if self.calendar_mode == "check_in":
            self.check_in_date = date
            self.check_in_input.setText(date.toString("dd/MM/yyyy"))
            if date >= self.check_out_date:
                self.check_out_date = date.addDays(1)
                self.check_out_input.setText(self.check_out_date.toString("dd/MM/yyyy"))
            # Actualizar shared_state
            self.shared_state.check_in = date
        else:
            if date <= self.check_in_date:
                date = self.check_in_date.addDays(1)
            self.check_out_date = date
            self.check_out_input.setText(date.toString("dd/MM/yyyy"))
            # Actualizar shared_state
            self.shared_state.check_out = date
        
        self.calendar.hide()
        self.calculate_total()

    def calculate_total(self):
        hotel = self.hotel_combo.currentText()
        if not hotel:
            return
            
        check_in_date = self.check_in_date
        check_out_date = self.check_out_date
        days = check_in_date.daysTo(check_out_date)
        
        if days <= 0:
            self.result_label.setText("Por favor seleccione fechas válidas")
            return
            
        # Calcular tarifas por tipo de habitación
        total_general = 0.0
        total_decas = 0
        desglose = []
        
        # Obtener datos del hotel
        datos_hotel = self.df[self.df['Hotel'] == hotel]
        
        for tipo, spinner in self.room_spinners.items():
            num_habitaciones = spinner.value()
            if num_habitaciones > 0:
                subtotal_tipo = 0.0
                desglose_tipo = []
                
                # Procesar días
                current_date = check_in_date
                while current_date < check_out_date:
                    # Si es sábado (6) o domingo (7)
                    if current_date.dayOfWeek() >= 6:
                        datos_dia = datos_hotel[datos_hotel['Dias de la Semana'] == 'Fin de semana']
                    else:
                        datos_dia = datos_hotel[datos_hotel['Dias de la Semana'] == 'Entre Semana']
                    
                    if not datos_dia.empty:
                        tarifa_decas = float(datos_dia[tipo].iloc[0])
                        total_decas += tarifa_decas
                        tarifa_usd = tarifa_decas * 5  # Convertir decas a USD
                        subtotal_tipo += tarifa_usd
                        desglose_tipo.append(f"{current_date.toString('dd/MM/yyyy')}: ${tarifa_usd:.2f} (${tarifa_decas:.2f} decas)")
                    
                    current_date = current_date.addDays(1)
                
                # Multiplicar por número de habitaciones
                total_tipo = subtotal_tipo * num_habitaciones
                total_decas = total_decas * num_habitaciones
                total_general += total_tipo
                
                # Agregar al desglose
                if num_habitaciones > 0:
                    desglose.append(f"\n{tipo}s ({num_habitaciones}):")
                    desglose.extend([f"  {linea}" for linea in desglose_tipo])
                    if num_habitaciones > 1:
                        desglose.append(f"  Subtotal por habitación: ${subtotal_tipo:.2f}")
        
        # Mostrar el total de decas
        desglose.append(f"\nTOTAL DECAS: {total_decas:.2f}")
        
        # Mostrar el total general en USD
        desglose.append(f"TOTAL USD: ${total_general:.2f}")
        
        # Calcular y mostrar el total en COP
        total_cop = total_general * 4000
        desglose.append(f"TOTAL COP: ${total_cop:,.2f}")
        
        self.result_label.setText("\n".join(desglose))

    def _on_hotel_changed(self, hotel):
        """Actualiza el hotel en el shared state"""
        self.shared_state.hotel = hotel
        self.calculate_total()

    def _on_season_changed(self, season):
        """Actualiza la temporada en el shared state"""
        self.shared_state.season = season
        self.calculate_total()

    def on_hotel_changed(self, hotel):
        """Recibe notificación de cambio de hotel desde shared state"""
        if hotel != self.hotel_combo.currentText():
            self.hotel_combo.setCurrentText(hotel)
            self.calculate_total()
            
    def on_season_changed(self, season):
        """Recibe notificación de cambio de temporada desde shared state"""
        if season != self.season_combo.currentText():
            self.season_combo.setCurrentText(season)
            self.calculate_total()

    def on_check_in_changed(self, date):
        """Recibe notificación de cambio de fecha de entrada desde shared state"""
        if date != self.check_in_date:
            self.check_in_date = date
            self.check_in_input.setText(date.toString("dd/MM/yyyy"))
            self.calculate_total()

    def on_check_out_changed(self, date):
        """Recibe notificación de cambio de fecha de salida desde shared state"""
        if date != self.check_out_date:
            self.check_out_date = date
            self.check_out_input.setText(date.toString("dd/MM/yyyy"))
            self.calculate_total()

def custom_wheel_event(spinbox, event):
    spinbox.clearFocus()
    event.ignore()  # Permite que el evento suba al padre (scroll area) 