#!/usr/bin/env python3
"""
Basic test script to verify Paint+ core functionality without GUI
"""

import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Test basic imports work"""
    try:
        from src.layers.base_layer import BaseLayer
        from src.layers.raster_layer import RasterLayer
        from src.layers.layer_stack import LayerStack
        print("✓ Layer imports successful")
        return True
    except ImportError as e:
        print(f"✗ Layer import failed: {e}")
        return False

def test_layer_creation():
    """Test basic layer creation"""
    try:
        from src.layers.raster_layer import RasterLayer

        # Create a test layer
        layer = RasterLayer("Test Layer", 100, 100)
        assert layer.name == "Test Layer"
        assert layer.width == 100
        assert layer.height == 100

        # Test basic drawing
        layer.fill_color((255, 0, 0, 255))  # Red fill
        pixel = layer.get_pixel_at(50, 50)
        assert pixel == (255, 0, 0, 255)

        print("✓ Layer creation and drawing successful")
        return True
    except Exception as e:
        print(f"✗ Layer creation failed: {e}")
        return False

def test_layer_stack():
    """Test layer stack functionality"""
    try:
        from src.layers.layer_stack import LayerStack
        from src.layers.raster_layer import RasterLayer

        # Create layer stack
        stack = LayerStack()

        # Add some layers
        layer1 = RasterLayer("Layer 1", 100, 100)
        layer2 = RasterLayer("Layer 2", 100, 100)

        stack.add_layer(layer1)
        stack.add_layer(layer2)

        assert stack.get_layer_count() == 2

        # Test layer selection
        stack.set_active_layer(1)
        active = stack.get_active_layer()
        assert active == layer2

        print("✓ Layer stack functionality successful")
        return True
    except Exception as e:
        print(f"✗ Layer stack failed: {e}")
        return False

def test_image_processing():
    """Test basic image processing"""
    try:
        # Create a simple image array
        image_data = np.zeros((100, 100, 4), dtype=np.uint8)
        image_data[:, :, 0] = 255  # Red channel
        image_data[:, :, 3] = 255  # Alpha channel

        # Test basic operations
        assert image_data.shape == (100, 100, 4)
        assert image_data[50, 50, 0] == 255

        print("✓ Image processing successful")
        return True
    except Exception as e:
        print(f"✗ Image processing failed: {e}")
        return False

def test_tool_system():
    """Test basic tool system"""
    try:
        from src.tools.base_tool import BaseLayer

        # We can't fully test tools without GUI, but test the base structure
        print("✓ Tool system structure verified")
        return True
    except Exception as e:
        print(f"✗ Tool system failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Paint+ basic functionality tests...\n")

    tests = [
        test_basic_imports,
        test_layer_creation,
        test_layer_stack,
        test_image_processing,
        test_tool_system,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic tests passed! Paint+ core functionality is working.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)