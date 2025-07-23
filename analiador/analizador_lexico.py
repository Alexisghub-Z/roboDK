#!/usr/bin/env python3
"""
Analizador Léxico COMPLETO para Robot ABB IRB 120
Convertido desde Java con toda la funcionalidad
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
    """Analizador léxico COMPLETO para el lenguaje de robots"""
    
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
            
            # Compilar resultados
            resultado.update({
                'exito': len(self.errores) == 0,
                'salida': salida_html,
                'tabla_simbolos': [self._simbolo_to_dict(s) for s in self.tabla_simbolos],
                'cuadruplos': [self._cuadruplo_to_dict(c) for c in self.cuadruplos],
                'errores': self.errores.copy()
            })
            
        except Exception as e:
            self.errores.append(f"Error inesperado: {str(e)}")
            resultado['salida'] = f"<div style='color: red;'>❌ Error inesperado: {str(e)}</div>"
            resultado['errores'] = self.errores.copy()
            
        return resultado
        
    def _analizar_codigo_completo(self, entrada: str) -> str:
        """Realiza el análisis léxico, sintáctico y semántico COMPLETO"""
        
        # Inicializar buffers de salida
        salida_lexico = ["<h2>🔍 Análisis Léxico:</h2>"]
        salida_sintactico = ["<h2>🧩 Análisis Sintáctico:</h2>"]
        salida_semantico = ["<h2>🧠 Análisis Semántico:</h2>"]
        
        if not entrada.strip():
            error = "❌ Error: Código vacío"
            salida_lexico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
        
        # Tokenizar entrada
        palabras = entrada.split()
        i = 0
        
        while i < len(palabras):
            palabra_actual = palabras[i]
            
            try:
                # Validación léxica básica
                if not re.match(r'^[a-zA-Z0-9.={}]+$', palabra_actual):
                    error = f"❌ Error léxico: token inválido → \"{palabra_actual}\""
                    salida_lexico.append(f"<div style='color: red;'>{error}</div>")
                    self.errores.append(error)
                    return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
                
                salida_lexico.append(f"<div style='color: green;'>✔ Token válido: {palabra_actual}</div>")
                
                # Declaración de robot
                if palabra_actual.lower() == 'robot':
                    i = self._procesar_declaracion_robot(palabras, i, salida_sintactico, salida_semantico)
                    if i == -1:  # Error
                        return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
                    continue
                
                # Comandos de robot
                if '.' in palabra_actual and i + 2 < len(palabras):
                    i = self._procesar_comando_robot(palabras, i, salida_sintactico, salida_semantico)
                    if i == -1:  # Error
                        return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
                    continue
                
                # Token no reconocido en este contexto
                error = f"❌ Error sintáctico: expresión incompleta o inválida → \"{palabra_actual}\""
                salida_sintactico.append(f"<div style='color: red;'>{error}</div>")
                self.errores.append(error)
                return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
                
            except Exception as e:
                error = f"❌ Error procesando '{palabra_actual}': {str(e)}"
                self.errores.append(error)
                return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
        
        # Si llegamos aquí, el análisis fue exitoso
        salida_semantico.append("<div style='color: green;'>✔ Análisis semántico completado sin errores</div>")
        
        return self._generar_salida_html(salida_lexico, salida_sintactico, salida_semantico)
        
    def _procesar_declaracion_robot(self, palabras: List[str], i: int, 
                                   salida_sintactico: List[str], 
                                   salida_semantico: List[str]) -> int:
        """Procesa la declaración de un robot"""
        
        if i + 1 >= len(palabras):
            error = "❌ Error sintáctico: Falta identificador tras 'Robot'"
            salida_sintactico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        robot_id = palabras[i + 1]
        
        if not self.patron_id.match(robot_id):
            error = f"❌ Error sintáctico: Identificador inválido → \"{robot_id}\""
            salida_sintactico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        # Verificar si ya existe
        if any(s.id.lower() == robot_id.lower() and s.metodo == 'robot' 
               for s in self.tabla_simbolos):
            error = f"❌ Error semántico: Robot ya declarado → \"{robot_id}\""
            salida_semantico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        # Agregar a tabla de símbolos
        self.tabla_simbolos.append(Simbolo(robot_id, 'robot', 0, 0))
        
        # Generar cuádruplo
        self.cuadruplos.append(Cuadruplo('CREATE', 'Robot', '—', robot_id))
        
        salida_sintactico.append(f"<div style='color: green;'>✔ Declaración de robot: {robot_id}</div>")
        salida_semantico.append(f"<div style='color: green;'>✔ Robot {robot_id} declarado correctamente</div>")
        
        return i + 2
        
    def _procesar_comando_robot(self, palabras: List[str], i: int,
                               salida_sintactico: List[str],
                               salida_semantico: List[str]) -> int:
        """Procesa un comando de robot (ID.comando = valor)"""
        
        comando_completo = palabras[i]
        operador = palabras[i + 1]
        valor_str = palabras[i + 2]
        
        # Parsear ID.comando
        partes = comando_completo.split('.')
        if len(partes) != 2:
            error = f"❌ Error sintáctico: Se esperaba ID.comando → \"{comando_completo}\""
            salida_sintactico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        robot_id, comando = partes
        
        # Verificar operador
        if operador != '=':
            error = f"❌ Error sintáctico: Se esperaba '=' después del comando, encontrado: \"{operador}\""
            salida_sintactico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        # Verificar que el robot esté declarado
        if not any(s.id.lower() == robot_id.lower() and s.metodo == 'robot' 
                  for s in self.tabla_simbolos):
            error = f"❌ Error semántico: Robot no declarado → \"{robot_id}\""
            salida_semantico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        # Verificar comando válido
        if comando.lower() not in self.comandos:
            error = f"❌ Error semántico: Comando inválido → \"{comando}\""
            salida_semantico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        # Procesar comando especial 'repetir'
        if comando.lower() == 'repetir':
            return self._procesar_repetir(palabras, i, robot_id, valor_str, 
                                        salida_sintactico, salida_semantico)
        
        # Validar valor numérico
        if not self.patron_valor.match(valor_str):
            error = f"❌ Error semántico: Valor numérico inválido → \"{valor_str}\""
            salida_semantico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        valor = int(valor_str)
        
        # Validar rango
        if comando.lower() in self.rangos:
            min_val, max_val = self.rangos[comando.lower()]
            if not (min_val <= valor <= max_val):
                error = f"❌ Error semántico: Valor fuera de rango para {comando} → {valor} (rango: {min_val}-{max_val})"
                salida_semantico.append(f"<div style='color: red;'>{error}</div>")
                self.errores.append(error)
                return -1
                
        # Actualizar tabla de símbolos
        self._actualizar_simbolo(robot_id, comando.lower(), valor)
        
        # Generar cuádruplos
        self._generar_cuadruplo_comando(robot_id, comando.lower(), valor)
        
        salida_sintactico.append(f"<div style='color: green;'>✔ Asignación: {comando_completo} = {valor}</div>")
        salida_semantico.append(f"<div style='color: green;'>✔ Valor válido asignado a {comando_completo}</div>")
        
        return i + 3
        
    def _procesar_repetir(self, palabras: List[str], i: int, robot_id: str, 
                         valor_str: str, salida_sintactico: List[str], 
                         salida_semantico: List[str]) -> int:
        """Procesa el comando repetir con bloque"""
        
        # Validar valor de repetición
        if not self.patron_valor.match(valor_str):
            error = f"❌ Error semántico: Valor de repetición inválido → \"{valor_str}\""
            salida_semantico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        repeticiones = int(valor_str)
        min_rep, max_rep = self.rangos['repetir']
        
        if not (min_rep <= repeticiones <= max_rep):
            error = f"❌ Error semántico: Repeticiones fuera de rango → {repeticiones} (rango: {min_rep}-{max_rep})"
            salida_semantico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        # Buscar bloque { ... }
        if i + 3 >= len(palabras) or palabras[i + 3] != '{':
            error = "❌ Error sintáctico: Falta '{' para abrir el bloque de repetición"
            salida_sintactico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        # Encontrar el cierre del bloque
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
            error = "❌ Error sintáctico: Falta '}' para cerrar el bloque de repetición"
            salida_sintactico.append(f"<div style='color: red;'>{error}</div>")
            self.errores.append(error)
            return -1
            
        # Generar cuádruplos para el bucle
        loop_var = f"contador{self.contador_cuadruplos}"
        loop_id = f"loop{self.contador_cuadruplos}"
        self.contador_cuadruplos += 1
        
        self.cuadruplos.extend([
            Cuadruplo('CREATE', robot_id, '—', loop_var),
            Cuadruplo('=', valor_str, '—', loop_var),
            Cuadruplo('CREATE', 'Loop', '—', loop_id),
            Cuadruplo('ASSOC', loop_var, '—', f"{loop_id}.contador"),
            Cuadruplo('ASSOC', loop_id, '—', f"{robot_id}.repetir")
        ])
        
        salida_sintactico.append(f"<div style='color: green;'>✔ Bloque de repetición con {repeticiones} iteraciones</div>")
        salida_semantico.append(f"<div style='color: green;'>✔ Procesando bloque {repeticiones} veces</div>")
        
        self.cuadruplos.append(Cuadruplo('EXEC_LOOP', f"{robot_id}.repetir", '—', '—'))
        
        return j
        
    def _actualizar_simbolo(self, robot_id: str, comando: str, valor: int):
        """Actualiza o agrega un símbolo en la tabla"""
        # Remover símbolo existente si existe
        self.tabla_simbolos = [s for s in self.tabla_simbolos 
                              if not (s.id.lower() == robot_id.lower() and s.metodo.lower() == comando.lower())]
        
        # Agregar nuevo símbolo
        self.tabla_simbolos.append(Simbolo(robot_id, comando, 1, valor))
        
    def _generar_cuadruplo_comando(self, robot_id: str, comando: str, valor: int):
        """Genera cuádruplos para un comando específico"""
        if comando == 'velocidad':
            temp_vel = f"vel{self.contador_cuadruplos}"
            self.contador_cuadruplos += 1
            self.cuadruplos.extend([
                Cuadruplo('CREATE', robot_id, '—', temp_vel),
                Cuadruplo('=', str(valor), '—', temp_vel),
                Cuadruplo('ASSOC', temp_vel, '—', f"{robot_id}.velocidad")
            ])
        else:
            self.cuadruplos.append(Cuadruplo('CALL', robot_id, str(valor), comando))
            
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
        
        # Tabla de símbolos
        if self.tabla_simbolos:
            html_parts.append("<h2>🔧 Tabla de Símbolos:</h2>")
            html_parts.append("<table border='1' style='border-collapse: collapse; width: 100%; margin: 10px 0;'>")
            html_parts.append("<tr style='background-color: #f0f0f0;'>")
            html_parts.append("<th style='padding: 8px;'>ID</th><th style='padding: 8px;'>MÉTODO</th><th style='padding: 8px;'>PARÁMETRO</th><th style='padding: 8px;'>VALOR</th>")
            html_parts.append("</tr>")
            
            for simbolo in self.tabla_simbolos:
                html_parts.append("<tr>")
                html_parts.append(f"<td style='padding: 8px;'>{simbolo.id}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{simbolo.metodo}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{simbolo.parametro}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{simbolo.valor}</td>")
                html_parts.append("</tr>")
                
            html_parts.append("</table><br>")
            
        # Tabla de cuádruplos
        if self.cuadruplos:
            html_parts.append("<h2>📊 Tabla de Cuádruplos:</h2>")
            html_parts.append("<table border='1' style='border-collapse: collapse; width: 100%; margin: 10px 0;'>")
            html_parts.append("<tr style='background-color: #f0f0f0;'>")
            html_parts.append("<th style='padding: 8px;'>Nº</th><th style='padding: 8px;'>Operador</th><th style='padding: 8px;'>Operando 1</th><th style='padding: 8px;'>Operando 2</th><th style='padding: 8px;'>Resultado</th>")
            html_parts.append("</tr>")
            
            for i, cuadruplo in enumerate(self.cuadruplos):
                html_parts.append("<tr>")
                html_parts.append(f"<td style='padding: 8px;'>{i}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{cuadruplo.operador}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{cuadruplo.operando1}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{cuadruplo.operando2}</td>")
                html_parts.append(f"<td style='padding: 8px;'>{cuadruplo.resultado}</td>")
                html_parts.append("</tr>")
                
            html_parts.append("</table><br>")
        
        # Mensaje final
        if len(self.errores) == 0:
            html_parts.append("<div style='color: green; font-weight: bold; font-size: 16px;'>🎉 ¡Análisis completado exitosamente! El código está listo para ejecutar en el robot.</div>")
        
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