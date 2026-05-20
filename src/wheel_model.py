import pychrono.core as chrono
import math


# ============================================================
# Base class for all wheel models
# ============================================================
class WheelBase:
    def __init__(self, radius, width, mass):
        self.radius = radius
        self.width = width
        self.mass = mass

    def create_body(self, system, material):
        """Create the Chrono body for this wheel model."""
        raise NotImplementedError


# ============================================================
# Simple cylindrical wheel
# ============================================================
class CylinderWheel(WheelBase):
    def create_body(self, system, material):
        """Create a simple cylindrical wheel."""
        wheel = chrono.ChBodyEasyCylinder(
            chrono.ChAxis_Z,
            self.radius,
            self.width,
            1000,      # density
            True,      # collide
            True,      # visual asset
            material
        )

        wheel.SetMass(self.mass)
        wheel.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
        wheel.SetPos(chrono.ChVector3d(0, self.radius + 0.5, 0))
        wheel.SetRot(chrono.QuatFromAngleZ(math.pi / 2))

        wheel.SetFixed(False)
        wheel.EnableCollision(True)
        system.Add(wheel)

        return wheel


# ============================================================
# Triangular-lug wheel
# ============================================================
class LuggedWheel(WheelBase):
    def __init__(self, radius, width, mass, lug_height, lug_width, lug_count):
        super().__init__(radius, width, mass)
        self.lug_height = lug_height
        self.lug_width = lug_width
        self.lug_count = lug_count

    def create_body(self, system, material):
        """Create a wheel with triangular lugs."""
        # Base cylinder
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
        wheel.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
        wheel.SetPos(chrono.ChVector3d(0, self.radius + 0.5, 0))
        wheel.SetRot(chrono.QuatFromAngleZ(math.pi / 2))

        # Lug mesh
        mesh = chrono.ChTriangleMeshConnected()

        for i in range(self.lug_count):
            angle = 2 * math.pi * i / self.lug_count

            # Base circle position
            cx = self.radius * math.cos(angle)
            cy = self.radius * math.sin(angle)

            # Radial and tangential directions
            nx, ny = math.cos(angle), math.sin(angle)
            tx, ty = -math.sin(angle), math.cos(angle)

            # Z extrusion
            z0 = -self.width * 0.5
            z1 =  self.width * 0.5

            # Triangle base
            v1  = chrono.ChVector3d(cx, cy, z0)
            v2  = chrono.ChVector3d(cx + nx * self.lug_height,
                                    cy + ny * self.lug_height, z0)
            v3  = chrono.ChVector3d(cx + tx * self.lug_width,
                                    cy + ty * self.lug_width, z0)

            # Extruded top
            v1b = chrono.ChVector3d(v1.x, v1.y, z1)
            v2b = chrono.ChVector3d(v2.x, v2.y, z1)
            v3b = chrono.ChVector3d(v3.x, v3.y, z1)

            # Front / back
            mesh.AddTriangle(v1, v2, v3)
            mesh.AddTriangle(v1b, v3b, v2b)

            # Side faces (extrusion)
            mesh.AddTriangle(v1, v1b, v2)
            mesh.AddTriangle(v2, v1b, v2b)

            mesh.AddTriangle(v2, v2b, v3)
            mesh.AddTriangle(v3, v2b, v3b)

            mesh.AddTriangle(v3, v3b, v1)
            mesh.AddTriangle(v1, v3b, v1b)

        # Attach mesh
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


# ============================================================
# Box-lug wheel
# ============================================================
class LuggedWheelBox(WheelBase):
    def __init__(self, radius, width, mass,
                 lug_height, lug_width, lug_count,
                 lug_thickness=None):
        super().__init__(radius, width, mass)
        self.lug_height = lug_height
        self.lug_width = lug_width
        self.lug_count = lug_count
        self.lug_thickness = lug_thickness if lug_thickness is not None else width

    def create_body(self, system, material):
        """Create a wheel with box-shaped lugs."""
        # Base cylinder
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
        wheel.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
        wheel.SetPos(chrono.ChVector3d(0, self.radius + 0.5, 0))
        wheel.SetRot(chrono.QuatFromAngleZ(math.pi / 2))

        # Lug mesh
        mesh = chrono.ChTriangleMeshConnected()

        z0 = -self.lug_thickness * 0.5
        z1 =  self.lug_thickness * 0.5

        for i in range(self.lug_count):
            angle = 2 * math.pi * i / self.lug_count

            cx = self.radius * math.cos(angle)
            cy = self.radius * math.sin(angle)

            nx, ny = math.cos(angle), math.sin(angle)
            tx, ty = -math.sin(angle), math.cos(angle)

            # Radial positions
            p_rad_pos = chrono.ChVector3d(cx + nx * self.lug_height,
                                          cy + ny * self.lug_height, 0)
            p_rad_neg = chrono.ChVector3d(cx, cy, 0)

            # Tangential offsets
            p_tan_pos = chrono.ChVector3d(tx * self.lug_width,
                                          ty * self.lug_width, 0)
            p_tan_neg = chrono.ChVector3d(-tx * self.lug_width,
                                          -ty * self.lug_width, 0)

            # Bottom face
            v1 = chrono.ChVector3d(p_rad_pos.x + p_tan_pos.x,
                                   p_rad_pos.y + p_tan_pos.y, z0)
            v2 = chrono.ChVector3d(p_rad_pos.x + p_tan_neg.x,
                                   p_rad_pos.y + p_tan_neg.y, z0)
            v3 = chrono.ChVector3d(p_rad_neg.x + p_tan_neg.x,
                                   p_rad_neg.y + p_tan_neg.y, z0)
            v4 = chrono.ChVector3d(p_rad_neg.x + p_tan_pos.x,
                                   p_rad_neg.y + p_tan_pos.y, z0)

            # Top face
            v1b = chrono.ChVector3d(v1.x, v1.y, z1)
            v2b = chrono.ChVector3d(v2.x, v2.y, z1)
            v3b = chrono.ChVector3d(v3.x, v3.y, z1)
            v4b = chrono.ChVector3d(v4.x, v4.y, z1)

            # Front / back
            mesh.AddTriangle(v1, v2, v3)
            mesh.AddTriangle(v1, v3, v4)

            mesh.AddTriangle(v1b, v3b, v2b)
            mesh.AddTriangle(v1b, v4b, v3b)

            # Sides
            mesh.AddTriangle(v1, v1b, v2)
            mesh.AddTriangle(v2, v1b, v2b)

            mesh.AddTriangle(v2, v2b, v3)
            mesh.AddTriangle(v3, v2b, v3b)

            mesh.AddTriangle(v3, v3b, v4)
            mesh.AddTriangle(v4, v3b, v4b)

            mesh.AddTriangle(v4, v4b, v1)
            mesh.AddTriangle(v1, v4b, v1b)

        # Attach mesh
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
