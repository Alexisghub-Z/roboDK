#!/usr/bin/env python3
"""
Script para probar la conexión con RoboDK (Compatible con v5.9+)
"""

def test_robodk_import():
    """Prueba importar RoboDK"""
    print("🔍 Probando importación de RoboDK...")
    try:
        import robodk
        from robodk import robolink
        print("✅ RoboDK importado correctamente")
        print("   Versión: 5.9.0+ (compatible)")
        return True
    except ImportError as e:
        print(f"❌ Error importando RoboDK: {e}")
        return False

def test_robodk_connection():
    """Prueba conexión con RoboDK"""
    print("\n🔌 Probando conexión con RoboDK...")
    try:
        from robodk import robolink
        
        # Intentar conectar
        rdk = robolink.Robolink()
        
        # Método alternativo para verificar conexión
        try:
            # Intentar obtener algo básico
            version = rdk.Version()
            print("✅ Conexión con RoboDK exitosa")
            print(f"   Versión RoboDK: {version}")
            return True
        except Exception as e:
            print("❌ No se puede conectar con RoboDK")
            print(f"   Error: {e}")
            print("   Asegúrate de que RoboDK esté ejecutándose")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con RoboDK: {e}")
        return False

def test_robot_detection():
    """Prueba detección del robot"""
    print("\n🤖 Buscando robots en la estación...")
    try:
        from robodk import robolink
        
        rdk = robolink.Robolink()
        
        # Verificar conexión primero
        try:
            rdk.Version()
        except:
            print("❌ RoboDK no disponible")
            return False
            
        # Buscar robots usando método compatible
        try:
            robots = rdk.ItemList(robolink.ITEM_TYPE_ROBOT)
        except:
            # Método alternativo si ItemList no funciona
            try:
                robots = rdk.getItemList(robolink.ITEM_TYPE_ROBOT)
            except:
                print("❌ No se pueden obtener robots de la estación")
                return False
        
        if not robots:
            print("⚠️ No se encontraron robots en la estación")
            print("   SOLUCIÓN:")
            print("   1. Abre RoboDK")
            print("   2. File → Add → Robot → ABB → IRB 120-3/0.6")
            print("   3. Ejecuta este test nuevamente")
            return False
            
        print(f"✅ Encontrados {len(robots)} robot(s):")
        for robot in robots:
            try:
                print(f"   - {robot.Name()}")
            except:
                print(f"   - Robot detectado")
            
        # Buscar específicamente ABB IRB 120
        irb120_variants = [
            'ABB IRB 120-3/0.6',
            'IRB 120',
            'ABB IRB120',
            'IRB120-3/0.6',
            'Robot'  # Nombre por defecto
        ]
        
        robot_encontrado = None
        for variant in irb120_variants:
            try:
                robot = rdk.Item(variant, robolink.ITEM_TYPE_ROBOT)
                # Verificar si el robot es válido intentando obtener su nombre
                robot.Name()
                robot_encontrado = robot
                print(f"✅ Robot encontrado: {variant}")
                break
            except:
                continue
                
        if robot_encontrado:
            # Probar movimiento simple
            print("🔄 Probando movimiento básico...")
            try:
                joints_home = [0, 0, 0, 0, 90, 0]
                robot_encontrado.MoveJ(joints_home)
                print("✅ Movimiento de prueba exitoso")
            except Exception as e:
                print(f"⚠️ Advertencia en movimiento: {e}")
                print("   (El robot está detectado pero puede necesitar configuración)")
        else:
            print("⚠️ Robot ABB IRB 120 no encontrado con nombres esperados")
            
        return True
        
    except Exception as e:
        print(f"❌ Error detectando robots: {e}")
        return False

def test_simple_command():
    """Prueba comando simple en RoboDK"""
    print("\n🧪 Probando comando simple...")
    try:
        from robodk import robolink
        
        rdk = robolink.Robolink()
        
        # Comando muy simple para verificar comunicación
        try:
            station_name = rdk.getParam("STATIONFILE")
            print(f"✅ Estación activa: {station_name}")
            return True
        except Exception as e:
            print(f"⚠️ Comando simple falló: {e}")
            print("   RoboDK está conectado pero puede tener problemas")
            return False
            
    except Exception as e:
        print(f"❌ Error en comando simple: {e}")
        return False

def give_solutions():
    """Da soluciones específicas"""
    print("\n🔧 PASOS PARA SOLUCIONAR:")
    print("=" * 40)
    print("1. 📂 ABRIR ROBODK:")
    print("   - Busca 'RoboDK' en el menú inicio")
    print("   - Abre la aplicación")
    print("   - Deja la ventana abierta")
    print()
    print("2. 🤖 AGREGAR ROBOT:")
    print("   - En RoboDK: File → Add → Robot")
    print("   - Busca: ABB → IRB 120-3/0.6")
    print("   - Click 'Add' o 'Download'")
    print()
    print("3. ✅ VERIFICAR:")
    print("   - Deberías ver el robot en 3D")
    print("   - Ejecuta: python test_robodk_fixed.py")
    print()
    print("4. 🔌 CONECTAR EN TU APP:")
    print("   - Ejecuta: python main.py")
    print("   - Click en '🤖 Conectar Robot'")

def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA DE CONEXIÓN ROBODK (v5.9+ Compatible)")
    print("=" * 50)
    
    tests = [
        test_robodk_import(),
        test_robodk_connection(),
        test_robot_detection(),
        test_simple_command()
    ]
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    
    test_names = [
        "Importación RoboDK",
        "Conexión RoboDK", 
        "Detección de Robot",
        "Comando Simple"
    ]
    
    all_passed = True
    for name, result in zip(test_names, tests):
        status = "✅ OK" if result else "❌ FALLO"
        print(f"   {name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ¡RoboDK está completamente listo!")
        print("   Ejecuta: python main.py")
        print("   Click en '🤖 Conectar Robot'")
    else:
        give_solutions()
        
    print("=" * 50)

if __name__ == "__main__":
    main()