from roboflow import Roboflow
rf = Roboflow(api_key="5zBHk22HJVNfPgSIf9Gz")
project = rf.workspace("drone-detection-i4yej").project("drone-detection-lzvig")
version = project.version(4)
dataset = version.download("yolov11")