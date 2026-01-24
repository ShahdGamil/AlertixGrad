"""
Quick Start Script for YOLO Ensemble Pipeline
Demonstrates basic usage and provides interactive setup
"""

import os
import sys
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   YOLO Ensemble Theft Detection Pipeline                     ║
    ║   Production-Ready CV Pipeline for Retail Surveillance       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n[1/5] Checking dependencies...")

    required = [
        'torch', 'torchvision', 'ultralytics', 'cv2', 'numpy',
        'pandas', 'matplotlib', 'seaborn', 'yaml', 'albumentations'
    ]

    missing = []

    for package in required:
        try:
            if package == 'cv2':
                __import__('cv2')
            elif package == 'yaml':
                __import__('yaml')
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)

    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False

    print("  All dependencies installed!")
    return True


def check_directory_structure():
    """Check and create required directories"""
    print("\n[2/5] Checking directory structure...")

    required_dirs = [
        'config',
        'src/validation',
        'src/cleaning',
        'src/balancing',
        'src/preprocessing',
        'src/splitting',
        'src/visualization',
        'src/training',
        'src/utils',
        'outputs/logs',
        'outputs/reports',
        'outputs/visualizations',
        'outputs/models',
        'data/raw',
        'data/cleaned',
        'data/processed',
        'data/train_ready'
    ]

    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {dir_path}")
        else:
            print(f"  ✓ {dir_path}")

    print("  Directory structure ready!")
    return True


def check_config():
    """Check configuration file"""
    print("\n[3/5] Checking configuration...")

    config_path = Path('config/config.yaml')

    if not config_path.exists():
        print("  ✗ config/config.yaml not found!")
        return False

    print(f"  ✓ Configuration file found")
    return True


def get_dataset_paths():
    """Get dataset paths from user"""
    print("\n[4/5] Dataset Setup")
    print("Please provide paths to your YOLO format dataset:")
    print("(Press Enter to skip and use default paths)")

    images_dir = input("\nImages directory path: ").strip()
    labels_dir = input("Labels directory path: ").strip()

    if not images_dir:
        images_dir = "data/raw/images"
    if not labels_dir:
        labels_dir = "data/raw/labels"

    images_path = Path(images_dir)
    labels_path = Path(labels_dir)

    print(f"\nUsing:")
    print(f"  Images: {images_path}")
    print(f"  Labels: {labels_path}")

    if not images_path.exists():
        print(f"\n⚠ Warning: Images directory not found: {images_path}")
        print("Please create it and add your images before running the pipeline.")

    if not labels_path.exists():
        print(f"⚠ Warning: Labels directory not found: {labels_path}")
        print("Please create it and add your YOLO labels before running the pipeline.")

    return str(images_path), str(labels_path)


def show_next_steps(images_path, labels_path):
    """Show next steps to user"""
    print("\n[5/5] Setup Complete!")

    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)

    print("\n1. Prepare Your Dataset:")
    print(f"   - Place images in: {images_path}")
    print(f"   - Place YOLO labels in: {labels_path}")
    print("   - Label format: class_id x_center y_center width height")

    print("\n2. Configure Pipeline:")
    print("   - Edit config/config.yaml")
    print("   - Update class names and counts")
    print("   - Adjust balancing and augmentation settings")

    print("\n3. Run Pipeline:")
    print(f"   python pipeline.py --images {images_path} --labels {labels_path}")

    print("\n4. Train Models:")
    print("   cd outputs/models")
    print("   python train_ensemble.py")

    print("\n5. Analyze Results:")
    print("   jupyter notebook analysis_notebook.ipynb")

    print("\n" + "="*70)
    print("USEFUL COMMANDS:")
    print("="*70)

    print("\n# View configuration")
    print("cat config/config.yaml")

    print("\n# Run validation only")
    print("python -c \"from pipeline import *; ...\"")

    print("\n# Monitor training")
    print("tensorboard --logdir runs/")

    print("\n# Check pipeline logs")
    print("cat outputs/logs/pipeline.log")

    print("\n" + "="*70)
    print("DOCUMENTATION:")
    print("="*70)
    print("  README.md  - Complete documentation")
    print("  USAGE.md   - Detailed usage examples")

    print("\n" + "="*70)
    print("\n✓ Ready to go! Good luck with your theft detection project!")
    print("="*70 + "\n")


def main():
    """Main quick start function"""
    print_banner()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check directory structure
    if not check_directory_structure():
        sys.exit(1)

    # Check config
    if not check_config():
        print("\n⚠ Please ensure config/config.yaml exists!")
        sys.exit(1)

    # Get dataset paths
    images_path, labels_path = get_dataset_paths()

    # Show next steps
    show_next_steps(images_path, labels_path)


if __name__ == '__main__':
    main()
