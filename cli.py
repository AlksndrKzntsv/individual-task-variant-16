#!/usr/bin/env python3
"""
CLI-приложение для визуализации графа зависимостей
Этап 3: Основные операции
"""

import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(__file__))

from config_loader import ConfigLoader
from apk_parser import APKParser
from dependency_graph import DependencyGraph

def display_graph(graph: dict, root_package: str):
    """Отображает граф зависимостей"""
    print(f"\n🌳 Граф зависимостей для '{root_package}':")
    for package, dependencies in graph.items():
        if dependencies:
            print(f"  {package} -> {', '.join(dependencies)}")
        else:
            print(f"  {package} -> (нет зависимостей)")

def main():
    """Основная функция CLI-приложения"""
    print("=== Визуализатор графа зависимостей пакетов ===")
    print("Этап 3: Основные операции")
    
    try:
        # Загрузка конфигурации
        loader = ConfigLoader("config.json")
        config = loader.load_config()
        
        # Вывод параметров
        loader.display_config()
        print()
        
        # Определяем URL/путь в зависимости от режима
        test_mode = config['test_repository_mode']
        repository_path = config['repository_url']
        
        if test_mode:
            print(f"🔧 Тестовый режим: {repository_path}")
        else:
            print(f"🌐 Реальный режим: {repository_path}")
        
        # Построение графа зависимостей
        print(f"\n📦 Построение графа зависимостей...")
        graph_builder = DependencyGraph(
            repository_path,
            max_depth=config['max_dependency_depth'],
            package_filter=config['package_filter'],
            test_mode=test_mode
        )
        
        graph = graph_builder.build_dependency_graph(config['package_name'])
        
        # Вывод результатов
        display_graph(graph, config['package_name'])
        
        # Статистика
        stats = graph_builder.get_statistics()
        print(f"\n📊 Статистика:")
        print(f"  Всего пакетов: {stats['total_packages']}")
        print(f"  Максимальная глубина: {stats['max_depth']}")
        
        if graph_builder.cycles_detected:
            print(f"  ⚠️ Обнаружены циклические зависимости:")
            for cycle in graph_builder.cycles_detected:
                print(f"    {cycle}")
        
        # Демонстрация фильтрации
        if config['package_filter']:
            filtered_count = sum(1 for pkg in graph_builder.visited 
                               if graph_builder._should_filter_package(pkg))
            print(f"  Отфильтровано пакетов: {filtered_count}")
        
        print(f"\n✅ Граф построен успешно!")
        
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
    except ValueError as e:
        print(f"❌ Ошибка валидации: {e}")
    except ConnectionError as e:
        print(f"❌ Ошибка подключения: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        
    finally:
        print("\nЗавершение работы...")

if __name__ == "__main__":
    main()