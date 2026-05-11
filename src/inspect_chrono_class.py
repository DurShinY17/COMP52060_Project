import pychrono as chrono
import inspect
import csv

chrono_classes = []

for name in dir(chrono):
    obj = getattr(chrono, name)
    if inspect.isclass(obj):
        # SWIG 生成クラスは __module__ に "pychrono" を含む
        if "pychrono" in obj.__module__:
            chrono_classes.append((name, obj.__module__))

# irrlicht
try:
    import pychrono.irrlicht as irr
    irr_classes = [
        (name, getattr(irr, name).__module__)
        for name in dir(irr)
        if inspect.isclass(getattr(irr, name)) and "pychrono" in getattr(irr, name).__module__
    ]
except ImportError:
    irr_classes = []

# vehicle
try:
    import pychrono.vehicle as veh
    veh_classes = [
        (name, getattr(veh, name).__module__)
        for name in dir(veh)
        if inspect.isclass(getattr(veh, name)) and "pychrono" in getattr(veh, name).__module__
    ]
except ImportError:
    veh_classes = []

with open("chrono_class_list_full.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["ClassName", "Module"])

    for cls, mod in chrono_classes:
        writer.writerow([cls, mod])

    for cls, mod in irr_classes:
        writer.writerow([cls, mod])

    for cls, mod in veh_classes:
        writer.writerow([cls, mod])

print("chrono_class_list_full.csv を出力しました。")
