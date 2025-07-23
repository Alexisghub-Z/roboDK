#!/usr/bin/env python3
"""
Analizador Léxico FUNCIONAL para Robot ABB IRB 120
Esta versión SÍ genera cuádruplos y tabla de símbolos
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
    """Analizador léxico FUNCIONAL para el lenguaje de robots"""
    
    def __init__(self):
        self.tabla_simbolos: List[Simbolo] = []
        self.cuadruplos: List[Cuadruplo] = []
        self.contador_cuadruplos = 0
        self.errores: List[str] = []
        
        # Patrones de expresiones regulares
        self.patron_id = re.compile(r'^[A-Z]+[0-9]*$', re.IGNORECASE)
        self.patron_valor = re.compile(r'^\d+$')
        
        # Comandos válidos
        self.comandos: Set[str] = {
            'base', 'codo', 'hombro', 'garra', 'velocidad', 'repetir'
        }
        
        # Rangos válidos para cada comando (ABB IRB 120 + Robotiq 2F-85)
        self.rangos = {
            'base': (0, 360),
            'hombro': (0, 180),
            'codo': (0, 180),
            'garra': (0, 85),  # Robotiq 2F-85: 0-85mm
            'velocidad': (1, 100),  # Porcentaje de velocidad
            'repetir': (1, 100)
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
            
            # Debug: mostrar las próximas 3 palabras
            if i + 3 < len(palabras):
                print(f"      Siguientes: '{palabras[i+1]}', '{palabras[i+2]}', '{palabras[i+3]}'")
            elif i + 2 < len(palabras):
                print(f"      Siguientes: '{palabras[i+1]}', '{palabras[i+2]}'")
            elif i + 1 < len(palabras):
                print(f"      Siguiente: '{palabras[i+1]}'")
            
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
                        # Procesar comando normal
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
        """Procesa un comando de robot (ID.comando = valor)"""
        
        comando_completo = palabras[i]
        operador = palabras[i + 1]
        valor_str = palabras[i + 2]
        
        print(f"   🤖 Procesando comando: {comando_completo} {operador} {valor_str}")
        
        # Parsear ID.comando
        partes = comando_completo.split('.')
        if len(partes) != 2:
            error = f"Se esperaba ID.comando: '{comando_completo}'"
            salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
            self.errores.append(error)
            return -1
            
        robot_id, comando = partes
        print(f"      Robot ID: '{robot_id}', Comando: '{comando}'")
        
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
        if comando.lower() not in self.comandos:
            error = f"Comando inválido: '{comando}'"
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
        if comando.lower() in self.rangos:
            min_val, max_val = self.rangos[comando.lower()]
            if not (min_val <= valor <= max_val):
                error = f"Valor fuera de rango para {comando}: {valor} (rango: {min_val}-{max_val})"
                salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
                self.errores.append(error)
                return -1
                
        # Actualizar tabla de símbolos
        self._actualizar_simbolo(robot_id, comando.lower(), valor)
        
        # Generar cuádruplos
        self._generar_cuadruplo_comando(robot_id, comando.lower(), valor)
        
        salida_sintactico.append(f"<div style='color: green;'>✔ Asignación: <strong>{comando_completo} = {valor}</strong></div>")
        salida_semantico.append(f"<div style='color: green;'>✔ Valor válido asignado a <strong>{comando_completo}</strong></div>")
        
        return i + 3
    def _procesar_repetir(self, palabras: List[str], i: int,
                         salida_sintactico: List[str],
                         salida_semantico: List[str]) -> int:
        """Procesa el comando repetir con bloque { }"""
        
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
        
        # Verificar operador
        if operador != '=':
            error = f"Se esperaba '=' después de repetir: '{operador}'"
            salida_sintactico.append(f"<div style='color: red;'>❌ Error sintáctico: {error}</div>")
            self.errores.append(error)
            return -1
            
        # Verificar llave de apertura
        if llave_abre != '{':
            error = f"Se esperaba '{{' para abrir bloque: '{llave_abre}'"
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
            
        # Validar valor de repetición
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
        
        # Analizar el contenido del bloque
        try:
            self._analizar_bloque(bloque, robot_id, salida_sintactico, salida_semantico)
        except Exception as e:
            error = f"Error en bloque de repetición: {str(e)}"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return -1
            
        # Si llegamos aquí, todo está bien
        # Actualizar tabla de símbolos para repetir
        self._actualizar_simbolo(robot_id, 'repetir', repeticiones)
        
        # Generar cuádruplos para el bucle
        loop_var = f"contador{self.contador_cuadruplos}"
        loop_id = f"loop{self.contador_cuadruplos}"
        self.contador_cuadruplos += 1
        
        cuadruplos_loop = [
            Cuadruplo('CREATE', robot_id, '—', loop_var),
            Cuadruplo('=', valor_str, '—', loop_var),
            Cuadruplo('CREATE', 'Loop', '—', loop_id),
            Cuadruplo('ASSOC', loop_var, '—', f"{loop_id}.contador"),
            Cuadruplo('ASSOC', loop_id, '—', f"{robot_id}.repetir"),
            Cuadruplo('BEGIN_LOOP', str(repeticiones), '—', loop_id),
        ]
        
        self.cuadruplos.extend(cuadruplos_loop)
        
        # Marcar los comandos del bloque como parte del bucle
        comandos_bucle_start = len(self.cuadruplos)
        
        # Analizar el contenido del bloque y generar sus cuádruplos
        try:
            self._analizar_bloque(bloque, robot_id, salida_sintactico, salida_semantico)
        except Exception as e:
            error = f"Error en bloque de repetición: {str(e)}"
            salida_semantico.append(f"<div style='color: red;'>❌ Error semántico: {error}</div>")
            self.errores.append(error)
            return -1
        
        # Agregar cuádruplo de fin de bucle
        self.cuadruplos.append(Cuadruplo('END_LOOP', loop_id, str(repeticiones), '—'))
        
        print(f"      ✅ Cuádruplos de bucle generados: {len(cuadruplos_loop) + 1}")
        
        salida_sintactico.append(f"<div style='color: green;'>✔ Bloque de repetición: <strong>{repeticiones} iteraciones</strong></div>")
        salida_semantico.append(f"<div style='color: green;'>✔ Bloque de repetición válido con <strong>{repeticiones}</strong> comandos</div>")
        
        return j
        
    def _analizar_bloque(self, bloque: List[str], robot_id: str, 
                        salida_sintactico: List[str], salida_semantico: List[str]):
        """Analiza el contenido de un bloque de repetición"""
        print(f"      🔍 Analizando bloque: {bloque}")
        
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
                
            partes = comando_completo.split('.')
            if len(partes) != 2:
                raise Exception(f"Sintaxis inválida en bloque: {comando_completo}")
                
            bloque_robot_id, comando = partes
            
            if operador != '=':
                raise Exception(f"Se esperaba '=' en bloque: {comando_completo} {operador}")
                
            if not self.patron_valor.match(valor_str):
                raise Exception(f"Valor inválido en bloque: {valor_str}")
                
            if comando.lower() not in self.comandos or comando.lower() == 'repetir':
                raise Exception(f"Comando inválido en bloque: {comando}")
                
            if bloque_robot_id.lower() != robot_id.lower():
                raise Exception(f"Robot diferente en bloque: {bloque_robot_id} (esperado: {robot_id})")
                
            valor = int(valor_str)
            if comando.lower() in self.rangos:
                min_val, max_val = self.rangos[comando.lower()]
                if not (min_val <= valor <= max_val):
                    raise Exception(f"Valor fuera de rango en bloque: {comando} = {valor}")
            
            # Generar cuádruplos para el bloque (se ejecutarán repetidas veces)
            self._generar_cuadruplo_comando(bloque_robot_id, comando.lower(), valor)
            comandos_bloque += 1
            
            i += 3
            
        if comandos_bloque == 0:
            raise Exception("Bloque de repetición vacío")
            
        print(f"      ✅ Bloque válido con {comandos_bloque} comandos")
            
    def _actualizar_simbolo(self, robot_id: str, comando: str, valor: int):
        """Actualiza o agrega un símbolo en la tabla"""
        # Remover símbolo existente si existe
        self.tabla_simbolos = [s for s in self.tabla_simbolos 
                              if not (s.id.lower() == robot_id.lower() and s.metodo.lower() == comando.lower())]
        
        # Agregar nuevo símbolo
        simbolo = Simbolo(robot_id, comando, 1, valor)
        self.tabla_simbolos.append(simbolo)
        print(f"      ✅ Símbolo actualizado: {simbolo}")
        
    def _generar_cuadruplo_comando(self, robot_id: str, comando: str, valor: int):
        """Genera cuádruplos para un comando específico"""
        if comando == 'velocidad':
            temp_vel = f"vel{self.contador_cuadruplos}"
            self.contador_cuadruplos += 1
            cuadruplos_vel = [
                Cuadruplo('CREATE', robot_id, '—', temp_vel),
                Cuadruplo('=', str(valor), '—', temp_vel),
                Cuadruplo('ASSOC', temp_vel, '—', f"{robot_id}.velocidad")
            ]
            self.cuadruplos.extend(cuadruplos_vel)
            print(f"      ✅ Cuádruplos de velocidad generados: {len(cuadruplos_vel)}")
        else:
            cuadruplo = Cuadruplo('CALL', robot_id, str(valor), comando)
            self.cuadruplos.append(cuadruplo)
            print(f"      ✅ Cuádruplo de comando generado: {cuadruplo}")
        """Actualiza o agrega un símbolo en la tabla"""
        # Remover símbolo existente si existe
        self.tabla_simbolos = [s for s in self.tabla_simbolos 
                              if not (s.id.lower() == robot_id.lower() and s.metodo.lower() == comando.lower())]
        
        # Agregar nuevo símbolo
        simbolo = Simbolo(robot_id, comando, 1, valor)
        self.tabla_simbolos.append(simbolo)
        print(f"      ✅ Símbolo actualizado: {simbolo}")
        
    def _generar_cuadruplo_comando(self, robot_id: str, comando: str, valor: int):
        """Genera cuádruplos para un comando específico"""
        if comando == 'velocidad':
            temp_vel = f"vel{self.contador_cuadruplos}"
            self.contador_cuadruplos += 1
            cuadruplos_vel = [
                Cuadruplo('CREATE', robot_id, '—', temp_vel),
                Cuadruplo('=', str(valor), '—', temp_vel),
                Cuadruplo('ASSOC', temp_vel, '—', f"{robot_id}.velocidad")
            ]
            self.cuadruplos.extend(cuadruplos_vel)
            print(f"      ✅ Cuádruplos de velocidad generados: {len(cuadruplos_vel)}")
        else:
            cuadruplo = Cuadruplo('CALL', robot_id, str(valor), comando)
            self.cuadruplos.append(cuadruplo)
            print(f"      ✅ Cuádruplo de comando generado: {cuadruplo}")
            
    def _generar_salida_html(self, salida_lexico: List[str], 
                           salida_sintactico: List[str], 
                           salida_semantico: List[str]) -> str:
        """Genera la salida HTML completa"""
        
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
        
        # Tabla de símbolos (SOLO si no hay errores)
        if self.tabla_simbolos and len(self.errores) == 0:
            html_parts.append("<h2 style='color: #2c3e50;'>🔧 Tabla de Símbolos:</h2>")
            html_parts.append("<table border='1' style='border-collapse: collapse; width: 100%; margin: 10px 0; font-family: monospace;'>")
            html_parts.append("<tr style='background-color: #3498db; color: white;'>")
            html_parts.append("<th style='padding: 8px;'>ID</th><th style='padding: 8px;'>MÉTODO</th><th style='padding: 8px;'>PARÁMETRO</th><th style='padding: 8px;'>VALOR</th>")
            html_parts.append("</tr>")
            
            for simbolo in self.tabla_simbolos:
                html_parts.append("<tr style='background-color: #ecf0f1;'>")
                html_parts.append(f"<td style='padding: 8px; font-weight: bold;'>{simbolo.id}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{simbolo.metodo}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{simbolo.parametro}</td>")
                html_parts.append(f"<td style='padding: 8px; color: #e74c3c; font-weight: bold;'>{simbolo.valor}</td>")
                html_parts.append("</tr>")
                
            html_parts.append("</table>")
            
        # Tabla de cuádruplos (SOLO si no hay errores)
        if self.cuadruplos and len(self.errores) == 0:
            html_parts.append("<h2 style='color: #2c3e50;'>📊 Tabla de Cuádruplos:</h2>")
            html_parts.append("<table border='1' style='border-collapse: collapse; width: 100%; margin: 10px 0; font-family: monospace;'>")
            html_parts.append("<tr style='background-color: #27ae60; color: white;'>")
            html_parts.append("<th style='padding: 8px;'>Nº</th><th style='padding: 8px;'>Operador</th><th style='padding: 8px;'>Operando 1</th><th style='padding: 8px;'>Operando 2</th><th style='padding: 8px;'>Resultado</th>")
            html_parts.append("</tr>")
            
            for i, cuadruplo in enumerate(self.cuadruplos):
                bg_color = "#d5f4e6" if i % 2 == 0 else "#ffffff"
                html_parts.append(f"<tr style='background-color: {bg_color};'>")
                html_parts.append(f"<td style='padding: 8px; font-weight: bold;'>{i}</td>")
                html_parts.append(f"<td style='padding: 8px; color: #8e44ad; font-weight: bold;'>{cuadruplo.operador}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{cuadruplo.operando1}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{cuadruplo.operando2}</td>")
                html_parts.append(f"<td style='padding: 8px; color: #e67e22; font-weight: bold;'>{cuadruplo.resultado}</td>")
                html_parts.append("</tr>")
                
            html_parts.append("</table>")
        
        # Mensaje final
        if len(self.errores) == 0:
            html_parts.append("<div style='background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 10px 0; font-weight: bold; font-size: 16px;'>")
            html_parts.append("🎉 ¡Análisis completado exitosamente! El código está listo para ejecutar en el robot.")
            html_parts.append(f"<br>📊 Generados: {len(self.tabla_simbolos)} símbolos y {len(self.cuadruplos)} cuádruplos")
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