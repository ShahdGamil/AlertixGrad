"""
Environment checker for data preprocessing pipeline
Run this to verify all dependencies are installed correctly
"""

import sys
print("=" * 60)
print("ENVIRONMENT CHECK")
print("=" * 60)

print(f"\nPython Version: {sys.version}")
print(f"Python Executable: {sys.executable}")

print("\n" + "-" * 60)
print("Checking Dependencies...")
print("-" * 60)

dependencies = {
    'numpy': None,
    'pandas': None,
    'matplotlib': None,
    'seaborn': None,
    'PIL': 'Pillow',
    'cv2': 'opencv-python',
    'yaml': 'PyYAML',
    'tqdm': None,
    'sklearn': 'scikit-learn',
}

all_ok = True

for module_name, package_name in dependencies.items():
    pkg_name = package_name if package_name else module_name
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"[OK] {pkg_name:20s} {version:15s}")
    except ImportError as e:
        print(f"[MISSING] {pkg_name:20s} {'':15s}")
        all_ok = False

print("-" * 60)

if all_ok:
    print("\n[SUCCESS] All dependencies installed correctly!")
    print("\nYou can now run the Jupyter notebook.")
    print("\nIMPORTANT: If running in Jupyter, restart your kernel:")
    print("  - Click: Kernel -> Restart Kernel")
    print("  - Or press the restart button")
else:
    print("\n[ERROR] Some dependencies are missing!")
    print("\nInstall missing packages:")
    print("  pip install -r requirements.txt")

print("\n" + "=" * 60)