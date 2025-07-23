#!/usr/bin/env python3
"""
Script para verificar que la instalación esté completa y correcta
"""

import sys
import os
import platform
from pathlib import Path

def print_header():
    """Imprime el header del script"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE INSTALACIÓN")
    print("🤖 Analizador Léxico - Robot ABB IRB 120")
    print("=" * 60)

def verificar_sistema():
    """Verifica información del sistema"""
    print("📋 INFORMACIÓN DEL SISTEMA:")
    print("-" * 30)
    print(f"Sistema Operativo: {platform.system()} {platform.release()}")
    print(f"Arquitectura: {platform.machine()}")
    print(f"Procesador: {platform.processor()}")
    print(f"Python: {sys.version}")
    print(f"Directorio actual: {os.getcwd()}")
    print()

def verificar_python():
    """Verifica la versión de Python"""
    print("🐍 VERIFICANDO PYTHON:")
    print("-" * 30)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Versión de Python: {version_str}")
    
    if version >= (3, 8):
        print("✅ Versión de Python compatible")
        return True
    else:
        print("❌ Versión de Python demasiado antigua")
        print("   Se requiere Python 3.8 o superior")
        return False

def verificar_entorno_virtual():
    """Verifica si se está ejecutando en un entorno virtual"""
    print("🔧 VERIFICANDO ENTORNO VIRTUAL:")
    print("-" * 30)
    
    # Verificar si está en entorno virtual
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print("✅ Ejecutándose en entorno virtual")
        print(f"   Ruta del entorno: {sys.prefix}")
        return True
    else:
        print("⚠️ No se detectó entorno virtual")
        print("   Recomendado: crear y activar entorno virtual")
        print("   Comandos:")
        if platform.system() == "Windows":
            print("   python -m venv venv")
            print("   venv\\Scripts\\activate")
        else:
            print("   python -m venv venv")
            print("   source venv/bin/activate")
        return False

def verificar_dependencia(nombre_modulo, nombre_display=None, obligatorio=True):
    """Verifica si una dependencia está instalada"""
    if nombre_display is None:
        nombre_display = nombre_modulo
        
    try:
        if nombre_modulo == "PyQt5":
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import Qt
            import PyQt5.QtCore
            version = PyQt5.QtCore.PYQT_VERSION_STR
            print(f"✅ {nombre_display}: v{version}")
        elif nombre_modulo == "numpy":
            import numpy
            print(f"✅ {nombre_display}: v{numpy.__version__}")
        elif nombre_modulo == "robodk":
            import robodk
            print(f"✅ {nombre_display}: Disponible")
        else:
            __import__(nombre_modulo)
            print(f"✅ {nombre_display}: Disponible")
        return True
    except ImportError:
        if obligatorio:
            print(f"❌ {nombre_display}: No disponible (REQUERIDO)")
        else:
            print(f"⚠️ {nombre_display}: No disponible (Opcional)")
        return False

def verificar_dependencias():
    """Verifica todas las dependencias"""
    print("📦 VERIFICANDO DEPENDENCIAS:")
    print("-" * 30)
    
    dependencias_obligatorias = [
        ("PyQt5", "PyQt5 (Interfaz Gráfica)"),
        ("numpy", "NumPy (Cálculos)"),
    ]
    
    dependencias_opcionales = [
        ("robodk", "RoboDK (Control de Robot)"),
    ]
    
    todas_obligatorias = True
    
    # Verificar dependencias obligatorias
    for modulo, display in dependencias_obligatorias:
        if not verificar_dependencia(modulo, display, True):
            todas_obligatorias = False
    
    # Verificar dependencias opcionales
    for modulo, display in dependencias_opcionales:
        verificar_dependencia(modulo, display, False)
    
    print()
    return todas_obligatorias

def verificar_archivos():
    """Verifica que los archivos del proyecto estén presentes"""
    print("📁 VERIFICANDO ARCHIVOS DEL PROYECTO:")
    print("-" * 30)
    
    archivos_requeridos = [
        "main.py",
        "run.py",
        "requirements.txt",
        "analizador/__init__.py",
        "analizador/analizador_lexico.py",
        "interfaz/__init__.py", 
        "interfaz/ventana_principal.py",
        "robodk_controller/__init__.py",
        "robodk_controller/robot_controller.py",
        "config/robot_config.py"
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} (FALTANTE)")
            archivos_faltantes.append(archivo)
    
    print()
    return len(archivos_faltantes) == 0

def verificar_permisos():
    """Verifica permisos de escritura"""
    print("🔐 VERIFICANDO PERMISOS:")
    print("-" * 30)
    
    directorios_test = [".", "logs", "temp", "exports"]
    permisos_ok = True
    
    for directorio in directorios_test:
        try:
            # Crear directorio si no existe
            os.makedirs(directorio, exist_ok=True)
            
            # Probar escritura
            test_file = os.path.join(directorio, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
            print(f"✅ {directorio}/: Lectura/Escritura OK")
        except Exception as e:
            print(f"❌ {directorio}/: Error - {e}")
            permisos_ok = False
    
    print()
    return permisos_ok

def ejecutar_prueba_importacion():
    """Prueba importar los módulos principales del proyecto"""
    print("🧪 PRUEBA DE IMPORTACIÓN:")
    print("-" * 30)
    
    modulos_proyecto = [
        ("analizador.analizador_lexico", "Analizador Léxico"),
        ("robodk_controller.robot_controller", "Controlador Robot"),
        ("config.robot_config", "Configuración"),
    ]
    
    importacion_ok = True
    
    for modulo, nombre in modulos_proyecto:
        try:
            __import__(modulo)
            print(f"✅ {nombre}: Importación OK")
        except Exception as e:
            print(f"❌ {nombre}: Error - {e}")
            importacion_ok = False
    
    # Prueba especial para interfaz (requiere PyQt5)
    try:
        # Esto puede fallar si no hay display en sistemas sin GUI
        print("🔄 Probando interfaz gráfica...")
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        print("✅ Interfaz Gráfica: Inicialización OK")
    except Exception as e:
        print(f"⚠️ Interfaz Gráfica: {e}")
        print("   (Normal en sistemas sin display)")
    
    print()
    return importacion_ok

def mostrar_comandos_instalacion():
    """Muestra comandos para solucionar problemas"""
    print("🔧 COMANDOS DE INSTALACIÓN:")
    print("-" * 30)
    print("Para instalar dependencias faltantes:")
    print("  pip install -r requirements.txt")
    print()
    print("Para crear entorno virtual:")
    if platform.system() == "Windows":
        print("  python -m venv venv")
        print("  venv\\Scripts\\activate")
    else:
        print("  python -m venv venv")
        print("  source venv/bin/activate")
    print()
    print("Para instalar RoboDK (opcional):")
    print("  pip install robodk")
    print()

def main():
    """Función principal"""
    print_header()
    
    # Ejecutar todas las verificaciones
    resultados = []
    
    verificar_sistema()
    
    resultados.append(verificar_python())
    resultados.append(verificar_entorno_virtual())
    resultados.append(verificar_dependencias())
    resultados.append(verificar_archivos())
    resultados.append(verificar_permisos())
    resultados.append(ejecutar_prueba_importacion())
    
    # Resumen final
    print("=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    print("-" * 30)
    
    verificaciones = [
        "Versión de Python",
        "Entorno Virtual", 
        "Dependencias",
        "Archivos del Proyecto",
        "Permisos de Escritura",
        "Importación de Módulos"
    ]
    
    for i, (verificacion, resultado) in enumerate(zip(verificaciones, resultados)):
        estado = "✅ OK" if resultado else "❌ FALLO"
        print(f"{verificacion}: {estado}")
    
    print("-" * 30)
    
    # Solo los primeros 3 y el 4to son críticos para funcionalidad básica
    criticos_ok = all(resultados[:4])
    
    if criticos_ok:
        print("🎉 VERIFICACIÓN COMPLETA: Sistema listo para usar")
        print("   Puedes ejecutar: python main.py")
    else:
        print("⚠️ PROBLEMAS DETECTADOS: Revisar elementos marcados con ❌")
        mostrar_comandos_instalacion()
    
    print("=" * 60)
    
    return criticos_ok

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)