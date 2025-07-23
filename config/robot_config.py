#!/usr/bin/env python3
"""
Configuración del Robot ABB IRB 120-3/0.6 con Garra Robotiq 2F-85
"""

# Configuración del Robot ABB IRB 120
ROBOT_CONFIG = {
    'modelo': 'ABB IRB 120-3/0.6',
    'payload_maximo': 3.0,  # kg
    'alcance_maximo': 580,  # mm
    'repetibilidad': 0.01,  # mm
    
    # Límites articulares (en grados)
    'limites_articulares': {
        'eje1_base': (-165, 165),
        'eje2_hombro': (-110, 110),
        'eje3_codo': (-110, 70),
        'eje4_muñeca1': (-160, 160),
        'eje5_muñeca2': (-120, 120),
        'eje6_muñeca3': (-400, 400)
    },
    
    # Velocidades máximas (grados/segundo)
    'velocidades_maximas': {
        'eje1': 250,
        'eje2': 250,
        'eje3': 250,
        'eje4': 320,
        'eje5': 320,
        'eje6': 420
    },
    
    # Configuración de movimiento
    'velocidad_lineal_maxima': 1500,  # mm/s
    'aceleracion_maxima': 12000,      # mm/s²
    'precision_defecto': 0.1          # mm
}

# Configuración de la Garra Robotiq 2F-85
GARRA_CONFIG = {
    'modelo': 'Robotiq 2F-85 Gripper',
    'apertura_maxima': 85,      # mm
    'fuerza_maxima': 235,       # N
    'velocidad_maxima': 150,    # mm/s
    'precision': 0.02,          # mm
    
    # Configuraciones predefinidas
    'posiciones_predefinidas': {
        'cerrada': 0,
        'semi_abierta': 42.5,
        'abierta': 85
    },
    
    # Parámetros de control
    'fuerza_defecto': 100,      # N
    'velocidad_defecto': 50     # mm/s
}

# Configuración de RoboDK
ROBODK_CONFIG = {
    'puerto': 20500,
    'host': 'localhost',
    'timeout_conexion': 5.0,    # segundos
    'intervalo_actualizacion': 0.1,  # segundos
    
    # Nombres esperados en RoboDK
    'nombre_robot': 'ABB IRB 120-3/0.6',
    'nombres_alternativos_robot': [
        'IRB 120',
        'ABB IRB120',
        'IRB120-3/0.6'
    ],
    
    'nombre_garra': 'Robotiq 2F-85',
    'nombres_alternativos_garra': [
        'Robotiq',
        '2F-85',
        'Gripper',
        'Garra'
    ]
}

# Configuración del analizador léxico
ANALIZADOR_CONFIG = {
    'comandos_validos': {
        'base', 'hombro', 'codo', 'garra', 'velocidad', 'repetir'
    },
    
    'rangos_comandos': {
        'base': (0, 360),       # Grados (0-360 para facilidad de uso)
        'hombro': (0, 180),     # Grados (rango seguro)
        'codo': (0, 180),       # Grados (rango seguro)
        'garra': (0, 85),       # mm (apertura Robotiq 2F-85)
        'velocidad': (1, 100),  # Porcentaje
        'repetir': (1, 100)     # Número de repeticiones
    },
    
    'mapeo_articulaciones': {
        'base': 0,      # Eje 1
        'hombro': 1,    # Eje 2
        'codo': 2,      # Eje 3
        'muñeca1': 3,   # Eje 4
        'muñeca2': 4,   # Eje 5
        'muñeca3': 5    # Eje 6
    }
}

# Configuración de seguridad
SEGURIDAD_CONFIG = {
    'velocidad_maxima_segura': 50,      # % de velocidad máxima
    'verificar_limites': True,
    'parada_emergencia_activa': True,
    'timeout_movimiento': 30.0,         # segundos
    
    # Zonas seguras (en mm desde la base)
    'zona_trabajo_segura': {
        'x_min': -400,
        'x_max': 400,
        'y_min': -400,
        'y_max': 400,
        'z_min': 0,
        'z_max': 600
    }
}

# Configuración de la interfaz
INTERFAZ_CONFIG = {
    'ventana': {
        'titulo': 'Analizador Léxico - Robot ABB IRB 120',
        'ancho': 1400,
        'alto': 800,
        'redimensionable': True
    },
    
    'editor': {
        'fuente': 'Courier New',
        'tamaño_fuente': 12,
        'mostrar_numeros_linea': True,
        'resaltado_sintaxis': True
    },
    
    'colores': {
        'fondo': '#f8f9fa',
        'texto': '#212529',
        'error': '#dc3545',
        'exito': '#28a745',
        'advertencia': '#ffc107',
        'info': '#17a2b8'
    }
}

# Ejemplos de código para la interfaz
EJEMPLOS_CODIGO = {
    'basico': """Robot ROBOT1
ROBOT1.base = 90
ROBOT1.hombro = 45
ROBOT1.codo = 60
ROBOT1.garra = 30
ROBOT1.velocidad = 25""",
    
    'con_repeticion': """Robot ROBOT1
ROBOT1.velocidad = 30
ROBOT1.repetir = 3 {
    ROBOT1.base = 180
    ROBOT1.garra = 0
    ROBOT1.base = 0
    ROBOT1.garra = 85
}""",
    
    'pick_and_place': """Robot BRAZO
BRAZO.velocidad = 40
BRAZO.base = 45
BRAZO.hombro = 30
BRAZO.codo = 90
BRAZO.garra = 85
BRAZO.repetir = 5 {
    BRAZO.hombro = 60
    BRAZO.garra = 10
    BRAZO.hombro = 30
    BRAZO.base = 135
    BRAZO.hombro = 60
    BRAZO.garra = 85
    BRAZO.hombro = 30
    BRAZO.base = 45
}""",
    
    'inspeccion': """Robot INSPECTOR
INSPECTOR.velocidad = 20
INSPECTOR.base = 0
INSPECTOR.repetir = 8 {
    INSPECTOR.base = 45
    INSPECTOR.hombro = 45
    INSPECTOR.codo = 45
    INSPECTOR.base = 90
    INSPECTOR.hombro = 60
    INSPECTOR.base = 135
    INSPECTOR.hombro = 45
    INSPECTOR.base = 180
}"""
}

# Configuración de logging
LOGGING_CONFIG = {
    'nivel': 'INFO',
    'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'archivo': 'robot_analizador.log',
    'rotar_archivo': True,
    'tamaño_maximo': '10MB',
    'copias_respaldo': 5
}