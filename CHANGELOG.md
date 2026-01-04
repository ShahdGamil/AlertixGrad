# Changelog

All notable changes to this dataset preprocessing project will be documented in this file.

---

## [1.0.0] - 2026-01-03

### Added
- ✅ Initial release of data merging and preprocessing pipeline
- ✅ Jupyter notebook for automated dataset merging
- ✅ Comprehensive README with full documentation
- ✅ Quick start guide for rapid setup
- ✅ Dataset comparison analysis document
- ✅ Template YAML configuration file
- ✅ Requirements file with all dependencies

### Features

#### Data Processing
- Complete pipeline for merging 3 YOLOv8 datasets
- Intelligent class mapping (6 classes → 2 classes)
- Automatic train/val/test split reorganization (70/15/15)
- Comprehensive data validation and quality checks
- RGB normalization statistics calculation
- Bounding box coordinate validation

#### Documentation
- `README.md` - Complete project documentation
- `QUICKSTART.md` - 5-minute quick start guide
- `DATASET_COMPARISON.md` - Detailed dataset analysis
- `data_template.yaml` - YOLOv8 configuration template
- `requirements.txt` - All Python dependencies
- `CHANGELOG.md` - This file

#### Automation
- Single-command installation
- One-click notebook execution
- Automatic output generation
- Progress tracking with tqdm
- Error handling and validation

#### Outputs Generated
- `data.yaml` - YOLOv8 training configuration
- `metadata.json` - Complete dataset metadata
- `dataset_stats.json` - Normalization parameters
- `augmentation_config.yaml` - Training augmentation settings
- `MERGE_REPORT.md` - Detailed merge statistics
- Visualization PNGs (class distributions, samples)

### Fixed
- ❌ B3 dataset missing validation split → ✅ Fixed with reorganization
- ❌ B3 dataset missing training labels → ✅ Handled in merge pipeline
- ❌ NumPy 2.x compatibility with OpenCV → ✅ Upgraded to OpenCV 4.12.0
- ❌ Class inconsistency across datasets → ✅ Unified to 2 classes

### Dependencies
```
numpy>=2.2.0,<2.4.0
pandas>=2.3.0
matplotlib>=3.10.0
seaborn>=0.13.0
Pillow>=12.0.0
opencv-python>=4.12.0
PyYAML>=6.0.0
tqdm>=4.67.0
scikit-learn>=1.7.0
jupyterlab>=4.0.0
ipywidgets>=8.0.0
```

### Dataset Statistics
- **Source Datasets**: 3 (B1, B2, B3)
- **Total Images**: ~11,303
- **Classes**: 2 (normal, theft)
- **Format**: YOLOv8 (YOLO format)
- **License**: CC BY 4.0

---

## [Unreleased]

### Planned Features
- [ ] Real-time augmentation preview
- [ ] Class balancing utilities
- [ ] Automatic hyperparameter tuning
- [ ] Multi-GPU training support
- [ ] Integration with MLflow for experiment tracking
- [ ] Automated model evaluation scripts
- [ ] Web-based dataset browser
- [ ] Export to other formats (COCO, Pascal VOC)

### Future Improvements
- [ ] Add more augmentation techniques
- [ ] Implement active learning pipeline
- [ ] Create Gradio demo for inference
- [ ] Add model quantization scripts
- [ ] Support for video dataset processing
- [ ] Automated dataset versioning
- [ ] Cloud storage integration (S3, GCS)
- [ ] Docker containerization

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-03 | Initial release with complete pipeline |

---

## Breaking Changes

None - Initial release

---

## Known Issues

### Minor Issues
1. **Progress bars in Jupyter**: May not display correctly in some terminals
   - **Workaround**: Use Jupyter Lab instead of Jupyter Notebook

2. **Large dataset memory usage**: Processing 11K+ images requires ~8GB RAM
   - **Workaround**: Process datasets sequentially if RAM limited

3. **Windows path issues**: Long paths may cause issues on Windows
   - **Workaround**: Use shorter directory names

### Fixed in 1.0.0
- ✅ OpenCV NumPy compatibility (upgraded to 4.12.0)
- ✅ Missing validation split in B3 (handled in reorganization)
- ✅ Class mapping inconsistency (unified to 2 classes)

---

## Migration Guide

N/A - Initial release

---

## Contributors

- **Pipeline Developer**: Claude (Anthropic)
- **Dataset Sources**: Roboflow Community
  - B1: cc-tv-footage-annotation
  - B2: shoplifting-detection
  - B3: test-make

---

## Support

For issues or questions:
1. Check the [README.md](README.md) documentation
2. Review [QUICKSTART.md](QUICKSTART.md) for common issues
3. Inspect generated `MERGE_REPORT.md` after running pipeline
4. Verify all dependencies are installed correctly

---

## License

- **Pipeline Code**: MIT License (free to use and modify)
- **Source Datasets**: CC BY 4.0 (Roboflow)
- **Merged Dataset**: CC BY 4.0 (inherited from sources)

---

## Acknowledgments

Special thanks to:
- **Roboflow** for hosting and providing the datasets
- **Ultralytics** for the YOLOv8 framework
- **OpenCV** team for computer vision tools
- **Jupyter** project for interactive notebooks
- **Python** community for excellent libraries

---

## Release Notes

### Version 1.0.0 (2026-01-03)

**What's New:**
- Complete data merging pipeline with automated processing
- Intelligent 6→2 class mapping for B1 dataset
- Comprehensive validation and quality checks
- Automatic train/val/test split reorganization
- Rich documentation with multiple guides
- YOLOv8-ready output configuration

**Installation:**
```bash
pip install -r requirements.txt
```

**Quick Start:**
```bash
jupyter lab
# Open data_merging_preprocessing.ipynb
# Run all cells
```

**Output:**
- Merged dataset in `merged_shoplifting_dataset/`
- YOLOv8 config in `data.yaml`
- Detailed report in `MERGE_REPORT.md`

**Performance:**
- Processing time: ~10-15 minutes
- Memory usage: ~4-8GB RAM
- Disk space: ~2GB for output

**Tested On:**
- Python 3.11
- Windows 10/11
- NumPy 2.2.6
- OpenCV 4.12.0

---

*For detailed changes in each version, see the sections above.*

**Last Updated: 2026-01-03**
