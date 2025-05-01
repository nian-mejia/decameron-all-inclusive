import os
import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QSpinBox, QGroupBox, QCalendarWidget,
                              QPushButton, QCheckBox, QScrollArea, QDialog,
                              QTextEdit, QFrame, QLineEdit, QCompleter)
from PySide6.QtCore import QDate, Qt, QPoint
from PySide6.QtGui import QPalette, QColor, QTextCharFormat
from decameron_styles import GROUPBOX_STYLE, COMBOBOX_STYLE, LABEL_STYLE

class RangeCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_date = None
        self.end_date = None
        self.is_first_selection = True
        
        # Formato para las fechas seleccionadas
        self.selected_format = QTextCharFormat()
        self.selected_format.setBackground(QColor(0, 120, 215))  # Azul Windows
        self.selected_format.setForeground(QColor(255, 255, 255))
        
        # Formato para las fechas en rango
        self.range_format = QTextCharFormat()
        self.range_format.setBackground(QColor(229, 241, 251))  # Azul claro
        
        # Formato para fines de semana
        self.weekend_format = QTextCharFormat()
        self.weekend_format.setForeground(QColor(255, 0, 0))  # Rojo
        
        self.setMinimumDate(QDate.currentDate())
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        
        # Primero pintar el fondo si es parte del rango
        if self.start_date and self.end_date and date >= self.start_date and date <= self.end_date:
            if date == self.start_date or date == self.end_date:
                painter.fillRect(rect, self.selected_format.background().color())
            else:
                painter.fillRect(rect, self.range_format.background().color())
        elif self.start_date and date == self.start_date:
            painter.fillRect(rect, self.selected_format.background().color())
        
        # Luego pintar el texto, rojo para fines de semana
        if date.dayOfWeek() >= 6:  # Sábado y domingo
            text = str(date.day())
            painter.setPen(self.weekend_format.foreground().color())
            painter.drawText(rect, Qt.AlignCenter, text)
        
        # Si es fecha seleccionada, pintar el texto en blanco
        if (self.start_date and date == self.start_date) or (self.end_date and date == self.end_date):
            text = str(date.day())
            painter.setPen(self.selected_format.foreground().color())
            painter.drawText(rect, Qt.AlignCenter, text)

    def mousePressEvent(self, event):
        date = self.dateAt(event.pos())
        if not date.isValid():
            return
            
        if self.is_first_selection:
            self.start_date = date
            self.end_date = None
            self.is_first_selection = False
        else:
            if date >= self.start_date:
                self.end_date = date
            else:
                self.end_date = self.start_date
                self.start_date = date
            self.is_first_selection = True
            self.clicked.emit(date)
        
        self.updateCells()

    def mouseMoveEvent(self, event):
        if not self.selecting:
            return
            
        pos = event.pos()
        date = self.dateAt(pos)
        if date.isValid() and date >= self.start_date:
            self.end_date = date
            self.updateCells()

    def mouseReleaseEvent(self, event):
        if self.selecting and self.end_date:
            self.selecting = False
            self.clicked.emit(self.end_date)

    def leaveEvent(self, event):
        if not self.is_first_selection and not self.end_date:
            self.end_date = None
            self.updateCells()

class DateInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setInputMask("0000-00-00")
        self.setMinimumWidth(120)
        self.setMaximumWidth(120)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #66afe9;
                outline: 0;
            }
        """)
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # Mostrar el calendario al hacer clic
        parent = self.parent()
        while parent and not isinstance(parent, TodoIncluidoTab):
            parent = parent.parent()
        if parent:
            parent.show_calendar(self)

class TodoIncluidoTab(QWidget):
    def __init__(self, shared_state, parent=None):
        super().__init__(parent)
        self.shared_state = shared_state
        self.shared_state.add_observer(self)
        
        # Usar fechas del shared_state
        self.check_in_date = self.shared_state.check_in
        self.check_out_date = self.shared_state.check_out
        
        self.current_prices = {'weekday': 0, 'weekend': 0}
        self.calculation_details = ""
        self.children_age_widgets = []
        self.active_date_input = None
        
        # Primero configuramos la UI
        self.setup_ui()
        
        # Luego cargamos los datos
        try:
            csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'data', 'todo_incluido.csv')
            print(f"Intentando cargar CSV desde: {csv_path}")
            print(f"El archivo existe: {os.path.exists(csv_path)}")
            
            self.df = pd.read_csv(csv_path)
            print(f"CSV cargado exitosamente. Columnas: {self.df.columns.tolist()}")
            
            # Inicializar los combos después de cargar los datos
            hoteles = sorted(self.df['Hotel'].unique())
            print(f"Agregando {len(hoteles)} hoteles al combo")
            self.hotel_combo.clear()
            self.hotel_combo.addItems(hoteles)
            
            # Establecer valores iniciales desde shared_state
            if self.shared_state.hotel:
                self.hotel_combo.setCurrentText(self.shared_state.hotel)
            else:
                # Si no hay hotel seleccionado, establecer Isleño como default
                default_index = self.hotel_combo.findText("Isleño")
                if default_index >= 0:
                    self.hotel_combo.setCurrentText("Isleño")
                    self.shared_state.hotel = "Isleño"
            
            self.season_combo.clear()
            self.season_combo.addItems(["Baja", "Media", "Alta"])
            self.season_combo.setCurrentText(self.shared_state.season)
            
        except Exception as e:
            print(f"Error cargando datos: {str(e)}")
            raise
            
        # Finalmente configuramos las conexiones
        self.setup_connections()
        
        # Crear el calendario una sola vez
        self.calendar = QCalendarWidget(self)
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.calendar.setMinimumWidth(300)
        self.setup_calendar_style()

    def setup_ui(self):    
        # Crear un QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Crear un widget contenedor para todo el contenido
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Grupo de selección de hotel
        hotel_group = QGroupBox("Selección de Hotel")
        hotel_group.setStyleSheet(GROUPBOX_STYLE)
        hotel_layout = QVBoxLayout()
        hotel_layout.setSpacing(10)
        hotel_layout.setContentsMargins(15, 15, 15, 15)
        
        # Crear los widgets
        hotel_label = QLabel("Hotel:")
        hotel_label.setStyleSheet(LABEL_STYLE)
        self.hotel_combo = QComboBox()
        self.hotel_combo.setMinimumWidth(300)
        self.hotel_combo.setEditable(True)
        self.hotel_combo.setInsertPolicy(QComboBox.NoInsert)
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
        
        room_label = QLabel("Tipo de Habitación:")
        room_label.setStyleSheet(LABEL_STYLE)
        self.room_combo = QComboBox()
        self.room_combo.setMinimumWidth(300)
        self.room_combo.setStyleSheet(COMBOBOX_STYLE)
        
        # Agregar los widgets al layout
        hotel_layout.addWidget(hotel_label)
        hotel_layout.addWidget(self.hotel_combo)
        hotel_layout.addSpacing(5)
        hotel_layout.addWidget(season_label)
        hotel_layout.addWidget(self.season_combo)
        hotel_layout.addSpacing(5)
        hotel_layout.addWidget(room_label)
        hotel_layout.addWidget(self.room_combo)
        
        hotel_group.setLayout(hotel_layout)
        layout.addWidget(hotel_group)
        
        # Grupo de personas (movido aquí, después de la selección del hotel)
        people_group = QGroupBox("Personas")
        people_group.setStyleSheet(GROUPBOX_STYLE)
        people_layout = QHBoxLayout()
        people_layout.setSpacing(15)
        
        # Layout izquierdo para adultos
        left_layout = QVBoxLayout()
        
        # Adultos
        adults_layout = QVBoxLayout()
        adults_label = QLabel("Adultos:")
        self.adults_spin = QSpinBox()
        self.adults_spin.setRange(1, 10)
        self.adults_spin.setValue(2)
        self.adults_spin.wheelEvent = lambda event, s=self.adults_spin: custom_wheel_event(s, event)
        self.adults_spin.setFocusPolicy(Qt.ClickFocus)
        adults_layout.addWidget(adults_label)
        adults_layout.addWidget(self.adults_spin)
        left_layout.addLayout(adults_layout)
        left_layout.addStretch()  # Esto mantendrá el layout de adultos arriba
        people_layout.addLayout(left_layout)
        
        # Layout derecho para niños
        right_layout = QVBoxLayout()
        
        # Niños
        children_label = QLabel("Niños:")
        self.children_spin = QSpinBox()
        self.children_spin.setRange(0, 8)
        self.children_spin.setValue(0)
        self.children_spin.valueChanged.connect(self.update_children_inputs)
        self.children_spin.wheelEvent = lambda event, s=self.children_spin: custom_wheel_event(s, event)
        self.children_spin.setFocusPolicy(Qt.ClickFocus)
        right_layout.addWidget(children_label)
        right_layout.addWidget(self.children_spin)
        
        # Contenedor para los inputs de edad de los niños
        self.children_ages_container = QVBoxLayout()
        right_layout.addLayout(self.children_ages_container)
        right_layout.addStretch()  # Esto empujará todo hacia arriba
        
        people_layout.addLayout(right_layout)
        
        people_group.setLayout(people_layout)
        layout.addWidget(people_group)
        
        # Grupo de fechas
        dates_group = QGroupBox("Selección de Fechas")
        dates_group.setStyleSheet(GROUPBOX_STYLE)
        dates_layout = QVBoxLayout()
        dates_layout.setContentsMargins(10, 20, 10, 10)
        
        # Layout para los campos de fecha
        date_fields_layout = QHBoxLayout()
        date_fields_layout.setSpacing(10)
        
        # Campo de fecha de entrada
        self.check_in_input = DateInput(self)
        self.check_in_input.setText(self.check_in_date.toString("yyyy-MM-dd"))
        self.check_in_input.textChanged.connect(self.on_date_input_changed)
        date_fields_layout.addWidget(self.check_in_input)
        
        # Label "to"
        to_label = QLabel("to")
        to_label.setAlignment(Qt.AlignCenter)
        to_label.setStyleSheet("font-size: 14px; color: #666;")
        date_fields_layout.addWidget(to_label)
        
        # Campo de fecha de salida
        self.check_out_input = DateInput(self)
        self.check_out_input.setText(self.check_out_date.toString("yyyy-MM-dd"))
        self.check_out_input.textChanged.connect(self.on_date_input_changed)
        date_fields_layout.addWidget(self.check_out_input)
        
        # Contenedor con borde para los campos de fecha
        date_container = QFrame()
        date_container.setLayout(date_fields_layout)
        date_container.setStyleSheet("""
            QFrame {
                border: none;
                border-radius: 6px;
                background: white;
                padding: 5px;
            }
        """)
        
        dates_layout.addWidget(date_container)
        dates_group.setLayout(dates_layout)
        layout.addWidget(dates_group)
        
        # Grupo de ofertas
        offers_group = QGroupBox("Ofertas")
        offers_group.setStyleSheet(GROUPBOX_STYLE)
        offers_layout = QVBoxLayout()
        
        # Layout para las opciones de ofertas
        offer_options_layout = QHBoxLayout()
        
        # Opción 2x1
        self.offer_2x1_checkbox = QCheckBox("Oferta 2x1")
        offer_options_layout.addWidget(self.offer_2x1_checkbox)
        
        # Opción de descuento porcentual
        self.discount_checkbox = QCheckBox("Aplicar Descuento")
        self.discount_spinbox = QSpinBox()
        self.discount_spinbox.setRange(1, 100)
        self.discount_spinbox.setValue(10)
        self.discount_spinbox.setSuffix("%")
        self.discount_spinbox.setEnabled(False)
        self.discount_spinbox.wheelEvent = lambda event, s=self.discount_spinbox: custom_wheel_event(s, event)
        self.discount_spinbox.setFocusPolicy(Qt.ClickFocus)
        offer_options_layout.addWidget(self.discount_checkbox)
        offer_options_layout.addWidget(self.discount_spinbox)
        offers_layout.addLayout(offer_options_layout)
        
        # Campo para el valor del dólar
        dollar_layout = QHBoxLayout()
        dollar_layout.addWidget(QLabel("Valor del Dólar (COP):"))
        self.dollar_value = QSpinBox()
        self.dollar_value.setRange(1, 10000)
        self.dollar_value.setValue(4000)
        self.dollar_value.wheelEvent = lambda event, s=self.dollar_value: custom_wheel_event(s, event)
        self.dollar_value.setFocusPolicy(Qt.ClickFocus)
        dollar_layout.addWidget(self.dollar_value)
        offers_layout.addLayout(dollar_layout)
        
        offers_group.setLayout(offers_layout)
        layout.addWidget(offers_group)
        
        # Botón Ver Detalles
        self.details_button = QPushButton("Ver Detalles del Cálculo")
        layout.addWidget(self.details_button)
        
        # Resultados
        self.result_label = QLabel()
        self.result_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.result_label)
        
        layout.addStretch()
        
        # Agregar el container al scroll area y el scroll area al widget principal
        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def setup_connections(self):
        # Conectar cambios en los combos al shared_state
        self.hotel_combo.currentTextChanged.connect(self._on_hotel_changed)
        self.season_combo.currentTextChanged.connect(self._on_season_changed)
        
        self.hotel_combo.currentIndexChanged.connect(self.update_rooms)
        self.room_combo.currentIndexChanged.connect(self.calculate_total)
        self.offer_2x1_checkbox.toggled.connect(self.on_offer_changed)
        self.discount_checkbox.toggled.connect(self.on_discount_toggled)
        self.discount_spinbox.valueChanged.connect(self.calculate_total)
        self.dollar_value.valueChanged.connect(self.calculate_total)
        self.adults_spin.valueChanged.connect(self.calculate_total)
        self.children_spin.valueChanged.connect(self.calculate_total)
        self.details_button.clicked.connect(self.show_details_popup)

    def show_calendar(self, date_input):
        if not self.calendar:
            return
            
        self.active_date_input = date_input
        
        # Establecer la fecha actual del calendario
        current_date = QDate.fromString(date_input.text(), "yyyy-MM-dd")
        if current_date.isValid():
            self.calendar.setSelectedDate(current_date)
        
        # Posicionar el calendario debajo del campo de fecha
        pos = date_input.mapToGlobal(date_input.rect().bottomLeft())
        self.calendar.move(pos.x(), pos.y() + 2)  # Agregar un pequeño offset vertical
        self.calendar.show()

    def on_date_input_changed(self):
        # Obtener las fechas de los inputs
        try:
            check_in = QDate.fromString(self.check_in_input.text(), "yyyy-MM-dd")
            check_out = QDate.fromString(self.check_out_input.text(), "yyyy-MM-dd")
            
            if check_in.isValid() and check_out.isValid():
                if check_out < check_in:
                    check_out = check_in.addDays(1)
                    self.check_out_input.setText(check_out.toString("yyyy-MM-dd"))
                
                self.check_in_date = check_in
                self.check_out_date = check_out
                self.calculate_total()
        except:
            pass

    def on_date_selected(self, date):
        if self.active_date_input:
            self.active_date_input.setText(date.toString("yyyy-MM-dd"))
            
            # Si es el campo de entrada, actualizar también la fecha de salida
            if self.active_date_input == self.check_in_input:
                self.check_in_date = date
                self.shared_state.check_in = date
                next_date = date.addDays(1)
                self.check_out_date = next_date
                self.shared_state.check_out = next_date
                self.check_out_input.setText(next_date.toString("yyyy-MM-dd"))
            else:
                self.check_out_date = date
                self.shared_state.check_out = date
            
            self.calendar.hide()
            self.active_date_input = None
            self.calculate_total()

    def on_check_in_changed(self, date):
        """Recibe notificación de cambio de fecha de entrada desde shared state"""
        if date != self.check_in_date:
            self.check_in_date = date
            self.check_in_input.setText(date.toString("yyyy-MM-dd"))
            self.calculate_total()

    def on_check_out_changed(self, date):
        """Recibe notificación de cambio de fecha de salida desde shared state"""
        if date != self.check_out_date:
            self.check_out_date = date
            self.check_out_input.setText(date.toString("yyyy-MM-dd"))
            self.calculate_total()

    def on_discount_toggled(self, checked):
        self.discount_spinbox.setEnabled(checked)
        if checked:
            self.offer_2x1_checkbox.setChecked(False)
        self.calculate_total()

    def on_offer_changed(self, checked):
        if checked:
            self.discount_checkbox.setChecked(False)
        self.calculate_total()

    def update_rooms(self):
        hotel = self.hotel_combo.currentText()
        self.room_combo.clear()
        if hotel:
            rooms = sorted(self.df[self.df['Hotel'] == hotel]['Tipo de Habitacion'].unique())
            self.room_combo.addItems(rooms)
            self.update_prices()
            
    def update_prices(self):
        hotel = self.hotel_combo.currentText()
        room = self.room_combo.currentText()
        season = self.season_combo.currentText()
        
        if hotel and room and season:
            # Obtener precios para días entre semana
            weekday_data = self.df[
                (self.df['Hotel'] == hotel) & 
                (self.df['Tipo de Habitacion'] == room) &
                (self.df['Dias de la Semana'].str.contains('Entre Semana', na=False))
            ]
            
            # Obtener precios para fin de semana
            weekend_data = self.df[
                (self.df['Hotel'] == hotel) & 
                (self.df['Tipo de Habitacion'] == room) &
                (self.df['Dias de la Semana'].str.contains('Fin de Semana', na=False))
            ]
            
            if not weekday_data.empty:
                self.current_prices['weekday'] = weekday_data[f'Tarifa {season}'].iloc[0]
            if not weekend_data.empty:
                self.current_prices['weekend'] = weekend_data[f'Tarifa {season}'].iloc[0]
                
            self.calculate_total()
        else:
            self.current_prices = {'weekday': 0, 'weekend': 0}
            self.result_label.setText("")

    def show_details_popup(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Detalles del Cálculo")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(300)
        
        layout = QVBoxLayout(dialog)
        
        details = QTextEdit()
        details.setReadOnly(True)
        details.setHtml(self.calculation_details)
        
        layout.addWidget(details)
        
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.exec()

    def calculate_total(self):
        if not all([self.hotel_combo.currentText(), self.room_combo.currentText(), 
                   self.season_combo.currentText()]):
            return
        
        check_in_date = self.check_in_date
        check_out_date = self.check_out_date
        nights = check_in_date.daysTo(check_out_date)
        
        if nights <= 0:
            self.result_label.setText("Por favor seleccione fechas válidas")
            return
        
        # Iniciar detalles del cálculo
        details = []
        details.append(f"<h3>Detalles de la Reserva</h3>")
        details.append(f"<p><b>Hotel:</b> {self.hotel_combo.currentText()}")
        details.append(f"<b>Habitación:</b> {self.room_combo.currentText()}")
        details.append(f"<b>Temporada:</b> {self.season_combo.currentText()}</p>")
        details.append(f"<p><b>Fechas:</b> {check_in_date.toString('dd/MM/yyyy')} - {check_out_date.toString('dd/MM/yyyy')}")
        details.append(f"<b>Total noches:</b> {nights}</p>")
        details.append(f"<p><b>Personas:</b> {self.adults_spin.value()} adultos, {self.children_spin.value()} niños</p>")
        
        # Obtener precios base
        weekday_price = float(self.current_prices.get('weekday', 0))
        weekend_price = float(self.current_prices.get('weekend', 0))
        
        details.append("<h4>Desglose de Precios por Día</h4>")
        details.append("<p><b>Tarifa entre semana:</b> ${:,.2f}<br>".format(weekday_price))
        details.append("<b>Tarifa fin de semana:</b> ${:,.2f}</p>".format(weekend_price))
        
        # Calcular días entre semana y fines de semana
        total = 0
        weekday_count = 0
        weekend_count = 0
        current_date = check_in_date
        
        while current_date < check_out_date:
            if current_date.dayOfWeek() >= 6:
                total += weekend_price
                weekend_count += 1
            else:
                total += weekday_price
                weekday_count += 1
            current_date = current_date.addDays(1)
        
        details.append(f"<p>Días entre semana: {weekday_count} (${weekday_count * weekday_price:,.2f})<br>")
        details.append(f"Días fin de semana: {weekend_count} (${weekend_count * weekend_price:,.2f})</p>")
        
        subtotal = total
        details.append(f"<p><b>Subtotal por día:</b> ${subtotal:,.2f}</p>")
        
        # Calcular total para adultos
        total_adults = subtotal
        if self.offer_2x1_checkbox.isChecked():
            total_adults = total_adults / 2
            details.append(f"<p><b>Oferta 2x1 aplicada a adultos:</b> -${subtotal/2:,.2f}</p>")
        elif self.discount_checkbox.isChecked():
            discount = self.discount_spinbox.value() / 100.0
            discount_amount = total_adults * discount
            total_adults = total_adults * (1 - discount)
            details.append(f"<p><b>Descuento {self.discount_spinbox.value()}% aplicado:</b> -${discount_amount:,.2f}</p>")
        
        # Multiplicar por número de adultos
        total_adults = total_adults * self.adults_spin.value()
        
        details.append("<h4>Cálculo por Personas</h4>")
        details.append(f"<p><b>Adultos ({self.adults_spin.value()}):</b><br>")
        details.append(f"Precio por adulto: ${total_adults/self.adults_spin.value():,.2f}<br>")
        details.append(f"Total adultos: ${total_adults:,.2f}</p>")
        
        # Calcular total para niños (sin aplicar 2x1)
        total_children = 0
        if self.children_spin.value() > 0:
            details.append("<b>Niños:</b><br>")
            for i, age_container in enumerate(self.children_age_widgets):
                age_spin = age_container.itemAt(1).widget()
                age = age_spin.value()
                child_price = 0
                if age >= 6 and age < 12:
                    child_price = subtotal * 0.75  # Niños pagan 75% del precio base
                    details.append(f"Niño {i+1} ({age} años) - 75% del precio base: ${child_price:,.2f}<br>")
                elif age < 6:
                    child_price = 0
                    details.append(f"Niño {i+1} ({age} años) - Gratis<br>")
                total_children += child_price
            
            details.append(f"Subtotal niños: ${total_children:,.2f}</p>")
        
        # Sumar total de adultos y niños
        total = total_adults + total_children
        
        # Convertir a COP
        total_cop = total * self.dollar_value.value()
        
        details.append("<h4>Total Final</h4>")
        details.append(f"<p><b>Total USD:</b> ${total:,.2f}<br>")
        details.append(f"<b>Total COP:</b> ${total_cop:,.0f}</p>")
        
        # Guardar detalles para el popup
        self.calculation_details = "<br>".join(details)
        
        # Mostrar resultados resumidos
        result_text = f"Total para {nights} días:\n"
        result_text += f"{self.adults_spin.value()} adultos, {self.children_spin.value()} niños\n"
        result_text += f"USD ${total:.2f}\n"
        result_text += f"COP ${total_cop:,.0f}"
        
        self.result_label.setText(result_text)

    def _on_hotel_changed(self, hotel):
        """Actualiza el hotel en el shared state"""
        self.shared_state.hotel = hotel
        self.update_rooms()
        self.update_prices()
        self.calculate_total()

    def _on_season_changed(self, season):
        """Actualiza la temporada en el shared state"""
        self.shared_state.season = season
        self.update_prices()
        self.calculate_total()

    def on_hotel_changed(self, hotel):
        """Recibe notificación de cambio de hotel desde shared state"""
        if hotel != self.hotel_combo.currentText():
            self.hotel_combo.setCurrentText(hotel)
            self.update_rooms()
            self.update_prices()
            self.calculate_total()
            
    def on_season_changed(self, season):
        """Recibe notificación de cambio de temporada desde shared state"""
        if season != self.season_combo.currentText():
            self.season_combo.setCurrentText(season)
            self.update_prices()
            self.calculate_total()

    def update_children_inputs(self, new_count):
        # Limpiar los spinboxes existentes
        while len(self.children_age_widgets) > new_count:
            # Eliminar el último widget
            widget_container = self.children_age_widgets.pop()
            # Eliminar del layout y destruir
            for i in range(widget_container.count()):
                w = widget_container.itemAt(i).widget()
                if w:
                    w.deleteLater()
            self.children_ages_container.removeItem(widget_container)
        
        # Agregar nuevos spinboxes si es necesario
        while len(self.children_age_widgets) < new_count:
            # Crear contenedor horizontal para la edad
            age_container = QHBoxLayout()
            
            # Crear label y spinbox
            label = QLabel(f"Edad niño {len(self.children_age_widgets) + 1}:")
            age_spin = QSpinBox()
            age_spin.setRange(0, 11)
            age_spin.setValue(5)
            age_spin.valueChanged.connect(self.calculate_total)
            age_spin.wheelEvent = lambda event, s=age_spin: custom_wheel_event(s, event)
            age_spin.setFocusPolicy(Qt.ClickFocus)
            
            # Agregar widgets al contenedor
            age_container.addWidget(label)
            age_container.addWidget(age_spin)
            
            # Agregar el contenedor al layout principal
            self.children_ages_container.addLayout(age_container)
            
            # Guardar referencia al contenedor
            self.children_age_widgets.append(age_container)
        
        self.calculate_total()

    def setup_calendar_style(self):
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
            QCalendarWidget QToolButton {
                color: #333;
                border: none;
                background: transparent;
                font-size: 13px;
                padding: 5px;
            }
            QCalendarWidget QMenu {
                background: white;
                border: 1px solid #ccc;
            }
            QCalendarWidget QSpinBox {
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: white;
                border-bottom: 1px solid #eee;
                padding: 4px;
            }
            QCalendarWidget QWidget { 
                alternate-background-color: #f9f9f9;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #333;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #ccc;
            }
            QCalendarWidget QWidget#qt_calendar_calendarview {
                border: none;
            }
            QCalendarWidget QTableView {
                outline: 0;
            }
        """) 

def custom_wheel_event(spinbox, event):
    spinbox.clearFocus()
    event.ignore() 