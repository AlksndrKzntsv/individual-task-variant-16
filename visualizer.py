from typing import Dict, List, Set
from collections import deque

class GraphVisualizer:
    """Класс для визуализации графа зависимостей"""
    
    def __init__(self):
        pass
    
    def generate_plantuml(self, graph: Dict[str, List[str]], root_package: str, 
                         reverse_deps: Dict[str, List[str]] = None) -> str:
        """
        Генерирует описание графа на языке PlantUML
        
        Args:
            graph: Граф зависимостей
            root_package: Корневой пакет
            reverse_deps: Обратные зависимости
            
        Returns:
            str: PlantUML код
        """
        plantuml_code = ["@startuml", "skinparam monochrome true", "skinparam shadowing false"]
        
        # Добавляем все узлы
        all_packages = set(graph.keys())
        for deps in graph.values():
            all_packages.update(deps)
        
        if reverse_deps:
            all_packages.update(reverse_deps.keys())
            for deps in reverse_deps.values():
                all_packages.update(deps)
        
        # Создаем узлы
        for package in sorted(all_packages):
            if package == root_package:
                plantuml_code.append(f"rectangle \"{package}\" as {package} #lightblue")
            elif package in graph:
                plantuml_code.append(f"rectangle \"{package}\" as {package}")
            else:
                plantuml_code.append(f"rectangle \"{package}\" as {package} #pink")
        
        # Добавляем прямые зависимости
        for package, dependencies in graph.items():
            for dep in dependencies:
                plantuml_code.append(f"{package} --> {dep}")
        
        # Добавляем обратные зависимости (если есть)
        if reverse_deps:
            for package, deps in reverse_deps.items():
                for dep in deps:
                    plantuml_code.append(f"{package} -[dashed]-> {dep} : reverse")
        
        plantuml_code.append("@enduml")
        return "\n".join(plantuml_code)
    
    def generate_ascii_tree(self, graph: Dict[str, List[str]], root_package: str) -> str:
        """
        Генерирует ASCII-дерево зависимостей
        
        Args:
            graph: Граф зависимостей
            root_package: Корневой пакет
            
        Returns:
            str: ASCII-дерево
        """
        if root_package not in graph:
            return f"{root_package}\n└── (нет зависимостей)"
        
        tree_lines = []
        visited = set()
        
        def build_tree(node: str, prefix: str = "", is_last: bool = True):
            if node in visited:
                tree_lines.append(f"{prefix}└── {node} ↺ (цикл)")
                return
            
            visited.add(node)
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{node}")
            
            if node in graph and graph[node]:
                new_prefix = prefix + ("    " if is_last else "│   ")
                children = graph[node]
                for i, child in enumerate(children):
                    build_tree(child, new_prefix, i == len(children) - 1)
        
        build_tree(root_package)
        return "\n".join(tree_lines)
    
    def find_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """
        Находит циклы в графе для пометки в ASCII-дереве
        """
        cycles = []
        visited = set()
        recursion_stack = set()
        path = []
        
        def dfs(node):
            if node in recursion_stack:
                # Найден цикл
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                if cycle not in cycles:
                    cycles.append(cycle.copy())
                return
            
            if node in visited:
                return
            
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)
            
            if node in graph:
                for neighbor in graph[node]:
                    dfs(neighbor)
            
            path.pop()
            recursion_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return cycles