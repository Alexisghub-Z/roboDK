#!/usr/bin/env python3
"""
Configuración CORREGIDA del Robot ABB IRB 120-3/0.6 con Garra Robotiq 2F-85
CON RANGOS EXPANDIDOS PARA SOPORTAR VALORES NEGATIVOS
"""

# Configuración del Robot ABB IRB 120
ROBOT_CONFIG = {
    'modelo': 'ABB IRB 120-3/0.6',
    'payload_maximo': 3.0,  # kg
    'alcance_maximo': 580,  # mm
    'repetibilidad': 0.01,  # mm
    
    # Límites articulares EXPANDIDOS PARA NEGATIVOS (en grados)
    'limites_articulares': {
        'eje1_base': (-360, 360),       # EXPANDIDO: Base bidireccional
        'eje2_hombro': (-180, 180),     # EXPANDIDO: Hombro bidireccional
        'eje3_codo': (-180, 180),       # EXPANDIDO: Codo bidireccional
        'eje4_muñeca1': (-160, 160),    # Muñeca 1 (ya era bidireccional)
        'eje5_muñeca2': (-120, 120),    # Muñeca 2 (ya era bidireccional)
        'eje6_muñeca3': (-400, 400)     # Muñeca 3 (ya era bidireccional)
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

# Configuración de la Garra Robotiq 2F-85 CON SOPORTE PARA NEGATIVOS
GARRA_CONFIG = {
    'modelo': 'Robotiq 2F-85 Gripper',
    'apertura_maxima': 85,      # mm (para referencia)
    'fuerza_maxima': 235,       # N
    'velocidad_maxima': 150,    # mm/s
    'precision': 0.02,          # mm
    
    # NUEVO: Rotación como eje 6 con soporte negativo
    'rotacion_eje6': {
        'rango_minimo': -360,   # Grados negativos soportados
        'rango_maximo': 360,    # Grados positivos soportados
        'precision_rotacion': 0.1  # Precisión en grados
    },
    
    # Configuraciones predefinidas EXPANDIDAS
    'posiciones_predefinidas': {
        'cerrada': 0,
        'semi_abierta': 42.5,
        'abierta': 85,
        # NUEVOS: Posiciones negativas
        'rotacion_negativa_90': -90,
        'rotacion_negativa_180': -180,
        'rotacion_positiva_90': 90,
        'rotacion_positiva_180': 180
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

# Configuración del analizador léxico CON SOPORTE .negativo
ANALIZADOR_CONFIG = {
    'comandos_validos': {
        'base', 'hombro', 'codo', 'garra', 'velocidad', 'repetir',
        # NUEVOS: Comandos con .negativo
        'base.negativo', 'hombro.negativo', 'codo.negativo', 'garra.negativo',
        'muñeca1.negativo', 'muñeca2.negativo', 'muñeca3.negativo'
    },
    
    'rangos_comandos': {
        # Rangos EXPANDIDOS para soportar negativos
        'base': (-360, 360),        # Base bidireccional completa
        'hombro': (-180, 180),      # Hombro bidireccional completa
        'codo': (-180, 180),        # Codo bidireccional completa
        'garra': (-360, 360),       # Garra como rotación eje 6 bidireccional
        'velocidad': (1, 100),      # Porcentaje (solo positivo)
        'repetir': (1, 100),        # Número de repeticiones (solo positivo)
        
        # NUEVOS: Rangos para comandos .negativo (valor positivo que se convierte)
        'base.negativo': (0, 360),
        'hombro.negativo': (0, 180),
        'codo.negativo': (0, 180),
        'garra.negativo': (0, 360),
        'muñeca1.negativo': (0, 160),
        'muñeca2.negativo': (0, 120),
        'muñeca3.negativo': (0, 400)
    },
    
    'mapeo_articulaciones': {
        'base': 0,      # Eje 1
        'hombro': 1,    # Eje 2
        'codo': 2,      # Eje 3
        'muñeca1': 3,   # Eje 4
        'muñeca2': 4,   # Eje 5
        'muñeca3': 5,   # Eje 6
        'garra': 5      # Eje 6 (mismo que muñeca3)
    }
}

# Configuración de seguridad EXPANDIDA
SEGURIDAD_CONFIG = {
    'velocidad_maxima_segura': 50,      # % de velocidad máxima
    'verificar_limites': True,
    'parada_emergencia_activa': True,
    'timeout_movimiento': 30.0,         # segundos
    
    # NUEVOS: Límites de seguridad para negativos
    'limites_seguridad_negativos': {
        'base_min': -300,           # Límite seguro para base negativa
        'hombro_min': -150,         # Límite seguro para hombro negativo
        'codo_min': -150,           # Límite seguro para codo negativo
        'garra_min': -300           # Límite seguro para garra negativa
    },
    
    # Zonas seguras (en mm desde la base) - EXPANDIDAS
    'zona_trabajo_segura': {
        'x_min': -500,              # EXPANDIDO: Permite movimientos negativos
        'x_max': 500,               # EXPANDIDO: Mayor rango positivo
        'y_min': -500,              # EXPANDIDO: Permite movimientos negativos
        'y_max': 500,               # EXPANDIDO: Mayor rango positivo
        'z_min': -100,              # EXPANDIDO: Permite algo por debajo de la base
        'z_max': 700                # EXPANDIDO: Mayor altura
    }
}

# Configuración de la interfaz
INTERFAZ_CONFIG = {
    'ventana': {
        'titulo': 'Analizador Léxico - Robot ABB IRB 120 (Soporte .negativo)',
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
        'info': '#17a2b8',
        # NUEVOS: Colores para valores negativos
        'negativo': '#8e44ad',      # Morado para valores negativos
        'positivo': '#27ae60'       # Verde para valores positivos
    }
}

# Ejemplos de código ACTUALIZADOS con .negativo
EJEMPLOS_CODIGO = {
    'basico': """Robot ROBOT1
ROBOT1.velocidad = 5
ROBOT1.base = 90
ROBOT1.hombro = 45
ROBOT1.codo = 60
ROBOT1.garra = 30""",
    
    'con_negativos': """Robot NEGATIVO
NEGATIVO.velocidad = 3
NEGATIVO.base = 90
NEGATIVO.base.negativo = 45
NEGATIVO.hombro.negativo = 30
NEGATIVO.garra.negativo = 90""",
    
    'con_repeticion_negativos': """Robot BUCLE_NEG
BUCLE_NEG.velocidad = 2
BUCLE_NEG.repetir = 3 {
    BUCLE_NEG.base = 180
    BUCLE_NEG.base.negativo = 90
    BUCLE_NEG.garra.negativo = 180
    BUCLE_NEG.garra = 0
}""",
    
    'pick_and_place_negativo': """Robot PICKER
PICKER.velocidad = 4
PICKER.base = 45
PICKER.hombro = 30
PICKER.velocidad = 2
PICKER.codo = 90
PICKER.garra.negativo = 85
PICKER.velocidad = 3
PICKER.hombro = 60
PICKER.base.negativo = 45
PICKER.velocidad = 1
PICKER.garra = 85
PICKER.hombro.negativo = 30
PICKER.base = 0""",
    
    'inspeccion_completa': """Robot INSPECTOR
INSPECTOR.velocidad = 3
INSPECTOR.base = 0
INSPECTOR.repetir = 4 {
    INSPECTOR.velocidad = 2
    INSPECTOR.base = 90
    INSPECTOR.hombro = 45
    INSPECTOR.garra.negativo = 45
    INSPECTOR.velocidad = 1
    INSPECTOR.base.negativo = 90
    INSPECTOR.hombro.negativo = 45
    INSPECTOR.garra = 90
    INSPECTOR.base = 180
}"""
}

# Configuración de logging
LOGGING_CONFIG = {
    'nivel': 'INFO',
    'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'archivo': 'robot_analizador_negativos.log',
    'rotar_archivo': True,
    'tamaño_maximo': '10MB',
    'copias_respaldo': 5,
    
    # NUEVO: Logging específico para valores negativos
    'log_negativos': True,
    'log_conversiones': True,
    'log_rangos_expandidos': True
}