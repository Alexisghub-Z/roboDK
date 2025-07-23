#!/usr/bin/env python3
"""
Script de instalación para el Analizador Léxico del Robot ABB IRB 120
"""

from setuptools import setup, find_packages
import os

# Leer README para la descripción larga
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Leer requirements.txt para las dependencias
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f 
                          if line.strip() and not line.startswith('#')]
    return requirements

setup(
    name='robot-analizador-lexico',
    version='1.0.0',
    author='Tu Nombre',
    author_email='tu-email@ejemplo.com',
    description='Analizador léxico para Robot ABB IRB 120-3/0.6 con garra Robotiq 2F-85',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/tu-usuario/robot-analizador-lexico',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Compilers',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],
    python_requires='>=3.8',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-qt>=4.0.0',
            'pylint>=2.10.0',
            'black>=21.0.0',
            'flake8>=3.9.0',
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
        'robodk': [
            'robodk>=5.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'robot-analizador=main:main',
        ],
        'gui_scripts': [
            'robot-analizador-gui=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'assets': ['fonts/*.ttf'],
        'config': ['*.py'],
        'tests': ['*.py'],
    },
    zip_safe=False,
    keywords='robot, abb, irb120, robotiq, analizador lexico, robodk, automation',
    project_urls={
        'Bug Reports': 'https://github.com/tu-usuario/robot-analizador-lexico/issues',
        'Documentation': 'https://github.com/tu-usuario/robot-analizador-lexico/wiki',
        'Source': 'https://github.com/tu-usuario/robot-analizador-lexico',
    },
)