#!/usr/bin/env python3
"""
Test específico para diagnosticar velocidad y garra
"""

def test_robot_controller():
    """Test directo del controlador"""
    print("🤖 TEST DIRECTO DEL CONTROLADOR")
    print("=" * 40)
    
    try:
        from robodk_controller.robot_controller import RobotController
        
        # Crear controlador
        robot = RobotController()
        
        # Conectar
        print("🔌 Conectando...")
        if not robot.conectar():
            print("❌ No se pudo conectar al robot")
            return False
        
        print("✅ Robot conectado")
        
        # TEST 1: Velocidad
        print("\n⚡ TESTING VELOCIDAD:")
        print("-" * 20)
        
        velocidades_test = [10, 50, 100]
        for vel in velocidades_test:
            print(f"Probando velocidad {vel}%...")
            resultado = robot.establecer_velocidad(vel)
            print(f"   Resultado: {resultado}")
            print(f"   Velocidad actual: {robot.velocidad_actual}%")
            
            # Mover para ver si afecta la velocidad
            print(f"   Moviendo base a 30° con velocidad {vel}%...")
            robot.mover_componente('base', 30)
            
            import time
            time.sleep(2)
            
            print(f"   Moviendo base a 0° con velocidad {vel}%...")
            robot.mover_componente('base', 0)
            time.sleep(2)
        
        # TEST 2: Garra
        print("\n🦾 TESTING GARRA:")
        print("-" * 20)
        
        aperturas_test = [0, 42, 85]
        for apertura in aperturas_test:
            print(f"Probando garra apertura {apertura}mm...")
            resultado = robot.mover_componente('garra', apertura)
            print(f"   Resultado: {resultado}")
            print(f"   Estado garra: {'ABIERTA' if robot.garra_abierta else 'CERRADA'}")
            print(f"   Posición actual: {robot.posicion_actual.garra}mm")
            time.sleep(1)
        
        # Desconectar
        robot.desconectar()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mover_componente():
    """Test de la función mover_componente específicamente"""
    print("\n🔧 TEST FUNCIÓN MOVER_COMPONENTE")
    print("=" * 40)
    
    try:
        from robodk_controller.robot_controller import RobotController
        
        robot = RobotController()
        if not robot.conectar():
            return False
        
        # Test llamadas específicas
        componentes_test = [
            ('velocidad', 20),
            ('base', 45),
            ('garra', 50),
            ('hombro', 30)
        ]
        
        for componente, valor in componentes_test:
            print(f"\n🔄 Llamando: robot.mover_componente('{componente}', {valor})")
            
            # Llamada directa
            resultado = robot.mover_componente(componente, valor)
            
            print(f"   Resultado: {resultado}")
            
            if componente == 'velocidad':
                print(f"   Velocidad interna: {robot.velocidad_actual}%")
            elif componente == 'garra':
                print(f"   Garra posición: {robot.posicion_actual.garra}mm")
                print(f"   Garra estado: {'ABIERTA' if robot.garra_abierta else 'CERRADA'}")
            
            import time
            time.sleep(1)
        
        robot.desconectar()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_robodk_speed():
    """Test directo de velocidad en RoboDK"""
    print("\n🏎️ TEST VELOCIDAD ROBODK DIRECTO")
    print("=" * 40)
    
    try:
        from robodk import robolink
        
        rdk = robolink.Robolink()
        
        # Encontrar robot
        robots = rdk.ItemList(robolink.ITEM_TYPE_ROBOT)
        if not robots:
            print("❌ No hay robots en RoboDK")
            return False
        
        robot = robots[0]
        print(f"✅ Usando robot: {robot.Name()}")
        
        # Test velocidades directas
        velocidades = [10, 100, 500]  # mm/s
        
        for vel in velocidades:
            print(f"\n🔄 Estableciendo velocidad {vel} mm/s en RoboDK...")
            robot.setSpeed(vel)
            
            # Mover para ver diferencia
            joints = [0, 0, 0, 0, 90, 0]
            print("   Moviendo a posición 1...")
            robot.MoveJ(joints)
            
            joints = [30, 0, 0, 0, 90, 0]
            print("   Moviendo a posición 2...")
            robot.MoveJ(joints)
            
            print(f"   ¿Viste diferencia en velocidad? (visual)")
            
            import time
            time.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 DIAGNÓSTICO ESPECÍFICO: VELOCIDAD Y GARRA")
    print("=" * 50)
    
    # Test 1: Controlador completo
    test1 = test_robot_controller()
    
    # Test 2: Función específica
    test2 = test_mover_componente() 
    
    # Test 3: RoboDK directo
    test3 = test_robodk_speed()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADOS:")
    print(f"   Test Controlador: {'✅ OK' if test1 else '❌ FALLO'}")
    print(f"   Test Mover Componente: {'✅ OK' if test2 else '❌ FALLO'}")
    print(f"   Test RoboDK Directo: {'✅ OK' if test3 else '❌ FALLO'}")
    
    print("\n🔍 PREGUNTAS IMPORTANTES:")
    print("1. ¿Viste cambios de velocidad visuales en RoboDK?")
    print("2. ¿La garra (muñeca) se movió al cambiar apertura?")
    print("3. ¿Qué mensajes salieron en cada test?")

if __name__ == "__main__":
    main()