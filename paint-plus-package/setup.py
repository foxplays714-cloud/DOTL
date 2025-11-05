from setuptools import setup, find_packages

setup(
    name="paint-plus",
    version="0.1.0",
    description="A professional image editor built with PyQt6",
    author="Paint+ Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "PyQt6>=6.5.0",
        "PyQt6-tools>=6.5.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "PyOpenGL>=3.1.0",
        "PyOpenGL-accelerate>=3.1.0",
        "little-cms2>=2.14.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.2.0",
            "pyinstaller>=5.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "paint-plus=app.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)