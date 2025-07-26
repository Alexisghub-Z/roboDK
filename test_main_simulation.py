#!/usr/bin/env python3
"""
Test que simula exactamente lo que hace la aplicación principal
"""

def test_flujo_completo():
    """Test del flujo completo como en main.py"""
    print("🔄 SIMULANDO FLUJO COMPLETO DE MAIN.PY")
    print("=" * 50)
    
    # Código de prueba
    codigo = """Robot INSPECTOR
INSPECTOR.velocidad = 20
INSPECTOR.repetir = 3 {
    INSPECTOR.base = 90
    INSPECTOR.garra = 0
    INSPECTOR.base = 0
    INSPECTOR.garra = 85
}"""
    
    print("📝 Código a procesar:")
    print(codigo)
    print()
    
    try:
        # PASO 1: Analizador léxico (como en main.py)
        print("🔍 PASO 1: ANÁLISIS LÉXICO")
        print("-" * 30)
        
        from analizador.analizador_lexico import AnalizadorLexico
        analizador = AnalizadorLexico()
        
        resultado = analizador.analizar(codigo)
        
        print(f"✅ Análisis exitoso: {resultado['exito']}")
        print(f"📊 Cuádruplos generados: {len(resultado['cuadruplos'])}")
        print(f"❌ Errores: {len(resultado['errores'])}")
        
        if not resultado['exito']:
            print("❌ Análisis falló, no se puede continuar")
            for error in resultado['errores']:
                print(f"   Error: {error}")
            return False
        
        # Mostrar cuádruplos generados
        print("\n🔧 CUÁDRUPLOS GENERADOS:")
        for i, cuad in enumerate(resultado['cuadruplos']):
            print(f"  {i:2d}: {cuad['operador']:12s} | {cuad['operando1']:12s} | {cuad['operando2']:12s} | {cuad['resultado']:12s}")
        
        # PASO 2: Conectar robot (como en main.py)
        print(f"\n🤖 PASO 2: CONEXIÓN DEL ROBOT")
        print("-" * 30)
        
        from robodk_controller.robot_controller import RobotController
        robot = RobotController()
        
        if not robot.conectar():
            print("❌ No se pudo conectar al robot")
            return False
        
        print("✅ Robot conectado")
        
        # PASO 3: Ejecutar cuádruplos (como en main.py)
        print(f"\n⚡ PASO 3: EJECUCIÓN DE CUÁDRUPLOS")
        print("-" * 30)
        
        # Simular exactamente lo que hace AnalysisThread
        _ejecutar_cuadruplos_como_main(resultado['cuadruplos'], robot)
        
        robot.desconectar()
        return True
        
    except Exception as e:
        print(f"❌ Error en flujo completo: {e}")
        import traceback
        traceback.print_exc()
        return False

def _ejecutar_cuadruplos_como_main(cuadruplos, robot):
    """Ejecuta cuádruplos exactamente como lo hace main.py"""
    
    # Verificar si hay cuádruplos con bucles
    begin_loops = [i for i, c in enumerate(cuadruplos) if c['operador'] == 'BEGIN_LOOP']
    velocidad_cmds = [c for c in cuadruplos if c['operador'] == 'CALL' and c['resultado'] == 'velocidad']
    
    print(f"🔍 Análisis de cuádruplos:")
    print(f"   Total cuádruplos: {len(cuadruplos)}")
    print(f"   BEGIN_LOOP encontrados: {len(begin_loops)}")
    print(f"   Comandos de velocidad: {len(velocidad_cmds)}")
    
    # PRIMERO: Aplicar configuraciones (velocidad) antes que movimientos
    print("\n🔧 Aplicando configuraciones iniciales...")
    for cuadruplo in cuadruplos:
        if cuadruplo['operador'] == 'CALL' and cuadruplo['resultado'] == 'velocidad':
            velocidad = int(cuadruplo['operando2'])
            print(f"⚡ Aplicando velocidad: {velocidad}%")
            
            # Llamada directa como en main.py
            resultado_vel = robot.mover_componente('velocidad', velocidad)
            print(f"   Resultado velocidad: {resultado_vel}")
            print(f"   Velocidad interna robot: {robot.velocidad_actual}%")
            
            import time
            time.sleep(0.5)  # Dar tiempo para que se aplique
    
    # SEGUNDO: Ejecutar movimientos y bucles
    print("\n🔄 Ejecutando movimientos...")
    i = 0
    while i < len(cuadruplos):
        cuadruplo = cuadruplos[i]
        
        if cuadruplo['operador'] == 'BEGIN_LOOP':
            # Encontrar el bucle completo
            repeticiones = int(cuadruplo['operando1'])
            loop_id = cuadruplo['resultado']
            
            print(f"\n🔁 BUCLE DETECTADO: {loop_id} con {repeticiones} repeticiones")
            
            # Encontrar comandos del bucle (entre BEGIN_LOOP y END_LOOP)
            comandos_bucle = []
            j = i + 1
            while j < len(cuadruplos):
                if cuadruplos[j]['operador'] == 'END_LOOP':
                    print(f"   END_LOOP encontrado en posición {j}")
                    break
                elif cuadruplos[j]['operador'] == 'CALL' and cuadruplos[j]['resultado'] != 'velocidad':
                    comandos_bucle.append(cuadruplos[j])
                    print(f"   Comando en bucle: {cuadruplos[j]['resultado']} = {cuadruplos[j]['operando2']}")
                j += 1
            
            print(f"   📋 Total comandos en bucle: {len(comandos_bucle)}")
            
            # EJECUTAR EL BUCLE COMPLETO
            for rep in range(repeticiones):
                print(f"\n   🔄 === REPETICIÓN {rep + 1}/{repeticiones} ===")
                for cmd_idx, cmd in enumerate(comandos_bucle):
                    print(f"      Ejecutando {cmd_idx + 1}: {cmd['resultado']} = {cmd['operando2']}")
                    
                    # Llamada exacta como en main.py
                    resultado_cmd = robot.mover_componente(cmd['resultado'], int(cmd['operando2']))
                    print(f"         Resultado: {resultado_cmd}")
                    
                    # Pausa entre comandos
                    import time
                    time.sleep(1.0)  # Pausa más larga para ver mejor
                
                # Pausa entre repeticiones (excepto la última)
                if rep < repeticiones - 1:
                    print(f"   ⏸️ Pausa entre repeticiones... (faltan {repeticiones - rep - 1})")
                    time.sleep(2.0)  # Pausa más larga
                else:
                    print(f"   ✅ Última repetición completada")
            
            print(f"\n✅ BUCLE {loop_id} COMPLETADO - {repeticiones} repeticiones ejecutadas")
            
            # Saltar hasta después del END_LOOP
            i = j + 1
            
        elif cuadruplo['operador'] == 'CALL' and cuadruplo['resultado'] != 'velocidad':
            # Comando normal (fuera de bucle) que NO sea velocidad
            print(f"\n🤖 Comando individual: {cuadruplo['resultado']} = {cuadruplo['operando2']}")
            resultado_cmd = robot.mover_componente(cuadruplo['resultado'], int(cuadruplo['operando2']))
            print(f"   Resultado: {resultado_cmd}")
            i += 1
        else:
            # Otros tipos de cuádruplos (CREATE, =, ASSOC, velocidad ya procesada, etc.)
            i += 1

def verificar_archivo_interfaz():
    """Verificar que el archivo de interfaz tenga los cambios"""
    print("\n🔍 VERIFICANDO ARCHIVO DE INTERFAZ")
    print("=" * 40)
    
    try:
        with open('interfaz/ventana_principal.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar funciones clave
        tiene_ejecutar_cuadruplos = '_ejecutar_cuadruplos_en_robot' in contenido
        tiene_begin_loop = 'BEGIN_LOOP' in contenido
        tiene_velocidad_primero = 'Aplicando configuraciones iniciales' in contenido
        
        print(f"✅ Archivo encontrado")
        print(f"✅ Función _ejecutar_cuadruplos_en_robot: {'SÍ' if tiene_ejecutar_cuadruplos else 'NO'}")
        print(f"✅ Manejo BEGIN_LOOP: {'SÍ' if tiene_begin_loop else 'NO'}")
        print(f"✅ Velocidad primero: {'SÍ' if tiene_velocidad_primero else 'NO'}")
        
        if not (tiene_ejecutar_cuadruplos and tiene_begin_loop and tiene_velocidad_primero):
            print("❌ EL ARCHIVO DE INTERFAZ NO TIENE LOS CAMBIOS NECESARIOS")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 DIAGNÓSTICO COMPLETO: MAIN.PY vs TESTS DIRECTOS")
    print("=" * 60)
    
    # Verificar archivos
    archivo_ok = verificar_archivo_interfaz()
    
    # Test flujo completo
    flujo_ok = test_flujo_completo()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNÓSTICO FINAL:")
    print(f"   Archivo interfaz actualizado: {'✅ SÍ' if archivo_ok else '❌ NO'}")
    print(f"   Flujo completo funciona: {'✅ SÍ' if flujo_ok else '❌ NO'}")
    
    if not archivo_ok:
        print("\n🔧 SOLUCIÓN:")
        print("   El archivo interfaz/ventana_principal.py NO tiene los cambios")
        print("   Necesitas actualizar la función _ejecutar_cuadruplos_en_robot")
    elif not flujo_ok:
        print("\n🔧 PROBLEMA:")
        print("   Hay un error en el flujo de ejecución")
    else:
        print("\n🎉 TODO DEBERÍA FUNCIONAR")
        print("   Si aún no funciona en main.py, puede ser un problema de threading")

if __name__ == "__main__":
    main()