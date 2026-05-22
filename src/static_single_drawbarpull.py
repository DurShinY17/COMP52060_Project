import csv
import math
from datetime import datetime

import pychrono.core as chrono
import pychrono.irrlicht as chronoirr
import pychrono.vehicle as veh

from wheel_model import CylinderWheel, LuggedWheel, LuggedWheelBox


# ----------------------------
# Wheel configuration
# ----------------------------
WHEEL_TYPE = "lug_box"   # "cylinder", "lug_tri", "lug_box"

radius = 0.3
width  = 0.2
mass   = 20

lug_height    = 0.05
lug_width     = 0.02
lug_count     = 12
lug_thickness = None  # default = width

# Tow speed and duration
TOW_SPEED = 0.1   # m/s
END_TIME  = 5.0   # s


# ----------------------------
# System and terrain
# ----------------------------
sys = chrono.ChSystemSMC()
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

terrain = veh.SCMTerrain(sys)
"""
terrain.SetReferenceFrame(
    chrono.ChCoordsysd(
        chrono.ChVector3d(0, 0, 0),
        chrono.QuatFromAngleX(-math.pi / 2)
    )
)
"""
terrain.SetReferenceFrame(chrono.ChCoordsysd(chrono.VNULL, 
                                                chrono.QuatFromAngleX(-chrono.CH_PI_2)))

# Soil parameters
soil_Kphi     = 2e6
soil_Kc       = 0
soil_n        = 1.1
soil_cohesion = 0
soil_friction = 30
soil_janosi   = 0.01
soil_elasticK = 2e8
soil_dampingR = 3e4

terrain.SetSoilParameters(
    soil_Kphi,
    soil_Kc,
    soil_n,
    soil_cohesion,
    soil_friction,
    soil_janosi,
    soil_elasticK,
    soil_dampingR
)

terrain.Initialize(8.0, 4.0, 0.02)  # X方向に長い地形を作る
terrain.SetPlotType(veh.SCMTerrain.PLOT_SINKAGE, 0, 0.1)

material = chrono.ChContactMaterialSMC()


# ----------------------------
# Ground and tow body
# ----------------------------
ground = chrono.ChBody()
ground.SetFixed(True)
sys.Add(ground)

tow = chrono.ChBody()
tow.SetMass(1.0)
tow.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
tow.SetPos(chrono.ChVector3d(0, radius + 0.5, 0))
tow.SetFixed(False)
shape = chrono.ChVisualShapeBox(chrono.ChVector3d(0.2, 0.2, 0.2))
tow.AddVisualShape(shape)
sys.Add(tow)


# ----------------------------
# Wheel creation
# ----------------------------
if WHEEL_TYPE == "cylinder":
    wheel = CylinderWheel(radius, width, mass).create_body(sys, material)
    wheel_label = "cylinder"
    lug_params = dict(lug_height=0, lug_width=0, lug_count=0, lug_thickness=0)

elif WHEEL_TYPE == "lug_tri":
    wheel = LuggedWheel(radius, width, mass,
                        lug_height=lug_height,
                        lug_width=lug_width,
                        lug_count=lug_count).create_body(sys, material)
    wheel_label = "lug_triangle"
    lug_params = dict(lug_height=lug_height,
                      lug_width=lug_width,
                      lug_count=lug_count,
                      lug_thickness=0)

elif WHEEL_TYPE == "lug_box":
    wheel = LuggedWheelBox(radius, width, mass,
                           lug_height=lug_height,
                           lug_width=lug_width,
                           lug_count=lug_count,
                           lug_thickness=lug_thickness).create_body(sys, material)
    wheel_label = "lug_box"
    lug_params = dict(lug_height=lug_height,
                      lug_width=lug_width,
                      lug_count=lug_count,
                      lug_thickness=(lug_thickness if lug_thickness is not None else width))
else:
    raise RuntimeError(f"Unknown WHEEL_TYPE: {WHEEL_TYPE}")

# Initial vertical position
initial_y = wheel.GetPos().y
initial_x = wheel.GetPos().x


"""
# ----------------------------
# Constrain wheel to tow (no rotation, same pose)
# ----------------------------
link_wheel_tow = chrono.ChLinkLockLock()
link_wheel_tow.Initialize(wheel, tow, chrono.ChFramed(wheel.GetPos(), wheel.GetRot()))
sys.Add(link_wheel_tow)
"""

# ----------------------------
# Constrain wheel to tow (no rotation, same pose)
# ----------------------------
link_wheel_tow = chrono.ChLinkMateGeneric(
    True,   # X translation: tow と同じXにする
    False,  # Y translation: 自由（沈み込みOK）
    True,   # Z translation: 横ずれ禁止
    True,   # Rx locked（回転禁止）
    True,   # Ry locked
    True    # Rz locked
)

frame_w = chrono.ChFramed(wheel.GetPos(), wheel.GetRot())
frame_t = chrono.ChFramed(tow.GetPos(),   tow.GetRot())

link_wheel_tow.Initialize(
    wheel,
    tow,
    False,      # 絶対座標
    frame_w,
    frame_t
)

sys.Add(link_wheel_tow)

# ----------------------------
# Prismatic joint + linear motor (tow vs ground)
# ----------------------------
# X軸だけ自由にする Generic プリズマティック
slide = chrono.ChLinkMateGeneric(
    False,  # X translation free
    True,   # Y locked
    True,   # Z locked
    True,   # Rx locked
    True,   # Ry locked
    True    # Rz locked
)

# ローカルZ軸を world X に向ける
point = tow.GetPos()
dir   = chrono.ChVector3d(1, 0, 0)  # X方向

slide.Initialize(ground, tow, False, point, point, dir, dir)
sys.Add(slide)


# Linear motor to move tow along X
motor = chrono.ChLinkMotorLinearPosition()

rot = chrono.QuatFromAngleY(chrono.CH_PI_2)
motor.Initialize(ground, tow, chrono.ChFramed(point, rot))

# Prescribed motion: x(t) = v * t
motion = chrono.ChFunctionRamp(0.0, TOW_SPEED)
motor.SetMotionFunction(motion)
sys.Add(motor)


# ----------------------------
# CSV logging
# ----------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"drawbar_{wheel_label}_{timestamp}.csv"

csv_file = open(csv_filename, "w", newline="")
csv_writer = csv.writer(csv_file)

csv_writer.writerow([
    "time",
    "wheel_type",
    "radius",
    "width",
    "mass",
    "lug_height",
    "lug_width",
    "lug_count",
    "lug_thickness",
    "displacement",
    "drawbar_pull",
    "normal_force",
    "sinkage",
    "soil_Kphi",
    "soil_Kc",
    "soil_n",
    "soil_cohesion",
    "soil_friction",
    "soil_janosi",
    "soil_elasticK",
    "soil_dampingR"
])


# ----------------------------
# Visualization
# ----------------------------
vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(sys)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("SCM Terrain - Drawbar Pull Test")
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVector3d(2.0, 1.0, 2.0), chrono.ChVector3d(0, 0, 0))
vis.AddTypicalLights()

step = 0.002
time = 0.0


# ----------------------------
# Simulation loop
# ----------------------------
while vis.Run() and time < END_TIME:
    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    pos = wheel.GetPos()
    force = wheel.GetContactForce()

    # Displacement along X
    displacement = pos.x - initial_x

    # Drawbar pull (X direction)
    drawbar_pull = -force.x   # soil resists motion

    # Normal force (Y direction)
    normal_force = max(0.0, -force.y)

    # Sinkage
    sinkage = max(0.0, initial_y - pos.y)

    csv_writer.writerow([
        time,
        wheel_label,
        radius,
        width,
        mass,
        lug_params["lug_height"],
        lug_params["lug_width"],
        lug_params["lug_count"],
        lug_params["lug_thickness"],
        displacement,
        drawbar_pull,
        normal_force,
        sinkage,
        soil_Kphi,
        soil_Kc,
        soil_n,
        soil_cohesion,
        soil_friction,
        soil_janosi,
        soil_elasticK,
        soil_dampingR
    ])

    sys.DoStepDynamics(step)
    time += step

csv_file.close()
