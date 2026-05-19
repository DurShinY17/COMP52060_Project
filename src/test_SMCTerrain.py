import pychrono.core as chrono
import pychrono.irrlicht as chronoirr
import pychrono.vehicle as veh
import math

# ----------------------------
# 円柱ホイールのパラメータ
# ----------------------------
radius = 0.3      # 0.3 m
width  = 0.2      # 0.2 m
mass   = 20       # 適当な質量（後で調整可）

# ----------------------------
# システム作成
# ----------------------------
sys = chrono.ChSystemSMC()
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

# ----------------------------
# SCM Terrain の作成
# ----------------------------
terrain = veh.SCMTerrain(sys)

# Terrain は Z-up なので、Y-up の世界に合わせて回転
terrain.SetReferenceFrame(
    chrono.ChCoordsysd(
        chrono.ChVector3d(0, 0, 0),
        chrono.QuatFromAngleX(-math.pi/2)
    )
)

# 土壌パラメータ（ここを変えて沈下量を比較）
terrain.SetSoilParameters(
    2e6,   # Bekker Kphi
    0,     # Bekker Kc
    1.1,   # Bekker n
    0,     # Cohesion
    30,    # Friction angle
    0.01,  # Janosi shear
    2e8,   # Elastic stiffness
    3e4    # Damping
)

# Terrain サイズと解像度
terrain.Initialize(2.0, 2.0, 0.02)

# 可視化モード（pressure / sinkage など切替可能）
terrain.SetPlotType(veh.SCMTerrain.PLOT_SINKAGE, 0, 0.1)

# ----------------------------
# 円柱ホイール（落下物体）
# ----------------------------
material = chrono.ChContactMaterialSMC()

wheel = chrono.ChBodyEasyCylinder(
    chrono.ChAxis_Z,   # 円柱の軸方向
    radius,            # 半径
    width,             # 高さ（幅）
    1000,              # 密度
    True,              # collide
    True,              # visual_asset
    material           # 衝突マテリアル
)

wheel.SetMass(mass)
wheel.SetPos(chrono.ChVector3d(0, radius + 0.5, 0))  # 少し上から落とす
wheel.SetRot(chrono.QuatFromAngleZ(math.pi/2))       # 円柱の軸を横向きに
wheel.SetFixed(False)
sys.Add(wheel)

# ----------------------------
# 可視化
# ----------------------------
vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(sys)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("SCM Terrain - Cylinder Sinkage Test")
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVector3d(1.5, 1.0, 1.5), chrono.ChVector3d(0, 0, 0))
vis.AddTypicalLights()

# ----------------------------
# シミュレーションループ
# ----------------------------
step = 0.002

while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    print("Wheel Position: ", wheel.GetPos().y)  # Y座標を出力して沈下量を確認

    sys.DoStepDynamics(step)
