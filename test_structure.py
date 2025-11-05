#!/usr/bin/env python3
"""
Basic structure test for Paint+ without external dependencies
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_project_structure():
    """Test that all expected files and directories exist"""
    base_path = Path(__file__).parent

    required_files = [
        "main.py",
        "requirements.txt",
        "setup.py",
        "README.md",
    ]

    required_dirs = [
        "src",
        "src/app",
        "src/ui",
        "src/canvas",
        "src/tools",
        "src/layers",
        "src/io",
        "src/utils",
        "tests",
        "docs",
        "scripts",
        "resources",
    ]

    missing_files = []
    missing_dirs = []

    # Check files
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)

    # Check directories
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)

    if missing_files:
        print(f"✗ Missing files: {missing_files}")
    else:
        print("✓ All required files present")

    if missing_dirs:
        print(f"✗ Missing directories: {missing_dirs}")
    else:
        print("✓ All required directories present")

    return len(missing_files) == 0 and len(missing_dirs) == 0

def test_python_imports():
    """Test that Python modules can be imported (without PyQt6)"""
    try:
        # Test basic Python modules structure
        import src.app.config
        print("✓ App config module structure ok")

        import src.layers.base_layer
        print("✓ Layer base module structure ok")

        import src.tools.base_tool
        print("✓ Tool base module structure ok")

        return True
    except Exception as e:
        print(f"✗ Import structure test failed: {e}")
        return False

def test_class_definitions():
    """Test that key classes are properly defined"""
    try:
        # Test config class
        from src.app.config import Config
        config = Config()
        assert hasattr(config, 'get')
        assert hasattr(config, 'set')
        print("✓ Config class properly defined")

        # Test layer base class
        from src.layers.base_layer import BaseLayer
        assert hasattr(BaseLayer, '__init__')
        assert hasattr(BaseLayer, 'get_image_data')
        assert hasattr(BaseLayer, 'set_image_data')
        print("✓ BaseLayer class properly defined")

        # Test tool base class
        from src.tools.base_tool import BaseTool
        assert hasattr(BaseTool, '__init__')
        assert hasattr(BaseTool, 'mouse_press')
        assert hasattr(BaseTool, 'mouse_move')
        assert hasattr(BaseTool, 'mouse_release')
        print("✓ BaseTool class properly defined")

        return True
    except Exception as e:
        print(f"✗ Class definition test failed: {e}")
        return False

def test_dependencies_file():
    """Test that requirements.txt contains expected dependencies"""
    try:
        requirements_file = Path(__file__).parent / "requirements.txt"
        content = requirements_file.read_text()

        required_deps = ["PyQt6", "numpy", "Pillow"]

        missing_deps = []
        for dep in required_deps:
            if dep not in content:
                missing_deps.append(dep)

        if missing_deps:
            print(f"✗ Missing dependencies in requirements.txt: {missing_deps}")
        else:
            print("✓ All required dependencies listed in requirements.txt")

        return len(missing_deps) == 0
    except Exception as e:
        print(f"✗ Requirements file test failed: {e}")
        return False

def test_main_entry_point():
    """Test that main.py has correct structure"""
    try:
        main_file = Path(__file__).parent / "main.py"
        content = main_file.read_text()

        required_imports = ["sys", "QApplication", "PaintPlusApplication"]
        required_functions = ["main()"]

        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)

        if missing_imports:
            print(f"✗ Missing imports in main.py: {missing_imports}")
        else:
            print("✓ main.py has required imports")

        # Check if main function exists
        if "def main():" in content:
            print("✓ main.py has main() function")
        else:
            print("✗ main.py missing main() function")

        return len(missing_imports) == 0 and "def main():" in content
    except Exception as e:
        print(f"✗ Main entry point test failed: {e}")
        return False

def main():
    """Run all structure tests"""
    print("Running Paint+ structure tests...\n")

    tests = [
        test_project_structure,
        test_python_imports,
        test_class_definitions,
        test_dependencies_file,
        test_main_entry_point,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All structure tests passed! Paint+ is properly organized.")
        return True
    else:
        print("❌ Some structure tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)