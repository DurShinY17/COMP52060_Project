import csv

# モジュール読み込み
import pychrono as chrono

# irrlicht（存在しない場合もある）
try:
    import pychrono.irrlicht as irr
    irr_available = True
except ImportError:
    irr_available = False

# vehicle（存在しない場合もある）
try:
    import pychrono.vehicle as veh
    veh_available = True
except ImportError:
    veh_available = False

# API 収集
core_items = set(dir(chrono))
irr_items = set(dir(irr)) if irr_available else set()
veh_items = set(dir(veh)) if veh_available else set()

# 全 API のユニオン
all_items = sorted(core_items | irr_items | veh_items)

# CSV 出力
with open("chrono_api_map.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["API_Name", "Module"])  # ヘッダ

    for item in all_items:
        modules = []
        if item in core_items:
            modules.append("CORE")
        if item in irr_items:
            modules.append("IRR")
        if item in veh_items:
            modules.append("VEH")

        writer.writerow([item, ", ".join(modules)])

print("chrono_api_map.csv を出力しました。")
