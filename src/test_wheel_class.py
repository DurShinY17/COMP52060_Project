import pychrono as chrono
import pychrono.irrlicht as chronoirr
import math

class WheelBase:
    def __init__(self, radius, width, mass):
        self.radius = radius
        self.width = width
        self.mass = mass

    def create_body(self, system, material):
        raise NotImplementedError

class CylinderWheel(WheelBase):
    def create_body(self, system, material):
        wheel = chrono.ChBodyEasyCylinder(
            chrono.ChAxis_Z,
            self.radius,
            self.width,
            1000,
            True,
            True,
            material
        )
        wheel.SetMass(self.mass)
        wheel.SetInertiaXX(chrono.ChVector3d(1,1,1))
        wheel.SetPos(chrono.ChVector3d(0, self.radius + 0.5, 0))
        wheel.SetRot(chrono.QuatFromAngleZ(math.pi/2))
        wheel.SetFixed(False)
        wheel.EnableCollision(True)
        system.Add(wheel)
        return wheel

class LuggedWheel(WheelBase):
    def __init__(self, radius, width, mass, lug_height, lug_width, lug_count):
        super().__init__(radius, width, mass)
        self.lug_height = lug_height
        self.lug_width = lug_width
        self.lug_count = lug_count

    def create_body(self, system, material):
        # 1) まず円柱ボディを作る
        wheel = chrono.ChBodyEasyCylinder(
            chrono.ChAxis_Z,
            self.radius,
            self.width,
            1000,
            True,
            True,
            material
        )
        wheel.SetMass(self.mass)
        wheel.SetInertiaXX(chrono.ChVector3d(1,1,1))
        wheel.SetPos(chrono.ChVector3d(0, self.radius + 0.5, 0))
        wheel.SetRot(chrono.QuatFromAngleZ(math.pi/2))

        # 2) ラグ用メッシュを作る
        mesh = chrono.ChTriangleMeshConnected()
        for i in range(self.lug_count):
            angle = 2 * math.pi * i / self.lug_count

            # 円周上の位置（XY平面）
            cx = self.radius * math.cos(angle)
            cy = self.radius * math.sin(angle)
            cz = 0

            # 放射方向の単位ベクトル
            nx = math.cos(angle)
            ny = math.sin(angle)
            nz = 0

            # ラグの根元（円周上）
            v1 = chrono.ChVector3d(cx, cy, cz)

            # ラグを外側に伸ばす（放射方向）
            v2 = chrono.ChVector3d(
                cx + nx * self.lug_height,
                cy + ny * self.lug_height,
                cz
            )

            # ラグの幅方向（接線方向）
            tx = -math.sin(angle)
            ty =  math.cos(angle)
            tz = 0

            v3 = chrono.ChVector3d(
                cx + tx * self.lug_width,
                cy + ty * self.lug_width,
                cz
            )

            mesh.AddTriangle(v1, v2, v3)

        # 3) ラグメッシュを同じボディに載せる
        vis = chrono.ChVisualShapeTriangleMesh()
        vis.SetMesh(mesh)
        vis.SetColor(chrono.ChColor(0.3, 0.3, 0.3))
        wheel.AddVisualShape(vis)

        col = chrono.ChCollisionShapeTriangleMesh(material, mesh, False, False, 0.01)
        wheel.AddCollisionShape(col)

        wheel.SetFixed(False)
        wheel.EnableCollision(True)
        system.Add(wheel)
        return wheel

# ----------------------------
# システム作成
# ----------------------------
sys = chrono.ChSystemSMC()
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

material = chrono.ChContactMaterialSMC()

# wheel = CylinderWheel(0.3, 0.2, 20).create_body(sys, material)
wheel = LuggedWheel(0.3, 0.2, 20, lug_height=0.05, lug_width=0.02, lug_count=12).create_body(sys, material)

wheel.SetFixed(False)
wheel.EnableCollision(True)
sys.Add(wheel)

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

while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()