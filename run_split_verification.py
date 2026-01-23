#!/usr/bin/env python3
"""
Simple script to run split verification without matplotlib visualization
"""

import sys
import os
from pathlib import Path
import json
import logging

# Add preprocessing to path
sys.path.insert(0, str(Path(__file__).parent / 'preprocessing'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def count_dataset_splits(dataset_path):
    """Count images and labels in each split."""
    dataset_path = Path(dataset_path)
    
    results = {}
    
    for split in ['train', 'valid', 'test']:
        split_path = dataset_path / split
        images_path = split_path / 'images'
        labels_path = split_path / 'labels'
        
        image_count = len(list(images_path.glob('*'))) if images_path.exists() else 0
        label_count = len(list(labels_path.glob('*.txt'))) if labels_path.exists() else 0
        
        results[split] = {
            'images': image_count,
            'labels': label_count,
            'matched': image_count == label_count
        }
    
    return results

def check_split_overlaps(dataset_path):
    """Check for filename overlaps between splits."""
    dataset_path = Path(dataset_path)
    
    split_files = {}
    overlaps = []
    
    for split in ['train', 'valid', 'test']:
        images_path = dataset_path / split / 'images'
        if images_path.exists():
            split_files[split] = {f.stem for f in images_path.iterdir()}
    
    # Check for overlaps
    splits_list = list(split_files.keys())
    for i, split1 in enumerate(splits_list):
        for split2 in splits_list[i+1:]:
            overlap = split_files[split1] & split_files[split2]
            if overlap:
                overlaps.append({
                    'split1': split1,
                    'split2': split2,
                    'count': len(overlap),
                    'examples': sorted(list(overlap))[:5]  # First 5 examples
                })
    
    return overlaps

def validate_bbox_format(dataset_path):
    """Validate bounding box format in labels."""
    dataset_path = Path(dataset_path)
    
    validation_results = {}
    
    for split in ['train', 'valid', 'test']:
        labels_path = dataset_path / split / 'labels'
        if not labels_path.exists():
            continue
        
        valid_count = 0
        invalid_count = 0
        errors = []
        
        for label_file in labels_path.glob('*.txt'):
            try:
                content = label_file.read_text().strip()
                if not content:  # Empty is valid
                    valid_count += 1
                    continue
                
                for line_num, line in enumerate(content.split('\n'), 1):
                    parts = line.split()
                    if len(parts) != 5:
                        invalid_count += 1
                        errors.append(f"{label_file.name}:{line_num} - Expected 5 values, got {len(parts)}")
                        continue
                    
                    try:
                        class_id = int(parts[0])
                        coords = [float(x) for x in parts[1:]]
                        
                        if not (0 <= class_id <= 5):
                            invalid_count += 1
                            errors.append(f"{label_file.name}:{line_num} - Invalid class_id: {class_id}")
                        
                        if not all(0 <= c <= 1 for c in coords):
                            invalid_count += 1
                            errors.append(f"{label_file.name}:{line_num} - Coordinates out of range [0,1]")
                        else:
                            valid_count += 1
                    except ValueError as e:
                        invalid_count += 1
                        errors.append(f"{label_file.name}:{line_num} - Parse error: {e}")
            except Exception as e:
                invalid_count += 1
                errors.append(f"{label_file.name} - Error reading: {e}")
        
        validation_results[split] = {
            'valid': valid_count,
            'invalid': invalid_count,
            'errors': errors[:10]  # First 10 errors
        }
    
    return validation_results

def main():
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print("\n" + "=" * 80)
    print("YOLO DATASET SPLIT VERIFICATION REPORT")
    print("=" * 80)
    print(f"Dataset Path: {dataset_path}\n")
    
    # 1. Count splits
    print("[1] SPLIT STATISTICS")
    print("-" * 80)
    split_counts = count_dataset_splits(dataset_path)
    for split, counts in split_counts.items():
        status = "✓ OK" if counts['matched'] else "✗ MISMATCH"
        print(f"  {split.upper():10} - Images: {counts['images']:5}, Labels: {counts['labels']:5} {status}")
    
    total_images = sum(s['images'] for s in split_counts.values())
    print(f"\n  TOTAL IMAGES: {total_images}")
    
    # 2. Check overlaps
    print("\n[2] SPLIT OVERLAP CHECK")
    print("-" * 80)
    overlaps = check_split_overlaps(dataset_path)
    if overlaps:
        print("  ✗ OVERLAPS DETECTED:")
        for overlap in overlaps:
            print(f"    - {overlap['split1']} ↔ {overlap['split2']}: {overlap['count']} files")
            print(f"      Examples: {', '.join(overlap['examples'][:3])}")
    else:
        print("  ✓ NO OVERLAPS - Splits are properly isolated")
    
    # 3. Validate bbox format
    print("\n[3] BOUNDING BOX FORMAT VALIDATION")
    print("-" * 80)
    bbox_validation = validate_bbox_format(dataset_path)
    for split, result in bbox_validation.items():
        total = result['valid'] + result['invalid']
        print(f"  {split.upper():10} - Valid: {result['valid']:5}, Invalid: {result['invalid']:5}")
        if result['errors']:
            for error in result['errors'][:3]:  # Show first 3 errors
                print(f"    • {error}")
    
    # 4. Generate report file
    print("\n[4] GENERATING REPORT FILE")
    print("-" * 80)
    
    report = {
        'split_statistics': split_counts,
        'total_images': total_images,
        'overlaps': overlaps,
        'bbox_validation': bbox_validation,
        'overall_status': 'PASS' if not overlaps and all(s['matched'] for s in split_counts.values()) else 'NEEDS_ATTENTION'
    }
    
    report_path = Path(dataset_path) / 'reports' / 'split_verification_report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"  Report saved to: {report_path}")
    
    # 5. Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"  Total Images Across All Splits: {total_images}")
    print(f"  Splits Properly Isolated: {'YES ✓' if not overlaps else 'NO ✗'}")
    print(f"  Overall Status: {report['overall_status']}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
