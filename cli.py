#!/usr/bin/env python3
"""
CLI-приложение для визуализации графа зависимостей
Этап 2: Сбор данных
"""

import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(__file__))

from config_loader import ConfigLoader
from apk_parser import APKParser

def main():
    """Основная функция CLI-приложения"""
    print("=== Визуализатор графа зависимостей пакетов ===")
    print("Этап 2: Сбор данных")
    
    try:
        # Загрузка конфигурации
        loader = ConfigLoader("config.json")
        config = loader.load_config()
        
        # Вывод параметров
        loader.display_config()
        print()
        
        # Получение зависимостей (новый функционал этапа 2)
        print("📦 Получение зависимостей пакета...")
        parser = APKParser(config['repository_url'])
        dependencies = parser.get_package_dependencies(config['package_name'])
        
        # Вывод прямых зависимостей (требование этапа)
        print(f"\n📋 Прямые зависимости пакета '{config['package_name']}':")
        if dependencies:
            for i, dep in enumerate(dependencies, 1):
                print(f"  {i}. {dep}")
        else:
            print("  ⚠️ Зависимости не найдены")
        
        print(f"\n✅ Найдено зависимостей: {len(dependencies)}")
        
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
        print("ℹ️  Создайте файл config.json с конфигурацией")
        
    except ValueError as e:
        print(f"❌ Ошибка валидации: {e}")
        print("ℹ️  Проверьте структуру config.json")
        
    except ConnectionError as e:
        print(f"❌ Ошибка подключения: {e}")
        print("ℹ️  Проверьте URL репозитория и подключение к интернету")
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        
    finally:
        print("\nЗавершение работы...")

if __name__ == "__main__":
    main()