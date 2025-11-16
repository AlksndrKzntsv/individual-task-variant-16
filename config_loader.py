import json
import os
from typing import Dict, Any

class ConfigLoader:
    """Загрузчик и валидатор конфигурационных параметров"""
    
    REQUIRED_KEYS = {
        'package_name': str,
        'repository_url': str,
        'test_repository_mode': bool,
        'ascii_tree_output': bool,
        'max_dependency_depth': int,
        'package_filter': str
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = {}
    
    def load_config(self) -> Dict[str, Any]:
        """Загружает и валидирует конфигурацию"""
        try:
            # Проверка существования файла
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Конфигурационный файл {self.config_path} не найден")
            
            # Чтение файла
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # Валидация структуры
            self._validate_config()
            
            return self.config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка формата JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки конфигурации: {e}")
    
    def _validate_config(self) -> None:
        """Валидация конфигурационных параметров"""
        missing_keys = []
        invalid_types = []
        
        # Проверка наличия всех ключей
        for key, expected_type in self.REQUIRED_KEYS.items():
            if key not in self.config:
                missing_keys.append(key)
            elif not isinstance(self.config[key], expected_type):
                invalid_types.append(f"{key} (ожидался {expected_type.__name__})")
        
        if missing_keys:
            raise ValueError(f"Отсутствуют обязательные параметры: {', '.join(missing_keys)}")
        
        if invalid_types:
            raise ValueError(f"Неверные типы параметров: {', '.join(invalid_types)}")
        
        # Дополнительная валидация значений
        if self.config['max_dependency_depth'] < 1:
            raise ValueError("max_dependency_depth должен быть положительным числом")
        
        if not isinstance(self.config['repository_url'], str) or not self.config['repository_url']:
            raise ValueError("repository_url должен быть непустой строкой")

    def display_config(self) -> None:
        """Вывод конфигурации в формате ключ-значение"""
        print("=== Конфигурационные параметры ===")
        for key, value in self.config.items():
            print(f"{key}: {value} ({type(value).__name__})")
        print("==================================")