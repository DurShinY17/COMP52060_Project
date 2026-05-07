import pychrono as chrono
import pychrono.irrlicht as chronoirr

# システム
system = chrono.ChSystemSMC()
system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

# 地面
ground = chrono.ChBodyEasyBox(
    10.0, 0.2, 10.0,
    1000,
    True,  # 可視化
    True   # 衝突
)
ground.SetPos(chrono.ChVector3d(0, -0.1, 0))
ground.SetFixed(True)
system.Add(ground)

# 車輪
wheel_radius = 0.3
wheel_width = 0.2

wheel = chrono.ChBodyEasyCylinder(
    chrono.ChAxis_Z,   # ← これが正しい
    wheel_radius,
    wheel_width,
    7800,
    True,
    True
)
wheel.SetPos(chrono.ChVector3d(0, 0.6, 0))
wheel.SetFixed(False)
system.Add(wheel)

# 可視化（最小構成）
vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(system)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("Rigid ground wheel drop")
vis.Initialize()   # ← これだけでカメラもライトも自動生成される

step = 1e-3
while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()
    system.DoStepDynamics(step)
