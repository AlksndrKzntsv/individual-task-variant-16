#!/usr/bin/env python3
"""
Демонстрация визуализации для 3 различных пакетов
"""

import json
import os
import sys
sys.path.append(os.path.dirname(__file__))

from config_loader import ConfigLoader
from dependency_graph import DependencyGraph
from visualizer import GraphVisualizer

def demo_package(package_name, config_path="config.json"):
    """Демонстрация для одного пакета"""
    print(f"\n{'='*60}")
    print(f"🎯 ДЕМОНСТРАЦИЯ ДЛЯ ПАКЕТА: {package_name}")
    print(f"{'='*60}")
    
    try:
        # Загружаем конфигурацию
        loader = ConfigLoader(config_path)
        config = loader.load_config()
        
        # Меняем пакет для демонстрации
        config['package_name'] = package_name
        
        # Строим граф
        graph_builder = DependencyGraph(
            config['repository_url'],
            max_depth=config['max_dependency_depth'],
            package_filter=config['package_filter'],
            test_mode=config['test_repository_mode']
        )
        
        graph = graph_builder.build_dependency_graph(package_name)
        
        # Визуализация
        visualizer = GraphVisualizer()
        
        # PlantUML
        plantuml_code = visualizer.generate_plantuml(graph, package_name)
        print(f"\n📊 PlantUML для '{package_name}':")
        print("```plantuml")
        print(plantuml_code)
        print("```")
        
        # ASCII-дерево
        if config['ascii_tree_output']:
            ascii_tree = visualizer.generate_ascii_tree(graph, package_name)
            print(f"\n🌲 ASCII-дерево для '{package_name}':")
            print(ascii_tree)
        
        # Статистика
        stats = graph_builder.get_statistics()
        print(f"\n📊 Статистика для '{package_name}':")
        print(f"  Пакетов: {stats['total_packages']}, Циклов: {stats['cycles_detected']}")
        
    except Exception as e:
        print(f"❌ Ошибка для {package_name}: {e}")

def main():
    """Демонстрация для 3 пакетов"""
    print("=== ДЕМОНСТРАЦИЯ ВИЗУАЛИЗАЦИИ ДЛЯ 3 ПАКЕТОВ ===")
    
    # Три различных пакета для демонстрации
    packages = ["A", "X", "M"]
    
    for package in packages:
        demo_package(package)
    
    print(f"\n{'='*60}")
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("Показаны пакеты: A (сложный), X (простой), M (независимый)")

if __name__ == "__main__":
    main()