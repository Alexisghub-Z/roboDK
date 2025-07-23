#!/usr/bin/env python3
"""
Analizador Léxico para Robot ABB IRB 120-3/0.6 con Garra Robotiq 2F-85
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

# Importar la ventana principal
from interfaz.ventana_principal import VentanaPrincipal

def main():
    """Función principal de la aplicación"""
    print("🤖 Iniciando Analizador Léxico para Robot ABB IRB 120...")
    
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8f9fa;
        }
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin: 2px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QPushButton:disabled {
            background-color: #6c757d;
        }
        QTextEdit, QPlainTextEdit {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }
        QLabel {
            color: #212529;
        }
    """)
    
    try:
        ventana = VentanaPrincipal()
        ventana.show()
        
        print("✅ Aplicación iniciada correctamente")
        print("💡 Busca el botón '🤖 Conectar Robot' en la parte superior")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Error iniciando la aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()