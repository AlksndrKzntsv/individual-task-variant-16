from typing import Dict, List, Set, Optional
from collections import deque
from apk_parser import APKParser

class DependencyGraph:
    """Класс для построения и анализа графа зависимостей"""
    
    def __init__(self, repository_url: str, max_depth: int = 3, package_filter: str = "", test_mode: bool = False):
        self.repository_url = repository_url
        self.max_depth = max_depth
        self.package_filter = package_filter.lower()
        self.test_mode = test_mode
        self.parser = APKParser(repository_url, test_mode=test_mode)
        self.visited = set()
        self.cycles_detected = []
        self._full_graph_cache = None
    
    def build_dependency_graph(self, root_package: str) -> Dict[str, List[str]]:
        """
        Строит граф зависимостей с помощью BFS
        
        Args:
            root_package: Корневой пакет для анализа
            
        Returns:
            Dict[str, List[str]]: Граф зависимостей {пакет: [зависимости]}
        """
        graph = {}
        queue = deque()
        
        # Инициализация BFS
        queue.append((root_package, 0))  # (пакет, глубина)
        self.visited = {root_package}
        self.cycles_detected = []
        
        while queue:
            current_package, current_depth = queue.popleft()
            
            # Пропускаем пакеты с фильтром
            if self._should_filter_package(current_package):
                continue
            
            # Получаем зависимости текущего пакета
            try:
                dependencies = self.parser.get_package_dependencies(current_package)
                filtered_dependencies = [dep for dep in dependencies if not self._should_filter_package(dep)]
                
                graph[current_package] = filtered_dependencies
                
                # Добавляем зависимости в очередь, если не превышена глубина
                if current_depth < self.max_depth - 1:
                    for dep in filtered_dependencies:
                        if dep not in self.visited:
                            self.visited.add(dep)
                            queue.append((dep, current_depth + 1))
                        else:
                            # Обнаружение циклов
                            if dep in graph and current_package in graph.get(dep, []):
                                cycle = f"{current_package} -> {dep}"
                                if cycle not in self.cycles_detected:
                                    self.cycles_detected.append(cycle)
                                    
            except Exception as e:
                print(f"⚠️ Ошибка при получении зависимостей {current_package}: {e}")
                graph[current_package] = []
        
        return graph
    
    def find_reverse_dependencies(self, target_package: str) -> Dict[str, List[str]]:
        """
        Находит обратные зависимости для заданного пакета
        (пакеты, которые зависят от target_package)
        
        Args:
            target_package: Пакет, для которого ищем обратные зависимости
            
        Returns:
            Dict[str, List[str]]: Граф обратных зависимостей
        """
        print(f"🔍 Поиск обратных зависимостей для пакета: {target_package}")
        
        # Строим полный граф для поиска обратных зависимостей
        full_graph = self._build_full_graph_for_reverse_search()
        
        # Ищем пакеты, которые зависят от target_package
        reverse_deps = {}
        
        for package, dependencies in full_graph.items():
            if target_package in dependencies:
                if package not in reverse_deps:
                    reverse_deps[package] = []
                reverse_deps[package].append(target_package)
        
        return reverse_deps
    
    def _build_full_graph_for_reverse_search(self) -> Dict[str, List[str]]:
        """
        Строит полный граф всех доступных пакетов для поиска обратных зависимостей
        """
        if self._full_graph_cache is not None:
            return self._full_graph_cache
        
        full_graph = {}
        
        if self.test_mode:
            # В тестовом режиме читаем все пакеты из файла
            full_graph = self._load_all_test_packages()
        else:
            # В реальном режиме используем BFS для построения полного графа
            # с увеличенной глубиной для более полного покрытия
            original_max_depth = self.max_depth
            self.max_depth = 10  # Временное увеличение глубины для обратного поиска
            
            # Получаем список популярных пакетов для старта
            starter_packages = self._get_starter_packages()
            
            for starter in starter_packages:
                try:
                    graph_part = self.build_dependency_graph(starter)
                    full_graph.update(graph_part)
                except Exception:
                    continue
            
            self.max_depth = original_max_depth
        
        self._full_graph_cache = full_graph
        return full_graph
    
    def _load_all_test_packages(self) -> Dict[str, List[str]]:
        """Загружает все пакеты из тестового файла"""
        full_graph = {}
        
        try:
            with open(self.repository_url, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line in lines:
                if ':' in line:
                    package, deps_str = line.split(':', 1)
                    package = package.strip()
                    dependencies = deps_str.strip().split()
                    full_graph[package] = dependencies
                    
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке тестовых пакетов: {e}")
        
        return full_graph
    
    def _get_starter_packages(self) -> List[str]:
        """Возвращает список пакетов для начала построения полного графа"""
        # В реальном режиме используем несколько популярных пакетов как стартовые точки
        popular_packages = [
            'nginx', 'bash', 'python3', 'openssl', 'curl', 
            'git', 'gcc', 'make', 'linux-firmware'
        ]
        return popular_packages
    
    def _should_filter_package(self, package_name: str) -> bool:
        """Проверяет, нужно ли фильтровать пакет"""
        if not self.package_filter:
            return False
        return self.package_filter in package_name.lower()
    
    def get_statistics(self) -> Dict[str, int]:
        """Возвращает статистику по графу"""
        return {
            'total_packages': len(self.visited),
            'cycles_detected': len(self.cycles_detected),
            'max_depth': self.max_depth
        }