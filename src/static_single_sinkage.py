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


# ----------------------------
# System and terrain
# ----------------------------
sys = chrono.ChSystemSMC()
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

terrain = veh.SCMTerrain(sys)
terrain.SetReferenceFrame(
    chrono.ChCoordsysd(
        chrono.ChVector3d(0, 0, 0),
        chrono.QuatFromAngleX(-math.pi / 2)
    )
)

# Soil parameters (record these in CSV)
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

terrain.Initialize(2.0, 2.0, 0.02)
terrain.SetPlotType(veh.SCMTerrain.PLOT_SINKAGE, 0, 0.1)

material = chrono.ChContactMaterialSMC()


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

# Initial vertical position (for sinkage)
initial_y = wheel.GetPos().y


# ----------------------------
# CSV logging setup
# ----------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"static_sinkage_{wheel_label}_{timestamp}.csv"

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
    "sinkage",
    "normal_force",
    "contact_area",
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
vis.SetWindowTitle("SCM Terrain - Static Sinkage Test")
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVector3d(1.5, 1.0, 1.5), chrono.ChVector3d(0, 0, 0))
vis.AddTypicalLights()

step = 0.002
time = 0.0


# ----------------------------
# Simulation loop
# ----------------------------
while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    pos = wheel.GetPos()
    force = wheel.GetContactForce()

    # Sinkage (positive when wheel moves downward)
    sinkage = max(0.0, initial_y - pos.y)

    # Normal force (Y-up)
    normal_force = max(0.0, -force.y)

    # Geometric approximation of contact area
    if sinkage > 0.0 and sinkage < radius * 2.0:
        contact_length = 2.0 * math.sqrt(max(0.0, 2.0 * radius * sinkage - sinkage * sinkage))
        contact_area = contact_length * width
    else:
        contact_area = 0.0

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
        sinkage,
        normal_force,
        contact_area,
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
