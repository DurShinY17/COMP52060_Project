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

            # 放射方向
            nx = math.cos(angle)
            ny = math.sin(angle)

            # 接線方向
            tx = -math.sin(angle)
            ty =  math.cos(angle)

            # Z方向の押し出し範囲（中心 ± 幅/2）
            z0 = -self.width * 0.5
            z1 =  self.width * 0.5

            # --- 三角形の元の3点（Z=z0） ---
            v1  = chrono.ChVector3d(cx, cy, z0)
            v2  = chrono.ChVector3d(cx + nx * self.lug_height,
                                    cy + ny * self.lug_height,
                                    z0)
            v3  = chrono.ChVector3d(cx + tx * self.lug_width,
                                    cy + ty * self.lug_width,
                                    z0)

            # --- 押し出し先（Z=z1） ---
            v1b = chrono.ChVector3d(v1.x, v1.y, z1)
            v2b = chrono.ChVector3d(v2.x, v2.y, z1)
            v3b = chrono.ChVector3d(v3.x, v3.y, z1)

            # 前面
            mesh.AddTriangle(v1, v2, v3)

            # 背面
            mesh.AddTriangle(v1b, v3b, v2b)

            # 側面（3つの四角 → 6三角）
            mesh.AddTriangle(v1, v1b, v2)
            mesh.AddTriangle(v2, v1b, v2b)

            mesh.AddTriangle(v2, v2b, v3)
            mesh.AddTriangle(v3, v2b, v3b)

            mesh.AddTriangle(v3, v3b, v1)
            mesh.AddTriangle(v1, v3b, v1b)

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

class LuggedWheelBox(WheelBase):
    def __init__(self, radius, width, mass, lug_height, lug_width, lug_count, lug_thickness=None):
        super().__init__(radius, width, mass)
        self.lug_height = lug_height        # 放射方向の長さ
        self.lug_width = lug_width          # 接線方向の幅
        # self.lug_thickness = lug_thickness  # Z方向の厚み（箱の厚さ）
        self.lug_count = lug_count

        # ★ デフォルトは円柱幅と同じ
        self.lug_thickness = lug_thickness if lug_thickness is not None else width

    def create_body(self, system, material):
        # 1) 円柱ボディ
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

        # 2) ラグ用メッシュ
        mesh = chrono.ChTriangleMeshConnected()

        # Z方向の押し出し（中心 ± 厚み/2）
        z0 = -self.lug_thickness * 0.5
        z1 =  self.lug_thickness * 0.5

        for i in range(self.lug_count):
            angle = 2 * math.pi * i / self.lug_count

            # 円周上の位置（XY平面）
            cx = self.radius * math.cos(angle)
            cy = self.radius * math.sin(angle)

            # 放射方向（外側）
            nx = math.cos(angle)
            ny = math.sin(angle)

            # 接線方向（円周方向）
            tx = -math.sin(angle)
            ty =  math.cos(angle)

            # --- 直方体の8頂点を作る ---
            # 中心点
            base = chrono.ChVector3d(cx, cy, 0)

            # 放射方向 ±
            p_rad_pos = chrono.ChVector3d(cx + nx * self.lug_height,
                                          cy + ny * self.lug_height,
                                          0)
            p_rad_neg = chrono.ChVector3d(cx, cy, 0)

            # 接線方向 ±
            p_tan_pos = chrono.ChVector3d(cx + tx * self.lug_width,
                                          cy + ty * self.lug_width,
                                          0)
            p_tan_neg = chrono.ChVector3d(cx - tx * self.lug_width,
                                          cy - ty * self.lug_width,
                                          0)

            # 直方体の4隅（Z=z0）
            v1 = chrono.ChVector3d(p_rad_pos.x + tx * self.lug_width,
                                   p_rad_pos.y + ty * self.lug_width,
                                   z0)
            v2 = chrono.ChVector3d(p_rad_pos.x - tx * self.lug_width,
                                   p_rad_pos.y - ty * self.lug_width,
                                   z0)
            v3 = chrono.ChVector3d(p_rad_neg.x - tx * self.lug_width,
                                   p_rad_neg.y - ty * self.lug_width,
                                   z0)
            v4 = chrono.ChVector3d(p_rad_neg.x + tx * self.lug_width,
                                   p_rad_neg.y + ty * self.lug_width,
                                   z0)

            # 直方体の4隅（Z=z1）
            v1b = chrono.ChVector3d(v1.x, v1.y, z1)
            v2b = chrono.ChVector3d(v2.x, v2.y, z1)
            v3b = chrono.ChVector3d(v3.x, v3.y, z1)
            v4b = chrono.ChVector3d(v4.x, v4.y, z1)

            # --- 直方体を構成する12三角形 ---
            # 前面
            mesh.AddTriangle(v1, v2, v3)
            mesh.AddTriangle(v1, v3, v4)

            # 背面
            mesh.AddTriangle(v1b, v3b, v2b)
            mesh.AddTriangle(v1b, v4b, v3b)

            # 側面
            mesh.AddTriangle(v1, v1b, v2)
            mesh.AddTriangle(v2, v1b, v2b)

            mesh.AddTriangle(v2, v2b, v3)
            mesh.AddTriangle(v3, v2b, v3b)

            mesh.AddTriangle(v3, v3b, v4)
            mesh.AddTriangle(v4, v3b, v4b)

            mesh.AddTriangle(v4, v4b, v1)
            mesh.AddTriangle(v1, v4b, v1b)

        # 3) 可視化と衝突
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
# wheel = LuggedWheel(0.3, 0.2, 20, lug_height=0.05, lug_width=0.02, lug_count=12).create_body(sys, material)
wheel = LuggedWheelBox(
    0.3, 0.2, 20,
    lug_height=0.05,
    lug_width=0.02,
    lug_count=12
).create_body(sys, material)


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