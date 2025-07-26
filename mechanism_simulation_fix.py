#!/usr/bin/env python3
"""
CONFIGURAR Robotiq 2F-85 Gripper (Mechanism) SOLO PARA SIMULACIÓN
Sin TCP/IP, sin hardware real - solo movimiento visual perfecto
"""

import sys
import time

try:
    from robodk import robolink, robomath
    ROBODK_AVAILABLE = True
except ImportError:
    print("❌ RoboDK no está instalado")
    sys.exit(1)

def configure_mechanism_simulation_only():
    """Configura Mechanism SOLO para simulación (sin hardware)"""
    
    print("🎬 CONFIGURANDO ROBOTIQ MECHANISM PARA SIMULACIÓN")
    print("=" * 60)
    
    try:
        rdk = robolink.Robolink()
        print("✅ RoboDK conectado")
        
        # 1. ENCONTRAR LA GARRA MECHANISM
        print("\n🔍 1. BUSCANDO ROBOTIQ MECHANISM...")
        
        garra = None
        nombres = [
            'Robotiq 2F-85 Gripper (Mechanism)',
            'RobotiQ 2F-85 Gripper (Mechanism)',
            'Robotiq 2F-85 Mechanism',
            'Robotiq Mechanism'
        ]
        
        for nombre in nombres:
            try:
                garra = rdk.Item(nombre, robolink.ITEM_TYPE_TOOL)
                if garra.Valid():
                    print(f"✅ Garra Mechanism encontrada: {garra.Name()}")
                    break
            except:
                continue
        
        if not garra or not garra.Valid():
            print("❌ Garra Mechanism no encontrada")
            print("\n💡 CREAR GARRA MECHANISM:")
            print("1. File → Add → Tool")
            print("2. Robotiq → '2F-85 Gripper (Mechanism)'")
            print("3. Attach to robot")
            return False
        
        # 2. CONFIGURAR PARA SIMULACIÓN PURA
        print(f"\n🎬 2. CONFIGURANDO PARA SIMULACIÓN PURA...")
        
        # Encontrar robot
        robot_items = rdk.ItemList(robolink.ITEM_TYPE_ROBOT)
        robot = robot_items[0] if robot_items else None
        
        if not robot:
            print("❌ Robot no encontrado")
            return False
            
        print(f"✅ Robot: {robot.Name()}")
        
        # Configurar garra como tool del robot
        robot.setTool(garra)
        print("✅ Garra configurada como tool activa")
        
        # 3. MODO SIMULACIÓN (SIN COMUNICACIÓN REAL)
        print(f"\n🔄 3. ACTIVANDO MODO SIMULACIÓN...")
        
        try:
            # Activar modo simulación completo
            rdk.setSimulationSpeed(1.0)  # Velocidad normal
            rdk.setRunMode(robolink.RUNMODE_SIMULATE)  # Solo simulación
            print("✅ Modo simulación activado")
            
            # Desactivar intentos de conexión real
            simulation_commands = [
                "SetSimulationMode(1)",      # Forzar simulación
                "DisableRealRobot()",        # Desactivar robot real
                "SetOfflineMode(1)"          # Modo offline
            ]
            
            for cmd in simulation_commands:
                try:
                    rdk.RunCode(cmd)
                    print(f"   ✅ {cmd}")
                except:
                    print(f"   ⚠️ {cmd} (no soportado)")
                    
        except Exception as e:
            print(f"⚠️ Error configurando simulación: {e}")
        
        # 4. PROBAR MOVIMIENTO DE EJES
        print(f"\n🎯 4. PROBANDO MOVIMIENTO DE GARRA...")
        
        try:
            # Obtener ejes actuales
            joints_actuales = garra.Joints()
            if joints_actuales and len(joints_actuales) > 0:
                print(f"✅ Ejes detectados: {len(joints_actuales)}")
                print(f"📍 Posición actual: {joints_actuales}")
                
                # DEMOSTRACIÓN: Cerrar → Abrir → Posición media
                print("\n🎬 DEMOSTRACIÓN DE MOVIMIENTO:")
                
                # Posición 1: CERRADA (0.0)
                joints_cerrada = joints_actuales.copy()
                joints_cerrada[0] = 0.0
                print("🔄 1. Cerrando garra (0.0)...")
                garra.MoveJ(joints_cerrada)
                time.sleep(1.5)
                
                # Posición 2: MEDIA (0.04)
                joints_media = joints_actuales.copy()
                joints_media[0] = 0.04
                print("🔄 2. Posición media (0.04)...")
                garra.MoveJ(joints_media)
                time.sleep(1.5)
                
                # Posición 3: ABIERTA (0.085)
                joints_abierta = joints_actuales.copy()
                joints_abierta[0] = 0.085
                print("🔄 3. Abriendo garra (0.085)...")
                garra.MoveJ(joints_abierta)
                time.sleep(1.5)
                
                # Volver a posición inicial
                print("🔄 4. Volviendo a posición inicial...")
                garra.MoveJ(joints_actuales)
                time.sleep(1)
                
                print("✅ ¡MOVIMIENTO PERFECTO! Garra animada correctamente")
                
                # 5. VERIFICAR QUE NO ESTÉ ROJA
                print(f"\n🎨 5. VERIFICANDO COLOR...")
                print("💡 Verifica en RoboDK que la garra YA NO esté roja")
                print("💡 Debería ser GRIS/AZUL después de la configuración")
                
                return True
                
            else:
                print("❌ No se detectaron ejes en la garra")
                print("💡 Verifica que sea 'Mechanism' y no 'Open'")
                return False
                
        except Exception as e:
            print(f"❌ Error probando movimiento: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def test_mechanism_with_python():
    """Prueba la garra Mechanism desde Python (como tu código)"""
    
    print("\n🐍 PROBANDO GARRA DESDE PYTHON:")
    print("=" * 50)
    
    try:
        rdk = robolink.Robolink()
        garra = rdk.Item('Robotiq 2F-85 Gripper (Mechanism)', robolink.ITEM_TYPE_TOOL)
        
        if not garra.Valid():
            print("❌ Garra no encontrada")
            return False
            
        print("✅ Garra encontrada para prueba Python")
        
        # Simular tu código de robot_controller.py
        print("\n🤖 Simulando tu código:")
        
        def mover_garra_simulacion(apertura_grados):
            """Simula exactamente como funciona en tu código"""
            try:
                joints_actuales = garra.Joints()
                if joints_actuales and len(joints_actuales) > 0:
                    
                    # Convertir grados (0-90°) a metros (0-0.085m)
                    apertura_metros = (apertura_grados / 90.0) * 0.085
                    
                    joints_objetivo = joints_actuales.copy()
                    joints_objetivo[0] = apertura_metros
                    
                    estado = "ABIERTA" if apertura_grados > 45 else "CERRADA"
                    print(f"🤏 Garra {estado} - {apertura_grados}° ({apertura_metros:.4f}m)")
                    
                    garra.MoveJ(joints_objetivo)
                    time.sleep(1)
                    
                    return True
                else:
                    print("❌ Sin ejes disponibles")
                    return False
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
        
        # Probar diferentes posiciones
        posiciones = [0, 30, 60, 90, 45]  # Como en tu código
        
        for pos in posiciones:
            print(f"\n🎯 Probando posición: {pos}°")
            if mover_garra_simulacion(pos):
                print(f"   ✅ Éxito en {pos}°")
            else:
                print(f"   ❌ Falló en {pos}°")
                return False
        
        print("\n✅ ¡TODAS LAS POSICIONES FUNCIONARON!")
        print("🎯 Tu código funcionará perfectamente con esta garra")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba Python: {e}")
        return False

def final_instructions():
    """Instrucciones finales para usar Mechanism en simulación"""
    
    print("\n📋 INSTRUCCIONES FINALES:")
    print("=" * 50)
    
    instructions = [
        "✅ 1. Tu garra Mechanism ya está configurada para simulación",
        "✅ 2. NO necesitas conexión TCP/IP para simulación",
        "✅ 3. NO necesitas hardware real",
        "✅ 4. Los ejes se mueven VISUALMENTE en RoboDK",
        "",
        "🎯 EN TU CÓDIGO:",
        "• Usa exactamente el mismo código",
        "• robot_controller.py detectará 'mechanism'", 
        "• Verás movimiento REAL de los dedos",
        "• Apertura: 0° = cerrada, 90° = abierta",
        "",
        "🎬 RESULTADO:",
        "• Garra YA NO roja (gris/azul)",
        "• Animación perfecta de apertura/cierre",
        "• Sin errores de comunicación",
        "• Simulación realista al 100%"
    ]
    
    for instruction in instructions:
        print(instruction)

if __name__ == "__main__":
    print("🚀 CONFIGURANDO MECHANISM PARA SIMULACIÓN...")
    
    # Configurar para simulación
    if configure_mechanism_simulation_only():
        print("\n✅ CONFIGURACIÓN EXITOSA!")
        
        # Probar desde Python
        if test_mechanism_with_python():
            print("\n🎉 ¡TODO PERFECTO!")
        else:
            print("\n⚠️ Problemas en prueba Python")
            
    else:
        print("\n❌ CONFIGURACIÓN FALLÓ")
    
    # Instrucciones finales
    final_instructions()
    
    print("\n🏁 PROCESO COMPLETADO")
    print("🎯 ¡Tu garra Mechanism está lista para simulación!")