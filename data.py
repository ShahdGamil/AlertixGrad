
from roboflow import Roboflow
rf = Roboflow(api_key="c7EdxncCd4UuZPz6saCQ")
project = rf.workspace("grad-lnwh2").project("cc-tv-footage-annotation-b8-lcysc-b1-wutkr")
version = project.version(2)
dataset = version.download("yolov8")
                