# Estilo base para todos los QGroupBox
GROUPBOX_STYLE = """
    QGroupBox {
        font-size: 13px;
        font-weight: bold;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-top: 20px;
        padding: 24px 16px 16px 16px;
        background-color: white;
        color: #1a365d;
    }
    QGroupBox::title {
        padding: 0 10px;
        top: -12px;
        left: 10px;
        color: #2c5282;
        font-weight: bold;
        background-color: white;
        position: absolute;
    }
"""

# Estilo para los ComboBox
COMBOBOX_STYLE = """
    QComboBox {
        padding: 5px 10px;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        background: white;
        min-height: 20px;
        font-size: 13px;
        color: #1a365d;
    }
    QComboBox:hover {
        border: 1px solid #2c5282;
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 8px;
    }
    QComboBox::down-arrow {
        image: url(assets/icons/down-arrow.png);
        width: 12px;
        height: 12px;
    }
    QComboBox QAbstractItemView {
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        background: white;
        selection-background-color: #0078D4;
        selection-color: white;
    }
"""

# Estilo para las etiquetas
LABEL_STYLE = """
    QLabel {
        font-size: 13px;
        font-weight: bold;
        color: #1a365d;
        margin-bottom: 5px;
    }
""" 