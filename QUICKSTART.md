# Quick Start Guide - Shoplifting Detection Dataset

> Get your dataset merged and ready for training in 5 simple steps!

---

## ⚡ 5-Minute Quick Start

### Step 1: Install Dependencies

Open your terminal/command prompt and run:

```bash
cd c:\Users\NIlEUN\Downloads\data_mix
pip install -r requirements.txt
```

**Expected output:** All packages installed successfully

---

### Step 2: Verify Installation

```bash
python -c "import cv2, numpy, pandas; print('Ready to go!')"
```

**Expected output:** `Ready to go!`

---

### Step 3: Launch Jupyter

```bash
jupyter lab
```

This will open Jupyter Lab in your browser.

---

### Step 4: Run the Notebook

1. In Jupyter Lab, open: `data_merging_preprocessing.ipynb`
2. Click: **Run** → **Run All Cells**
3. Wait 10-15 minutes for completion

**What happens:**
- ✅ Analyzes 3 datasets
- ✅ Merges ~11,303 images
- ✅ Maps classes (6 → 2)
- ✅ Creates train/val/test splits
- ✅ Validates all data
- ✅ Generates reports and visualizations

---

### Step 5: Check Output

Navigate to: `c:\Users\NIlEUN\Downloads\data_mix\merged_shoplifting_dataset\`

**You should see:**
```
merged_shoplifting_dataset/
├── train/           ← 70% of data
├── valid/           ← 15% of data
├── test/            ← 15% of data
├── data.yaml        ← YOLOv8 config (IMPORTANT!)
├── MERGE_REPORT.md  ← Read this for statistics
└── *.png            ← Visualizations
```

---

## 🚀 Start Training (Optional)

If you have YOLOv8 installed:

```python
from ultralytics import YOLO

# Load model
model = YOLO('yolov8n.pt')

# Train
model.train(
    data='c:/Users/NIlEUN/Downloads/data_mix/merged_shoplifting_dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='shoplifting_detection'
)
```

---

## ❓ Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'cv2'"

**Solution:**
```bash
pip install --upgrade opencv-python
```
Then restart your Jupyter kernel.

---

### Problem: NumPy compatibility error

**Solution:**
```bash
pip install --upgrade opencv-python numpy>=2.2.0
```
Restart Jupyter kernel.

---

### Problem: Jupyter kernel keeps dying

**Solution:**
- Reduce batch processing in the notebook
- Use a machine with more RAM (8GB+ recommended)
- Process datasets one at a time

---

## 📊 What to Expect

After successful completion:

| Metric | Value |
|--------|-------|
| Total Images | ~11,303 |
| Classes | 2 (normal, theft) |
| Train Set | ~7,912 images (70%) |
| Val Set | ~1,695 images (15%) |
| Test Set | ~1,696 images (15%) |
| Format | YOLOv8 ready |

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `data.yaml` | **Use this for YOLOv8 training** |
| `MERGE_REPORT.md` | Read detailed statistics here |
| `metadata.json` | Complete dataset information |
| `dataset_stats.json` | Normalization parameters |

---

## ✅ Checklist

- [ ] Dependencies installed
- [ ] OpenCV working
- [ ] Jupyter Lab running
- [ ] Notebook executed successfully
- [ ] Output directory created
- [ ] `data.yaml` exists
- [ ] Reviewed `MERGE_REPORT.md`
- [ ] Ready to train!

---

## 🎯 Next Steps

1. **Review the data:**
   - Check `MERGE_REPORT.md` for statistics
   - View visualization PNGs
   - Inspect sample images

2. **Train a model:**
   - Use the generated `data.yaml`
   - Start with YOLOv8n (fastest)
   - Monitor training metrics

3. **Evaluate results:**
   - Check mAP@50 and mAP@50-95
   - Analyze confusion matrix
   - Test on real-world images

---

## 📞 Need Help?

1. Check [README.md](README.md) for detailed documentation
2. Review [Troubleshooting section](README.md#troubleshooting)
3. Inspect the generated `MERGE_REPORT.md`

---

**You're all set! Happy training! 🚀**

*Estimated time to complete: 10-15 minutes*
