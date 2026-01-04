"""
Fix for Unicode encoding issues in the notebook
This script patches the notebook to use UTF-8 encoding for file writes
"""

import json
from pathlib import Path

# Read the notebook
notebook_path = Path(r'c:\Users\NIlEUN\Downloads\data_mix\data_merging_preprocessing.ipynb')

with open(notebook_path, 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find and fix cells that write to files
fixes_applied = 0

for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])

        # Fix 1: Add encoding='utf-8' to all open() calls for writing
        if "open(OUTPUT_DIR / 'MERGE_REPORT.md', 'w')" in source:
            source = source.replace(
                "with open(OUTPUT_DIR / 'MERGE_REPORT.md', 'w') as f:",
                "with open(OUTPUT_DIR / 'MERGE_REPORT.md', 'w', encoding='utf-8') as f:"
            )
            cell['source'] = source.split('\n')
            if not source.endswith('\n'):
                cell['source'][-1] = cell['source'][-1]
            else:
                cell['source'] = [line + '\n' if i < len(cell['source']) - 1 else line
                                  for i, line in enumerate(cell['source'])]
            fixes_applied += 1
            print("Fixed MERGE_REPORT.md encoding")

        # Fix 2: data.yaml encoding
        if "with open(OUTPUT_DIR / 'data.yaml', 'w') as f:" in source:
            source = source.replace(
                "with open(OUTPUT_DIR / 'data.yaml', 'w') as f:",
                "with open(OUTPUT_DIR / 'data.yaml', 'w', encoding='utf-8') as f:"
            )
            cell['source'] = source.split('\n')
            if source.endswith('\n'):
                cell['source'] = [line + '\n' if i < len(source.split('\n')) - 1 else line
                                  for i, line in enumerate(source.split('\n'))]
            fixes_applied += 1
            print("Fixed data.yaml encoding")

        # Fix 3: augmentation_config.yaml encoding
        if "with open(OUTPUT_DIR / 'augmentation_config.yaml', 'w') as f:" in source:
            source = source.replace(
                "with open(OUTPUT_DIR / 'augmentation_config.yaml', 'w') as f:",
                "with open(OUTPUT_DIR / 'augmentation_config.yaml', 'w', encoding='utf-8') as f:"
            )
            cell['source'] = source.split('\n')
            if source.endswith('\n'):
                cell['source'] = [line + '\n' if i < len(source.split('\n')) - 1 else line
                                  for i, line in enumerate(source.split('\n'))]
            fixes_applied += 1
            print("Fixed augmentation_config.yaml encoding")

# Save the fixed notebook
backup_path = notebook_path.with_suffix('.ipynb.backup')
import shutil
shutil.copy2(notebook_path, backup_path)
print(f"\nBackup saved to: {backup_path}")

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"\nFixed {fixes_applied} encoding issues")
print(f"Notebook updated: {notebook_path}")
print("\nYou can now restart your kernel and run the notebook!")
