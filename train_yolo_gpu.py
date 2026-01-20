from ultralytics import YOLO
import torch

def train_yolo():
    # Check GPU
    assert torch.cuda.is_available(), "CUDA not available"
    print("Using GPU:", torch.cuda.get_device_name(0))

    # Load model
    model = YOLO("yolov8n.pt")

    # Train
    model.train(
    data="cc-tv-footage-annotation-b8-lcysc-b1-2/data.yaml",
    epochs=120,          # 🔥 very important
    imgsz=768,           # better localization
    batch=16,            # if OOM → change to 8
    device=0,
    workers=4,
    optimizer="SGD",     # YOLO works best with SGD
    lr0=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    patience=30,
    amp=True,            # SAFE for GTX 1650
    pretrained=True
)

if __name__ == "__main__":
    train_yolo()
