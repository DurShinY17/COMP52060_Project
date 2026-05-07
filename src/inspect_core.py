import pychrono as chrono
import csv

# 取得
core_items = dir(chrono)

# CSV に保存
with open("chrono_core_api.csv", "w", newline="") as f:
    writer = csv.writer(f)
    for item in core_items:
        writer.writerow([item])

print("chrono_core_api.csv に出力しました。")
