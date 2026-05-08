import pychrono as chrono
import pychrono.irrlicht as chronoirr

# システム
system = chrono.ChSystemSMC()
system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

# 地面
ground = chrono.ChBodyEasyBox(
    10.0, 0.2, 10.0,
    1000,
    False,  # 可視化 OFF （手動設定）
    True    # 衝突
)
ground.SetPos(chrono.ChVector3d(0, -0.1, 0))
ground.SetFixed(True)

# VisualShape
ground_vis = chrono.ChVisualShapeBox(chrono.ChVector3d(10.0, 0.2, 10.0))

# Material（色）
ground_mat = chrono.ChVisualMaterial()
ground_mat.SetDiffuseColor(chrono.ChColor(0.2, 0.6, 0.2))  # 緑

# ★ ここがあなたの環境で正しい色設定方法
ground_vis.GetMaterials().push_back(ground_mat)

ground.AddVisualShape(ground_vis)

system.Add(ground)

# 車輪
wheel_radius = 0.3
wheel_width = 0.2

wheel = chrono.ChBodyEasyCylinder(
    chrono.ChAxis_Z,   # ← これが正しい
    wheel_radius,
    wheel_width,
    7800,
    False,  # 可視化 OFF （手動設定）
    True
)
wheel.SetPos(chrono.ChVector3d(0, 0.6, 0))
wheel.SetFixed(False)

# VisualShape
wheel_vis = chrono.ChVisualShapeCylinder(0.3, 0.2)

# Material（色）
wheel_mat = chrono.ChVisualMaterial()
wheel_mat.SetDiffuseColor(chrono.ChColor(0.8, 0.2, 0.2))  # 赤

# ★ ここも push_back
wheel_vis.GetMaterials().push_back(wheel_mat)

wheel.AddVisualShape(wheel_vis)

system.Add(wheel)

# 可視化（最小構成）
vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(system)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("Rigid ground wheel drop")
vis.Initialize()   # ← これだけでカメラもライトも自動生成される

# ★ カメラを手動で追加（これが重要）
vis.AddCamera(
    chrono.ChVector3d(2, 1, 2),   # カメラ位置
    chrono.ChVector3d(0, 0, 0)    # 注視点
)

step = 1e-3
while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()
    system.DoStepDynamics(step)
