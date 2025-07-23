#!/usr/bin/env python3
"""
Script para probar la conexión con RoboDK
"""

def test_robodk_import():
    """Prueba importar RoboDK"""
    print("🔍 Probando importación de RoboDK...")
    try:
        import robodk
        print("✅ RoboDK importado correctamente")
        try:
            print(f"   Versión: {robodk.__version__}")
        except AttributeError:
            print("   Versión: 5.9.0+ (detectada)")
        return True
    except ImportError as e:
        print(f"❌ Error importando RoboDK: {e}")
        print("   Solución: pip install robodk")
        return False

def test_robodk_connection():
    """Prueba conexión con RoboDK"""
    print("\n🔌 Probando conexión con RoboDK...")
    try:
        from robodk import robolink
        
        # Intentar conectar
        rdk = robolink.Robolink()
        
        if not rdk.Valid():
            print("❌ No se puede conectar con RoboDK")
            print("   Asegúrate de que RoboDK esté ejecutándose")
            return False
            
        print("✅ Conexión con RoboDK exitosa")
        
        # Obtener información de la estación
        print(f"   Puerto: {rdk.getParam('SERVER_PORT')}")
        print(f"   Versión RoboDK: {rdk.Version()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando con RoboDK: {e}")
        return False

def test_robot_detection():
    """Prueba detección del robot"""
    print("\n🤖 Buscando robots en la estación...")
    try:
        from robodk import robolink
        
        rdk = robolink.Robolink()
        if not rdk.Valid():
            print("❌ RoboDK no disponible")
            return False
            
        # Buscar robots
        robots = rdk.ItemList(robolink.ITEM_TYPE_ROBOT)
        
        if not robots:
            print("⚠️ No se encontraron robots en la estación")
            print("   Agrega un robot ABB IRB 120 en RoboDK:")
            print("   File → Add → Robot → ABB → IRB 120-3/0.6")
            return False
            
        print(f"✅ Encontrados {len(robots)} robot(s):")
        for robot in robots:
            print(f"   - {robot.Name()}")
            
        # Buscar específicamente ABB IRB 120
        irb120_variants = [
            'ABB IRB 120-3/0.6',
            'IRB 120',
            'ABB IRB120',
            'IRB120-3/0.6'
        ]
        
        robot_encontrado = None
        for variant in irb120_variants:
            robot = rdk.Item(variant, robolink.ITEM_TYPE_ROBOT)
            if robot.Valid():
                robot_encontrado = robot
                break
                
        if robot_encontrado:
            print(f"✅ Robot ABB IRB 120 encontrado: {robot_encontrado.Name()}")
            
            # Probar movimiento simple
            print("🔄 Probando movimiento básico...")
            joints_home = [0, 0, 0, 0, 90, 0]
            robot_encontrado.MoveJ(joints_home)
            print("✅ Movimiento de prueba exitoso")
            
        else:
            print("⚠️ Robot ABB IRB 120 no encontrado con nombres esperados")
            print("   Robots disponibles:")
            for robot in robots:
                print(f"   - {robot.Name()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error detectando robots: {e}")
        return False

def test_tools():
    """Prueba detección de herramientas/garra"""
    print("\n🛠️ Buscando herramientas/garra...")
    try:
        from robodk import robolink
        
        rdk = robolink.Robolink()
        if not rdk.Valid():
            return False
            
        # Buscar herramientas
        tools = rdk.ItemList(robolink.ITEM_TYPE_TOOL)
        
        if tools:
            print(f"✅ Encontradas {len(tools)} herramienta(s):")
            for tool in tools:
                print(f"   - {tool.Name()}")
        else:
            print("⚠️ No se encontraron herramientas")
            print("   Opcional: Agregar garra Robotiq en RoboDK")
            
        return True
        
    except Exception as e:
        print(f"❌ Error detectando herramientas: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA DE CONEXIÓN ROBODK")
    print("=" * 40)
    
    tests = [
        test_robodk_import(),
        test_robodk_connection(),
        test_robot_detection(),
        test_tools()
    ]
    
    print("\n" + "=" * 40)
    print("📊 RESUMEN DE PRUEBAS:")
    
    test_names = [
        "Importación RoboDK",
        "Conexión RoboDK", 
        "Detección de Robot",
        "Detección de Herramientas"
    ]
    
    for name, result in zip(test_names, tests):
        status = "✅ OK" if result else "❌ FALLO"
        print(f"   {name}: {status}")
    
    if all(tests[:3]):  # Los primeros 3 son críticos
        print("\n🎉 ¡RoboDK está listo para usar!")
        print("   Tu aplicación debería detectar RoboDK correctamente")
    else:
        print("\n⚠️ Problemas detectados")
        print("\n🔧 SOLUCIONES:")
        print("1. Asegúrate de que RoboDK esté ejecutándose")
        print("2. Instala la API: pip install robodk")
        print("3. Agrega robot ABB IRB 120 en RoboDK")
        
    print("=" * 40)

if __name__ == "__main__":
    main()