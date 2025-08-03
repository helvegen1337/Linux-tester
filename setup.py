#!/usr/bin/env python3
"""
Linux Training Platform - Setup Script
Установка интерактивного тренажера Linux командной строки
"""

from setuptools import setup, find_packages
import os
import sys

# Проверка версии Python
if sys.version_info < (3, 6):
    sys.exit('Требуется Python 3.6 или новее')

# Читаем README для длинного описания
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Interactive Linux Command Line Training Platform"

# Читаем requirements если есть
def read_requirements():
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

# Получаем версию из основного модуля
def get_version():
    try:
        # Читаем версию из artix_training.py если она там определена
        version_line = None
        with open('artix_training.py', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__') or line.startswith('VERSION'):
                    version_line = line
                    break
        
        if version_line:
            return version_line.split('=')[1].strip().strip('"\'')
        else:
            return "1.0.0"
    except FileNotFoundError:
        return "1.0.0"

setup(
    name="linux-training-platform",
    version=get_version(),
    description="🐧 Interactive Linux Command Line Training Platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Artix Team",
    author_email="naidicj.v@artix.team",
    url="https://github.com/helvegen1337/Linux-tester",
    license="MIT",
    
    # Классификаторы для PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: System Administrators",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: System :: Systems Administration",
        "Topic :: Terminals",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    
    # Ключевые слова
    keywords="linux, training, education, cli, terminal, system-administration, learning",
    
    # Python пакеты
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=read_requirements(),
    
    # Дополнительные файлы
    package_data={
        '': ['*.json', '*.md', '*.txt'],
    },
    include_package_data=True,
    
    # Точки входа для создания исполняемых команд
    entry_points={
        'console_scripts': [
            'linux-training=artix_training:main',
            'artix-training=artix_training:main',
        ],
    },
    
    # Дополнительные зависимости для разработки
    extras_require={
        'dev': [
            'pytest>=6.0',
            'black',
            'flake8',
        ],
    },
    
    # Метаданные проекта
    project_urls={
        "Bug Reports": "https://github.com/helvegen1337/Linux-tester/issues",
        "Source": "https://github.com/helvegen1337/Linux-tester",
        "Documentation": "https://github.com/helvegen1337/Linux-tester/blob/main/README.md",
    },
)