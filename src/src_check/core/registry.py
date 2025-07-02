"""Plugin registry for managing checkers."""
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Type
import logging

from src_check.core.base import BaseChecker

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Registry for managing and discovering checker plugins."""
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._checkers: Dict[str, Type[BaseChecker]] = {}
        self._instances: Dict[str, BaseChecker] = {}
        
    def register(self, checker_class: Type[BaseChecker]) -> None:
        """Register a checker class.
        
        Args:
            checker_class: The checker class to register
        """
        name = checker_class.__name__
        if name in self._checkers:
            logger.warning(f"Checker {name} is already registered, overwriting")
        
        self._checkers[name] = checker_class
        logger.info(f"Registered checker: {name}")
        
    def get_checker(self, name: str) -> BaseChecker:
        """Get an instance of a registered checker.
        
        Args:
            name: Name of the checker
            
        Returns:
            Instance of the checker
            
        Raises:
            KeyError: If checker is not registered
        """
        if name not in self._checkers:
            raise KeyError(f"Checker '{name}' is not registered")
            
        # Create instance if not already created
        if name not in self._instances:
            self._instances[name] = self._checkers[name]()
            
        return self._instances[name]
        
    def get_all_checkers(self) -> List[BaseChecker]:
        """Get instances of all registered checkers.
        
        Returns:
            List of checker instances
        """
        checkers = []
        for name in self._checkers:
            checkers.append(self.get_checker(name))
        return checkers
        
    def discover_plugins(self, package_name: str = "src_check.rules") -> None:
        """Discover and register all checker plugins in a package.
        
        Args:
            package_name: Name of the package to search for plugins
        """
        try:
            # Import the package
            package = importlib.import_module(package_name)
            
            # Get package path
            if hasattr(package, '__path__'):
                package_path = package.__path__
            else:
                logger.warning(f"Package {package_name} has no __path__ attribute")
                return
                
            # Iterate through all modules in the package
            for importer, modname, ispkg in pkgutil.iter_modules(package_path):
                if ispkg:
                    continue  # Skip sub-packages for now
                    
                # Import the module
                module_name = f"{package_name}.{modname}"
                try:
                    module = importlib.import_module(module_name)
                    
                    # Look for BaseChecker subclasses
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        # Check if it's a class and subclass of BaseChecker
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseChecker) and 
                            attr is not BaseChecker):
                            
                            # Register the checker
                            self.register(attr)
                            
                except Exception as e:
                    logger.error(f"Error importing module {module_name}: {e}")
                    
        except ImportError as e:
            logger.error(f"Error importing package {package_name}: {e}")
            
    def list_checkers(self) -> List[str]:
        """List all registered checker names.
        
        Returns:
            List of checker names
        """
        return list(self._checkers.keys())
        
    def clear(self) -> None:
        """Clear all registered checkers."""
        self._checkers.clear()
        self._instances.clear()
        
    def is_registered(self, name: str) -> bool:
        """Check if a checker is registered.
        
        Args:
            name: Name of the checker
            
        Returns:
            True if registered, False otherwise
        """
        return name in self._checkers


# Global registry instance
registry = PluginRegistry()