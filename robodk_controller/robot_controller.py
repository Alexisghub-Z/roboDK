#!/usr/bin/env python3
"""
Controlador para Robot ABB IRB 120-3/0.6 con Garra Robotiq 2F-85
Integración con RoboDK (Compatible con v5.9+)
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
    garra: float = 0.0

@dataclass
class ConfiguracionRobot:
    """Configuración del robot"""
    velocidad_maxima: float = 100.0  # mm/s
    aceleracion_maxima: float = 250.0  # mm/s²
    velocidad_articular: float = 45.0  # deg/s
    precision_movimiento: float = 0.1  # mm

class RobotController:
    """Controlador principal del robot ABB IRB 120 (Compatible RoboDK 5.9+)"""
    
    def __init__(self):
        self.conectado = False
        self.rdk = None
        self.robot = None
        self.garra = None
        
        # Estado actual del robot
        self.posicion_actual = PosicionRobot()
        self.velocidad_actual = 50.0  # Porcentaje
        
        # Configuración
        self.config = ConfiguracionRobot()
        
        # Límites articulares del ABB IRB 120
        self.limites_articulares = {
            'base': (-165, 165),      # Eje 1
            'hombro': (-110, 110),    # Eje 2
            'codo': (-110, 70),       # Eje 3
            'muñeca1': (-160, 160),   # Eje 4
            'muñeca2': (-120, 120),   # Eje 5
            'muñeca3': (-400, 400),   # Eje 6
            'garra': (0, 85)          # Robotiq 2F-85: 0-85mm
        }
        
        # Estado de la garra
        self.garra_abierta = True
        
    def conectar(self) -> bool:
        """
        Conecta con RoboDK y configura el robot (Compatible v5.9+)
        
        Returns:
            True si la conexión fue exitosa
        """
        if not ROBODK_AVAILABLE:
            print("🔄 Iniciando en modo simulación (RoboDK no disponible)")
            self.conectado = True
            return True
            
        try:
            # Conectar con RoboDK
            self.rdk = robolink.Robolink()
            
            # Verificar que RoboDK esté ejecutándose (método compatible)
            try:
                version = self.rdk.Version()
                print(f"✅ RoboDK detectado - Versión: {version}")
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
            
            # Buscar la garra Robotiq
            self.garra = self._configurar_garra()
            
            # Configurar parámetros del robot
            self._configurar_robot()
            
            # Obtener posición actual
            self._actualizar_posicion_actual()
            
            self.conectado = True
            print("✅ Robot conectado exitosamente")
            print(f"📍 Posición actual: {self._posicion_to_string()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error conectando con el robot: {e}")
            return False
    
    def _buscar_robot(self):
        """Busca el robot ABB IRB 120 en la estación (Compatible v5.9+)"""
        try:
            # Lista de nombres posibles para el robot
            nombres_robot = [
                'ABB IRB 120-3/0.6',
                'IRB 120',
                'ABB IRB120',
                'IRB120-3/0.6',
                'Robot'  # Nombre por defecto
            ]
            
            for nombre in nombres_robot:
                try:
                    robot = self.rdk.Item(nombre, robolink.ITEM_TYPE_ROBOT)
                    # Verificar que el robot sea válido intentando obtener su nombre
                    robot_name = robot.Name()
                    print(f"✅ Robot encontrado: {robot_name}")
                    return robot
                except:
                    continue
            
            # Si no se encuentra por nombre, buscar el primer robot disponible
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
                    # Detener movimientos
                    try:
                        self.robot.Stop()
                    except:
                        pass
                    
                self.conectado = False
                self.rdk = None
                self.robot = None
                self.garra = None
                
                print("🔌 Robot desconectado")
                
            except Exception as e:
                print(f"⚠️ Error al desconectar: {e}")
                
    def _configurar_garra(self):
        """Configura la garra Robotiq 2F-85 (Compatible v5.9+)"""
        try:
            # Buscar la garra en la estación
            nombres_garra = ['Robotiq 2F-85', 'Robotiq', '2F-85', 'Gripper', 'Garra']
            
            for nombre in nombres_garra:
                try:
                    garra = self.rdk.Item(nombre, robolink.ITEM_TYPE_TOOL)
                    garra_name = garra.Name()  # Verificar que sea válida
                    
                    # Configurar como herramienta activa
                    self.robot.setTool(garra)
                    print(f"🤖 Garra configurada: {garra_name}")
                    return garra
                except:
                    continue
                    
            print("⚠️ Garra Robotiq no encontrada, usando herramienta por defecto")
            return None
                
        except Exception as e:
            print(f"⚠️ Error configurando garra: {e}")
            return None
            
    def _configurar_robot(self):
        """Configura los parámetros del robot"""
        try:
            if not self.robot:
                return
                
            # Configurar velocidades
            self.robot.setSpeed(self.config.velocidad_maxima)
            self.robot.setAcceleration(self.config.aceleracion_maxima)
            
            # Configurar precisión si el método existe
            try:
                self.robot.setPrecision(self.config.precision_movimiento)
            except:
                pass
            
            print("⚙️ Parámetros del robot configurados")
            
        except Exception as e:
            print(f"⚠️ Error configurando robot: {e}")
            
    def _actualizar_posicion_actual(self):
        """Actualiza la posición actual del robot"""
        try:
            if not self.robot:
                return
                
            # Obtener articulaciones actuales
            joints = self.robot.Joints()
            
            if joints and len(joints) >= 6:
                self.posicion_actual.base = joints[0]
                self.posicion_actual.hombro = joints[1]
                self.posicion_actual.codo = joints[2]
                self.posicion_actual.muñeca1 = joints[3]
                self.posicion_actual.muñeca2 = joints[4]
                self.posicion_actual.muñeca3 = joints[5]
                
        except Exception as e:
            print(f"⚠️ Error obteniendo posición actual: {e}")
            
    def mover_componente(self, componente: str, valor: float) -> bool:
        """
        Mueve un componente específico del robot
        
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
            return self.establecer_velocidad(valor)
        
        # Validar componente
        if componente not in self.limites_articulares:
            print(f"❌ Componente desconocido: {componente}")
            return False
            
        # Validar límites
        min_val, max_val = self.limites_articulares[componente]
        if not (min_val <= valor <= max_val):
            print(f"❌ Valor fuera de rango para {componente}: {valor} (rango: {min_val}-{max_val})")
            return False
            
        try:
            if componente == 'garra':
                return self._mover_garra(valor)
            else:
                return self._mover_articulacion(componente, valor)
                
        except Exception as e:
            print(f"❌ Error moviendo {componente}: {e}")
            return False
            
    def _mover_articulacion(self, componente: str, valor: float) -> bool:
        """Mueve una articulación específica del robot"""
        
        if not ROBODK_AVAILABLE or not self.robot:
            # Modo simulación
            print(f"🔄 [SIMULACIÓN] Moviendo {componente} a {valor}°")
            self._actualizar_posicion_simulada(componente, valor)
            time.sleep(0.5)  # Simular tiempo de movimiento
            return True
            
        try:
            # Obtener articulaciones actuales
            try:
                joints_actuales = self.robot.Joints()
                if not joints_actuales or len(joints_actuales) < 6:
                    # Usar posición home por defecto
                    joints_actuales = [0, 0, 0, 0, 90, 0]
                    print("⚠️ Usando posición home por defecto")
            except:
                # Usar posición home por defecto si falla
                joints_actuales = [0, 0, 0, 0, 90, 0]
                print("⚠️ No se pudieron obtener articulaciones, usando home")
                
            # Crear nueva configuración articular
            joints_objetivo = list(joints_actuales)
            
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
                
            # Actualizar articulación objetivo
            joints_objetivo[indice_articulacion] = valor
            
            # Aplicar velocidad
            velocidad_escalada = (self.velocidad_actual / 100.0) * self.config.velocidad_articular
            self.robot.setSpeed(velocidad_escalada, velocidad_escalada)
            
            # Ejecutar movimiento
            print(f"🔄 Moviendo {componente} de {joints_actuales[indice_articulacion]:.1f}° a {valor:.1f}°")
            
            self.robot.MoveJ(joints_objetivo)
            
            # Actualizar posición interna
            self._actualizar_posicion_simulada(componente, valor)
            
            print(f"✅ {componente} movido a {valor}°")
            return True
            
        except Exception as e:
            print(f"❌ Error en movimiento articular: {e}")
            return False
            
    def _mover_garra(self, apertura_mm: float) -> bool:
        """Mueve la garra Robotiq 2F-85"""
        
        if not ROBODK_AVAILABLE or not self.robot:
            # Modo simulación
            estado = "ABIERTA" if apertura_mm > 42.5 else "CERRADA"
            print(f"🔄 [SIMULACIÓN] Garra {estado} - Apertura: {apertura_mm:.1f}mm")
            self.posicion_actual.garra = apertura_mm
            self.garra_abierta = apertura_mm > 42.5
            time.sleep(0.3)
            return True
            
        try:
            # Para ABB IRB 120, simular garra con un joint extra o como pose
            estado = "ABIERTA" if apertura_mm > 42.5 else "CERRADA"
            
            # Obtener posición actual
            joints_actuales = self.robot.Joints()
            if joints_actuales and len(joints_actuales) >= 6:
                # Crear nueva configuración con "garra" simulada
                joints_con_garra = list(joints_actuales)
                
                # Simular apertura de garra modificando ligeramente la muñeca
                # (esto es solo visual, en robot real sería diferente)
                offset_garra = (apertura_mm - 42.5) * 0.1  # Pequeño offset visual
                joints_con_garra[5] += offset_garra  # Rotación de muñeca
                
                self.robot.MoveJ(joints_con_garra)
            
            print(f"✅ Garra {estado} - Apertura: {apertura_mm:.1f}mm (simulada)")
            
            self.posicion_actual.garra = apertura_mm
            self.garra_abierta = apertura_mm > 42.5
            
            return True
            
        except Exception as e:
            print(f"❌ Error moviendo garra: {e}")
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
            
    def establecer_velocidad(self, velocidad_porcentaje: float) -> bool:
        """Establece la velocidad del robot"""
        if not (1 <= velocidad_porcentaje <= 100):
            print(f"❌ Velocidad fuera de rango: {velocidad_porcentaje}% (rango: 1-100%)")
            return False
            
        self.velocidad_actual = velocidad_porcentaje
        
        if not ROBODK_AVAILABLE or not self.robot:
            print(f"🔄 [SIMULACIÓN] Velocidad establecida: {velocidad_porcentaje}%")
            return True
            
        try:
            velocidad_lineal = (velocidad_porcentaje / 100.0) * self.config.velocidad_maxima
            velocidad_articular = (velocidad_porcentaje / 100.0) * self.config.velocidad_articular
            
            self.robot.setSpeed(velocidad_lineal, velocidad_articular)
            
            print(f"✅ Velocidad establecida: {velocidad_porcentaje}%")
            return True
            
        except Exception as e:
            print(f"❌ Error estableciendo velocidad: {e}")
            return False
            
    def obtener_estado(self) -> Dict:
        """Obtiene el estado completo del robot"""
        return {
            'conectado': self.conectado,
            'posicion': {
                'base': self.posicion_actual.base,
                'hombro': self.posicion_actual.hombro,
                'codo': self.posicion_actual.codo,
                'muñeca1': self.posicion_actual.muñeca1,
                'muñeca2': self.posicion_actual.muñeca2,
                'muñeca3': self.posicion_actual.muñeca3,
                'garra': self.posicion_actual.garra
            },
            'velocidad': self.velocidad_actual,
            'garra_abierta': self.garra_abierta,
            'robodk_disponible': ROBODK_AVAILABLE
        }
        
    def _posicion_to_string(self) -> str:
        """Convierte la posición actual a string legible"""
        return (f"Base: {self.posicion_actual.base:.1f}°, "
                f"Hombro: {self.posicion_actual.hombro:.1f}°, "
                f"Codo: {self.posicion_actual.codo:.1f}°, "
                f"Garra: {self.posicion_actual.garra:.1f}mm")