#!/usr/bin/env python3
"""
Controlador MEJORADO para Robot ABB IRB 120-3/0.6 con Garra Robotiq 2F-85
NUEVA CARACTERÍSTICA: 
- Sistema de velocidades independientes por movimiento
- Garra controla rotación del EJE 6 (muñeca3) para efecto visual
- Cada movimiento puede tener su propia velocidad (1-60 segundos)
"""

import sys
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from robodk import robolink, robomath
    ROBODK_AVAILABLE = True
except ImportError:
    ROBODK_AVAILABLE = False
    print("⚠️ RoboDK no está instalado. Ejecutando en modo simulación.")

@dataclass
class PosicionRobot:
    """Representa una posición del robot"""
    base: float = 0.0
    hombro: float = 0.0
    codo: float = 0.0
    muñeca1: float = 0.0
    muñeca2: float = 0.0
    muñeca3: float = 0.0
    garra: float = 0.0  # Ahora representa rotación del eje 6

@dataclass
class ConfiguracionRobot:
    """Configuración del robot"""
    velocidad_maxima: float = 100.0  # mm/s
    aceleracion_maxima: float = 250.0  # mm/s²
    velocidad_articular: float = 45.0  # deg/s
    precision_movimiento: float = 0.1  # mm

class RobotController:
    """Controlador MEJORADO del robot ABB IRB 120 - GARRA COMO ROTACIÓN EJE 6"""
    
    def __init__(self):
        self.conectado = False
        self.rdk = None
        self.robot = None
        self.garra = None
        self.garra_real_encontrada = False
        self.tipo_garra = "ninguna"
        
        # Estado actual del robot
        self.posicion_actual = PosicionRobot()
        self.delay_actual = 5.0  # VELOCIDAD GLOBAL POR DEFECTO
        
        # NUEVO: Historial de velocidades para debugging
        self.historial_velocidades = []
        self.contador_movimientos = 0
        
        # Configuración
        self.config = ConfiguracionRobot()
        
        # Límites articulares del ABB IRB 120
        self.limites_articulares = {
    'base': (-360, 360),         # CORREGIDO: Base bidireccional
    'hombro': (-180, 180),       # CORREGIDO: Hombro bidireccional  
    'codo': (-180, 180),         # CORREGIDO: Codo bidireccional
    'muñeca1': (-160, 160),      # Ya era correcto
    'muñeca2': (-120, 120),      # Ya era correcto
    'muñeca3': (-400, 400),      # Ya era correcto
    'garra': (-360, 360),        # CORREGIDO: Garra bidireccional
    'velocidad': (1, 60)         # Velocidades (solo positivo)
}
        
        # Estado de la garra (ahora basado en rotación)
        self.garra_abierta = True
        
    def conectar(self) -> bool:
        """
        Conecta con RoboDK y configura el robot (Compatible v5.9+)
        
        Returns:
            True si la conexión fue exitosa
        """
        if not ROBODK_AVAILABLE:
            print("🔄 Iniciando en modo simulación (RoboDK no disponible)")
            print("⚡ VELOCIDADES INDEPENDIENTES: Activadas en simulación")
            print("🔄 GARRA COMO ROTACIÓN EJE 6: Activada en simulación")
            self.conectado = True
            return True
            
        try:
            # Conectar con RoboDK
            self.rdk = robolink.Robolink()
            
            # Verificar que RoboDK esté ejecutándose
            try:
                version = self.rdk.Version()
                print(f"✅ RoboDK detectado - Versión: {version}")
                print(f"⚡ VELOCIDADES INDEPENDIENTES: Activadas")
                print(f"🔄 GARRA COMO ROTACIÓN EJE 6: Activada")
            except Exception as e:
                print(f"❌ No se puede conectar con RoboDK: {e}")
                print("💡 Asegúrate de que RoboDK esté ejecutándose")
                return False
                
            # Buscar el robot ABB IRB 120
            robot_encontrado = self._buscar_robot()
            
            if not robot_encontrado:
                print("❌ Robot ABB IRB 120-3/0.6 no encontrado en RoboDK")
                print("💡 Solución:")
                print("   1. En RoboDK: File → Add → Robot")
                print("   2. Buscar: ABB → IRB 120-3/0.6")
                print("   3. Agregar el robot a la estación")
                return False
                
            self.robot = robot_encontrado
            
            # Buscar la garra Robotiq (opcional)
            self.garra = self._configurar_garra()
            
            # Configurar parámetros del robot
            self._configurar_robot()
            
            # Obtener posición actual
            self._actualizar_posicion_actual()
            
            self.conectado = True
            print("✅ Robot conectado exitosamente")
            print(f"⚡ Sistema de velocidades independientes: ACTIVO")
            print(f"🔄 Garra como rotación del eje 6: ACTIVA")
            print(f"📍 Posición actual: {self._posicion_to_string()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error conectando con el robot: {e}")
            return False
    
    def _buscar_robot(self):
        """Busca el robot ABB IRB 120 en la estación"""
        try:
            nombres_robot = [
                'ABB IRB 120-3/0.6',
                'IRB 120',
                'ABB IRB120',
                'IRB120-3/0.6',
                'Robot'
            ]
            
            for nombre in nombres_robot:
                try:
                    robot = self.rdk.Item(nombre, robolink.ITEM_TYPE_ROBOT)
                    robot_name = robot.Name()
                    print(f"✅ Robot encontrado: {robot_name}")
                    return robot
                except:
                    continue
            
            # Buscar el primer robot disponible
            try:
                robots = self.rdk.ItemList(robolink.ITEM_TYPE_ROBOT)
                if robots:
                    robot = robots[0]
                    robot_name = robot.Name()
                    print(f"✅ Usando primer robot encontrado: {robot_name}")
                    return robot
            except:
                pass
                
            return None
            
        except Exception as e:
            print(f"⚠️ Error buscando robot: {e}")
            return None
            
    def desconectar(self):
        """Desconecta del robot y limpia recursos"""
        if self.conectado:
            try:
                if self.robot:
                    try:
                        self.robot.Stop()
                    except:
                        pass
                    
                self.conectado = False
                self.rdk = None
                self.robot = None
                self.garra = None
                self.garra_real_encontrada = False
                self.tipo_garra = "ninguna"
                
                # MOSTRAR RESUMEN DE VELOCIDADES
                if self.historial_velocidades:
                    print("📊 RESUMEN DE VELOCIDADES UTILIZADAS:")
                    for entrada in self.historial_velocidades[-10:]:  # Últimas 10
                        print(f"   {entrada}")
                
                print("🔌 Robot desconectado")
                
            except Exception as e:
                print(f"⚠️ Error al desconectar: {e}")
                
    def _configurar_garra(self):
        """Configura la garra Robotiq 2F-85 Gripper (OPCIONAL - Solo para detección)"""
        try:
            nombres_garra = [
                'Robotiq 2F-85 Gripper (Open)',
                'RobotiQ 2F-85 Gripper (Open)',
                'Robotiq 2F-85 Gripper',
                'Robotiq 2F-85 Open',
                'Robotiq Open',
                'Robotiq 2F-85',
                'Robotiq 2F85',
                'Robotiq',
                '2F-85',
                'Gripper',
                'Garra',
                'Tool'
            ]
            
            print("🔍 Buscando Robotiq 2F-85 Gripper (Open)...")
            
            for nombre in nombres_garra:
                try:
                    garra = self.rdk.Item(nombre, robolink.ITEM_TYPE_TOOL)
                    garra_name = garra.Name()
                    
                    self.robot.setTool(garra)
                    self.garra_real_encontrada = True
                    
                    if 'open' in garra_name.lower() or 'gripper' in garra_name.lower():
                        self.tipo_garra = "open"
                        print(f"🎯 ROBOTIQ 2F-85 GRIPPER (OPEN) ENCONTRADA!")
                        print(f"   Nombre: {garra_name}")
                        print(f"   ✅ Garra detectada (control por rotación eje 6)")
                    elif 'closed' in garra_name.lower():
                        self.tipo_garra = "closed"
                        print(f"🎯 ROBOTIQ CLOSED encontrada: {garra_name}")
                    else:
                        self.tipo_garra = "real"
                        print(f"🎯 Garra Robotiq encontrada: {garra_name}")
                    
                    print(f"   🔧 Configurada como herramienta activa")
                    print(f"   🔄 Control de garra: Rotación del eje 6")
                    return garra
                except:
                    continue
                    
            print("⚠️ Garra Robotiq no encontrada")
            print("🔄 Usando control de garra por rotación del eje 6")
            self.tipo_garra = "rotacion_eje6"
            return None
                
        except Exception as e:
            print(f"⚠️ Error configurando garra: {e}")
            print("🔄 Usando control de garra por rotación del eje 6")
            self.tipo_garra = "rotacion_eje6"
            return None
            
    def _configurar_robot(self):
        """Configura los parámetros del robot"""
        try:
            if not self.robot:
                return
                
            # Configurar velocidades iniciales
            self.robot.setSpeed(self.config.velocidad_maxima)
            self.robot.setAcceleration(self.config.aceleracion_maxima)
            
            try:
                self.robot.setPrecision(self.config.precision_movimiento)
            except:
                pass
            
            print("⚙️ Parámetros del robot configurados")
            print("⚡ Sistema de velocidades independientes: LISTO")
            print("🔄 Control de garra por rotación eje 6: LISTO")
            
        except Exception as e:
            print(f"⚠️ Error configurando robot: {e}")
            
    def _actualizar_posicion_actual(self):
        """Actualiza la posición actual del robot AL CONECTAR"""
        try:
            if not self.robot:
                # Inicializar en posición home si no hay robot
                self.posicion_actual.base = 0.0
                self.posicion_actual.hombro = 0.0
                self.posicion_actual.codo = 0.0
                self.posicion_actual.muñeca1 = 0.0
                self.posicion_actual.muñeca2 = 90.0
                self.posicion_actual.muñeca3 = 0.0
                self.posicion_actual.garra = 0.0  # Rotación inicial
                return
                
            try:
                joints = self.robot.Joints()
                
                if joints and len(joints) >= 6:
                    self.posicion_actual.base = joints[0]
                    self.posicion_actual.hombro = joints[1]
                    self.posicion_actual.codo = joints[2]
                    self.posicion_actual.muñeca1 = joints[3]
                    self.posicion_actual.muñeca2 = joints[4]
                    self.posicion_actual.muñeca3 = joints[5]
                    self.posicion_actual.garra = joints[5]  # Garra = eje 6
                    print(f"📍 Posición inicial del robot:")
                    print(f"   Base: {joints[0]:.1f}°, Hombro: {joints[1]:.1f}°, Codo: {joints[2]:.1f}°")
                    print(f"   Eje 6 (garra): {joints[5]:.1f}°")
                else:
                    # Usar posición home
                    self.posicion_actual.base = 0.0
                    self.posicion_actual.hombro = 0.0
                    self.posicion_actual.codo = 0.0
                    self.posicion_actual.muñeca1 = 0.0
                    self.posicion_actual.muñeca2 = 90.0
                    self.posicion_actual.muñeca3 = 0.0
                    self.posicion_actual.garra = 0.0
                    print(f"📍 Usando posición home como inicial")
                    
            except Exception as e:
                # Usar posición home como fallback
                self.posicion_actual.base = 0.0
                self.posicion_actual.hombro = 0.0
                self.posicion_actual.codo = 0.0
                self.posicion_actual.muñeca1 = 0.0
                self.posicion_actual.muñeca2 = 90.0
                self.posicion_actual.muñeca3 = 0.0
                self.posicion_actual.garra = 0.0
                print(f"⚠️ Error leyendo posición inicial, usando home: {e}")
                
        except Exception as e:
            print(f"⚠️ Error obteniendo posición actual: {e}")
            # Inicializar en posición home como fallback
            self.posicion_actual.base = 0.0
            self.posicion_actual.hombro = 0.0
            self.posicion_actual.codo = 0.0
            self.posicion_actual.muñeca1 = 0.0
            self.posicion_actual.muñeca2 = 90.0
            self.posicion_actual.muñeca3 = 0.0
            self.posicion_actual.garra = 0.0
            
    def mover_componente(self, componente: str, valor: float) -> bool:
        """
        Mueve un componente específico del robot CON VELOCIDAD INDEPENDIENTE ACTUAL
        GARRA ahora controla la rotación del EJE 6 (muñeca3)
        
        Args:
            componente: Nombre del componente ('base', 'hombro', 'codo', 'garra', 'velocidad')
            valor: Valor objetivo para el componente
            
        Returns:
            True si el movimiento fue exitoso
        """
        if not self.conectado:
            print("❌ Robot no conectado")
            return False
            
        componente = componente.lower()
        
        # Manejar velocidad como caso especial
        if componente == 'velocidad':
            return self.establecer_delay(valor)
        
        # Validar componente
        if componente not in self.limites_articulares:
            print(f"❌ Componente desconocido: {componente}")
            print(f"   Componentes válidos: base, hombro, codo, garra, velocidad")
            return False
            
        # Validar límites SEGÚN TABLA
        min_val, max_val = self.limites_articulares[componente]
        if not (min_val <= valor <= max_val):
            if componente == 'base':
                print(f"❌ Base fuera de rango: {valor}° (rango permitido: 0° a 360°)")
            elif componente == 'hombro':
                print(f"❌ Hombro fuera de rango: {valor}° (rango permitido: 0° a 180°)")
            elif componente == 'codo':
                print(f"❌ Codo fuera de rango: {valor}° (rango permitido: 0° a 180°)")
            elif componente == 'garra':
                print(f"❌ Garra (rotación) fuera de rango: {valor}° (rango permitido: 0° a 360°)")
                print(f"   La garra rota el eje 6 del robot para efecto visual")
            else:
                print(f"❌ Valor fuera de rango para {componente}: {valor} (rango: {min_val}-{max_val})")
            return False
            
        try:
            # REGISTRAR VELOCIDAD UTILIZADA PARA ESTE MOVIMIENTO
            self.contador_movimientos += 1
            if componente == 'garra':
                signo = "+" if valor >= 0 else ""
                registro = f"Movimiento {self.contador_movimientos}: {componente} (eje 6) = {signo}{valor}° (velocidad: {self.delay_actual}s)"
            else:
                signo = "+" if valor >= 0 else ""
                registro = f"Movimiento {self.contador_movimientos}: {componente} = {signo}{valor}° (velocidad: {self.delay_actual}s)"
            self.historial_velocidades.append(registro)
            
            if componente == 'garra':
                return self._mover_garra_con_soporte_negativo(valor)
            else:
                return self._mover_articulacion_con_soporte_negativo(componente, valor)
                
        except Exception as e:
            print(f"❌ Error moviendo {componente}: {e}")
            return False
            
    def _mover_articulacion_con_soporte_negativo(self, componente: str, valor: float) -> bool:
        """NUEVA FUNCIÓN: Mueve una articulación CON SOPORTE PARA VALORES NEGATIVOS"""
        
        if not ROBODK_AVAILABLE or not self.robot:
            # Modo simulación
            signo = "+" if valor >= 0 else ""
            print(f"🔄 [SIMULACIÓN] {componente.upper()} = {signo}{valor}° (velocidad independiente: {self.delay_actual}s)")
            self._actualizar_posicion_simulada(componente, valor)
            time.sleep(self.delay_actual)
            return True
            
        try:
            # USAR POSICIÓN INTERNA ACUMULATIVA
            joints_objetivo = [
                self.posicion_actual.base,
                self.posicion_actual.hombro,
                self.posicion_actual.codo,
                self.posicion_actual.muñeca1,
                self.posicion_actual.muñeca2,
                self.posicion_actual.muñeca3
            ]
            
            # Mapear componente a índice de articulación
            indice_articulacion = {
                'base': 0,
                'hombro': 1,
                'codo': 2,
                'muñeca1': 3,
                'muñeca2': 4,
                'muñeca3': 5
            }.get(componente)
            
            if indice_articulacion is None:
                print(f"❌ No se puede mapear componente: {componente}")
                return False
                
            # Obtener valor actual del componente
            valor_actual = joints_objetivo[indice_articulacion]
            
            # ACTUALIZAR LA ARTICULACIÓN (PUEDE SER NEGATIVA)
            joints_objetivo[indice_articulacion] = valor
            
            # CALCULAR VELOCIDAD BASADA EN DISTANCIA Y TIEMPO INDEPENDIENTE
            distancia_grados = abs(valor - valor_actual)
            
            signo_actual = "+" if valor_actual >= 0 else ""
            signo_objetivo = "+" if valor >= 0 else ""
            
            print(f"🚀 VELOCIDAD INDEPENDIENTE CON SOPORTE NEGATIVO: {componente.upper()}")
            print(f"   De {signo_actual}{valor_actual:.1f}° a {signo_objetivo}{valor:.1f}° (distancia: {distancia_grados:.1f}°)")
            print(f"   ⚡ Tiempo asignado: {self.delay_actual}s")
            
            if distancia_grados < 0.1:
                print(f"✅ {componente} ya está en posición {signo_objetivo}{valor}°")
                self._actualizar_posicion_simulada(componente, valor)
                return True
            
            # Calcular velocidad específica para esta velocidad independiente
            velocidad_necesaria = distancia_grados / self.delay_actual
            
            # Aplicar límites de velocidad (seguridad)
            velocidad_min = 1.0
            velocidad_max = 150.0
            velocidad_necesaria = max(velocidad_min, min(velocidad_max, velocidad_necesaria))
            
            # Configurar velocidad del robot ESPECÍFICA PARA ESTE MOVIMIENTO
            self.robot.setSpeed(velocidad_necesaria, velocidad_necesaria)
            
            print(f"   🎯 Velocidad calculada: {velocidad_necesaria:.1f}°/s")
            print(f"   📍 Manteniendo otras posiciones")
            
            # Ejecutar movimiento CON VALOR NEGATIVO SI ES NECESARIO
            inicio_tiempo = time.time()
            self.robot.MoveJ(joints_objetivo)
            tiempo_real = time.time() - inicio_tiempo
            
            print(f"✅ {componente.upper()} movido a {signo_objetivo}{valor}° (tiempo real: {tiempo_real:.1f}s)")
            
            # Actualizar posición interna
            self._actualizar_posicion_simulada(componente, valor)
            
            return True
            
        except Exception as e:
            print(f"❌ Error en movimiento con soporte negativo: {e}")
            return False
    
    def _mover_garra_con_soporte_negativo(self, rotacion_objetivo: float) -> bool:
        """
        NUEVA FUNCIÓN: Mueve la garra con soporte para rotación negativa
        """
        
        if not ROBODK_AVAILABLE or not self.robot:
            # Modo simulación
            signo = "+" if rotacion_objetivo >= 0 else ""
            print(f"🔄 [SIMULACIÓN] GARRA (EJE 6) = {signo}{rotacion_objetivo}° (velocidad independiente: {self.delay_actual}s)")
            self.posicion_actual.garra = rotacion_objetivo
            self.posicion_actual.muñeca3 = rotacion_objetivo
            time.sleep(self.delay_actual)
            return True
            
        try:
            rotacion_actual = self.posicion_actual.garra
            
            signo_actual = "+" if rotacion_actual >= 0 else ""
            signo_objetivo = "+" if rotacion_objetivo >= 0 else ""
            
            print(f"🔄 CONTROL DE GARRA CON SOPORTE NEGATIVO")
            print(f"   Objetivo: {signo_objetivo}{rotacion_objetivo}° (rotación del eje 6)")
            print(f"   Actual: {signo_actual}{rotacion_actual}°")
            print(f"   ⚡ Velocidad independiente: {self.delay_actual}s")
            
            # USAR POSICIÓN INTERNA ACUMULATIVA MANTENIENDO TODAS LAS ARTICULACIONES
            joints_objetivo = [
                self.posicion_actual.base,      # Mantener base actual
                self.posicion_actual.hombro,    # Mantener hombro actual  
                self.posicion_actual.codo,      # Mantener codo actual
                self.posicion_actual.muñeca1,   # Mantener muñeca 1
                self.posicion_actual.muñeca2,   # Mantener muñeca 2
                rotacion_objetivo               # EJE 6 CON ROTACIÓN (PUEDE SER NEGATIVA)
            ]
            
            # CALCULAR VELOCIDAD BASADA EN DISTANCIA Y VELOCIDAD INDEPENDIENTE
            distancia_rotacion = abs(rotacion_objetivo - rotacion_actual)
            
            print(f"   🎯 Rotación del eje 6:")
            print(f"      De {signo_actual}{rotacion_actual:.1f}° a {signo_objetivo}{rotacion_objetivo:.1f}° (distancia: {distancia_rotacion:.1f}°)")
            print(f"      Manteniendo: Base={joints_objetivo[0]:.1f}°, Hombro={joints_objetivo[1]:.1f}°, Codo={joints_objetivo[2]:.1f}°")
            
            if distancia_rotacion < 0.1:
                print(f"✅ Garra (eje 6) ya está en rotación {signo_objetivo}{rotacion_objetivo}°")
                self._actualizar_posicion_simulada('garra', rotacion_objetivo)
                return True
            
            # Calcular velocidad específica para la velocidad independiente
            velocidad_garra = distancia_rotacion / self.delay_actual
            velocidad_garra = max(1.0, min(150.0, velocidad_garra))  # Límites de seguridad
            
            # Configurar velocidad del robot
            self.robot.setSpeed(velocidad_garra, velocidad_garra)
            
            print(f"      Velocidad calculada: {velocidad_garra:.1f}°/s")
            print(f"      Tiempo objetivo: {self.delay_actual}s")
            
            # Ejecutar movimiento BIDIRECCIONAL (CON NEGATIVOS)
            inicio_tiempo = time.time()
            self.robot.MoveJ(joints_objetivo)
            tiempo_real = time.time() - inicio_tiempo
            
            print(f"✅ GARRA (EJE 6) rotada a {signo_objetivo}{rotacion_objetivo}° (tiempo real: {tiempo_real:.1f}s)")
            print(f"   📍 Robot mantiene todas las demás posiciones")
            
            # Actualizar posiciones internas
            self.posicion_actual.garra = rotacion_objetivo
            self.posicion_actual.muñeca3 = rotacion_objetivo
            self.garra_abierta = rotacion_objetivo > 0  # Simplificado para rotación
            
            return True
            
        except Exception as e:
            print(f"❌ Error en rotación de garra con soporte negativo: {e}")
            return False
        """Mueve una articulación CON LA VELOCIDAD INDEPENDIENTE ACTUAL"""
        
        if not ROBODK_AVAILABLE or not self.robot:
            # Modo simulación
            print(f"🔄 [SIMULACIÓN] {componente.upper()} = {valor}° (velocidad independiente: {self.delay_actual}s)")
            self._actualizar_posicion_simulada(componente, valor)
            time.sleep(self.delay_actual)
            return True
            
        try:
            # USAR POSICIÓN INTERNA ACUMULATIVA
            joints_objetivo = [
                self.posicion_actual.base,
                self.posicion_actual.hombro,
                self.posicion_actual.codo,
                self.posicion_actual.muñeca1,
                self.posicion_actual.muñeca2,
                self.posicion_actual.muñeca3
            ]
            
            # Mapear componente a índice de articulación
            indice_articulacion = {
                'base': 0,
                'hombro': 1,
                'codo': 2,
                'muñeca1': 3,
                'muñeca2': 4,
                'muñeca3': 5
            }.get(componente)
            
            if indice_articulacion is None:
                print(f"❌ No se puede mapear componente: {componente}")
                return False
                
            # Obtener valor actual del componente
            valor_actual = joints_objetivo[indice_articulacion]
            
            # ACTUALIZAR SOLO LA ARTICULACIÓN QUE SE ESTÁ MOVIENDO
            joints_objetivo[indice_articulacion] = valor
            
            # CALCULAR VELOCIDAD BASADA EN DISTANCIA Y TIEMPO INDEPENDIENTE
            distancia_grados = abs(valor - valor_actual)
            
            print(f"🚀 VELOCIDAD INDEPENDIENTE: {componente.upper()}")
            print(f"   De {valor_actual:.1f}° a {valor:.1f}° (distancia: {distancia_grados:.1f}°)")
            print(f"   ⚡ Tiempo asignado: {self.delay_actual}s")
            
            if distancia_grados < 0.1:
                print(f"✅ {componente} ya está en posición {valor}°")
                self._actualizar_posicion_simulada(componente, valor)
                return True
            
            # Calcular velocidad específica para esta velocidad independiente
            velocidad_necesaria = distancia_grados / self.delay_actual
            
            # Aplicar límites de velocidad (seguridad)
            velocidad_min = 1.0
            velocidad_max = 150.0
            velocidad_necesaria = max(velocidad_min, min(velocidad_max, velocidad_necesaria))
            
            # Configurar velocidad del robot ESPECÍFICA PARA ESTE MOVIMIENTO
            self.robot.setSpeed(velocidad_necesaria, velocidad_necesaria)
            
            print(f"   🎯 Velocidad calculada: {velocidad_necesaria:.1f}°/s")
            print(f"   📍 Manteniendo: Base={joints_objetivo[0]:.1f}°, Hombro={joints_objetivo[1]:.1f}°, Codo={joints_objetivo[2]:.1f}°")
            
            # Ejecutar movimiento CON VELOCIDAD INDEPENDIENTE
            inicio_tiempo = time.time()
            self.robot.MoveJ(joints_objetivo)
            tiempo_real = time.time() - inicio_tiempo
            
            print(f"✅ {componente.upper()} movido a {valor}° (tiempo real: {tiempo_real:.1f}s)")
            
            # Actualizar posición interna
            self._actualizar_posicion_simulada(componente, valor)
            
            return True
            
        except Exception as e:
            print(f"❌ Error en movimiento con velocidad independiente: {e}")
            return False
    
    def _mover_garra_como_rotacion_eje6(self, rotacion_grados: float) -> bool:
        """
        NUEVA FUNCIÓN: Mueve la garra controlando la ROTACIÓN DEL EJE 6 (muñeca3)
        En lugar de mover la garra física, rota el eje 6 para efecto visual
        """
        
        if not ROBODK_AVAILABLE or not self.robot:
            # Modo simulación
            print(f"🔄 [SIMULACIÓN] GARRA (EJE 6) = {rotacion_grados}° (velocidad independiente: {self.delay_actual}s)")
            self.posicion_actual.garra = rotacion_grados
            self.posicion_actual.muñeca3 = rotacion_grados  # Sincronizar con eje 6
            time.sleep(self.delay_actual)
            return True
            
        try:
            print(f"🔄 CONTROL DE GARRA POR ROTACIÓN DEL EJE 6")
            print(f"   Objetivo: {rotacion_grados}° (rotación del eje 6)")
            print(f"   ⚡ Velocidad independiente: {self.delay_actual}s")
            
            # USAR POSICIÓN INTERNA ACUMULATIVA MANTENIENDO TODAS LAS ARTICULACIONES
            joints_objetivo = [
                self.posicion_actual.base,      # Mantener base actual
                self.posicion_actual.hombro,    # Mantener hombro actual  
                self.posicion_actual.codo,      # Mantener codo actual
                self.posicion_actual.muñeca1,   # Mantener muñeca 1
                self.posicion_actual.muñeca2,   # Mantener muñeca 2
                rotacion_grados                 # SOLO CAMBIAR EL EJE 6 (muñeca3)
            ]
            
            # Obtener rotación actual del eje 6
            rotacion_actual = self.posicion_actual.muñeca3
            
            # CALCULAR VELOCIDAD BASADA EN DISTANCIA Y VELOCIDAD INDEPENDIENTE
            distancia_rotacion = abs(rotacion_grados - rotacion_actual)
            
            print(f"   🎯 Rotación del eje 6:")
            print(f"      De {rotacion_actual:.1f}° a {rotacion_grados}° (distancia: {distancia_rotacion:.1f}°)")
            print(f"      Manteniendo: Base={joints_objetivo[0]:.1f}°, Hombro={joints_objetivo[1]:.1f}°, Codo={joints_objetivo[2]:.1f}°")
            
            if distancia_rotacion < 0.1:
                print(f"✅ Garra (eje 6) ya está en rotación {rotacion_grados}°")
                self._actualizar_posicion_simulada('garra', rotacion_grados)
                return True
            
            # Calcular velocidad específica para la velocidad independiente
            velocidad_garra = distancia_rotacion / self.delay_actual
            velocidad_garra = max(1.0, min(150.0, velocidad_garra))  # Límites de seguridad
            
            # Configurar velocidad del robot
            self.robot.setSpeed(velocidad_garra, velocidad_garra)
            
            print(f"      Velocidad calculada: {velocidad_garra:.1f}°/s")
            print(f"      Tiempo objetivo: {self.delay_actual}s")
            
            # Ejecutar movimiento SOLO DEL EJE 6
            inicio_tiempo = time.time()
            self.robot.MoveJ(joints_objetivo)
            tiempo_real = time.time() - inicio_tiempo
            
            print(f"✅ GARRA (EJE 6) rotada a {rotacion_grados}° (tiempo real: {tiempo_real:.1f}s)")
            print(f"   📍 Robot mantiene todas las demás posiciones")
            
            # Actualizar posiciones internas
            self.posicion_actual.garra = rotacion_grados
            self.posicion_actual.muñeca3 = rotacion_grados
            self.garra_abierta = rotacion_grados > 180  # Simplificado para rotación
            
            return True
            
        except Exception as e:
            print(f"❌ Error en rotación de garra (eje 6): {e}")
            return False
            
    def _actualizar_posicion_simulada(self, componente: str, valor: float):
        """Actualiza la posición simulada internamente"""
        if componente == 'base':
            self.posicion_actual.base = valor
        elif componente == 'hombro':
            self.posicion_actual.hombro = valor
        elif componente == 'codo':
            self.posicion_actual.codo = valor
        elif componente == 'muñeca1':
            self.posicion_actual.muñeca1 = valor
        elif componente == 'muñeca2':
            self.posicion_actual.muñeca2 = valor
        elif componente == 'muñeca3':
            self.posicion_actual.muñeca3 = valor
        elif componente == 'garra':
            self.posicion_actual.garra = valor
            self.posicion_actual.muñeca3 = valor  # Sincronizar garra con eje 6
            
    def establecer_delay(self, delay_segundos: float) -> bool:
        """
        Establece el delay (velocidad independiente) del robot
        
        Args:
            delay_segundos: Tiempo en segundos para el próximo movimiento (1-60s)
            
        Returns:
            True si se estableció correctamente
        """
        if not (1 <= delay_segundos <= 60):
            print(f"❌ Velocidad independiente fuera de rango: {delay_segundos}s (rango: 1-60s)")
            return False
            
        delay_anterior = self.delay_actual
        self.delay_actual = delay_segundos
        
        # REGISTRAR CAMBIO DE VELOCIDAD
        registro_velocidad = f"Cambio de velocidad: {delay_anterior}s → {delay_segundos}s"
        self.historial_velocidades.append(registro_velocidad)
        
        if not ROBODK_AVAILABLE or not self.robot:
            print(f"🔄 [SIMULACIÓN] Velocidad independiente: {delay_segundos}s")
            return True
            
        try:
            # Calcular velocidad basada en delay para configuración general
            velocidad_calculada = self._calcular_velocidad_por_delay(delay_segundos)
            
            print(f"⚡ VELOCIDAD INDEPENDIENTE ESTABLECIDA:")
            print(f"   Tiempo por movimiento: {delay_segundos}s")
            print(f"   Velocidad base calculada: {velocidad_calculada:.1f}°/s")
            print(f"   Los próximos movimientos (incluida garra/eje 6) usarán esta velocidad")
            
            return True
            
        except Exception as e:
            print(f"❌ Error estableciendo velocidad independiente: {e}")
            return False
            
    def _calcular_velocidad_por_delay(self, delay_segundos: float) -> float:
        """Calcula velocidad base del robot basada en el delay deseado"""
        # Mapear delay (1-60s) a velocidad base (5-100°/s)
        velocidad_min = 5.0   # °/s para delay máximo
        velocidad_max = 100.0 # °/s para delay mínimo
        
        # Mapeo inverso: menor delay = mayor velocidad
        factor = (60.0 - delay_segundos) / (60.0 - 1.0)
        velocidad = velocidad_min + (velocidad_max - velocidad_min) * factor
        
        return max(velocidad_min, min(velocidad_max, velocidad))
    
    def obtener_estado_con_velocidades(self) -> Dict:
        """Obtiene el estado completo del robot CON INFORMACIÓN DE VELOCIDADES Y GARRA"""
        return {
            'conectado': self.conectado,
            'garra_real': self.garra_real_encontrada,
            'tipo_garra': self.tipo_garra,
            'control_garra': 'rotacion_eje6',  # NUEVO: Indicar tipo de control
            'posicion': {
                'base': self.posicion_actual.base,
                'hombro': self.posicion_actual.hombro,
                'codo': self.posicion_actual.codo,
                'muñeca1': self.posicion_actual.muñeca1,
                'muñeca2': self.posicion_actual.muñeca2,
                'muñeca3': self.posicion_actual.muñeca3,
                'garra_rotacion_eje6': self.posicion_actual.garra  # NUEVO: Clarificar que es rotación
            },
            'velocidad_independiente_actual': self.delay_actual,
            'total_movimientos': self.contador_movimientos,
            'historial_velocidades': self.historial_velocidades[-5:] if self.historial_velocidades else [],  # Últimas 5
            'garra_abierta': self.garra_abierta,
            'robodk_disponible': ROBODK_AVAILABLE,
            'sistema_velocidades_independientes': True
        }
        
    def obtener_estado(self) -> Dict:
        """Método de compatibilidad - obtiene estado básico"""
        estado_completo = self.obtener_estado_con_velocidades()
        # Convertir para compatibilidad con código anterior
        estado_completo['delay'] = estado_completo['velocidad_independiente_actual']
        return estado_completo
        
    def _posicion_to_string(self) -> str:
        """Convierte la posición actual a string legible CON VELOCIDAD Y GARRA"""
        control_garra_info = "ROTACIÓN EJE 6"
        
        return (f"Base: {self.posicion_actual.base:.1f}°, "
                f"Hombro: {self.posicion_actual.hombro:.1f}°, "
                f"Codo: {self.posicion_actual.codo:.1f}°, "
                f"Garra ({control_garra_info}): {self.posicion_actual.garra:.1f}°, "
                f"Velocidad Independiente: {self.delay_actual:.1f}s, "
                f"Movimientos: {self.contador_movimientos}")
    
    def obtener_resumen_velocidades(self) -> str:
        """Obtiene un resumen de las velocidades utilizadas"""
        if not self.historial_velocidades:
            return "📊 Sin historial de velocidades"
            
        resumen = "📊 RESUMEN DE VELOCIDADES INDEPENDIENTES:\n"
        resumen += f"   Total de cambios: {len(self.historial_velocidades)}\n"
        resumen += f"   Velocidad actual: {self.delay_actual}s\n"
        resumen += f"   Movimientos realizados: {self.contador_movimientos}\n"
        resumen += f"   Control de garra: Rotación del eje 6\n"
        
        if len(self.historial_velocidades) > 0:
            resumen += "   Últimas velocidades:\n"
            for entrada in self.historial_velocidades[-5:]:
                resumen += f"     - {entrada}\n"
                
        return resumen
    
    def resetear_historial_velocidades(self):
        """Resetea el historial de velocidades y movimientos"""
        self.historial_velocidades.clear()
        self.contador_movimientos = 0
        print("🔄 Historial de velocidades reseteado")
        
    # MÉTODOS ADICIONALES PARA DEBUGGING Y ANÁLISIS
    
    def simular_secuencia_velocidades(self, secuencia: List[Dict]) -> bool:
        """
        Simula una secuencia completa de movimientos con velocidades independientes
        INCLUYE CONTROL DE GARRA POR ROTACIÓN DEL EJE 6
        
        Args:
            secuencia: Lista de diccionarios con 'componente', 'valor', 'velocidad'
            
        Returns:
            True si la simulación fue exitosa
        """
        print("🎬 SIMULANDO SECUENCIA CON VELOCIDADES INDEPENDIENTES:")
        print("🔄 Garra controlada por rotación del eje 6")
        
        try:
            for i, paso in enumerate(secuencia):
                componente = paso.get('componente', '')
                valor = paso.get('valor', 0)
                velocidad = paso.get('velocidad', self.delay_actual)
                
                if componente == 'garra':
                    print(f"   Paso {i+1}: {componente} (eje 6) = {valor}° (velocidad: {velocidad}s)")
                else:
                    print(f"   Paso {i+1}: {componente} = {valor}° (velocidad: {velocidad}s)")
                
                # Establecer velocidad independiente
                if not self.establecer_delay(velocidad):
                    print(f"   ❌ Error estableciendo velocidad {velocidad}s")
                    return False
                    
                # Ejecutar movimiento
                if not self.mover_componente(componente, valor):
                    print(f"   ❌ Error ejecutando movimiento {componente} = {valor}")
                    return False
                    
                print(f"   ✅ Paso {i+1} completado")
                
            print("🎉 SECUENCIA COMPLETADA EXITOSAMENTE")
            print(self.obtener_resumen_velocidades())
            return True
            
        except Exception as e:
            print(f"❌ Error en simulación de secuencia: {e}")
            return False
    
    def validar_secuencia_velocidades(self, codigo_robot: str) -> Dict:
        """
        Valida un código de robot para verificar las velocidades independientes
        INCLUYE VALIDACIÓN DE GARRA COMO ROTACIÓN
        
        Args:
            codigo_robot: Código del robot como string
            
        Returns:
            Diccionario con resultado de validación
        """
        print("🔍 VALIDANDO VELOCIDADES INDEPENDIENTES EN CÓDIGO:")
        print("🔄 Validando garra como rotación del eje 6")
        
        resultado = {
            'valido': False,
            'velocidades_encontradas': [],
            'movimientos_encontrados': [],
            'movimientos_garra': [],
            'errores': [],
            'resumen': ''
        }
        
        try:
            lineas = codigo_robot.strip().split('\n')
            velocidad_actual = 5.0  # Por defecto
            
            for i, linea in enumerate(lineas, 1):
                linea = linea.strip()
                if not linea or linea.startswith('#'):
                    continue
                    
                if '.velocidad' in linea:
                    try:
                        partes = linea.split('=')
                        if len(partes) == 2:
                            nueva_velocidad = float(partes[1].strip())
                            if 1 <= nueva_velocidad <= 60:
                                velocidad_actual = nueva_velocidad
                                resultado['velocidades_encontradas'].append({
                                    'linea': i,
                                    'velocidad': nueva_velocidad,
                                    'texto': linea
                                })
                            else:
                                resultado['errores'].append(f"Línea {i}: Velocidad fuera de rango: {nueva_velocidad}")
                    except ValueError:
                        resultado['errores'].append(f"Línea {i}: Valor de velocidad inválido")
                        
                elif '.garra' in linea:
                    try:
                        partes = linea.split('=')
                        if len(partes) == 2:
                            valor = float(partes[1].strip())
                            if 0 <= valor <= 360:  # Rango de rotación
                                resultado['movimientos_garra'].append({
                                    'linea': i,
                                    'valor_rotacion': valor,
                                    'velocidad_asignada': velocidad_actual,
                                    'texto': linea
                                })
                                resultado['movimientos_encontrados'].append({
                                    'linea': i,
                                    'componente': 'garra (eje 6)',
                                    'valor': valor,
                                    'velocidad_asignada': velocidad_actual,
                                    'texto': linea
                                })
                            else:
                                resultado['errores'].append(f"Línea {i}: Rotación de garra fuera de rango: {valor}° (0-360°)")
                    except (ValueError, IndexError):
                        resultado['errores'].append(f"Línea {i}: Sintaxis de garra inválida")
                        
                elif any(comp in linea for comp in ['.base', '.hombro', '.codo']):
                    try:
                        partes = linea.split('=')
                        if len(partes) == 2:
                            valor = float(partes[1].strip())
                            componente = linea.split('.')[1].split('=')[0].strip()
                            resultado['movimientos_encontrados'].append({
                                'linea': i,
                                'componente': componente,
                                'valor': valor,
                                'velocidad_asignada': velocidad_actual,
                                'texto': linea
                            })
                    except (ValueError, IndexError):
                        resultado['errores'].append(f"Línea {i}: Sintaxis de movimiento inválida")
            
            # Generar resumen
            total_velocidades = len(resultado['velocidades_encontradas'])
            total_movimientos = len(resultado['movimientos_encontrados'])
            total_movimientos_garra = len(resultado['movimientos_garra'])
            total_errores = len(resultado['errores'])
            
            resultado['resumen'] = f"""
📊 ANÁLISIS DE VELOCIDADES INDEPENDIENTES:
   ⚡ Cambios de velocidad: {total_velocidades}
   🤖 Movimientos articulaciones: {total_movimientos - total_movimientos_garra}
   🔄 Movimientos garra (eje 6): {total_movimientos_garra}
   📊 Total movimientos: {total_movimientos}
   ❌ Errores encontrados: {total_errores}
   ✅ Código válido: {'Sí' if total_errores == 0 else 'No'}
   🔄 Control de garra: Rotación del eje 6 (0-360°)
"""
            
            resultado['valido'] = total_errores == 0 and total_movimientos > 0
            
            print(resultado['resumen'])
            
            if resultado['movimientos_encontrados']:
                print("🎯 MOVIMIENTOS CON SUS VELOCIDADES:")
                for mov in resultado['movimientos_encontrados']:
                    if 'garra' in mov['componente']:
                        print(f"   Línea {mov['linea']}: {mov['componente']} = {mov['valor']}° (rotación eje 6, velocidad: {mov['velocidad_asignada']}s)")
                    else:
                        print(f"   Línea {mov['linea']}: {mov['componente']} = {mov['valor']}° (velocidad: {mov['velocidad_asignada']}s)")
            
            if resultado['movimientos_garra']:
                print("🔄 MOVIMIENTOS DE GARRA DETECTADOS:")
                for mov_garra in resultado['movimientos_garra']:
                    print(f"   Línea {mov_garra['linea']}: Rotación eje 6 = {mov_garra['valor_rotacion']}° (velocidad: {mov_garra['velocidad_asignada']}s)")
            
            return resultado
            
        except Exception as e:
            resultado['errores'].append(f"Error general en validación: {str(e)}")
            resultado['resumen'] = f"❌ Error durante validación: {str(e)}"
            return resultado
    
    def probar_garra_rotacion(self, rotaciones: List[float], velocidad: float = 3.0) -> bool:
        """
        Función de prueba específica para la garra como rotación del eje 6
        
        Args:
            rotaciones: Lista de ángulos de rotación a probar
            velocidad: Velocidad en segundos para cada movimiento
            
        Returns:
            True si todas las pruebas fueron exitosas
        """
        print("🔄 PROBANDO GARRA COMO ROTACIÓN DEL EJE 6:")
        print(f"   Rotaciones a probar: {rotaciones}")
        print(f"   Velocidad: {velocidad}s por movimiento")
        
        try:
            # Establecer velocidad de prueba
            if not self.establecer_delay(velocidad):
                return False
            
            for i, rotacion in enumerate(rotaciones):
                print(f"\n   🔄 Prueba {i+1}/{len(rotaciones)}: Rotar eje 6 a {rotacion}°")
                
                if not self.mover_componente('garra', rotacion):
                    print(f"   ❌ Error en prueba {i+1}")
                    return False
                    
                print(f"   ✅ Prueba {i+1} completada - Eje 6 en {rotacion}°")
                
                # Pausa entre pruebas
                if i < len(rotaciones) - 1:
                    print(f"   ⏸️ Pausa antes de siguiente prueba...")
                    time.sleep(0.5)
            
            print("\n🎉 TODAS LAS PRUEBAS DE GARRA (EJE 6) COMPLETADAS!")
            print(f"🔄 La garra ahora controla la rotación del eje 6 para efecto visual")
            print(self.obtener_resumen_velocidades())
            
            return True
            
        except Exception as e:
            print(f"❌ Error en pruebas de garra: {e}")
            return False