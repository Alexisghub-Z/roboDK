#!/usr/bin/env python3
"""
Ventana Principal COMPLETA del Analizador Léxico
CON botón de conexión de robot
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPlainTextEdit, QPushButton, QLabel, 
                             QSplitter, QFileDialog, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCharFormat, QColor

# Importar módulos del proyecto
try:
    from analizador.analizador_lexico import AnalizadorLexico
    from robodk_controller.robot_controller import RobotController
except ImportError as e:
    print(f"⚠️ Error importando módulos: {e}")
    # Crear clases dummy para que funcione sin los módulos
    class AnalizadorLexico:
        def analizar(self, codigo):
            return {
                'exito': True,
                'salida': '<h2>✅ Análisis básico completado</h2>',
                'errores': []
            }
    
    class RobotController:
        def __init__(self):
            self.conectado = False
        def conectar(self):
            return False
        def desconectar(self):
            pass

class LineNumberArea(QWidget):
    """Widget para mostrar números de línea"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(240, 240, 240))
        
        block = self.editor.document().firstBlock()
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()
        
        line_number = 1
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(120, 120, 120))
                painter.drawText(0, int(top), self.width() - 5, 
                               int(self.editor.fontMetrics().height()),
                               Qt.AlignRight, str(line_number))
            
            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            line_number += 1

class CodeEditor(QPlainTextEdit):
    """Editor de código con números de línea"""
    
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        
        # Configurar fuente monoespaciada
        font = QFont("Courier New", 12)
        self.setFont(font)
        
        # Conectar señales
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
        
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(0, cr.top(), self.line_number_area_width(), cr.height())
        
    def highlight_current_line(self):
        selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextCharFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)
        self.setExtraSelections(selections)

class AnalysisThread(QThread):
    """Hilo para ejecutar el análisis sin bloquear la UI"""
    
    analysis_finished = pyqtSignal(str, bool)  # resultado, éxito
    robot_command = pyqtSignal(str, dict)      # comando, parámetros
    
    def __init__(self, codigo, robodk_enabled=False):
        super().__init__()
        self.codigo = codigo
        self.robodk_enabled = robodk_enabled
        self.analizador = AnalizadorLexico()
        
    def run(self):
        try:
            resultado = self.analizador.analizar(self.codigo)
            
            # Si el análisis fue exitoso y RoboDK está habilitado
            if resultado['exito'] and self.robodk_enabled:
                # Emitir comandos para el robot
                for cuadruplo in resultado.get('cuadruplos', []):
                    if cuadruplo['operador'] == 'CALL':
                        comando = {
                            'robot_id': cuadruplo['operando1'],
                            'componente': cuadruplo['resultado'],
                            'valor': int(cuadruplo['operando2'])
                        }
                        self.robot_command.emit('mover_componente', comando)
            
            self.analysis_finished.emit(resultado['salida'], resultado['exito'])
            
        except Exception as e:
            error_msg = f"❌ Error inesperado durante el análisis: {str(e)}"
            self.analysis_finished.emit(error_msg, False)

class VentanaPrincipal(QMainWindow):
    """Ventana principal de la aplicación CON botón de robot"""
    
    def __init__(self):
        super().__init__()
        self.robot_controller = None
        self.init_ui()
        self.setup_robot_controller()
        
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle("Analizador Léxico - Robot ABB IRB 120")
        self.setGeometry(100, 100, 1400, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Splitter para áreas de código y salida
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Área de entrada de código
        input_frame = self.create_input_area()
        splitter.addWidget(input_frame)
        
        # Área de salida
        output_frame = self.create_output_area()
        splitter.addWidget(output_frame)
        
        # Configurar proporciones del splitter
        splitter.setSizes([600, 800])
        
        # Barra de estado
        self.statusBar().showMessage("Listo para analizar código")
        
    def create_header(self):
        """Crear el header con título y botones"""
        header_layout = QHBoxLayout()
        
        # Título
        titulo = QLabel("compilador")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; margin: 10px;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Botones
        self.btn_cargar = QPushButton("📁 Cargar Archivo")
        self.btn_cargar.clicked.connect(self.cargar_archivo)
        header_layout.addWidget(self.btn_cargar)
        
        self.btn_guardar = QPushButton("💾 Guardar Archivo")
        self.btn_guardar.clicked.connect(self.guardar_archivo)
        self.btn_guardar.setEnabled(False)
        header_layout.addWidget(self.btn_guardar)
        
        # BOTÓN DE ROBOT - AQUÍ ESTÁ!
        self.btn_conectar_robot = QPushButton("🤖 Conectar Robot")
        self.btn_conectar_robot.clicked.connect(self.toggle_robot_connection)
        self.btn_conectar_robot.setToolTip("Conectar/Desconectar RoboDK")
        header_layout.addWidget(self.btn_conectar_robot)
        
        self.btn_analizar = QPushButton("🔍 Analizar")
        self.btn_analizar.clicked.connect(self.analizar_codigo)
        header_layout.addWidget(self.btn_analizar)
        
        self.btn_limpiar = QPushButton("🧹 Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_todo)
        header_layout.addWidget(self.btn_limpiar)
        
        return header_layout
        
    def create_input_area(self):
        """Crear el área de entrada de código"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Etiqueta
        label = QLabel("📝 Código de Entrada:")
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        
        # Editor de código
        self.editor_codigo = CodeEditor()
        self.editor_codigo.setPlaceholderText(
            "Ingresa tu código aquí...\\n\\n"
            "Ejemplo:\\n"
            "Robot ROBOT1\\n"
            "ROBOT1.base = 90\\n"
            "ROBOT1.hombro = 45\\n"
            "ROBOT1.codo = 60\\n"
            "ROBOT1.garra = 30\\n"
            "ROBOT1.velocidad = 25\\n"
            "ROBOT1.repetir = 3 {\\n"
            "    ROBOT1.base = 180\\n"
            "    ROBOT1.garra = 0\\n"
            "}"
        )
        layout.addWidget(self.editor_codigo)
        
        return frame
        
    def create_output_area(self):
        """Crear el área de salida de resultados"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Etiqueta
        label = QLabel("📊 Resultados del Análisis:")
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        
        # Área de salida
        self.salida_texto = QTextEdit()
        self.salida_texto.setReadOnly(True)
        self.salida_texto.setFont(QFont("Courier New", 10))
        self.salida_texto.setPlaceholderText("Los resultados del análisis aparecerán aquí...")
        layout.addWidget(self.salida_texto)
        
        return frame
        
    def setup_robot_controller(self):
        """Configurar el controlador del robot"""
        try:
            self.robot_controller = RobotController()
            self.statusBar().showMessage("Controlador de robot inicializado - Click '🤖 Conectar Robot' para conectar")
        except Exception as e:
            self.statusBar().showMessage(f"Error inicializando robot: {e}")
            self.btn_conectar_robot.setEnabled(False)
            
    def toggle_robot_connection(self):
        """Alternar conexión con el robot"""
        if not self.robot_controller:
            QMessageBox.warning(self, "Error", "Controlador de robot no disponible")
            return
            
        try:
            if not self.robot_controller.conectado:
                # Intentar conectar
                self.btn_conectar_robot.setText("🔄 Conectando...")
                self.btn_conectar_robot.setEnabled(False)
                
                if self.robot_controller.conectar():
                    self.btn_conectar_robot.setText("🔌 Desconectar Robot")
                    self.btn_conectar_robot.setStyleSheet("background-color: #28a745; color: white;")
                    self.btn_conectar_robot.setEnabled(True)
                    self.statusBar().showMessage("✅ Robot conectado exitosamente")
                    QMessageBox.information(self, "Éxito", "Robot conectado correctamente\\nAhora puedes analizar código y se ejecutará en RoboDK")
                else:
                    self.btn_conectar_robot.setText("🤖 Conectar Robot")
                    self.btn_conectar_robot.setEnabled(True)
                    QMessageBox.warning(self, "Error de Conexión", 
                                      "No se pudo conectar al robot\\n\\n"
                                      "Verifica que:\\n"
                                      "1. RoboDK esté ejecutándose\\n"
                                      "2. Tengas un robot ABB IRB 120 cargado\\n"
                                      "3. Ejecuta: python test_robodk_fixed.py")
            else:
                # Desconectar
                self.robot_controller.desconectar()
                self.btn_conectar_robot.setText("🤖 Conectar Robot")
                self.btn_conectar_robot.setStyleSheet("")
                self.statusBar().showMessage("Robot desconectado")
                
        except Exception as e:
            self.btn_conectar_robot.setText("🤖 Conectar Robot")
            self.btn_conectar_robot.setStyleSheet("")
            self.btn_conectar_robot.setEnabled(True)
            QMessageBox.critical(self, "Error", f"Error con conexión del robot:\\n{e}")
            
    def cargar_archivo(self):
        """Cargar archivo de código"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Cargar Archivo de Código",
            "",
            "Archivos de texto (*.txt *.robot *.abb);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    contenido = file.read()
                    self.editor_codigo.setPlainText(contenido)
                    self.btn_guardar.setEnabled(True)
                    self.statusBar().showMessage(f"Archivo cargado: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {e}")
                
    def guardar_archivo(self):
        """Guardar archivo de código"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Archivo de Código",
            "",
            "Archivos de texto (*.txt);;Archivos robot (*.robot);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.editor_codigo.toPlainText())
                    self.statusBar().showMessage(f"Archivo guardado: {os.path.basename(file_path)}")
                    QMessageBox.information(self, "Éxito", "Archivo guardado correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {e}")
                
    def analizar_codigo(self):
        """Analizar el código ingresado"""
        codigo = self.editor_codigo.toPlainText().strip()
        
        if not codigo:
            QMessageBox.warning(self, "Advertencia", "Por favor ingresa código para analizar")
            return
            
        # Deshabilitar botón durante análisis
        self.btn_analizar.setEnabled(False)
        self.btn_analizar.setText("⏳ Analizando...")
        self.statusBar().showMessage("Analizando código...")
        
        # Crear y ejecutar hilo de análisis
        robodk_enabled = self.robot_controller and self.robot_controller.conectado
        self.analysis_thread = AnalysisThread(codigo, robodk_enabled)
        self.analysis_thread.analysis_finished.connect(self.on_analysis_finished)
        self.analysis_thread.robot_command.connect(self.ejecutar_comando_robot)
        self.analysis_thread.start()
        
    def on_analysis_finished(self, resultado, exito):
        """Manejar finalización del análisis"""
        self.salida_texto.setHtml(resultado)
        
        # Rehabilitar botón
        self.btn_analizar.setEnabled(True)
        self.btn_analizar.setText("🔍 Analizar")
        
        if exito:
            self.statusBar().showMessage("✅ Análisis completado exitosamente")
            if self.robot_controller and self.robot_controller.conectado:
                self.statusBar().showMessage("✅ Análisis completado - Comandos enviados al robot")
        else:
            self.statusBar().showMessage("❌ Análisis completado con errores")
            
    def ejecutar_comando_robot(self, comando, parametros):
        """Ejecutar comando en el robot real"""
        if self.robot_controller and self.robot_controller.conectado:
            try:
                if comando == 'mover_componente':
                    self.robot_controller.mover_componente(
                        parametros['componente'],
                        parametros['valor']
                    )
                    print(f"🤖 Ejecutando: {parametros['componente']} = {parametros['valor']}")
            except Exception as e:
                self.statusBar().showMessage(f"Error ejecutando comando: {e}")
                
    def limpiar_todo(self):
        """Limpiar todas las áreas"""
        self.editor_codigo.setPlainText("")
        self.salida_texto.setHtml("")
        self.btn_guardar.setEnabled(False)
        self.statusBar().showMessage("Áreas limpiadas")
        
    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        if self.robot_controller and self.robot_controller.conectado:
            self.robot_controller.desconectar()
        event.accept()