import pychrono.core as chrono
import pychrono.irrlicht as chronoirr
import pychrono.vehicle as veh
import math

from wheel_model import LuggedWheel, LuggedWheelBox

# ============================================================
# Step2: ホイールモデル選択
#   "cylinder" → 円柱ホイール（今までのやつ）
#   "mesh"     → メッシュホイール（tractor_wheel.obj）
# ============================================================
WHEEL_TYPE = "mesh"   # 必要に応じて "mesh" に変更

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
# ホイール生成（Step2）
# ----------------------------
material = chrono.ChContactMaterialSMC()

"""
if WHEEL_TYPE == "cylinder":
    # 円柱ホイール
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
    # 慣性はとりあえず仮（後で理論値にしてもいい）
    wheel.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
    wheel.SetPos(chrono.ChVector3d(0, radius + 0.5, 0))
    wheel.SetRot(chrono.QuatFromAngleZ(math.pi/2))

elif WHEEL_TYPE == "mesh":
    # メッシュホイール（tractor_wheel.obj）
    mesh = chrono.ChTriangleMeshConnected()
    mesh.LoadWavefrontMesh(chrono.GetChronoDataFile('models/tractor_wheel/tractor_wheel.obj'))

    wheel = chrono.ChBody()
    wheel.SetMass(20)
    wheel.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
    wheel.SetPos(chrono.ChVector3d(0, 0.8, 0))  # 少し上から落とす

    # 可視化
    vis_shape = chrono.ChVisualShapeTriangleMesh()
    vis_shape.SetMesh(mesh)
    vis_shape.SetColor(chrono.ChColor(0.3, 0.3, 0.3))
    wheel.AddVisualShape(vis_shape)

    # 衝突形状
    body_ct_shape = chrono.ChCollisionShapeTriangleMesh(
        material,  # contact material
        mesh,      # mesh
        False,     # static?
        False,     # convex?
        0.01       # thickness
    )
    wheel.AddCollisionShape(body_ct_shape)

else:
    raise RuntimeError("Unknown WHEEL_TYPE: " + WHEEL_TYPE)
"""

# ----------------------------
# ホイール生成（クラス呼び出し）
# ----------------------------
wheel = LuggedWheelBox(
    radius=0.3,
    width=0.2,
    mass=20,
    lug_height=0.05,
    lug_width=0.02,
    lug_count=12
).create_body(sys, material)

# wheel.SetFixed(False)
# wheel.EnableCollision(True)
# sys.Add(wheel)

# ----------------------------
# 可視化
# ----------------------------
vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(sys)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("SCM Terrain - Step2 Wheel Model Test")
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

    print("Wheel Position Y: ", wheel.GetPos().y)

    sys.DoStepDynamics(step)
