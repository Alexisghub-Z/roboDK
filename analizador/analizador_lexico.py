#!/usr/bin/env python3
"""
Analizador Léxico MEJORADO para Robot ABB IRB 120
NUEVA CARACTERÍSTICA: Método .negativo para usar grados negativos
Ejemplo: Robot.garra.negativo = 40  -> Robot usa -40°
"""

import re
from typing import List, Dict, Set, Any, Optional
from dataclasses import dataclass

@dataclass
class Token:
    """Representa un token del análisis léxico"""
    tipo: str
    valor: str
    linea: int = 0
    columna: int = 0

@dataclass
class Simbolo:
    """Representa un símbolo en la tabla de símbolos"""
    id: str
    metodo: str
    parametro: int
    valor: int

@dataclass
class Cuadruplo:
    """Representa un cuádruplo del código intermedio"""
    operador: str
    operando1: str
    operando2: str
    resultado: str

class AnalizadorLexico:
    """Analizador léxico con MÉTODO .negativo para grados negativos"""
    
    def __init__(self):
        self.tabla_simbolos: List[Simbolo] = []
        self.cuadruplos: List[Cuadruplo] = []
        self.contador_cuadruplos = 0
        self.errores: List[str] = []
        
        # NUEVO: Registro de velocidades por robot
        self.velocidades_por_robot: Dict[str, float] = {}
        
        # Patrones de expresiones regulares
        self.patron_id = re.compile(r'^[A-Z]+[0-9]*$', re.IGNORECASE)
        self.patron_valor = re.compile(r'^\d+$')
        
        # Comandos válidos - EXPANDIDO CON .negativo
        self.comandos: Set[str] = {
            'base', 'codo', 'hombro', 'garra', 'velocidad', 'repetir',
            # NUEVOS: Comandos con .negativo
            'base.negativo', 'codo.negativo', 'hombro.negativo', 'garra.negativo',
            'muñeca1.negativo', 'muñeca2.negativo', 'muñeca3.negativo'
        }
        
        # Rangos válidos para cada comando
        self.rangos = {
            'base': (0, 360),
            'hombro': (0, 180),
            'codo': (0, 180),
            'garra': (0, 360),  # Rotación 0-360°
            'velocidad': (1, 60),  # 1-60 segundos
            'repetir': (1, 100),
            # NUEVOS: Rangos para comandos negativos (valor positivo que se convertirá a negativo)
            'base.negativo': (0, 360),
            'hombro.negativo': (0, 180),
            'codo.negativo': (0, 180),
            'garra.negativo': (0, 360),
            'muñeca1.negativo': (0, 160),
            'muñeca2.negativo': (0, 120),
            'muñeca3.negativo': (0, 400)
        }
        
        # NUEVO: Mapeo de comandos negativos a sus equivalentes
        self.comandos_negativos = {
            'base.negativo': 'base',
            'hombro.negativo': 'hombro', 
            'codo.negativo': 'codo',
            'garra.negativo': 'garra',
            'muñeca1.negativo': 'muñeca1',
            'muñeca2.negativo': 'muñeca2',
            'muñeca3.negativo': 'muñeca3'
        }
        
    def analizar(self, entrada: str) -> Dict[str, Any]:
        """
        Analiza el código de entrada y retorna los resultados COMPLETOS
        """
        # Limpiar estado anterior
        self.tabla_simbolos.clear()
        self.cuadruplos.clear()
        self.errores.clear()
        self.contador_cuadruplos = 0
        self.velocidades_por_robot.clear()
        
        print(f"🔍 Iniciando análisis del código:")
        print(f"   Código: {repr(entrada)}")
        
        # Construir resultados
        resultado = {
            'exito': False,
            'salida': '',
            'tokens': [],
            'tabla_simbolos': [],
            'cuadruplos': [],
            'errores': []
        }
        
        try:
            # Realizar análisis COMPLETO
            salida_html = self._analizar_codigo_completo(entrada)
            
            print(f"📊 Análisis completado:")
            print(f"   Símbolos: {len(self.tabla_simbolos)}")
            print(f"   Cuádruplos: {len(self.cuadruplos)}")
            print(f"   Errores: {len(self.errores)}")
            print(f"   Velocidades registradas: {self.velocidades_por_robot}")
            
            # Compilar resultados
            resultado.update({
                'exito': len(self.errores) == 0,
                'salida': salida_html,
                'tabla_simbolos': [self._simbolo_to_dict(s) for s in self.tabla_simbolos],
                'cuadruplos': [self._cuadruplo_to_dict(c) for c in self.cuadruplos],
                'errores': self.errores.copy()
            })
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            print(f"❌ {error_msg}")
            self.errores.append(error_msg)
            resultado['salida'] = f"<div style='color: red;'>❌ {error_msg}</div>"
            resultado['errores'] = self.errores.copy()
            
        return resultado
        
    def _analizar_codigo_completo(self, entrada: str) -> str:
        """Realiza el análisis léxico, sintáctico y semántico COMPLETO"""
        
        # Inicializar buffers de salida
        salida_lexico = ["<h2 style='color: #2c3e50;'>🔍 Análisis Léxico:</h2>"]
        salida_sintactico = ["<h2 style='color: #2c3e50;'>🧩 Análisis Sintáctico:</h2>"]
        salida_semantico = ["<h2 style='color: #2c3e50;'>🧠 Análisis Semántico:</h2>"]
        
        if not entrada.strip():
            error = "Código vacío"
            salida_lexico.append(f"<div style='color: red;'>❌ Error: {error}</div>")
            self.errores.append(error)
            return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
        
        # Tokenizar entrada
        palabras = entrada.split()
        i = 0
        
        print(f"🔤 Palabras encontradas: {palabras}")
        
        while i < len(palabras):
            palabra_actual = palabras[i]
            print(f"   Procesando palabra {i}: '{palabra_actual}' (quedan {len(palabras) - i - 1} palabras)")
            
            try:
                # Validación léxica básica
                if not re.match(r'^[a-zA-Z0-9.={}]+$', palabra_actual):
                    error = f"Token inválido: '{palabra_actual}'"
                    salida_lexico.append(f"<div style='color: red;'>❌ Error léxico: {error}</div>")
                    self.errores.append(error)
                    return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
                
                salida_lexico.append(f"<div style='color: green;'>✔ Token válido: <strong>{palabra_actual}</strong></div>")
                
                # Declaración de robot
                if palabra_actual.lower() == 'robot':
                    i = self._procesar_declaracion_robot(palabras, i, salida_sintactico, salida_semantico)
                    if i == -1:  # Error
                        return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
                    continue
                
                # Comandos de robot
                if '.' in palabra_actual and i + 2 < len(palabras):
                    print(f"      📍 Detectado comando de robot: {palabra_actual}")
                    
                    # Verificar si es comando repetir con bloque
                    if (i + 3 < len(palabras) and 
                        palabra_actual.lower().endswith('.repetir') and 
                        palabras[i + 1] == '=' and 
                        palabras[i + 3] == '{'):
                        print(f"      🔁 Es comando repetir con bloque")
                        # Procesar comando repetir con bloque
                        i = self._procesar_repetir(palabras, i, salida_sintactico, salida_semantico)
                        if i == -1:  # Error
                            return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
                        continue
                    else:
                        print(f"      🤖 Es comando normal")
                        # Procesar comando normal (incluye .negativo)
                        i = self._procesar_comando_robot(palabras, i, salida_sintactico, salida_semantico)
                        if i == -1:  # Error
                            return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
                        continue
                
                print(f"      ⚠️ Token no reconocido en contexto actual")
                
                # Token no reconocido en este contexto
                error = f"Expresión incompleta o inválida: '{palabra_actual}'"
                salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
                self.errores.append(error)
                return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
                
            except Exception as e:
                error = f"Error procesando '{palabra_actual}': {str(e)}"
                print(f"❌ {error}")
                self.errores.append(error)
                return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
        
        # Si llegamos aquí, el análisis fue exitoso
        salida_semantico.append("<div style='color: green; font-weight: bold;'>✔ Análisis semántico completado sin errores</div>")
        
        return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
        
    def _procesar_declaracion_robot(self, palabras: List[str], i: int, 
                                   salida_sintactico: List[str], 
                                   salida_semantico: List[str]) -> int:
        """Procesa la declaración de un robot"""
        
        print(f"   📝 Procesando declaración de robot en posición {i}")
        
        if i + 1 >= len(palabras):
            error = "Falta identificador tras 'Robot'"
            salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
            self.errores.append(error)
            return -1
            
        robot_id = palabras[i + 1]
        print(f"      ID del robot: '{robot_id}'")
        
        if not self.patron_id.match(robot_id):
            error = f"Identificador inválido: '{robot_id}'"
            salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
            self.errores.append(error)
            return -1
            
        # Verificar si ya existe
        if any(s.id.lower() == robot_id.lower() and s.metodo == 'robot' 
               for s in self.tabla_simbolos):
            error = f"Robot ya declarado: '{robot_id}'"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return -1
            
        # Inicializar velocidad por defecto para este robot
        self.velocidades_por_robot[robot_id.lower()] = 5.0
        print(f"      ⚡ Velocidad inicial para {robot_id}: {self.velocidades_por_robot[robot_id.lower()]}s")
            
        # Agregar a tabla de símbolos
        simbolo = Simbolo(robot_id, 'robot', 0, 0)
        self.tabla_simbolos.append(simbolo)
        print(f"      ✅ Símbolo agregado: {simbolo}")
        
        # Generar cuádruplo
        cuadruplo = Cuadruplo('CREATE', 'Robot', '—', robot_id)
        self.cuadruplos.append(cuadruplo)
        print(f"      ✅ Cuádruplo generado: {cuadruplo}")
        
        salida_sintactico.append(f"<div style='color: green;'>✔ Declaración de robot: <strong>{robot_id}</strong></div>")
        salida_semantico.append(f"<div style='color: green;'>✔ Robot <strong>{robot_id}</strong> declarado correctamente</div>")
        
        return i + 2
        
    def _procesar_comando_robot(self, palabras: List[str], i: int,
                               salida_sintactico: List[str],
                               salida_semantico: List[str]) -> int:
        """Procesa un comando de robot CON SOPORTE PARA .negativo"""
        
        comando_completo = palabras[i]
        operador = palabras[i + 1]
        valor_str = palabras[i + 2]
        
        print(f"   🤖 Procesando comando: {comando_completo} {operador} {valor_str}")
        
        # Parsear ID.comando (puede incluir .negativo)
        if comando_completo.count('.') == 1:
            # Comando normal: ID.comando
            partes = comando_completo.split('.')
            robot_id, comando_base = partes
            comando_completo_normalizado = comando_base.lower()
            es_negativo = False
        elif comando_completo.count('.') == 2:
            # Comando con .negativo: ID.comando.negativo
            partes = comando_completo.split('.')
            if len(partes) == 3 and partes[2].lower() == 'negativo':
                robot_id, comando_base, negativo_flag = partes
                comando_completo_normalizado = f"{comando_base.lower()}.negativo"
                es_negativo = True
            else:
                error = f"Sintaxis inválida: '{comando_completo}'"
                salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
                self.errores.append(error)
                return -1
        else:
            error = f"Se esperaba ID.comando o ID.comando.negativo: '{comando_completo}'"
            salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
            self.errores.append(error)
            return -1
            
        print(f"      Robot ID: '{robot_id}', Comando: '{comando_completo_normalizado}', Es negativo: {es_negativo}")
        
        # Verificar operador
        if operador != '=':
            error = f"Se esperaba '=' después del comando: '{operador}'"
            salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
            self.errores.append(error)
            return -1
            
        # Verificar que el robot esté declarado
        if not any(s.id.lower() == robot_id.lower() and s.metodo == 'robot' 
                  for s in self.tabla_simbolos):
            error = f"Robot no declarado: '{robot_id}'"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return -1
            
        # Verificar comando válido
        if comando_completo_normalizado not in self.comandos:
            error = f"Comando inválido: '{comando_completo_normalizado}'"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return -1
            
        # Validar valor numérico
        if not self.patron_valor.match(valor_str):
            error = f"Valor numérico inválido: '{valor_str}'"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return -1
            
        valor = int(valor_str)
        print(f"      Valor numérico: {valor}")
        
        # Validar rango
        if comando_completo_normalizado in self.rangos:
            min_val, max_val = self.rangos[comando_completo_normalizado]
            if not (min_val <= valor <= max_val):
                error = f"Valor fuera de rango para {comando_completo_normalizado}: {valor} (rango: {min_val}-{max_val})"
                salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
                self.errores.append(error)
                return -1
        
        # NUEVO: Convertir a negativo si es necesario
        if es_negativo:
            valor_final = -valor  # Convertir a negativo
            comando_real = self.comandos_negativos[comando_completo_normalizado]
            print(f"      ➖ Comando negativo detectado: {valor} → {valor_final}° en componente '{comando_real}'")
        else:
            valor_final = valor
            comando_real = comando_completo_normalizado
            
        # Procesar según el tipo de comando
        if comando_real == 'velocidad':
            self._procesar_cambio_velocidad(robot_id, valor_final, salida_semantico)
        else:
            # Para movimientos, usar la velocidad actual del robot
            velocidad_actual = self.velocidades_por_robot.get(robot_id.lower(), 5.0)
            if es_negativo:
                self._procesar_movimiento_negativo(robot_id, comando_real, valor_final, velocidad_actual, salida_semantico)
            else:
                self._procesar_movimiento_con_velocidad(robot_id, comando_real, valor_final, velocidad_actual, salida_semantico)
                
        # Actualizar tabla de símbolos
        self._actualizar_simbolo(robot_id, comando_real, valor_final)
        
        # Mostrar resultado en salida sintáctica
        if es_negativo:
            salida_sintactico.append(f"<div style='color: green;'>✔ Asignación negativa: <strong>{comando_completo} = {valor}</strong> → <strong>{comando_real} = {valor_final}°</strong></div>")
        else:
            salida_sintactico.append(f"<div style='color: green;'>✔ Asignación: <strong>{comando_completo} = {valor}</strong></div>")
        
        return i + 3
    
    def _procesar_cambio_velocidad(self, robot_id: str, nueva_velocidad: float, salida_semantico: List[str]):
        """Procesa un cambio de velocidad para un robot específico"""
        
        # Para velocidad, no permitir negativos
        if nueva_velocidad < 0:
            error = f"Velocidad no puede ser negativa: {nueva_velocidad}"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return
            
        velocidad_anterior = self.velocidades_por_robot.get(robot_id.lower(), 5.0)
        self.velocidades_por_robot[robot_id.lower()] = float(abs(nueva_velocidad))  # Asegurar positivo
        
        print(f"      ⚡ Cambio de velocidad para {robot_id}: {velocidad_anterior}s → {abs(nueva_velocidad)}s")
        
        # Generar cuádruplo de cambio de velocidad
        cuadruplo = Cuadruplo('SET_SPEED', robot_id, str(int(abs(nueva_velocidad))), f'speed_{self.contador_cuadruplos}')
        self.cuadruplos.append(cuadruplo)
        self.contador_cuadruplos += 1
        
        salida_semantico.append(f"<div style='color: blue;'>⚡ Velocidad de <strong>{robot_id}</strong> cambiada a <strong>{abs(nueva_velocidad)}s</strong></div>")
        
    def _procesar_movimiento_con_velocidad(self, robot_id: str, comando: str, valor: float, velocidad: float, salida_semantico: List[str]):
        """Procesa un movimiento positivo con su velocidad asociada"""
        
        print(f"      🏃 Movimiento {comando} = {valor}° con velocidad {velocidad}s")
        
        # Generar cuádruplos: primero configurar velocidad, luego ejecutar movimiento
        cuadruplos_movimiento = [
            Cuadruplo('SET_SPEED', robot_id, str(int(velocidad)), f'pre_speed_{self.contador_cuadruplos}'),
            Cuadruplo('MOVE', robot_id, str(int(valor)), comando)
        ]
        
        self.cuadruplos.extend(cuadruplos_movimiento)
        self.contador_cuadruplos += 1
        
        salida_semantico.append(f"<div style='color: green;'>🤖 Movimiento <strong>{comando} = {valor}°</strong> con velocidad <strong>{velocidad}s</strong></div>")
        
    def _procesar_movimiento_negativo(self, robot_id: str, comando: str, valor_negativo: float, velocidad: float, salida_semantico: List[str]):
        """NUEVA FUNCIÓN: Procesa un movimiento negativo con su velocidad asociada"""
        
        print(f"      ➖ Movimiento NEGATIVO {comando} = {valor_negativo}° con velocidad {velocidad}s")
        
        # Generar cuádruplos: primero configurar velocidad, luego ejecutar movimiento negativo
        cuadruplos_movimiento = [
            Cuadruplo('SET_SPEED', robot_id, str(int(velocidad)), f'pre_speed_neg_{self.contador_cuadruplos}'),
            Cuadruplo('MOVE_NEG', robot_id, str(int(valor_negativo)), comando)  # NUEVO: MOVE_NEG para negativos
        ]
        
        self.cuadruplos.extend(cuadruplos_movimiento)
        self.contador_cuadruplos += 1
        
        salida_semantico.append(f"<div style='color: purple;'>➖ Movimiento NEGATIVO <strong>{comando} = {valor_negativo}°</strong> con velocidad <strong>{velocidad}s</strong></div>")
        
    def _procesar_repetir(self, palabras: List[str], i: int,
                         salida_sintactico: List[str],
                         salida_semantico: List[str]) -> int:
        """Procesa el comando repetir con bloque { } CON SOPORTE PARA .negativo"""
        
        comando_completo = palabras[i]
        operador = palabras[i + 1]
        valor_str = palabras[i + 2]
        llave_abre = palabras[i + 3]
        
        print(f"   🔁 Procesando repetir: {comando_completo} {operador} {valor_str} {llave_abre}")
        
        # Parsear ID.comando
        partes = comando_completo.split('.')
        if len(partes) != 2 or partes[1].lower() != 'repetir':
            error = f"Se esperaba ID.repetir: '{comando_completo}'"
            salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
            self.errores.append(error)
            return -1
            
        robot_id = partes[0]
        
        # Validaciones básicas
        if operador != '=' or llave_abre != '{':
            error = f"Sintaxis incorrecta en repetir"
            salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
            self.errores.append(error)
            return -1
            
        if not self.patron_valor.match(valor_str):
            error = f"Valor de repetición inválido: '{valor_str}'"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return -1
            
        repeticiones = int(valor_str)
        min_rep, max_rep = self.rangos['repetir']
        
        if not (min_rep <= repeticiones <= max_rep):
            error = f"Repeticiones fuera de rango: {repeticiones} (rango: {min_rep}-{max_rep})"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return -1
            
        # Buscar el bloque hasta encontrar }
        j = i + 4
        bloque = []
        nivel_llaves = 1
        
        while j < len(palabras) and nivel_llaves > 0:
            if palabras[j] == '{':
                nivel_llaves += 1
            elif palabras[j] == '}':
                nivel_llaves -= 1
                
            if nivel_llaves > 0:
                bloque.append(palabras[j])
            j += 1
            
        if nivel_llaves > 0:
            error = "Falta '}' para cerrar el bloque de repetición"
            salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
            self.errores.append(error)
            return -1
            
        print(f"      Bloque encontrado: {bloque}")
        
        # GENERAR CUÁDRUPLO DE INICIO DE BUCLE
        loop_id = f"loop{self.contador_cuadruplos}"
        self.contador_cuadruplos += 1
        
        # BEGIN_LOOP cuádruplo
        begin_loop_cuadruplo = Cuadruplo('BEGIN_LOOP', str(repeticiones), '—', loop_id)
        self.cuadruplos.append(begin_loop_cuadruplo)
        print(f"      ✅ Cuádruplo BEGIN_LOOP generado: {begin_loop_cuadruplo}")
        
        # Analizar el contenido del bloque y generar sus cuádruplos
        try:
            self._analizar_bloque_con_velocidades_y_negativos(bloque, robot_id, salida_sintactico, salida_semantico)
        except Exception as e:
            error = f"Error en bloque de repetición: {str(e)}"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return -1
        
        # GENERAR CUÁDRUPLO DE FIN DE BUCLE
        end_loop_cuadruplo = Cuadruplo('END_LOOP', loop_id, str(repeticiones), '—')
        self.cuadruplos.append(end_loop_cuadruplo)
        print(f"      ✅ Cuádruplo END_LOOP generado: {end_loop_cuadruplo}")
        
        salida_sintactico.append(f"<div style='color: green;'>✔ Bloque de repetición: <strong>{repeticiones} iteraciones</strong></div>")
        salida_semantico.append(f"<div style='color: green;'>✔ Bloque válido con velocidades independientes y soporte .negativo</div>")
        
        return j
        
    def _analizar_bloque_con_velocidades_y_negativos(self, bloque: List[str], robot_id: str, 
                                                     salida_sintactico: List[str], salida_semantico: List[str]):
        """FUNCIÓN CORREGIDA: Analiza el contenido de un bloque CON SOPORTE COMPLETO PARA .negativo"""
        print(f"      🔍 Analizando bloque con velocidades y negativos: {bloque}")
        
        i = 0
        comandos_bloque = 0
        
        while i < len(bloque):
            if i + 2 >= len(bloque):
                break
                
            comando_completo = bloque[i]
            operador = bloque[i + 1]
            valor_str = bloque[i + 2]
            
            print(f"         Comando en bloque: {comando_completo} {operador} {valor_str}")
            
            # Validaciones básicas
            if '.' not in comando_completo:
                i += 1
                continue
            
            # CORREGIDO: Determinar si es comando negativo en bucle
            if comando_completo.count('.') == 2:
                # Verificar si termina en .negativo
                if comando_completo.lower().endswith('.negativo'):
                    # Comando negativo: ID.comando.negativo
                    partes = comando_completo.split('.')
                    if len(partes) == 3:
                        bloque_robot_id, comando_base, negativo_flag = partes
                        es_negativo = True
                        comando_normalizado = f"{comando_base.lower()}.negativo"
                        comando_real = comando_base.lower()
                        print(f"            ➖ Detectado comando NEGATIVO en bucle: {comando_completo}")
                    else:
                        raise Exception(f"Sintaxis inválida en bloque: {comando_completo}")
                else:
                    raise Exception(f"Sintaxis inválida en bloque: {comando_completo}")
                    
            elif comando_completo.count('.') == 1:
                # Comando normal: ID.comando
                partes = comando_completo.split('.')
                if len(partes) == 2:
                    bloque_robot_id, comando_base = partes
                    es_negativo = False
                    comando_normalizado = comando_base.lower()
                    comando_real = comando_base.lower()
                    print(f"            ✅ Detectado comando POSITIVO en bucle: {comando_completo}")
                else:
                    raise Exception(f"Sintaxis inválida en bloque: {comando_completo}")
            else:
                raise Exception(f"Sintaxis inválida en bloque: {comando_completo}")
                
            if operador != '=':
                raise Exception(f"Se esperaba '=' en bloque: {comando_completo} {operador}")
                
            if not self.patron_valor.match(valor_str):
                raise Exception(f"Valor inválido en bloque: {valor_str}")
                
            # CORREGIDO: Verificar comando válido (incluyendo .negativo)
            if comando_normalizado not in self.comandos:
                raise Exception(f"Comando inválido en bloque: {comando_normalizado}")
                
            if comando_normalizado == 'repetir':
                raise Exception(f"No se permite repetir anidado")
                
            if bloque_robot_id.lower() != robot_id.lower():
                raise Exception(f"Robot diferente en bloque: {bloque_robot_id} (esperado: {robot_id})")
                
            valor = int(valor_str)
            
            # CORREGIDO: Validar rango según el tipo de comando
            if comando_normalizado in self.rangos:
                min_val, max_val = self.rangos[comando_normalizado]
                if not (min_val <= valor <= max_val):
                    raise Exception(f"Valor fuera de rango en bloque: {comando_normalizado} = {valor} (rango: {min_val}-{max_val})")
            
            # CORREGIDO: Convertir a negativo si es necesario
            if es_negativo:
                valor_final = -valor
                print(f"         ➖ Conversión en bucle: {valor} → {valor_final}° para '{comando_real}'")
            else:
                valor_final = valor
                print(f"         ✅ Valor positivo en bucle: {valor}° para '{comando_real}'")
            
            # CORREGIDO: Procesar comandos con velocidades en bloques
            if comando_real == 'velocidad':
                if valor_final < 0:
                    raise Exception(f"Velocidad no puede ser negativa en bloque: {valor_final}")
                self._procesar_cambio_velocidad(bloque_robot_id, abs(valor_final), salida_semantico)
            else:
                # Para movimientos, usar la velocidad actual del robot
                velocidad_actual = self.velocidades_por_robot.get(bloque_robot_id.lower(), 5.0)
                if es_negativo:
                    print(f"         🔧 Procesando movimiento NEGATIVO en bucle: {comando_real} = {valor_final}°")
                    self._procesar_movimiento_negativo(bloque_robot_id, comando_real, valor_final, velocidad_actual, salida_semantico)
                else:
                    print(f"         🔧 Procesando movimiento POSITIVO en bucle: {comando_real} = {valor_final}°")
                    self._procesar_movimiento_con_velocidad(bloque_robot_id, comando_real, valor_final, velocidad_actual, salida_semantico)
            
            comandos_bloque += 1
            i += 3
            
        if comandos_bloque == 0:
            raise Exception("Bloque de repetición vacío")
            
        print(f"      ✅ Bloque válido con {comandos_bloque} comandos (positivos y negativos)")
        print(f"      📊 Se procesaron comandos con .negativo correctamente en el bucle")
            
    def _actualizar_simbolo(self, robot_id: str, comando: str, valor: float):
        """Actualiza o agrega un símbolo en la tabla (SOPORTE PARA NEGATIVOS)"""
        # Remover símbolo existente si existe
        self.tabla_simbolos = [s for s in self.tabla_simbolos 
                              if not (s.id.lower() == robot_id.lower() and s.metodo.lower() == comando.lower())]
        
        # Agregar nuevo símbolo (puede ser negativo)
        simbolo = Simbolo(robot_id, comando, 1, int(valor))
        self.tabla_simbolos.append(simbolo)
        print(f"      ✅ Símbolo actualizado: {simbolo}")
        
    def _generar_salida_html(self, salida_lexico: List[str], 
                           salida_sintactico: List[str], 
                           salida_semantico: List[str]) -> str:
        """Genera la salida HTML completa CON INFORMACIÓN DE .negativo"""
        
        html_parts = []
        
        # Análisis léxico
        html_parts.extend(salida_lexico)
        html_parts.append("<br>")
        
        # Análisis sintáctico
        html_parts.extend(salida_sintactico)
        html_parts.append("<br>")
        
        # Análisis semántico
        html_parts.extend(salida_semantico)
        html_parts.append("<br>")
        
        # Mostrar registro de velocidades
        if self.velocidades_por_robot and len(self.errores) == 0:
            html_parts.append("<h2 style='color: #2c3e50;'>⚡ Registro de Velocidades:</h2>")
            html_parts.append("<table border='1' style='border-collapse: collapse; width: 100%; margin: 10px 0; font-family: monospace;'>")
            html_parts.append("<tr style='background-color: #f39c12; color: white;'>")
            html_parts.append("<th style='padding: 8px;'>ROBOT</th><th style='padding: 8px;'>VELOCIDAD ACTUAL</th>")
            html_parts.append("</tr>")
            
            for robot_id, velocidad in self.velocidades_por_robot.items():
                html_parts.append("<tr style='background-color: #fef5e7;'>")
                html_parts.append(f"<td style='padding: 8px; font-weight: bold;'>{robot_id.upper()}</td>")
                html_parts.append(f"<td style='padding: 8px; color: #d68910; font-weight: bold;'>{velocidad}s</td>")
                html_parts.append("</tr>")
                
            html_parts.append("</table>")
        
        # Tabla de símbolos (SOLO si no hay errores)
        if self.tabla_simbolos and len(self.errores) == 0:
            html_parts.append("<h2 style='color: #2c3e50;'>🔧 Tabla de Símbolos (Con Negativos):</h2>")
            html_parts.append("<table border='1' style='border-collapse: collapse; width: 100%; margin: 10px 0; font-family: monospace;'>")
            html_parts.append("<tr style='background-color: #3498db; color: white;'>")
            html_parts.append("<th style='padding: 8px;'>ID</th><th style='padding: 8px;'>MÉTODO</th><th style='padding: 8px;'>PARÁMETRO</th><th style='padding: 8px;'>VALOR</th>")
            html_parts.append("</tr>")
            
            for simbolo in self.tabla_simbolos:
                # Resaltar valores negativos
                color_valor = "#e74c3c" if simbolo.valor >= 0 else "#8e44ad"
                signo = "+" if simbolo.valor >= 0 else ""
                
                html_parts.append("<tr style='background-color: #ecf0f1;'>")
                html_parts.append(f"<td style='padding: 8px; font-weight: bold;'>{simbolo.id}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{simbolo.metodo}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{simbolo.parametro}</td>")
                html_parts.append(f"<td style='padding: 8px; color: {color_valor}; font-weight: bold;'>{signo}{simbolo.valor}°</td>")
                html_parts.append("</tr>")
                
            html_parts.append("</table>")
            
        # Tabla de cuádruplos (SOLO si no hay errores)
        if self.cuadruplos and len(self.errores) == 0:
            html_parts.append("<h2 style='color: #2c3e50;'>📊 Tabla de Cuádruplos (Con Soporte .negativo):</h2>")
            html_parts.append("<table border='1' style='border-collapse: collapse; width: 100%; margin: 10px 0; font-family: monospace;'>")
            html_parts.append("<tr style='background-color: #27ae60; color: white;'>")
            html_parts.append("<th style='padding: 8px;'>Nº</th><th style='padding: 8px;'>Operador</th><th style='padding: 8px;'>Operando 1</th><th style='padding: 8px;'>Operando 2</th><th style='padding: 8px;'>Resultado</th>")
            html_parts.append("</tr>")
            
            for i, cuadruplo in enumerate(self.cuadruplos):
                bg_color = "#d5f4e6" if i % 2 == 0 else "#ffffff"
                
                # Resaltar cuádruplos especiales
                if cuadruplo.operador == 'SET_SPEED':
                    bg_color = "#fff3cd"  # Amarillo para velocidades
                elif cuadruplo.operador == 'MOVE':
                    bg_color = "#d1ecf1"  # Azul para movimientos positivos
                elif cuadruplo.operador == 'MOVE_NEG':
                    bg_color = "#e2d5f0"  # Morado para movimientos negativos
                    
                html_parts.append(f"<tr style='background-color: {bg_color};'>")
                html_parts.append(f"<td style='padding: 8px; font-weight: bold;'>{i}</td>")
                
                # Resaltar operadores especiales
                operador_color = "#8e44ad"
                if cuadruplo.operador == 'SET_SPEED':
                    operador_color = "#f39c12"  # Naranja para velocidad
                elif cuadruplo.operador == 'MOVE':
                    operador_color = "#3498db"  # Azul para movimiento
                elif cuadruplo.operador == 'MOVE_NEG':
                    operador_color = "#9b59b6"  # Morado para movimiento negativo
                    
                html_parts.append(f"<td style='padding: 8px; color: {operador_color}; font-weight: bold;'>{cuadruplo.operador}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{cuadruplo.operando1}</td>")
                
                # Mostrar valores negativos apropiadamente
                operando2_display = cuadruplo.operando2
                if cuadruplo.operador == 'MOVE_NEG' and cuadruplo.operando2.lstrip('-').isdigit():
                    operando2_display = f"{cuadruplo.operando2}°"
                    
                html_parts.append(f"<td style='padding: 8px;'>{operando2_display}</td>")
                html_parts.append(f"<td style='padding: 8px; color: #e67e22; font-weight: bold;'>{cuadruplo.resultado}</td>")
                html_parts.append("</tr>")
                
            html_parts.append("</table>")
        
        # Mensaje final
        if len(self.errores) == 0:
            robots_count = len(self.velocidades_por_robot)
            comandos_negativos_count = len([c for c in self.cuadruplos if c.operador == 'MOVE_NEG'])
            
            html_parts.append("<div style='background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 10px 0; font-weight: bold; font-size: 16px;'>")
            html_parts.append("🎉 ¡Análisis completado exitosamente con soporte .negativo!")
            html_parts.append(f"<br>📊 Generados: {len(self.tabla_simbolos)} símbolos y {len(self.cuadruplos)} cuádruplos")
            html_parts.append(f"<br>⚡ Robots con velocidades: {robots_count}")
            html_parts.append(f"<br>➖ Movimientos negativos: {comandos_negativos_count}")
            html_parts.append("<br>💡 Usa Robot.componente.negativo = X para grados negativos")
            html_parts.append("</div>")
        
        return ''.join(html_parts)
        
    def _simbolo_to_dict(self, simbolo: Simbolo) -> Dict[str, Any]:
        """Convierte un símbolo a diccionario"""
        return {
            'id': simbolo.id,
            'metodo': simbolo.metodo,
            'parametro': simbolo.parametro,
            'valor': simbolo.valor
        }
        
    def _cuadruplo_to_dict(self, cuadruplo: Cuadruplo) -> Dict[str, Any]:
        """Convierte un cuádruplo a diccionario"""
        return {
            'operador': cuadruplo.operador,
            'operando1': cuadruplo.operando1,
            'operando2': cuadruplo.operando2,
            'resultado': cuadruplo.resultado
        }