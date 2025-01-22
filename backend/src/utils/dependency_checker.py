import os
import ast
import logging

logger = logging.getLogger(__name__)

class ImportChecker(ast.NodeVisitor):
    def __init__(self):
        self.selenium_imports = []
        self.chrome_imports = []
        
    def visit_Import(self, node):
        for alias in node.names:
            if 'selenium' in alias.name or 'chrome' in alias.name.lower():
                self.selenium_imports.append(alias.name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        if 'selenium' in node.module or (node.module and 'chrome' in node.module.lower()):
            for alias in node.names:
                self.selenium_imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)

def check_dependencies():
    logger.info("Checking for Chrome/Selenium dependencies...")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        checker = ImportChecker()
                        checker.visit(tree)
                        if checker.selenium_imports or checker.chrome_imports:
                            logger.warning(f"Found Chrome/Selenium imports in {file_path}:")
                            for imp in checker.selenium_imports:
                                logger.warning(f"  - {imp}")
                except Exception as e:
                    logger.error(f"Error checking {file_path}: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_dependencies() 