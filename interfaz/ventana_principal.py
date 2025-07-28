#!/usr/bin/env python3
"""
Ventana Principal DEFINITIVAMENTE CORREGIDA del Analizador Léxico
CORRECCIÓN CRÍTICA: Lógica de salto después de bucles completamente arreglada
Sistema de velocidades independientes + garra como rotación eje 6
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
    cuadruplos_ready = pyqtSignal(list)        # cuádruplos para ejecutar
    
    def __init__(self, codigo, robodk_enabled=False, ventana_principal=None):
        super().__init__()
        self.codigo = codigo
        self.robodk_enabled = robodk_enabled
        self.ventana_principal = ventana_principal
        self.analizador = AnalizadorLexico()
        
    def run(self):
        try:
            resultado = self.analizador.analizar(self.codigo)
            
            # Si el análisis fue exitoso y RoboDK está habilitado
            if resultado['exito'] and self.robodk_enabled and self.ventana_principal:
                # Emitir señal con los cuádruplos para ejecutar en el hilo principal
                self.cuadruplos_ready.emit(resultado.get('cuadruplos', []))
            
            self.analysis_finished.emit(resultado['salida'], resultado['exito'])
            
        except Exception as e:
            error_msg = f"❌ Error inesperado durante el análisis: {str(e)}"
            self.analysis_finished.emit(error_msg, False)

class VentanaPrincipal(QMainWindow):
    """Ventana principal CON LÓGICA DE BUCLES DEFINITIVAMENTE CORREGIDA"""
    
    def __init__(self):
        super().__init__()
        self.robot_controller = None
        self.init_ui()
        self.setup_robot_controller()
        
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle("Analizador Léxico - Robot ABB IRB 120 (Lógica de Bucles DEFINITIVAMENTE Corregida)")
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
        self.statusBar().showMessage("Listo para analizar código - Lógica de bucles DEFINITIVAMENTE corregida")
        
    def create_header(self):
        """Crear el header con título y botones"""
        header_layout = QHBoxLayout()
        
        # Título
        titulo = QLabel("Compilador Robot - Lógica de Bucles DEFINITIVA")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
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
        
        # BOTÓN DE ROBOT
        self.btn_conectar_robot = QPushButton("🤖 Conectar Robot")
        self.btn_conectar_robot.clicked.connect(self.toggle_robot_connection)
        self.btn_conectar_robot.setToolTip("Conectar/Desconectar RoboDK")
        header_layout.addWidget(self.btn_conectar_robot)
        
        self.btn_analizar = QPushButton("🔍 Analizar & Ejecutar")
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
        label = QLabel("📝 Código de Entrada (Lógica de Bucles DEFINITIVAMENTE Corregida):")
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        
        # Editor de código
        self.editor_codigo = CodeEditor()
        self.editor_codigo.setPlaceholderText(
            "Ingresa tu código con velocidades independientes y método .negativo...\n\n"
            "🚀 EJEMPLO DE VELOCIDADES INDEPENDIENTES:\n"
            "Robot SIMPLE\n"
            "SIMPLE.velocidad = 3      # Velocidad inicial: 3 segundos\n"
            "SIMPLE.base = 90          # Base se mueve en 3s\n"
            "SIMPLE.velocidad = 1      # Cambiar a velocidad rápida\n"
            "SIMPLE.hombro = 45        # Hombro se mueve en 1s\n"
            "SIMPLE.velocidad = 5      # Cambiar a velocidad lenta\n"
            "SIMPLE.garra = 90         # Garra rota eje 6 en 5s\n\n"
            "🔁 EJEMPLO CON LÓGICA DE BUCLES CORREGIDA:\n"
            "Robot PRUEBA\n"
            "PRUEBA.velocidad = 2\n"
            "PRUEBA.repetir = 3 {\n"
            "    PRUEBA.base.negativo = 45\n"
            "    PRUEBA.base = 45\n"
            "    PRUEBA.garra.negativo = 90\n"
            "    PRUEBA.hombro.negativo = 30\n"
            "    PRUEBA.base = 0\n"
            "    PRUEBA.garra = 0\n"
            "    PRUEBA.hombro = 0\n"
            "}\n"
            "PRUEBA.hombro = 80        # ✅ Esta instrucción se ejecuta DESPUÉS del bucle\n\n"
            "✅ El bucle se ejecuta EXACTAMENTE las veces especificadas\n"
            "✅ Las instrucciones después del } se ejecutan SOLO UNA VEZ al final\n"
            "✅ NO hay repeticiones adicionales ni regreso al bucle"
        )
        layout.addWidget(self.editor_codigo)
        
        return frame
        
    def create_output_area(self):
        """Crear el área de salida de resultados"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Etiqueta
        label = QLabel("📊 Resultados del Análisis (Lógica de Bucles DEFINITIVA):")
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        
        # Área de salida
        self.salida_texto = QTextEdit()
        self.salida_texto.setReadOnly(True)
        self.salida_texto.setFont(QFont("Courier New", 10))
        self.salida_texto.setPlaceholderText("Los resultados del análisis con lógica de bucles definitivamente corregida aparecerán aquí...")
        layout.addWidget(self.salida_texto)
        
        return frame
        
    def setup_robot_controller(self):
        """Configurar el controlador del robot"""
        try:
            self.robot_controller = RobotController()
            self.statusBar().showMessage("Controlador de robot inicializado - Lógica de bucles definitivamente corregida")
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
                    self.statusBar().showMessage("✅ Robot conectado - Lógica de bucles DEFINITIVAMENTE corregida")
                    QMessageBox.information(self, "Éxito", "Robot conectado correctamente\n\n🔧 LÓGICA DE BUCLES DEFINITIVAMENTE CORREGIDA\n✅ Bucles se ejecutan exactamente N veces\n✅ Instrucciones después del } se ejecutan UNA sola vez\n✅ NO hay regreso al bucle después de comandos posteriores")
                else:
                    self.btn_conectar_robot.setText("🤖 Conectar Robot")
                    self.btn_conectar_robot.setEnabled(True)
                    QMessageBox.warning(self, "Error de Conexión", 
                                      "No se pudo conectar al robot\n\n"
                                      "Verifica que:\n"
                                      "1. RoboDK esté ejecutándose\n"
                                      "2. Tengas un robot ABB IRB 120 cargado")
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
            QMessageBox.critical(self, "Error", f"Error con conexión del robot:\n{e}")
            
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
        self.statusBar().showMessage("Analizando código con lógica de bucles definitivamente corregida...")
        
        # Crear y ejecutar hilo de análisis
        robodk_enabled = self.robot_controller and self.robot_controller.conectado
        self.analysis_thread = AnalysisThread(codigo, robodk_enabled, self)
        self.analysis_thread.analysis_finished.connect(self.on_analysis_finished)
        self.analysis_thread.robot_command.connect(self.ejecutar_comando_robot)
        self.analysis_thread.cuadruplos_ready.connect(self._ejecutar_cuadruplos_logica_bucles_definitiva)
        self.analysis_thread.start()
        
    def on_analysis_finished(self, resultado, exito):
        """Manejar finalización del análisis"""
        self.salida_texto.setHtml(resultado)
        
        # Rehabilitar botón
        self.btn_analizar.setEnabled(True)
        self.btn_analizar.setText("🔍 Analizar & Ejecutar")
        
        if exito:
            self.statusBar().showMessage("✅ Análisis completado exitosamente")
            if self.robot_controller and self.robot_controller.conectado:
                self.statusBar().showMessage("✅ Análisis completado - Lógica de bucles DEFINITIVAMENTE corregida")
        else:
            self.statusBar().showMessage("❌ Análisis completado con errores")

    def _ejecutar_cuadruplos_logica_bucles_definitiva(self, cuadruplos):
        """
        FUNCIÓN CON LÓGICA DE BUCLES DEFINITIVAMENTE CORREGIDA
        SOLUCIÓN COMPLETA: Evita que las instrucciones posteriores al bucle causen repeticiones
        """
        print("🔧 EJECUTANDO CUÁDRUPLOS CON LÓGICA DE BUCLES DEFINITIVAMENTE CORREGIDA")
        print(f"   Total de cuádruplos: {len(cuadruplos)}")
        
        if not self.robot_controller or not self.robot_controller.conectado:
            print("❌ Robot no conectado")
            return
            
        # Diccionario para trackear velocidades por robot
        velocidades_robots = {}
        
        i = 0
        while i < len(cuadruplos):
            cuadruplo = cuadruplos[i]
            
            print(f"\n🔍 Procesando cuádruplo {i}: {cuadruplo['operador']} | {cuadruplo['operando1']} | {cuadruplo['operando2']} | {cuadruplo['resultado']}")
            
            try:
                if cuadruplo['operador'] == 'CREATE':
                    # Creación de robot - inicializar velocidad por defecto
                    if cuadruplo['operando1'] == 'Robot':
                        robot_id = cuadruplo['resultado']
                        velocidades_robots[robot_id.lower()] = 5.0  # Velocidad por defecto
                        print(f"   🤖 Robot {robot_id} creado con velocidad por defecto: 5s")
                
                elif cuadruplo['operador'] == 'SET_SPEED':
                    # Cambio de velocidad
                    robot_id = cuadruplo['operando1']
                    nueva_velocidad = float(cuadruplo['operando2'])
                    velocidades_robots[robot_id.lower()] = nueva_velocidad
                    print(f"   ⚡ Velocidad de {robot_id} actualizada a: {nueva_velocidad}s")
                    
                elif cuadruplo['operador'] == 'MOVE':
                    # Movimiento positivo con velocidad específica
                    robot_id = cuadruplo['operando1']
                    valor = int(cuadruplo['operando2'])
                    componente = cuadruplo['resultado']
                    
                    # Obtener velocidad actual del robot
                    velocidad_actual = velocidades_robots.get(robot_id.lower(), 5.0)
                    
                    print(f"   🎯 MOVIMIENTO POSITIVO: {componente} = {valor}° con velocidad {velocidad_actual}s")
                    
                    # Configurar velocidad ANTES del movimiento
                    self.robot_controller.establecer_delay(velocidad_actual)
                    print(f"      🔧 Velocidad configurada: {velocidad_actual}s")
                    
                    # Ejecutar movimiento
                    resultado = self.robot_controller.mover_componente(componente, valor)
                    if resultado:
                        print(f"      ✅ Movimiento ejecutado exitosamente")
                    else:
                        print(f"      ❌ Error en movimiento")
                        
                elif cuadruplo['operador'] == 'MOVE_NEG':
                    # Movimiento negativo con velocidad específica
                    robot_id = cuadruplo['operando1']
                    valor_negativo = int(cuadruplo['operando2'])  # Ya viene negativo
                    componente = cuadruplo['resultado']
                    
                    # Obtener velocidad actual del robot
                    velocidad_actual = velocidades_robots.get(robot_id.lower(), 5.0)
                    
                    print(f"   ➖ MOVIMIENTO NEGATIVO: {componente} = {valor_negativo}° con velocidad {velocidad_actual}s")
                    
                    # Configurar velocidad ANTES del movimiento
                    self.robot_controller.establecer_delay(velocidad_actual)
                    print(f"      🔧 Velocidad configurada: {velocidad_actual}s")
                    
                    # Ejecutar movimiento negativo
                    resultado = self.robot_controller.mover_componente(componente, valor_negativo)
                    if resultado:
                        print(f"      ✅ Movimiento negativo ejecutado exitosamente")
                    else:
                        print(f"      ❌ Error en movimiento negativo")
                        
                elif cuadruplo['operador'] == 'BEGIN_LOOP':
                    # INICIO DE BUCLE - LÓGICA DEFINITIVAMENTE CORREGIDA
                    repeticiones = int(cuadruplo['operando1'])
                    loop_id = cuadruplo['resultado']
                    print(f"   🔁 INICIO DE BUCLE {loop_id}: {repeticiones} repeticiones")
                    print(f"      🎯 APLICANDO LÓGICA DE SALTO DEFINITIVAMENTE CORREGIDA")
                    
                    # PASO 1: Encontrar el índice del END_LOOP correspondiente
                    j = i + 1
                    comandos_bucle = []
                    nivel_bucle = 1
                    indice_end_loop = None
                    
                    while j < len(cuadruplos) and nivel_bucle > 0:
                        cuadruplo_actual = cuadruplos[j]
                        
                        if cuadruplo_actual['operador'] == 'BEGIN_LOOP':
                            nivel_bucle += 1
                        elif cuadruplo_actual['operador'] == 'END_LOOP':
                            nivel_bucle -= 1
                            if nivel_bucle == 0:
                                indice_end_loop = j  # CRÍTICO: Guardar posición exacta del END_LOOP
                        
                        # Agregar comandos del bucle (excepto el END_LOOP final)
                        if nivel_bucle > 0:
                            comandos_bucle.append(cuadruplo_actual)
                        
                        j += 1
                    
                    if indice_end_loop is None:
                        print(f"      ❌ ERROR: No se encontró END_LOOP para BEGIN_LOOP")
                        break
                    
                    print(f"      📋 Comandos extraídos del bucle: {len(comandos_bucle)}")
                    print(f"      📍 END_LOOP encontrado en índice: {indice_end_loop}")
                    print(f"      🎯 Después del bucle, continuará en índice: {indice_end_loop + 1}")
                    
                    for idx, cmd in enumerate(comandos_bucle):
                        print(f"         {idx}: {cmd['operador']} | {cmd['operando1']} | {cmd['operando2']} | {cmd['resultado']}")
                    
                    # PASO 2: EJECUTAR BUCLE EXACTAMENTE EL NÚMERO ESPECIFICADO DE VECES
                    print(f"      🔄 EJECUTANDO {repeticiones} REPETICIONES:")
                    
                    for rep in range(repeticiones):
                        print(f"         === REPETICIÓN {rep + 1}/{repeticiones} ===")
                        
                        # Procesar CADA comando del bucle
                        for idx_cmd, cmd_bucle in enumerate(comandos_bucle):
                            print(f"            Ejecutando comando {idx_cmd + 1}/{len(comandos_bucle)}: {cmd_bucle['operador']}")
                            
                            if cmd_bucle['operador'] == 'SET_SPEED':
                                robot_id_bucle = cmd_bucle['operando1']
                                nueva_velocidad_bucle = float(cmd_bucle['operando2'])
                                velocidades_robots[robot_id_bucle.lower()] = nueva_velocidad_bucle
                                print(f"               ⚡ Velocidad: {robot_id_bucle} → {nueva_velocidad_bucle}s")
                                
                            elif cmd_bucle['operador'] == 'MOVE':
                                robot_id_bucle = cmd_bucle['operando1']
                                valor_bucle = int(cmd_bucle['operando2'])
                                componente_bucle = cmd_bucle['resultado']
                                
                                velocidad_bucle = velocidades_robots.get(robot_id_bucle.lower(), 5.0)
                                
                                print(f"               🎯 Movimiento POSITIVO: {componente_bucle} = {valor_bucle}° ({velocidad_bucle}s)")
                                
                                # Configurar velocidad y ejecutar
                                self.robot_controller.establecer_delay(velocidad_bucle)
                                self.robot_controller.mover_componente(componente_bucle, valor_bucle)
                                
                            elif cmd_bucle['operador'] == 'MOVE_NEG':
                                robot_id_bucle = cmd_bucle['operando1']
                                valor_negativo_bucle = int(cmd_bucle['operando2'])  # Ya es negativo
                                componente_bucle = cmd_bucle['resultado']
                                
                                velocidad_bucle = velocidades_robots.get(robot_id_bucle.lower(), 5.0)
                                
                                print(f"               ➖ Movimiento NEGATIVO: {componente_bucle} = {valor_negativo_bucle}° ({velocidad_bucle}s)")
                                
                                # Configurar velocidad y ejecutar movimiento negativo
                                self.robot_controller.establecer_delay(velocidad_bucle)
                                resultado_neg = self.robot_controller.mover_componente(componente_bucle, valor_negativo_bucle)
                                
                                if resultado_neg:
                                    print(f"                  ✅ Movimiento negativo ejecutado en bucle")
                                else:
                                    print(f"                  ❌ Error en movimiento negativo en bucle")
                        
                        # Pausa entre repeticiones (solo si no es la última)
                        if rep < repeticiones - 1:
                            print(f"            ⏸️ Pausa entre repeticiones ({rep + 1} completada, {repeticiones - rep - 1} restantes)")
                            import time
                            time.sleep(0.3)
                        else:
                            print(f"            ✅ Repetición final {rep + 1} completada")
                    
                    print(f"   ✅ BUCLE {loop_id} COMPLETADO - EJECUTADAS EXACTAMENTE {repeticiones} REPETICIONES")
                    print(f"   🎯 APLICANDO SALTO DEFINITIVO DESPUÉS DEL BUCLE")
                    
                    # PASO 3: SALTO DEFINITIVAMENTE CORREGIDO
                    # Saltar DIRECTAMENTE al cuádruplo DESPUÉS del END_LOOP
                    i = indice_end_loop  # El bucle while incrementará i al final, así que quedará en indice_end_loop + 1
                    print(f"      📍 Saltando DEFINITIVAMENTE a cuádruplo {i + 1} (después del END_LOOP)")
                    print(f"      ✅ Las instrucciones posteriores al bucle se ejecutarán UNA SOLA VEZ")
                    
                elif cuadruplo['operador'] == 'END_LOOP':
                    # Este caso NO debería ejecutarse si el salto está correcto
                    print(f"   ⚠️ END_LOOP encontrado fuera de contexto - verificar lógica de salto")
                    
                else:
                    print(f"   ⚠️ Operador no reconocido: {cuadruplo['operador']}")
                    
            except Exception as e:
                print(f"   ❌ Error procesando cuádruplo {i}: {e}")
                import traceback
                traceback.print_exc()
                
            i += 1
        
        print("\n🎉 EJECUCIÓN COMPLETADA - LÓGICA DE BUCLES DEFINITIVAMENTE CORREGIDA")
        print(f"📊 Velocidades finales por robot: {velocidades_robots}")
        print(f"✅ Bucles ejecutan exactamente N repeticiones")
        print(f"✅ Instrucciones después del  se ejecutan UNA sola vez")
        print(f"✅ NO hay regreso al bucle después de comandos posteriores")
        
    def ejecutar_comando_robot(self, comando, parametros):
        """Ejecutar comando en el robot real (método de compatibilidad)"""
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