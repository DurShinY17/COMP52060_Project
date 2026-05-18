import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.irrlicht as irr
import inspect
import csv

print(chrono.__file__)

modules = {
    "core": chrono,
    "vehicle": veh,
    "irrlicht": irr,
}

rows = []

for mod_name, mod in modules.items():
    for name in dir(mod):
        obj = getattr(mod, name)

        # SWIG クラス判定
        if inspect.isclass(obj) and "pychrono" in obj.__module__:
            cls = obj

            # メソッド一覧
            methods = [m for m in dir(cls) if not m.startswith("_")]

            for m in methods:
                rows.append([mod_name, cls.__name__, m])

with open("chrono_api_map.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Module", "Class", "Method"])
    writer.writerows(rows)

print("chrono_api_map.csv を出力しました。")
