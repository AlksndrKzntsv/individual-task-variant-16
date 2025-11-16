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