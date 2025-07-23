#!/usr/bin/env python3
"""
Script de ejecución simplificado para el Analizador Léxico del Robot ABB IRB 120
"""

import sys
import os
import logging
from pathlib import Path

def setup_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('robot_analizador.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    missing_deps = []
    
    try:
        import PyQt5
    except ImportError:
        missing_deps.append('PyQt5')
    
    try:
        import numpy
    except ImportError:
        missing_deps.append('numpy')
        
    # RoboDK es opcional
    try:
        import robodk
        print("✅ RoboDK disponible")
    except ImportError:
        print("⚠️ RoboDK no disponible - Funcionará en modo simulación")
    
    if missing_deps:
        print("❌ Dependencias faltantes:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstala las dependencias con:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias principales están disponibles")
    return True

def setup_environment():
    """Configura el entorno de ejecución"""
    # Agregar directorios al path
    current_dir = Path(__file__).parent.absolute()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Crear directorios necesarios
    directories = ['logs', 'temp', 'exports']
    for directory in directories:
        dir_path = current_dir / directory
        dir_path.mkdir(exist_ok=True)
    
    print(f"🔧 Entorno configurado en: {current_dir}")

def run_application():
    """Ejecuta la aplicación principal"""
    try:
        # Importar y ejecutar la aplicación
        from main import main
        print("🚀 Iniciando Analizador Léxico del Robot ABB IRB 120...")
        main()
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("Verifica que todos los archivos estén en su lugar")
        return False
        
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")
        logging.exception("Error en aplicación principal")
        return False
    
    return True

def main():
    """Función principal del script de ejecución"""
    print("=" * 60)
    print("🤖 ANALIZADOR LÉXICO - ROBOT ABB IRB 120-3/0.6")
    print("=" * 60)
    
    # Configurar logging
    setup_logging()
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Configurar entorno
    setup_environment()
    
    # Ejecutar aplicación
    if not run_application():
        sys.exit(1)
    
    print("👋 Aplicación finalizada")

if __name__ == "__main__":
    main()