#!/usr/bin/env python3
"""
CLI-приложение для визуализации графа зависимостей
Этап 4: Дополнительные операции
"""

import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(__file__))

from config_loader import ConfigLoader
from apk_parser import APKParser
from dependency_graph import DependencyGraph

def display_graph(graph: dict, title: str):
    """Отображает граф зависимостей"""
    print(f"\n{title}:")
    if not graph:
        print("  (пусто)")
        return
        
    for package, dependencies in graph.items():
        if dependencies:
            print(f"  {package} -> {', '.join(dependencies)}")
        else:
            print(f"  {package} -> (нет зависимостей)")

def display_reverse_dependencies(reverse_deps: dict, target_package: str):
    """Отображает обратные зависимости"""
    print(f"\n🔄 Обратные зависимости для '{target_package}':")
    if not reverse_deps:
        print("  ⚠️ Обратные зависимости не найдены")
        return
        
    for package, deps in reverse_deps.items():
        print(f"  {package} зависит от {target_package}")

def main():
    """Основная функция CLI-приложения"""
    print("=== Визуализатор графа зависимостей пакетов ===")
    print("Этап 4: Дополнительные операции")
    
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
        
        # Обычные зависимости
        graph = graph_builder.build_dependency_graph(config['package_name'])
        display_graph(graph, f"🌳 Прямые зависимости для '{config['package_name']}'")
        
        # Обратные зависимости (НОВЫЙ ФУНКЦИОНАЛ ЭТАПА 4)
        print(f"\n{'='*50}")
        print("🔍 РЕЖИМ ОБРАТНЫХ ЗАВИСИМОСТЕЙ (ЭТАП 4)")
        reverse_deps = graph_builder.find_reverse_dependencies(config['package_name'])
        display_reverse_dependencies(reverse_deps, config['package_name'])
        
        # Статистика
        stats = graph_builder.get_statistics()
        print(f"\n📊 Статистика:")
        print(f"  Всего пакетов: {stats['total_packages']}")
        print(f"  Максимальная глубина: {stats['max_depth']}")
        print(f"  Найдено обратных зависимостей: {len(reverse_deps)}")
        
        if graph_builder.cycles_detected:
            print(f"  ⚠️ Обнаружены циклические зависимости:")
            for cycle in graph_builder.cycles_detected:
                print(f"    {cycle}")
        
        # Демонстрация фильтрации
        if config['package_filter']:
            filtered_count = sum(1 for pkg in graph_builder.visited 
                               if graph_builder._should_filter_package(pkg))
            print(f"  Отфильтровано пакетов: {filtered_count}")
        
        print(f"\n✅ Все операции выполнены успешно!")
        
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