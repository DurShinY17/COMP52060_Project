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
        mesh = chrono.ChTriangleMeshConnected()

        # --- 円柱のベースメッシュを生成（簡易版） ---
        # 本格的には円柱メッシュを生成するが、まずはラグだけでもOK

        # --- ラグを円周に配置 ---
        for i in range(self.lug_count):
            angle = 2 * math.pi * i / self.lug_count
            x = self.radius * math.cos(angle)
            z = self.radius * math.sin(angle)

            # ラグの四角形を三角形2枚で作る
            # （ここは後で本格的にする）
            v1 = chrono.ChVector3d(x, 0, z)
            v2 = chrono.ChVector3d(x, self.lug_height, z)
            v3 = chrono.ChVector3d(x + self.lug_width, 0, z)

            mesh.AddTriangle(v1, v2, v3)

        # --- ボディ作成 ---
        wheel = chrono.ChBody()
        wheel.SetMass(self.mass)
        wheel.SetInertiaXX(chrono.ChVector3d(1,1,1))
        wheel.SetPos(chrono.ChVector3d(0, self.radius + 0.5, 0))

        # 可視化
        vis = chrono.ChVisualShapeTriangleMesh()
        vis.SetMesh(mesh)
        vis.SetColor(chrono.ChColor(0.3, 0.3, 0.3))
        wheel.AddVisualShape(vis)

        # 衝突形状
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