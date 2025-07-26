#!/usr/bin/env python3
"""
Controlador para Robot ABB IRB 120-3/0.6 con Garra Robotiq 2F-85 Gripper (Open)
VERSIÓN CON SISTEMA DE DELAY (1-60 segundos por movimiento)
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
    """Controlador principal del robot ABB IRB 120 - SISTEMA DE DELAY"""
    
    def __init__(self):
        self.conectado = False
        self.rdk = None
        self.robot = None
        self.garra = None
        self.garra_real_encontrada = False
        self.tipo_garra = "ninguna"
        
        # Estado actual del robot
        self.posicion_actual = PosicionRobot()
        self.delay_actual = 5.0  # CAMBIO: delay en segundos (1-60)
        
        # Configuración
        self.config = ConfiguracionRobot()
        
        # Límites articulares del ABB IRB 120 - RANGOS CORREGIDOS SEGÚN TABLA
        self.limites_articulares = {
            'base': (0, 360),         # Plataforma base: 0° a 360°
            'hombro': (0, 180),       # Articulación hombro: 0° a 180°
            'codo': (0, 180),         # Articulación codo: 0° a 180°
            'muñeca1': (-160, 160),   # Eje 4 (mantener original)
            'muñeca2': (-120, 120),   # Eje 5 (mantener original)
            'muñeca3': (-400, 400),   # Eje 6 (mantener original)
            'garra': (0, 90),         # Pinza/garra: 0° a 90°
            'velocidad': (1, 60)      # Tiempo de espera: 1 a 60 segundos
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
                self.garra_real_encontrada = False
                self.tipo_garra = "ninguna"
                
                print("🔌 Robot desconectado")
                
            except Exception as e:
                print(f"⚠️ Error al desconectar: {e}")
                
    def _configurar_garra(self):
        """Configura la garra Robotiq 2F-85 Gripper (Open) - DETECCIÓN INTELIGENTE"""
        try:
            # Nombres específicos para Robotiq 2F-85 Gripper (Open)
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
                    garra_name = garra.Name()  # Verificar que sea válida
                    
                    # Configurar como herramienta activa
                    self.robot.setTool(garra)
                    self.garra_real_encontrada = True
                    
                    # Determinar tipo de garra
                    if 'open' in garra_name.lower() or 'gripper' in garra_name.lower():
                        self.tipo_garra = "open"
                        print(f"🎯 ROBOTIQ 2F-85 GRIPPER (OPEN) ENCONTRADA!")
                        print(f"   Nombre: {garra_name}")
                        print(f"   ✅ Garra con DEDOS MÓVILES detectada")
                    elif 'closed' in garra_name.lower():
                        self.tipo_garra = "closed"
                        print(f"🎯 ROBOTIQ CLOSED encontrada: {garra_name}")
                        print(f"   ⚠️ Garra fija - Usando simulación")
                    else:
                        self.tipo_garra = "real"
                        print(f"🎯 Garra Robotiq encontrada: {garra_name}")
                    
                    print(f"   🔧 Configurada como herramienta activa")
                    return garra
                except:
                    continue
                    
            print("⚠️ Garra Robotiq no encontrada")
            print("💡 Para garra realista:")
            print("   1. En RoboDK: File → Add → Tool")
            print("   2. Buscar: Robotiq → 2F-85 Gripper (Open)")
            print("   3. Attach to robot")
            print("🔧 Usando simulación MEGA-VISIBLE como fallback")
            self.tipo_garra = "ninguna"
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
        """Actualiza la posición actual del robot AL CONECTAR"""
        try:
            if not self.robot:
                # Inicializar en posición home si no hay robot
                self.posicion_actual.base = 0.0
                self.posicion_actual.hombro = 0.0
                self.posicion_actual.codo = 0.0
                self.posicion_actual.muñeca1 = 0.0
                self.posicion_actual.muñeca2 = 90.0  # Muñeca 2 típicamente empieza en 90°
                self.posicion_actual.muñeca3 = 0.0
                return
                
            # Obtener articulaciones actuales del robot real SOLO AL CONECTAR
            try:
                joints = self.robot.Joints()
                
                if joints and len(joints) >= 6:
                    self.posicion_actual.base = joints[0]
                    self.posicion_actual.hombro = joints[1]
                    self.posicion_actual.codo = joints[2]
                    self.posicion_actual.muñeca1 = joints[3]
                    self.posicion_actual.muñeca2 = joints[4]
                    self.posicion_actual.muñeca3 = joints[5]
                    print(f"📍 Posición inicial del robot:")
                    print(f"   Base: {joints[0]:.1f}°, Hombro: {joints[1]:.1f}°, Codo: {joints[2]:.1f}°")
                else:
                    # Si no puede leer joints, usar posición home
                    self.posicion_actual.base = 0.0
                    self.posicion_actual.hombro = 0.0
                    self.posicion_actual.codo = 0.0
                    self.posicion_actual.muñeca1 = 0.0
                    self.posicion_actual.muñeca2 = 90.0
                    self.posicion_actual.muñeca3 = 0.0
                    print(f"📍 Usando posición home como inicial")
                    
            except Exception as e:
                # Si hay error leyendo joints, usar posición home
                self.posicion_actual.base = 0.0
                self.posicion_actual.hombro = 0.0
                self.posicion_actual.codo = 0.0
                self.posicion_actual.muñeca1 = 0.0
                self.posicion_actual.muñeca2 = 90.0
                self.posicion_actual.muñeca3 = 0.0
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
            
    def mover_componente(self, componente: str, valor: float) -> bool:
        """
        Mueve un componente específico del robot CON VALIDACIONES SEGÚN TABLA
        
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
        
        # Manejar velocidad como caso especial - AHORA ES DELAY
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
            # Mensajes específicos según la tabla
            if componente == 'base':
                print(f"❌ Base fuera de rango: {valor}° (rango permitido: 0° a 360°)")
                print(f"   La plataforma base puede rotar de 0° a 360°")
            elif componente == 'hombro':
                print(f"❌ Hombro fuera de rango: {valor}° (rango permitido: 0° a 180°)")
                print(f"   La articulación del hombro se mueve de 0° a 180°")
            elif componente == 'codo':
                print(f"❌ Codo fuera de rango: {valor}° (rango permitido: 0° a 180°)")
                print(f"   La articulación del codo se mueve de 0° a 180°")
            elif componente == 'garra':
                print(f"❌ Garra fuera de rango: {valor}° (rango permitido: 0° a 90°)")
                print(f"   La pinza/garra se abre de 0° (cerrada) a 90° (abierta)")
            elif componente == 'velocidad':
                print(f"❌ Velocidad fuera de rango: {valor}s (rango permitido: 1 a 60 segundos)")
                print(f"   El tiempo de espera debe estar entre 1 y 60 segundos")
            else:
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
        """Mueve una articulación específica del robot MANTENIENDO POSICIONES ANTERIORES"""
        
        if not ROBODK_AVAILABLE or not self.robot:
            # Modo simulación
            print(f"🔄 [SIMULACIÓN] Moviendo {componente} a {valor}° (tiempo: {self.delay_actual}s)")
            self._actualizar_posicion_simulada(componente, valor)
            time.sleep(self.delay_actual)
            return True
            
        try:
            # USAR POSICIÓN INTERNA ACUMULATIVA EN LUGAR DE POSICIÓN REAL DEL ROBOT
            # Esto mantiene todas las posiciones anteriores
            joints_objetivo = [
                self.posicion_actual.base,      # Eje 1: Base
                self.posicion_actual.hombro,    # Eje 2: Hombro  
                self.posicion_actual.codo,      # Eje 3: Codo
                self.posicion_actual.muñeca1,   # Eje 4: Muñeca 1
                self.posicion_actual.muñeca2,   # Eje 5: Muñeca 2
                self.posicion_actual.muñeca3    # Eje 6: Muñeca 3
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
            
            # CALCULAR VELOCIDAD BASADA EN DISTANCIA Y TIEMPO DESEADO
            distancia_grados = abs(valor - valor_actual)
            
            print(f"🔄 Moviendo {componente} de {valor_actual:.1f}° a {valor:.1f}°")
            print(f"   📏 Distancia: {distancia_grados:.1f}°")
            print(f"   ⏱️ Tiempo objetivo: {self.delay_actual}s")
            print(f"   🎯 Posición completa: Base={joints_objetivo[0]:.1f}°, Hombro={joints_objetivo[1]:.1f}°, Codo={joints_objetivo[2]:.1f}°")
            
            if distancia_grados < 0.1:  # Movimiento muy pequeño
                print(f"✅ {componente} ya está muy cerca de {valor}° - movimiento completado")
                self._actualizar_posicion_simulada(componente, valor)
                return True
            
            # Calcular velocidad necesaria: distancia / tiempo = velocidad
            velocidad_necesaria = distancia_grados / self.delay_actual
            
            # Aplicar límites de velocidad (muy importante para seguridad)
            velocidad_min = 1.0   # °/s mínima
            velocidad_max = 150.0 # °/s máxima
            velocidad_necesaria = max(velocidad_min, min(velocidad_max, velocidad_necesaria))
            
            # Configurar velocidad del robot
            self.robot.setSpeed(velocidad_necesaria, velocidad_necesaria)
            
            print(f"   🚀 Velocidad calculada: {velocidad_necesaria:.1f}°/s")
            
            # Ejecutar movimiento CON TODAS LAS POSICIONES ACUMULADAS
            inicio_tiempo = time.time()
            self.robot.MoveJ(joints_objetivo)
            tiempo_real = time.time() - inicio_tiempo
            
            print(f"✅ {componente} movido a {valor}° (tiempo real: {tiempo_real:.1f}s)")
            print(f"   📍 Robot mantiene: Base={joints_objetivo[0]:.1f}°, Hombro={joints_objetivo[1]:.1f}°, Codo={joints_objetivo[2]:.1f}°")
            
            # Actualizar posición interna SIEMPRE
            self._actualizar_posicion_simulada(componente, valor)
            
            return True
            
        except Exception as e:
            print(f"❌ Error en movimiento articular: {e}")
            return False
    
    def _calcular_velocidad_por_delay(self, delay_segundos: float) -> float:
        """Calcula la velocidad del robot basada en el delay deseado"""
        # Mapear delay (1-60s) a velocidad (5-100°/s)
        # delay = 1s -> velocidad rápida (100°/s)
        # delay = 60s -> velocidad lenta (5°/s)
        
        velocidad_min = 5.0   # °/s para delay máximo
        velocidad_max = 100.0 # °/s para delay mínimo
        
        # Mapeo inverso: menor delay = mayor velocidad
        factor = (60.0 - delay_segundos) / (60.0 - 1.0)  # 0 a 1
        velocidad = velocidad_min + (velocidad_max - velocidad_min) * factor
        
        return max(velocidad_min, min(velocidad_max, velocidad))
            
    def _mover_garra(self, apertura_grados: float) -> bool:
        """Mueve la garra Robotiq 2F-85 Gripper MANTENIENDO POSICIONES DEL ROBOT"""
        
        if not ROBODK_AVAILABLE or not self.robot:
            # Modo simulación
            estado = "ABIERTA" if apertura_grados > 45 else "CERRADA"
            print(f"🔄 [SIMULACIÓN] Garra {estado} - Apertura: {apertura_grados:.1f}° (tiempo: {self.delay_actual}s)")
            self.posicion_actual.garra = apertura_grados
            self.garra_abierta = apertura_grados > 45
            time.sleep(self.delay_actual)
            return True
            
        try:
            estado = "ABIERTA" if apertura_grados > 45 else "CERRADA"
            
            print(f"🤏 ROBOTIQ 2F-85 GRIPPER (OPEN)")
            print(f"   Objetivo: {apertura_grados:.1f}° -> {estado}")
            print(f"   ⏱️ Tiempo objetivo: {self.delay_actual}s")
            
            # MÉTODO REAL: Digital Output con control de tiempo
            if self.garra_real_encontrada and self.garra:
                print(f"   🎯 Ejecutando comando de garra...")
                
                try:
                    print(f"      🔧 Método: Digital Output con tiempo controlado")
                    
                    # Usar salidas digitales para controlar garra
                    # Convertir grados (0-90°) a comando apropiado
                    if apertura_grados < 45:  # Cerrar (0° a 44°)
                        comando_do = "SetDO(1,1)"  # DO1 = cerrar
                        print(f"         Comando: {comando_do} (grados: {apertura_grados:.1f}°)")
                        self.garra.RunInstruction(comando_do, robolink.INSTRUCTION_CALL_PROGRAM)
                    else:  # Abrir (45° a 90°)
                        comando_do = "SetDO(1,0)"  # DO1 = abrir
                        print(f"         Comando: {comando_do} (grados: {apertura_grados:.1f}°)")
                        self.garra.RunInstruction(comando_do, robolink.INSTRUCTION_CALL_PROGRAM)
                    
                    # ESPERAR EL TIEMPO ESPECIFICADO
                    print(f"         ⏳ Esperando {self.delay_actual}s para completar movimiento...")
                    time.sleep(self.delay_actual)
                    
                    print(f"✅ GARRA REAL {estado} (tiempo: {self.delay_actual}s)")
                    self.posicion_actual.garra = apertura_grados
                    self.garra_abierta = apertura_grados > 45
                    return True
                    
                except Exception as e1:
                    print(f"      ⚠️ Método DO falló: {e1}")
            
            # ESTRATEGIA FINAL: SIMULACIÓN VISUAL MANTENIENDO POSICIONES DEL ROBOT
            print(f"   🎬 SIMULACIÓN VISUAL MANTENIENDO POSICIONES")
            
            # USAR POSICIÓN INTERNA ACUMULATIVA PARA MANTENER TODAS LAS ARTICULACIONES
            joints_con_garra = [
                self.posicion_actual.base,      # Mantener base actual
                self.posicion_actual.hombro,    # Mantener hombro actual  
                self.posicion_actual.codo,      # Mantener codo actual
                self.posicion_actual.muñeca1,   # Mantener muñeca 1
                self.posicion_actual.muñeca2,   # Mantener muñeca 2
                self.posicion_actual.muñeca3    # Mantener muñeca 3
            ]
            
            # Convertir grados de garra (0-90°) a factor (-1 a +1)
            factor_apertura = (apertura_grados - 45.0) / 45.0  # 0°=-1, 45°=0, 90°=+1
            
            # APLICAR EFECTO VISUAL A LAS MUÑECAS (sin afectar otras articulaciones)
            angulo_muneca3_original = joints_con_garra[5]
            angulo_muneca2_original = joints_con_garra[4]
            angulo_muneca1_original = joints_con_garra[3]
            
            # Aplicar efectos dramáticos solo a las muñecas
            joints_con_garra[5] = angulo_muneca3_original + (factor_apertura * 170.0)  # ±170°
            joints_con_garra[4] = angulo_muneca2_original + (factor_apertura * 80.0)   # ±80°
            joints_con_garra[3] = angulo_muneca1_original + (factor_apertura * 50.0)   # ±50°
            
            # CALCULAR VELOCIDAD BASADA EN DISTANCIA Y TIEMPO
            distancia_muneca3 = abs(joints_con_garra[5] - angulo_muneca3_original)
            distancia_muneca2 = abs(joints_con_garra[4] - angulo_muneca2_original)
            distancia_muneca1 = abs(joints_con_garra[3] - angulo_muneca1_original)
            
            # Usar la mayor distancia para calcular velocidad
            distancia_maxima = max(distancia_muneca3, distancia_muneca2, distancia_muneca1)
            
            if distancia_maxima < 0.1:
                print(f"✅ Garra ya está en posición {estado}")
                self._actualizar_posicion_simulada('garra', apertura_grados)
                return True
            
            # Calcular velocidad: distancia / tiempo = velocidad
            velocidad_garra = distancia_maxima / self.delay_actual
            velocidad_garra = max(1.0, min(150.0, velocidad_garra))  # Límites de seguridad
            
            self.robot.setSpeed(velocidad_garra, velocidad_garra)
            
            print(f"      🎭 Movimiento controlado manteniendo posiciones:")
            print(f"         Base: {joints_con_garra[0]:.1f}°, Hombro: {joints_con_garra[1]:.1f}°, Codo: {joints_con_garra[2]:.1f}°")
            print(f"         Apertura: {apertura_grados:.1f}° (0°=cerrada, 90°=abierta)")
            print(f"         Velocidad calculada: {velocidad_garra:.1f}°/s")
            
            # Ejecutar movimiento principal
            inicio_tiempo = time.time()
            self.robot.MoveJ(joints_con_garra)
            tiempo_real = time.time() - inicio_tiempo
            
            print(f"✅ GARRA SIMULADA {estado} (tiempo real: {tiempo_real:.1f}s)")
            print(f"   📍 Robot mantiene todas sus posiciones anteriores")
            
            self.posicion_actual.garra = apertura_grados
            self.garra_abierta = apertura_grados > 45
            
            return True
            
        except Exception as e:
            print(f"❌ Error crítico: {e}")
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
            
    def establecer_delay(self, delay_segundos: float) -> bool:
        """Establece el delay del robot (ANTES ERA establecer_velocidad)"""
        if not (1 <= delay_segundos <= 60):
            print(f"❌ Delay fuera de rango: {delay_segundos}s (rango: 1-60s)")
            return False
            
        self.delay_actual = delay_segundos
        
        if not ROBODK_AVAILABLE or not self.robot:
            print(f"🔄 [SIMULACIÓN] Delay establecido: {delay_segundos}s")
            return True
            
        try:
            # Calcular velocidad basada en delay
            velocidad_calculada = self._calcular_velocidad_por_delay(delay_segundos)
            
            self.robot.setSpeed(velocidad_calculada, velocidad_calculada)
            
            print(f"✅ Delay establecido: {delay_segundos}s (velocidad: {velocidad_calculada:.1f}°/s)")
            return True
            
        except Exception as e:
            print(f"❌ Error estableciendo delay: {e}")
            return False
            
    def obtener_estado(self) -> Dict:
        """Obtiene el estado completo del robot"""
        return {
            'conectado': self.conectado,
            'garra_real': self.garra_real_encontrada,
            'tipo_garra': self.tipo_garra,
            'posicion': {
                'base': self.posicion_actual.base,
                'hombro': self.posicion_actual.hombro,
                'codo': self.posicion_actual.codo,
                'muñeca1': self.posicion_actual.muñeca1,
                'muñeca2': self.posicion_actual.muñeca2,
                'muñeca3': self.posicion_actual.muñeca3,
                'garra': self.posicion_actual.garra
            },
            'delay': self.delay_actual,  # CAMBIO: delay en lugar de velocidad
            'garra_abierta': self.garra_abierta,
            'robodk_disponible': ROBODK_AVAILABLE
        }
        
    def _posicion_to_string(self) -> str:
        """Convierte la posición actual a string legible"""
        if self.tipo_garra == "open":
            garra_tipo = "ROBOTIQ 2F-85 GRIPPER (OPEN) - REAL"
        elif self.tipo_garra == "closed":
            garra_tipo = "ROBOTIQ CLOSED"
        else:
            garra_tipo = "SIMULADA MEGA-VISIBLE"
            
        return (f"Base: {self.posicion_actual.base:.1f}°, "
                f"Hombro: {self.posicion_actual.hombro:.1f}°, "
                f"Codo: {self.posicion_actual.codo:.1f}°, "
                f"Garra {garra_tipo}: {self.posicion_actual.garra:.1f}mm, "
                f"Delay: {self.delay_actual:.1f}s")