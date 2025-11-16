import urllib.request
import urllib.error
import re
from typing import List, Dict
import gzip
import io

class APKParser:
    """Парсер для извлечения зависимостей APK пакетов Alpine Linux"""
    
    def __init__(self, repository_url: str):
        self.repository_url = repository_url.rstrip('/')
        self.package_cache = {}
    
    def get_package_dependencies(self, package_name: str) -> List[str]:
        """
        Получает прямые зависимости указанного пакета
        
        Args:
            package_name: Имя пакета для анализа
            
        Returns:
            List[str]: Список прямых зависимостей
        """
        try:
            print(f"🔍 Поиск информации о пакете: {package_name}")
            
            # Получаем индекс пакетов
            packages_index = self._fetch_packages_index()
            
            # Ищем информацию о конкретном пакете
            package_info = self._find_package_info(packages_index, package_name)
            
            if not package_info:
                raise ValueError(f"Пакет '{package_name}' не найден в репозитории")
            
            # Извлекаем зависимости
            dependencies = self._extract_dependencies(package_info)
            
            return dependencies
            
        except urllib.error.URLError as e:
            raise ConnectionError(f"Ошибка подключения к репозиторию: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении зависимостей: {e}")
    
    def _fetch_packages_index(self) -> str:
        """Загружает индекс пакетов из репозитория"""
        index_url = f"{self.repository_url}/x86_64/APKINDEX.tar.gz"
        
        print(f"📥 Загрузка индекса пакетов: {index_url}")
        
        try:
            with urllib.request.urlopen(index_url) as response:
                compressed_data = response.read()
            
            # Распаковываем gzip с обработкой бинарных данных
            with gzip.open(io.BytesIO(compressed_data), 'rb') as f:
                decompressed_data = f.read()
            
            # Пробуем разные кодировки
            try:
                return decompressed_data.decode('utf-8')
            except UnicodeDecodeError:
                # Если utf-8 не работает, пробуем latin-1
                return decompressed_data.decode('latin-1')
                
        except urllib.error.HTTPError as e:
            raise ConnectionError(f"Не удалось загрузить индекс пакетов: {e.code} {e.reason}")
        except gzip.BadGzipFile:
            raise ValueError("Загруженный файл не является корректным gzip архивом")
    
    def _find_package_info(self, packages_index: str, package_name: str) -> Dict[str, str]:
        """
        Ищет информацию о конкретном пакете в индексе
        
        Args:
            packages_index: Содержимое APKINDEX
            package_name: Имя искомого пакета
            
        Returns:
            Dict[str, str]: Информация о пакете
        """
        # Разбиваем индекс на пакеты (разделитель - пустая строка)
        packages = packages_index.strip().split('\n\n')
        
        for package_block in packages:
            package_info = self._parse_package_block(package_block)
            if package_info.get('P') == package_name:
                return package_info
        
        return {}
    
    def _parse_package_block(self, package_block: str) -> Dict[str, str]:
        """Парсит блок информации о пакете"""
        info = {}
        lines = package_block.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        
        return info
    
    def _extract_dependencies(self, package_info: Dict[str, str]) -> List[str]:
        """
        Извлекает зависимости из информации о пакете
        
        Args:
            package_info: Словарь с информацией о пакете
            
        Returns:
            List[str]: Список зависимостей
        """
        dependencies = []
        
        # Зависимости хранятся в поле 'D'
        if 'D' in package_info and package_info['D']:
            dep_string = package_info['D']
            # Зависимости разделены пробелами, могут содержать версии
            raw_deps = dep_string.split()
            
            for dep in raw_deps:
                # Убираем информацию о версиях (всё что после =, <, >, ~)
                clean_dep = re.split(r'[=<>~]', dep)[0]
                if clean_dep and clean_dep not in dependencies:
                    dependencies.append(clean_dep)
        
        return dependencies