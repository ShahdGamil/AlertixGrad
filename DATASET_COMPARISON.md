# Dataset Comparison & Analysis

> Detailed comparison of the 3 source datasets before merging

---

## 📊 Overview Table

| Feature | B1 (cc-tv-footage) | B2 (shoplifting-detection) | B3 (test-make) |
|---------|-------------------|---------------------------|----------------|
| **Total Images** | 2,998 | 7,111 | 1,194 |
| **Original Classes** | 6 | 2 | 2 |
| **Final Classes** | 2 (mapped) | 2 | 2 |
| **Train Split** | 2,095 (70%) | 5,307 (75%) | 1,030 (86%) |
| **Valid Split** | 600 (20%) | 1,064 (15%) | ❌ Missing |
| **Test Split** | 303 (10%) | 740 (10%) | 164 (14%) |
| **File Size (ZIP)** | 454 MB | 529 MB | 83 MB |
| **License** | CC BY 4.0 | CC BY 4.0 | CC BY 4.0 |
| **Version** | v2 | v1 | v1 |

---

## 🎯 Class Analysis

### B1 Dataset - Detailed (6 classes)

**Original Classes:**
1. `Customer-Bagpack` (class 0)
2. `Product` (class 1)
3. `Product-Picked` (class 2)
4. `Shopping-Cart` (class 3)
5. `normal` (class 4)
6. `theft` (class 5)

**Mapping Strategy:**
```
Customer-Bagpack  →  normal (0)  [Legitimate customer with bag]
Product           →  normal (0)  [Product on shelf - normal state]
Shopping-Cart     →  normal (0)  [Using cart - legitimate shopping]
normal            →  normal (0)  [Explicit normal behavior]
Product-Picked    →  theft (1)   [Picking product - suspicious action]
theft             →  theft (1)   [Explicit theft behavior]
```

**Rationale:**
- B1 provides **granular annotations** for understanding shoplifting mechanics
- Useful for **behavior analysis** and **action recognition**
- Maps well to binary classification (normal vs theft)
- `Product-Picked` is considered suspicious → mapped to theft

---

### B2 Dataset - Binary (2 classes)

**Classes:**
1. `normal` (class 0) - Normal shopping behavior
2. `theft` (class 1) - Shoplifting behavior

**Characteristics:**
- ✅ **Largest dataset** (7,111 images)
- ✅ **Simple binary classification**
- ✅ **Best for production** deployment
- ✅ **Proper train/val/test splits**
- ⭐ **Recommended primary dataset**

---

### B3 Dataset - Binary (2 classes)

**Classes:**
1. `normal` (class 0) - Normal shopping behavior
2. `theft` (class 1) - Shoplifting behavior

**Characteristics:**
- ⚠️ **Smallest dataset** (1,194 images)
- ⚠️ **Missing validation split**
- ⚠️ **No labels in train folder** (only images)
- ✅ **Good for augmentation** after fixing

**Issues Handled:**
- Validation split created during merge
- Labels validated and fixed
- Properly integrated into final dataset

---

## 📈 Statistical Comparison

### Image Count Distribution

```
Dataset   Train    Valid    Test     Total
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
B1        2,095    600      303      2,998
B2        5,307    1,064    740      7,111
B3        1,030    ---      164      1,194
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL     8,432    1,664    1,207    11,303
```

### Split Ratios (Original)

```
Dataset   Train    Valid    Test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
B1        70%      20%      10%
B2        75%      15%      10%
B3        86%      0%       14%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Merged    70%      15%      15%  ← Reorganized
```

---

## 🔄 Merging Strategy

### Step 1: Class Harmonization
- B1: Map 6 classes → 2 classes (normal, theft)
- B2: Use as-is (already 2 classes)
- B3: Use as-is (already 2 classes)

### Step 2: Data Combination
- Prefix all files with dataset ID (B1_, B2_, B3_)
- Copy images and labels to temporary location
- Validate all annotations

### Step 3: Split Reorganization
- Collect all images from all splits
- Shuffle randomly (seed=42 for reproducibility)
- Create new 70/15/15 train/val/test splits
- Ensure balanced distribution

### Step 4: Quality Assurance
- Validate bounding box coordinates (0-1 range)
- Check for missing labels
- Identify corrupted images
- Generate quality report

---

## ✅ Advantages of Merging

### 1. **Increased Dataset Size**
- Single dataset: Max 7,111 images
- Merged dataset: **11,303 images** (+59% more data)

### 2. **Diverse Perspectives**
- B1: Detailed behavior annotations
- B2: Large-scale general patterns
- B3: Additional variety

### 3. **Improved Generalization**
- Multiple camera angles
- Different lighting conditions
- Varied store layouts
- More robust model

### 4. **Proper Validation**
- B3's missing validation split fixed
- Consistent 70/15/15 split across all data
- Better evaluation metrics

### 5. **Unified Format**
- Single YOLOv8 configuration
- Consistent class labels
- Standardized preprocessing

---

## ⚠️ Challenges Addressed

### Challenge 1: Class Inconsistency
- **Issue:** B1 has 6 classes vs 2 in B2/B3
- **Solution:** Intelligent class mapping based on behavior
- **Result:** Unified 2-class system

### Challenge 2: Missing Validation (B3)
- **Issue:** B3 has no validation split
- **Solution:** Reorganize all data into proper splits
- **Result:** Balanced 70/15/15 distribution

### Challenge 3: Name Conflicts
- **Issue:** Same image names across datasets
- **Solution:** Prefix with dataset ID (B1_, B2_, B3_)
- **Result:** No conflicts, traceable origins

### Challenge 4: Quality Variations
- **Issue:** Different annotation quality
- **Solution:** Comprehensive validation pipeline
- **Result:** All invalid annotations identified/fixed

---

## 📊 Expected Class Distribution

### Before Mapping (Estimated)

**B1 (6 classes):**
- Customer-Bagpack: ~15-20%
- Product: ~25-30%
- Product-Picked: ~10-15%
- Shopping-Cart: ~5-10%
- normal: ~20-25%
- theft: ~10-15%

**B2 (2 classes):**
- normal: ~60-70%
- theft: ~30-40%

**B3 (2 classes):**
- normal: ~60-70%
- theft: ~30-40%

### After Mapping (Unified)

**Merged Dataset (2 classes):**
- **normal**: ~60-70% of annotations
- **theft**: ~30-40% of annotations

> **Note:** Exact percentages calculated during merge. See `MERGE_REPORT.md` for precise statistics.

---

## 🎯 Best Practices

### When to Use Each Source Dataset Individually

**Use B1 alone when:**
- Researching shoplifting behavior patterns
- Need granular action recognition
- Studying specific object interactions
- Analyzing multi-step theft sequences

**Use B2 alone when:**
- Quick prototyping (largest dataset)
- Binary classification only
- Production deployment (simple model)
- Baseline performance benchmarking

**Use B3 alone when:**
- Testing on smaller dataset
- Quick experiments
- Limited computational resources
- **NOT recommended** due to size and issues

### When to Use Merged Dataset

**Use merged dataset when:**
- Training production models (recommended)
- Maximizing accuracy and generalization
- Need diverse training examples
- Want robust real-world performance
- **This is the recommended approach** ⭐

---

## 📉 Limitations

### Individual Datasets

**B1 Limitations:**
- Smaller size (only 2,998 images)
- Complex class structure
- May overfit with 6 classes

**B2 Limitations:**
- Less detailed annotations
- Binary only (no behavior granularity)

**B3 Limitations:**
- Very small (1,194 images)
- Missing validation split
- Quality issues
- Not suitable for standalone use

### Merged Dataset Limitations

- Different annotation styles may cause inconsistencies
- B1's complex classes simplified (may lose information)
- Requires more preprocessing time
- Larger storage requirements

---

## 🔬 Recommended Use Cases

| Use Case | Recommended Dataset | Reason |
|----------|-------------------|--------|
| Production Deployment | **Merged** | Largest, most diverse, robust |
| Research (Behavior Analysis) | **B1** | Granular 6-class annotations |
| Quick Prototyping | **B2** | Large, clean, simple binary |
| Baseline Comparison | **B2** | Well-balanced, standard split |
| Academic Research | **Merged** | Comprehensive, publishable |
| Real-world Application | **Merged** | Best generalization |

---

## 📋 Merging Checklist

Before merging, ensure:
- [ ] All 3 datasets downloaded and extracted
- [ ] Paths verified in notebook
- [ ] Sufficient disk space (~2GB for merged output)
- [ ] Dependencies installed
- [ ] Class mapping strategy reviewed
- [ ] Split ratios confirmed (70/15/15)

After merging, verify:
- [ ] Total images match expected count
- [ ] All classes mapped correctly
- [ ] No missing labels
- [ ] Bounding boxes valid (0-1 range)
- [ ] Splits are balanced
- [ ] `data.yaml` generated correctly
- [ ] Reports created successfully

---

## 📊 Quality Metrics

### Expected Validation Results

**Good Quality Indicators:**
- ✅ Missing labels: < 1%
- ✅ Invalid annotations: < 0.5%
- ✅ Corrupted images: < 0.1%
- ✅ Class distribution: 60:40 to 70:30 ratio

**Warning Signs:**
- ⚠️ Missing labels: > 5%
- ⚠️ Invalid annotations: > 2%
- ⚠️ Heavily imbalanced classes (> 90:10)
- ⚠️ Many corrupted images (> 1%)

---

## 🎓 Training Recommendations

### Model Selection

- **YOLOv8n**: Fast inference, good for edge devices
- **YOLOv8s**: Balanced speed/accuracy
- **YOLOv8m**: Better accuracy, moderate speed (recommended)
- **YOLOv8l/x**: Best accuracy, slower inference

### Training Tips

1. **Start small**: Train YOLOv8n first (quick feedback)
2. **Monitor metrics**: Watch mAP@50 and mAP@50-95
3. **Use augmentation**: Enabled by default in config
4. **Patience**: Set patience=50 for early stopping
5. **Checkpoints**: Save every 10 epochs
6. **Validation**: Never train on test set

---

**For detailed merge results, see `MERGE_REPORT.md` after running the pipeline.**

---

*Last Updated: 2026-01-03*
