import ctypes
from pathlib import Path
from unittest import TestCase

from api_data_types import Float3D, _STypes, _CameraInfoParameterizedEXT, Float2D, _MeshInfoSurfaceTriangles, \
    CategoryFlags, HASH, _LightInfoSphereEXT, FilterModes, WrapModes, _MaterialInfoOpaqueEXT, BlendTypes, \
    AlphaTestTypes, _MaterialInfoOpaqueSubsurfaceEXT, _MaterialInfoTranslucentEXT, _MaterialInfoPortalEXT
from components import Camera, CameraTypes, Vertex, MeshSurface, Mesh, Transform, MeshInstance, LightShapingInfo, Light, \
    SphereLight, Material, OpacityPBR, OpacitySSSData, TranslucentPBR, Portal, SkinningData
from exceptions import WrongSkinningDataCount, MissmatchingSkinningDataArrays


class TestCamera(TestCase):
    def assertAlmostEqualFloat3D(self, first: Float3D, second: Float3D, places: int = 5):
        self.assertAlmostEqual(first.x, second.x, places)
        self.assertAlmostEqual(first.y, second.y, places)
        self.assertAlmostEqual(first.z, second.z, places)

    def test_default_initialization(self):
        camera = Camera()
        camera_info = camera.as_struct()

        self.assertEqual(camera_info.sType, _STypes.CAMERA_INFO)
        self.assertNotEqual(camera_info.pNext, 0)
        self.assertEqual(camera_info.type, CameraTypes.WORLD)

        cam_params_info = ctypes.cast(camera_info.pNext, ctypes.POINTER(_CameraInfoParameterizedEXT)).contents
        self.assertEqual(cam_params_info.sType, _STypes.CAMERA_INFO_PARAMETERIZED_EXT)
        self.assertAlmostEqualFloat3D(cam_params_info.position, Float3D(0, 0, 0))
        self.assertAlmostEqualFloat3D(cam_params_info.forward, Float3D(0, 0, 1))
        self.assertAlmostEqualFloat3D(cam_params_info.up, Float3D(0, 1, 0))
        self.assertAlmostEqualFloat3D(cam_params_info.right, Float3D(1, 0, 0))
        self.assertEqual(cam_params_info.fovYInDegrees, 70)
        self.assertAlmostEqual(cam_params_info.aspect, 16.0/9.0, 5)
        self.assertAlmostEqual(cam_params_info.nearPlane, 0.1, 5)
        self.assertAlmostEqual(cam_params_info.farPlane, 1000, 5)

    def test_custom_initialization(self):
        camera = Camera(
            cam_type=CameraTypes.SKY,
            position=Float3D(3.1415, 550.32, 7.4),
            forward=Float3D(0, 1, 1),
            up=Float3D(1, 1, 0),
            right=Float3D(1, 0, 1),
            fov_y=90,
            aspect=32.0 / 9.0,
            near_plane=0.5,
            far_plane=1500
        )
        camera_info = camera.as_struct()

        self.assertEqual(camera_info.sType, _STypes.CAMERA_INFO)
        self.assertNotEqual(camera_info.pNext, 0)
        self.assertEqual(camera_info.type, CameraTypes.SKY)

        cam_params_info = ctypes.cast(camera_info.pNext, ctypes.POINTER(_CameraInfoParameterizedEXT)).contents
        self.assertEqual(cam_params_info.sType, _STypes.CAMERA_INFO_PARAMETERIZED_EXT)
        self.assertAlmostEqualFloat3D(cam_params_info.position, Float3D(3.1415, 550.32, 7.4))
        self.assertAlmostEqualFloat3D(cam_params_info.forward, Float3D(0, 1, 1))
        self.assertAlmostEqualFloat3D(cam_params_info.up, Float3D(1, 1, 0))
        self.assertAlmostEqualFloat3D(cam_params_info.right, Float3D(1, 0, 1))
        self.assertEqual(cam_params_info.fovYInDegrees, 90)
        self.assertAlmostEqual(cam_params_info.aspect, 32.0 / 9.0, 5)
        self.assertAlmostEqual(cam_params_info.nearPlane, 0.5, 5)
        self.assertAlmostEqual(cam_params_info.farPlane, 1500, 5)


class TestVertex(TestCase):
    def test_default_initialization(self):
        vertex = Vertex()
        vertex_struct = vertex.as_struct()

        self.assertAlmostEqual(vertex_struct.position[0], 0, 5)
        self.assertAlmostEqual(vertex_struct.position[1], 0, 5)
        self.assertAlmostEqual(vertex_struct.position[2], 0, 5)
        self.assertAlmostEqual(vertex_struct.normal[0], 0, 5)
        self.assertAlmostEqual(vertex_struct.normal[1], 0, 5)
        self.assertAlmostEqual(vertex_struct.normal[2], 1, 5)
        self.assertAlmostEqual(vertex_struct.texcoord[0], 0, 5)
        self.assertAlmostEqual(vertex_struct.texcoord[1], 0, 5)
        self.assertEqual(vertex_struct.color, 0XFFFFFFFF)

    def test_custom_initialization(self):
        vertex = Vertex(
            position=Float3D(3.1415, 92.65, 35.89),
            normal=Float3D(2.14, 3.14, -0.5),
            texcoord=Float2D(-0.13, 0.3),
            color=0XA2A3A4,
        )
        vertex_struct = vertex.as_struct()

        self.assertAlmostEqual(vertex_struct.position[0], 3.1415, 5)
        self.assertAlmostEqual(vertex_struct.position[1], 92.65, 5)
        self.assertAlmostEqual(vertex_struct.position[2], 35.89, 5)
        self.assertAlmostEqual(vertex_struct.normal[0], 2.14, 5)
        self.assertAlmostEqual(vertex_struct.normal[1], 3.14, 5)
        self.assertAlmostEqual(vertex_struct.normal[2], -0.5, 5)
        self.assertAlmostEqual(vertex_struct.texcoord[0], -0.13, 5)
        self.assertAlmostEqual(vertex_struct.texcoord[1], 0.3, 5)
        self.assertEqual(vertex_struct.color, 0XA2A3A4)


class TestSkinningData(TestCase):
    def test_python_ctypes_round_trip(self):
        skinning_data = SkinningData(
            bones_per_vertex=2,
            blend_weights=[0.1, 0.9, 0.3, 0.7],  # 2 vertices, 2 bones_per_vertex
            blend_indices=[3, 7, 4, 8],  # 2 vertices, 2 bones_per_vertex
        )
        skinning_struct = skinning_data.as_struct()

        self.assertEqual(skinning_struct.bonesPerVertex, 2)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[0], 0.1, 4)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[1], 0.9, 4)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[2], 0.3, 4)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[3], 0.7, 4)
        self.assertEqual(skinning_struct.blendWeights_count, 4)
        self.assertEqual(skinning_struct.blendIndices_values[0], 3)
        self.assertEqual(skinning_struct.blendIndices_values[1], 7)
        self.assertEqual(skinning_struct.blendIndices_values[2], 4)
        self.assertEqual(skinning_struct.blendIndices_values[3], 8)
        self.assertEqual(skinning_struct.blendIndices_count, 4)

    def test_blending_weights_not_multiple_of_bones_per_vertex_should_raise_exception(self):
        with self.assertRaises(MissmatchingSkinningDataArrays):
            SkinningData(
                bones_per_vertex=2,
                blend_weights=[0.1, 0.9, 0.3, 0.7, 0.5],  # 2 vertices, 2 bones_per_vertex
                blend_indices=[3, 7, 4, 8],  # 2 vertices, 2 bones_per_vertex
            )

    def test_blending_indices_not_multiple_of_bones_per_vertex_should_raise_exception(self):
        with self.assertRaises(MissmatchingSkinningDataArrays):
            SkinningData(
                bones_per_vertex=2,
                blend_weights=[0.1, 0.9, 0.3, 0.7],  # 2 vertices, 2 bones_per_vertex
                blend_indices=[3, 7, 4, 8, 9],  # 2 vertices, 2 bones_per_vertex
            )

    def test_blending_indices_count_missmatching_blend_weights_count_should_raise_exception(self):
        with self.assertRaises(MissmatchingSkinningDataArrays):
            SkinningData(
                bones_per_vertex=2,
                blend_weights=[0.1, 0.9, 0.3, 0.7, 0.9, 0.1],  # 2 vertices, 2 bones_per_vertex
                blend_indices=[3, 7, 4, 8, 9],  # 2 vertices, 2 bones_per_vertex
            )


class TestMeshSurface(TestCase):
    def test_python_ctypes_round_trip(self):
        vertices = [
            Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct(),
            Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1), color=0x0).as_struct(),
            Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct()
        ]
        surface = MeshSurface(vertices=vertices, indices=[0, 1, 2])
        surface_struct = surface.as_struct()

        self.assertEqual(len(surface.vertex_array), 3)
        self.assertEqual(len(surface.index_array), 3)

        self.assertEqual(surface_struct.indices_count, 3)
        self.assertEqual(surface_struct.indices_values[0], 0)
        self.assertEqual(surface_struct.indices_values[1], 1)
        self.assertEqual(surface_struct.indices_values[2], 2)

        self.assertEqual(surface_struct.vertices_count, 3)

        vertex0 = surface_struct.vertices_values[0]
        self.assertAlmostEqual(vertex0.position[0], 5, 5)
        self.assertAlmostEqual(vertex0.position[1], -5, 5)
        self.assertAlmostEqual(vertex0.position[2], 10, 5)
        self.assertAlmostEqual(vertex0.normal[0], 0, 5)
        self.assertAlmostEqual(vertex0.normal[1], 0, 5)
        self.assertAlmostEqual(vertex0.normal[2], -1, 5)
        self.assertAlmostEqual(vertex0.texcoord[0], 0.2, 5)
        self.assertAlmostEqual(vertex0.texcoord[1], 0.1, 5)
        self.assertEqual(vertex0.color, 0XFFFFFFFF)

        vertex1 = surface_struct.vertices_values[1]
        self.assertAlmostEqual(vertex1.position[0], 0, 5)
        self.assertAlmostEqual(vertex1.position[1], 5, 5)
        self.assertAlmostEqual(vertex1.position[2], 10, 5)
        self.assertAlmostEqual(vertex1.normal[0], 0, 5)
        self.assertAlmostEqual(vertex1.normal[1], 0, 5)
        self.assertAlmostEqual(vertex1.normal[2], -1, 5)
        self.assertAlmostEqual(vertex1.texcoord[0], 0.2, 5)
        self.assertAlmostEqual(vertex1.texcoord[1], 0.1, 5)
        self.assertEqual(vertex1.color, 0X0)

        vertex2 = surface_struct.vertices_values[2]
        self.assertAlmostEqual(vertex2.position[0], -5, 5)
        self.assertAlmostEqual(vertex2.position[1], -5, 5)
        self.assertAlmostEqual(vertex2.position[2], 10, 5)
        self.assertAlmostEqual(vertex2.normal[0], 0, 5)
        self.assertAlmostEqual(vertex2.normal[1], 0, 5)
        self.assertAlmostEqual(vertex2.normal[2], -1, 5)
        self.assertAlmostEqual(vertex2.texcoord[0], 0.2, 5)
        self.assertAlmostEqual(vertex2.texcoord[1], 0.1, 5)
        self.assertEqual(vertex2.color, 0XFFFFFFFF)

    def test_with_skinning_data(self):
        vertices = [
            Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct(),
            Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1), color=0x0).as_struct(),
            Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct()
        ]
        skinning_data = SkinningData(
            bones_per_vertex=2,
            blend_weights=[0.1, 0.9, 0.3, 0.7, 0.5, 0.5],  # 3 vertices, 2 bones_per_vertex
            blend_indices=[3, 7, 4, 8, 0, 1],  # 3 vertices, 2 bones_per_vertex
        )
        surface = MeshSurface(vertices=vertices, indices=[0, 1, 2], skinning_data=skinning_data)
        surface_struct = surface.as_struct()
        self.assertEqual(surface_struct.skinning_hasvalue, 1)

        skinning_struct = surface_struct.skinning_value
        self.assertEqual(skinning_struct.bonesPerVertex, 2)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[0], 0.1, 4)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[1], 0.9, 4)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[2], 0.3, 4)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[3], 0.7, 4)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[4], 0.5, 4)
        self.assertAlmostEqual(skinning_struct.blendWeights_values[5], 0.5, 4)
        self.assertEqual(skinning_struct.blendWeights_count, 6)
        self.assertEqual(skinning_struct.blendIndices_values[0], 3)
        self.assertEqual(skinning_struct.blendIndices_values[1], 7)
        self.assertEqual(skinning_struct.blendIndices_values[2], 4)
        self.assertEqual(skinning_struct.blendIndices_values[3], 8)
        self.assertEqual(skinning_struct.blendIndices_values[4], 0)
        self.assertEqual(skinning_struct.blendIndices_values[5], 1)
        self.assertEqual(skinning_struct.blendIndices_count, 6)

    def test_with_wrong_skinning_data_count_should_raise_exception(self):
        vertices = [
            Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct(),
            Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1), color=0x0).as_struct(),
            Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct()
        ]
        skinning_data = SkinningData(
            bones_per_vertex=2,
            blend_weights=[0.1, 0.9, 0.3, 0.7],  # 2 vertices, 2 bones_per_vertex
            blend_indices=[3, 7, 4, 8],  # 2 vertices, 2 bones_per_vertex
        )
        with self.assertRaises(WrongSkinningDataCount):
            MeshSurface(vertices=vertices, indices=[0, 1, 2], skinning_data=skinning_data)

    # TODO: Test materials.


class TestMesh(TestCase):
    def test_python_ctypes_round_trip(self):
        vertices = [
            Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct(),
            Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1), color=0x0).as_struct(),
            Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct()
        ]
        surface = MeshSurface(vertices=vertices, indices=[0, 1, 2])
        mesh = Mesh(surfaces=[surface.as_struct()], mesh_hash=0x1234)
        mesh_struct = mesh.as_struct()
        self.assertEqual(mesh.handle.value, None)
        self.assertEqual(mesh_struct.sType, _STypes.MESH_INFO)
        self.assertEqual(mesh_struct.pNext, None)
        self.assertEqual(mesh_struct.hash, 0x1234)
        self.assertEqual(mesh_struct.surfaces_count, 1)

        surface_struct = mesh_struct.surfaces_values[0]
        self.assertEqual(surface_struct.indices_count, 3)
        self.assertEqual(surface_struct.indices_values[0], 0)
        self.assertEqual(surface_struct.indices_values[1], 1)
        self.assertEqual(surface_struct.indices_values[2], 2)

        self.assertEqual(surface_struct.vertices_count, 3)

        vertex0 = surface_struct.vertices_values[0]
        self.assertAlmostEqual(vertex0.position[0], 5, 5)
        self.assertAlmostEqual(vertex0.position[1], -5, 5)
        self.assertAlmostEqual(vertex0.position[2], 10, 5)
        self.assertAlmostEqual(vertex0.normal[0], 0, 5)
        self.assertAlmostEqual(vertex0.normal[1], 0, 5)
        self.assertAlmostEqual(vertex0.normal[2], -1, 5)
        self.assertAlmostEqual(vertex0.texcoord[0], 0.2, 5)
        self.assertAlmostEqual(vertex0.texcoord[1], 0.1, 5)
        self.assertEqual(vertex0.color, 0XFFFFFFFF)

        vertex1 = surface_struct.vertices_values[1]
        self.assertAlmostEqual(vertex1.position[0], 0, 5)
        self.assertAlmostEqual(vertex1.position[1], 5, 5)
        self.assertAlmostEqual(vertex1.position[2], 10, 5)
        self.assertAlmostEqual(vertex1.normal[0], 0, 5)
        self.assertAlmostEqual(vertex1.normal[1], 0, 5)
        self.assertAlmostEqual(vertex1.normal[2], -1, 5)
        self.assertAlmostEqual(vertex1.texcoord[0], 0.2, 5)
        self.assertAlmostEqual(vertex1.texcoord[1], 0.1, 5)
        self.assertEqual(vertex1.color, 0X0)

        vertex2 = surface_struct.vertices_values[2]
        self.assertAlmostEqual(vertex2.position[0], -5, 5)
        self.assertAlmostEqual(vertex2.position[1], -5, 5)
        self.assertAlmostEqual(vertex2.position[2], 10, 5)
        self.assertAlmostEqual(vertex2.normal[0], 0, 5)
        self.assertAlmostEqual(vertex2.normal[1], 0, 5)
        self.assertAlmostEqual(vertex2.normal[2], -1, 5)
        self.assertAlmostEqual(vertex2.texcoord[0], 0.2, 5)
        self.assertAlmostEqual(vertex2.texcoord[1], 0.1, 5)
        self.assertEqual(vertex2.color, 0XFFFFFFFF)


class TestTransform(TestCase):
    def test_default_initialization(self):
        transform = Transform()
        transform_struct = transform.as_struct()

        self.assertAlmostEqual(transform_struct.matrix[0][0], 1, 5)
        self.assertAlmostEqual(transform_struct.matrix[0][1], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[0][2], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[0][3], 0, 5)

        self.assertAlmostEqual(transform_struct.matrix[1][0], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[1][1], 1, 5)
        self.assertAlmostEqual(transform_struct.matrix[1][2], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[1][3], 0, 5)

        self.assertAlmostEqual(transform_struct.matrix[2][0], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[2][1], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[2][2], 1, 5)
        self.assertAlmostEqual(transform_struct.matrix[2][3], 0, 5)

    def test_custom_initialization(self):
        transform = Transform(matrix=[
            [0,  1,  2,  3],
            [4,  5,  6,  7],
            [8,  9, 10, 11],
        ])
        transform_struct = transform.as_struct()

        self.assertAlmostEqual(transform_struct.matrix[0][0], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[0][1], 1, 5)
        self.assertAlmostEqual(transform_struct.matrix[0][2], 2, 5)
        self.assertAlmostEqual(transform_struct.matrix[0][3], 3, 5)

        self.assertAlmostEqual(transform_struct.matrix[1][0], 4, 5)
        self.assertAlmostEqual(transform_struct.matrix[1][1], 5, 5)
        self.assertAlmostEqual(transform_struct.matrix[1][2], 6, 5)
        self.assertAlmostEqual(transform_struct.matrix[1][3], 7, 5)

        self.assertAlmostEqual(transform_struct.matrix[2][0], 8, 5)
        self.assertAlmostEqual(transform_struct.matrix[2][1], 9, 5)
        self.assertAlmostEqual(transform_struct.matrix[2][2], 10, 5)
        self.assertAlmostEqual(transform_struct.matrix[2][3], 11, 5)

    def test_reset(self):
        transform = Transform(matrix=[
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [8, 9, 10, 11],
        ])
        transform.reset()
        transform_struct = transform.as_struct()

        self.assertAlmostEqual(transform_struct.matrix[0][0], 1, 5)
        self.assertAlmostEqual(transform_struct.matrix[0][1], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[0][2], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[0][3], 0, 5)

        self.assertAlmostEqual(transform_struct.matrix[1][0], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[1][1], 1, 5)
        self.assertAlmostEqual(transform_struct.matrix[1][2], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[1][3], 0, 5)

        self.assertAlmostEqual(transform_struct.matrix[2][0], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[2][1], 0, 5)
        self.assertAlmostEqual(transform_struct.matrix[2][2], 1, 5)
        self.assertAlmostEqual(transform_struct.matrix[2][3], 0, 5)


class TestMeshInstance(TestCase):
    def test_default_initialization(self):
        vertices = [
            Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct(),
            Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1),
                   color=0x0).as_struct(),
            Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct()
        ]
        surface = MeshSurface(vertices=vertices, indices=[0, 1, 2])
        mesh = Mesh(surfaces=[surface.as_struct()], mesh_hash=0x1234)
        mesh.handle = ctypes.c_void_p(12345)
        mesh_instance = MeshInstance(mesh=mesh)
        instance_struct = mesh_instance.as_struct()

        self.assertEqual(instance_struct.sType, _STypes.INSTANCE_INFO)
        self.assertEqual(instance_struct.pNext, None)
        self.assertEqual(instance_struct.mesh, mesh.handle.value)
        self.assertEqual(instance_struct.mesh, 12345)
        self.assertEqual(instance_struct.transform.matrix[0][0], 1)
        self.assertEqual(instance_struct.transform.matrix[1][1], 1)
        self.assertEqual(instance_struct.transform.matrix[2][2], 1)
        self.assertEqual(instance_struct.doubleSided, 1)

    def test_custom_initialization(self):
        vertices = [
            Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct(),
            Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1),
                   color=0x0).as_struct(),
            Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0.2, 0.1)).as_struct()
        ]
        surface = MeshSurface(vertices=vertices, indices=[0, 1, 2])
        mesh = Mesh(surfaces=[surface.as_struct()], mesh_hash=0x1234)
        mesh.handle = ctypes.c_void_p(12345)
        transform = Transform(matrix=[
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [8, 9, 10, 11],
        ])
        mesh_instance = MeshInstance(
            mesh=mesh,
            category_flags=CategoryFlags.DECAL_NO_OFFSET,
            double_sided=0,
            transform=transform,
        )
        instance_struct = mesh_instance.as_struct()

        self.assertEqual(instance_struct.sType, _STypes.INSTANCE_INFO)
        self.assertEqual(instance_struct.pNext, None)
        self.assertEqual(instance_struct.mesh, mesh.handle.value)
        self.assertEqual(instance_struct.mesh, 12345)

        self.assertAlmostEqual(instance_struct.transform.matrix[0][0], 0, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[0][1], 1, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[0][2], 2, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[0][3], 3, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[1][0], 4, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[1][1], 5, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[1][2], 6, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[1][3], 7, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[2][0], 8, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[2][1], 9, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[2][2], 10, 5)
        self.assertAlmostEqual(instance_struct.transform.matrix[2][3], 11, 5)

        self.assertEqual(instance_struct.doubleSided, 0)


class TestLightShapingInfo(TestCase):
    def test_default_initialization(self):
        light_shaping = LightShapingInfo()
        shaping_struct = light_shaping.as_struct()

        self.assertAlmostEqual(shaping_struct.direction.x, 0, 4)
        self.assertAlmostEqual(shaping_struct.direction.y, -1, 4)
        self.assertAlmostEqual(shaping_struct.direction.z, 0, 4)
        self.assertAlmostEqual(shaping_struct.coneAngleDegrees, 0, 4)
        self.assertAlmostEqual(shaping_struct.coneSoftness, 0, 4)
        self.assertAlmostEqual(shaping_struct.focusExponent, 0, 4)


class TestLight(TestCase):
    def test_raises_when_used_directly(self):
        with self.assertRaises(TypeError):
            Light(light_hash=ctypes.c_uint64(0x3))


class TestSphereLight(TestCase):
    def test_default_initialization(self):
        sphere_light = SphereLight(HASH(0x5))
        light_struct = sphere_light.as_struct()

        self.assertEqual(light_struct.sType, _STypes.LIGHT_INFO)
        self.assertEqual(light_struct.hash, 0x5)
        self.assertAlmostEqual(light_struct.radiance.x, 1.0, 4)
        self.assertAlmostEqual(light_struct.radiance.y, 1.0, 4)
        self.assertAlmostEqual(light_struct.radiance.z, 1.0, 4)

        sphere_light_struct = ctypes.cast(light_struct.pNext, ctypes.POINTER(_LightInfoSphereEXT))[0]
        self.assertEqual(sphere_light_struct.sType, _STypes.LIGHT_INFO_SPHERE_EXT)
        self.assertEqual(sphere_light_struct.pNext, None)
        self.assertAlmostEqual(sphere_light_struct.position.x, 0, 4)
        self.assertAlmostEqual(sphere_light_struct.position.y, 0, 4)
        self.assertAlmostEqual(sphere_light_struct.position.z, 0, 4)
        self.assertAlmostEqual(sphere_light_struct.radius, 0.1, 5)
        self.assertEqual(sphere_light_struct.shaping_hasvalue, 0)

    def test_custom_initialization(self):
        sphere_light = SphereLight(
            light_hash=HASH(0x5),
            position=Float3D(5, 4, 3),
            radius=0.5,
            radiance=Float3D(0.2, 700, 256.7)
        )
        light_struct = sphere_light.as_struct()

        self.assertEqual(light_struct.sType, _STypes.LIGHT_INFO)
        self.assertEqual(light_struct.hash, 0x5)
        self.assertAlmostEqual(light_struct.radiance.x, 0.2, 4)
        self.assertAlmostEqual(light_struct.radiance.y, 700, 4)
        self.assertAlmostEqual(light_struct.radiance.z, 256.7, 4)

        sphere_light_struct = ctypes.cast(light_struct.pNext, ctypes.POINTER(_LightInfoSphereEXT))[0]
        self.assertEqual(sphere_light_struct.sType, _STypes.LIGHT_INFO_SPHERE_EXT)
        self.assertEqual(sphere_light_struct.pNext, None)
        self.assertAlmostEqual(sphere_light_struct.position.x, 5, 4)
        self.assertAlmostEqual(sphere_light_struct.position.y, 4, 4)
        self.assertAlmostEqual(sphere_light_struct.position.z, 3, 4)
        self.assertAlmostEqual(sphere_light_struct.radius, 0.5, 5)
        self.assertEqual(sphere_light_struct.shaping_hasvalue, 0)

    def test_initialization_with_shaping_value(self):
        shaping_value = LightShapingInfo()
        shaping_value.direction = Float3D(3, -1, 7)
        shaping_value.cone_angle = 35.0
        shaping_value.cone_softness = 3
        shaping_value.focus_exponent = 4

        sphere_light = SphereLight(
            light_hash=HASH(0x5),
            position=Float3D(5, 4, 3),
            radius=0.5,
            radiance=Float3D(0.2, 700, 256.7),
            shaping_value=shaping_value
        )
        light_struct = sphere_light.as_struct()

        self.assertEqual(light_struct.sType, _STypes.LIGHT_INFO)
        self.assertEqual(light_struct.hash, 0x5)
        self.assertAlmostEqual(light_struct.radiance.x, 0.2, 4)
        self.assertAlmostEqual(light_struct.radiance.y, 700, 4)
        self.assertAlmostEqual(light_struct.radiance.z, 256.7, 4)

        sphere_light_struct = ctypes.cast(light_struct.pNext, ctypes.POINTER(_LightInfoSphereEXT))[0]
        self.assertEqual(sphere_light_struct.sType, _STypes.LIGHT_INFO_SPHERE_EXT)
        self.assertEqual(sphere_light_struct.pNext, None)
        self.assertAlmostEqual(sphere_light_struct.position.x, 5, 4)
        self.assertAlmostEqual(sphere_light_struct.position.y, 4, 4)
        self.assertAlmostEqual(sphere_light_struct.position.z, 3, 4)
        self.assertAlmostEqual(sphere_light_struct.radius, 0.5, 5)
        self.assertEqual(sphere_light_struct.shaping_hasvalue, 1)

        self.assertAlmostEqual(sphere_light_struct.shaping_value.direction.x, 3, 4)
        self.assertAlmostEqual(sphere_light_struct.shaping_value.direction.y, -1, 4)
        self.assertAlmostEqual(sphere_light_struct.shaping_value.direction.z, 7, 4)
        self.assertAlmostEqual(sphere_light_struct.shaping_value.coneAngleDegrees, 35.0, 4)
        self.assertAlmostEqual(sphere_light_struct.shaping_value.coneSoftness, 3, 4)
        self.assertAlmostEqual(sphere_light_struct.shaping_value.focusExponent, 4, 4)


class TestMaterial(TestCase):
    def test_raises_when_used_directly(self):
        with self.assertRaises(TypeError):
            Material(mat_hash=ctypes.c_uint64(0x3))


class TestOpacityPBR(TestCase):
    def test_default_initialization(self):
        mat = OpacityPBR(mat_hash=ctypes.c_uint64(0x3))
        mat_struct = mat.as_struct()

        self.assertEqual(mat_struct.sType, _STypes.MATERIAL_INFO)
        self.assertNotEqual(mat_struct.pNext, None)
        self.assertEqual(mat_struct.albedoTexture, "")
        self.assertEqual(mat_struct.normalTexture, "")
        self.assertEqual(mat_struct.tangentTexture, "")
        self.assertEqual(mat_struct.emissiveTexture, "")
        self.assertEqual(mat_struct.emissiveIntensity, 0)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.x, 0, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.y, 0, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.z, 0, 4)
        self.assertEqual(mat_struct.spriteSheetRow, 0)
        self.assertEqual(mat_struct.spriteSheetCol, 0)
        self.assertEqual(mat_struct.spriteSheetFps, 0)
        self.assertEqual(mat_struct.filterMode, FilterModes.LINEAR)
        self.assertEqual(mat_struct.wrapModeU, WrapModes.REPEAT)
        self.assertEqual(mat_struct.wrapModeV, WrapModes.REPEAT)

        opacity_struct = ctypes.cast(mat_struct.pNext, ctypes.POINTER(_MaterialInfoOpaqueEXT))[0]
        self.assertEqual(opacity_struct.sType, _STypes.MATERIAL_INFO_OPAQUE_EXT)
        self.assertEqual(opacity_struct.pNext, None)
        self.assertEqual(opacity_struct.roughnessTexture, "")
        self.assertAlmostEqual(opacity_struct.anisotropy, 0, 4)
        self.assertAlmostEqual(opacity_struct.albedoConstant.x, 1, 4)
        self.assertAlmostEqual(opacity_struct.albedoConstant.y, 1, 4)
        self.assertAlmostEqual(opacity_struct.albedoConstant.z, 1, 4)
        self.assertAlmostEqual(opacity_struct.opacityConstant, 1, 4)
        self.assertAlmostEqual(opacity_struct.roughnessConstant, 1, 4)
        self.assertAlmostEqual(opacity_struct.metallicConstant, 0, 4)
        self.assertEqual(opacity_struct.thinFilmThickness_hasvalue, 0)
        self.assertAlmostEqual(opacity_struct.thinFilmThickness_value, 0, 4)
        self.assertEqual(opacity_struct.alphaIsThinFilmThickness, 0)
        self.assertEqual(opacity_struct.heightTexture, "")
        self.assertAlmostEqual(opacity_struct.heightTextureStrength, 0, 4)
        self.assertEqual(opacity_struct.useDrawCallAlphaState, 0)
        self.assertEqual(opacity_struct.blendType_hasvalue, 0)
        self.assertEqual(opacity_struct.blendType_value, 0)
        self.assertEqual(opacity_struct.invertedBlend, 0)
        self.assertEqual(opacity_struct.alphaTestType, AlphaTestTypes.NEVER)
        self.assertEqual(opacity_struct.alphaReferenceValue, 0)

    def test_custom_initialization(self):
        mat = OpacityPBR(
            mat_hash=ctypes.c_uint64(0x3),
            albedo_texture="albedo.dds",
            normal_texture="normal.dds",
            tangent_texture="tangent.dds",
            emissive_texture="emissive.dds",
            emissive_intensity=1.5,
            emissive_color_constant=Float3D(0.2, 0.6, 0.9),
            sprite_sheet_row=2,
            sprite_sheet_col=5,
            sprite_sheet_fps=7,
            filter_mode=FilterModes.NEAREST,
            wrap_mode_u=WrapModes.CLAMP,
            wrap_mode_v=WrapModes.CLAMP,
            # OpacityPBR Parameters:
            roughness_texture="roughness.dds",
            metallic_texture="metallic.dds",
            anisotropy=0.7,
            albedo_constant=Float3D(0.2, 0.25, 0.33),
            opacity_constant=0.7,
            roughness_constant=0.75,
            metallic_constant=0.19,
            thin_film_thickness_value=0.314,
            alpha_is_thin_film_thickness=True,
            height_texture=Path("displacement.dds"),
            height_texture_strength=0.00015,
            use_draw_call_alpha_state=True,
            blend_type_value=BlendTypes.REVERSE_COLOR_EMISSIVE,
            inverted_blend=True,
            alpha_test_type=AlphaTestTypes.GREATER_OR_EQUAL,
            alpha_reference_value=255,
        )

        mat_struct = mat.as_struct()

        self.assertEqual(mat_struct.sType, _STypes.MATERIAL_INFO)
        self.assertNotEqual(mat_struct.pNext, None)
        self.assertEqual(mat_struct.albedoTexture, "albedo.dds")
        self.assertEqual(mat_struct.normalTexture, "normal.dds")
        self.assertEqual(mat_struct.tangentTexture, "tangent.dds")
        self.assertEqual(mat_struct.emissiveTexture, "emissive.dds")
        self.assertEqual(mat_struct.emissiveIntensity, 1.5)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.x, 0.2, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.y, 0.6, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.z, 0.9, 4)
        self.assertEqual(mat_struct.spriteSheetRow, 2)
        self.assertEqual(mat_struct.spriteSheetCol, 5)
        self.assertEqual(mat_struct.spriteSheetFps, 7)
        self.assertEqual(mat_struct.filterMode, FilterModes.NEAREST)
        self.assertEqual(mat_struct.wrapModeU, WrapModes.CLAMP)
        self.assertEqual(mat_struct.wrapModeV, WrapModes.CLAMP)

        opacity_struct = ctypes.cast(mat_struct.pNext, ctypes.POINTER(_MaterialInfoOpaqueEXT))[0]
        self.assertEqual(opacity_struct.sType, _STypes.MATERIAL_INFO_OPAQUE_EXT)
        self.assertEqual(opacity_struct.pNext, None)
        self.assertEqual(opacity_struct.roughnessTexture, "roughness.dds")
        self.assertAlmostEqual(opacity_struct.anisotropy, 0.7, 4)
        self.assertAlmostEqual(opacity_struct.albedoConstant.x, 0.2, 4)
        self.assertAlmostEqual(opacity_struct.albedoConstant.y, 0.25, 4)
        self.assertAlmostEqual(opacity_struct.albedoConstant.z, 0.33, 4)
        self.assertAlmostEqual(opacity_struct.opacityConstant, 0.7, 4)
        self.assertAlmostEqual(opacity_struct.roughnessConstant, 0.75, 4)
        self.assertAlmostEqual(opacity_struct.metallicConstant, 0.19, 4)
        self.assertEqual(opacity_struct.thinFilmThickness_hasvalue, 1)
        self.assertAlmostEqual(opacity_struct.thinFilmThickness_value, 0.314, 4)
        self.assertEqual(opacity_struct.alphaIsThinFilmThickness, 1)
        self.assertEqual(opacity_struct.heightTexture, "displacement.dds")
        self.assertAlmostEqual(opacity_struct.heightTextureStrength, 0.00015, 6)
        self.assertEqual(opacity_struct.useDrawCallAlphaState, 1)
        self.assertEqual(opacity_struct.blendType_hasvalue, 1)
        self.assertEqual(opacity_struct.blendType_value, BlendTypes.REVERSE_COLOR_EMISSIVE)
        self.assertEqual(opacity_struct.invertedBlend, 1)
        self.assertEqual(opacity_struct.alphaTestType, AlphaTestTypes.GREATER_OR_EQUAL)
        self.assertEqual(opacity_struct.alphaReferenceValue, 255)

    def test_sss_data(self):
        sss_data = OpacitySSSData(
            transmittance_texture=Path("transmittance.dds"),
            thickness_texture=Path("thickness.dds"),
            single_scattering_albedo_texture=Path("ss_albedo.dds"),
            transmittance_color=Float3D(1, 0.3, 0.7),
            measurement_distance=0.5,
            single_scattering_albedo=Float3D(0.87, 0.3, 0.8),
            volumetric_anisotropy=0.4,
        )
        mat = OpacityPBR(mat_hash=ctypes.c_uint64(0x3), subsurface_data=sss_data)
        mat_struct = mat.as_struct()
        opacity_struct = ctypes.cast(mat_struct.pNext, ctypes.POINTER(_MaterialInfoOpaqueEXT))[0]
        sss_struct = ctypes.cast(opacity_struct.pNext, ctypes.POINTER(_MaterialInfoOpaqueSubsurfaceEXT))[0]

        self.assertEqual(sss_struct.sType, _STypes.MATERIAL_INFO_OPAQUE_SUBSURFACE_EXT)
        self.assertEqual(sss_struct.pNext, None)
        self.assertEqual(sss_struct.subsurfaceTransmittanceTexture, "transmittance.dds")
        self.assertEqual(sss_struct.subsurfaceThicknessTexture, "thickness.dds")
        self.assertEqual(sss_struct.subsurfaceSingleScatteringAlbedoTexture, "ss_albedo.dds")
        self.assertAlmostEqual(sss_struct.subsurfaceTransmittanceColor.x, 1, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceTransmittanceColor.y, 0.3, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceTransmittanceColor.z, 0.7, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceMeasurementDistance, 0.5, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceSingleScatteringAlbedo.x, 0.87, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceSingleScatteringAlbedo.y, 0.3, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceSingleScatteringAlbedo.z, 0.8, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceVolumetricAnisotropy, 0.4, 4)


class TestOpacitySSSData(TestCase):
    def test_default_initialization(self):
        mat = OpacitySSSData()
        sss_struct = mat.as_struct()

        self.assertEqual(sss_struct.sType, _STypes.MATERIAL_INFO_OPAQUE_SUBSURFACE_EXT)
        self.assertEqual(sss_struct.pNext, None)
        self.assertEqual(sss_struct.subsurfaceTransmittanceTexture, "")
        self.assertEqual(sss_struct.subsurfaceThicknessTexture, "")
        self.assertEqual(sss_struct.subsurfaceSingleScatteringAlbedoTexture, "")
        self.assertAlmostEqual(sss_struct.subsurfaceTransmittanceColor.x, 0, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceTransmittanceColor.y, 0, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceTransmittanceColor.z, 0, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceMeasurementDistance, 0.1, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceSingleScatteringAlbedo.x, 0, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceSingleScatteringAlbedo.y, 0, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceSingleScatteringAlbedo.z, 0, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceVolumetricAnisotropy, 0, 4)

    def test_custom_initialization(self):
        mat = OpacitySSSData(
            transmittance_texture=Path("transmittance.dds"),
            thickness_texture=Path("thickness.dds"),
            single_scattering_albedo_texture=Path("ss_albedo.dds"),
            transmittance_color=Float3D(1, 0.3, 0.7),
            measurement_distance=0.5,
            single_scattering_albedo=Float3D(0.87, 0.3, 0.8),
            volumetric_anisotropy=0.4,
        )
        sss_struct = mat.as_struct()

        self.assertEqual(sss_struct.sType, _STypes.MATERIAL_INFO_OPAQUE_SUBSURFACE_EXT)
        self.assertEqual(sss_struct.pNext, None)
        self.assertEqual(sss_struct.subsurfaceTransmittanceTexture, "transmittance.dds")
        self.assertEqual(sss_struct.subsurfaceThicknessTexture, "thickness.dds")
        self.assertEqual(sss_struct.subsurfaceSingleScatteringAlbedoTexture, "ss_albedo.dds")
        self.assertAlmostEqual(sss_struct.subsurfaceTransmittanceColor.x, 1, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceTransmittanceColor.y, 0.3, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceTransmittanceColor.z, 0.7, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceMeasurementDistance, 0.5, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceSingleScatteringAlbedo.x, 0.87, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceSingleScatteringAlbedo.y, 0.3, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceSingleScatteringAlbedo.z, 0.8, 4)
        self.assertAlmostEqual(sss_struct.subsurfaceVolumetricAnisotropy, 0.4, 4)


class TestTranslucentPBR(TestCase):
    def test_default_initialization(self):
        mat = TranslucentPBR(mat_hash=ctypes.c_uint64(0x3))
        mat_struct = mat.as_struct()

        self.assertEqual(mat_struct.sType, _STypes.MATERIAL_INFO)
        self.assertNotEqual(mat_struct.pNext, None)
        self.assertEqual(mat_struct.albedoTexture, "")
        self.assertEqual(mat_struct.normalTexture, "")
        self.assertEqual(mat_struct.tangentTexture, "")
        self.assertEqual(mat_struct.emissiveTexture, "")
        self.assertEqual(mat_struct.emissiveIntensity, 0)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.x, 0, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.y, 0, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.z, 0, 4)
        self.assertEqual(mat_struct.spriteSheetRow, 0)
        self.assertEqual(mat_struct.spriteSheetCol, 0)
        self.assertEqual(mat_struct.spriteSheetFps, 0)
        self.assertEqual(mat_struct.filterMode, FilterModes.LINEAR)
        self.assertEqual(mat_struct.wrapModeU, WrapModes.REPEAT)
        self.assertEqual(mat_struct.wrapModeV, WrapModes.REPEAT)

        translucent_struct = ctypes.cast(mat_struct.pNext, ctypes.POINTER(_MaterialInfoTranslucentEXT))[0]
        self.assertEqual(translucent_struct.sType, _STypes.MATERIAL_INFO_TRANSLUCENT_EXT)
        self.assertEqual(translucent_struct.pNext, None)
        self.assertEqual(translucent_struct.transmittanceTexture, "")
        self.assertAlmostEqual(translucent_struct.refractiveIndex, 0, 4)
        self.assertAlmostEqual(translucent_struct.transmittanceColor.x, 0, 4)
        self.assertAlmostEqual(translucent_struct.transmittanceColor.y, 0, 4)
        self.assertAlmostEqual(translucent_struct.transmittanceColor.z, 0, 4)
        self.assertAlmostEqual(translucent_struct.transmittanceMeasurementDistance, 0.1, 4)
        self.assertEqual(translucent_struct.thinWallThickness_hasvalue, 0)
        self.assertAlmostEqual(translucent_struct.thinWallThickness_value, 0, 4)
        self.assertEqual(translucent_struct.useDiffuseLayer, 0)

    def test_custom_initialization(self):
        mat = TranslucentPBR(
            mat_hash=ctypes.c_uint64(0x3),
            albedo_texture="albedo.dds",
            normal_texture="normal.dds",
            tangent_texture="tangent.dds",
            emissive_texture="emissive.dds",
            emissive_intensity=1.5,
            emissive_color_constant=Float3D(0.2, 0.6, 0.9),
            sprite_sheet_row=2,
            sprite_sheet_col=5,
            sprite_sheet_fps=7,
            filter_mode=FilterModes.NEAREST,
            wrap_mode_u=WrapModes.CLAMP,
            wrap_mode_v=WrapModes.CLAMP,
            # TranslucentPBR Parameters:
            transmittance_texture="transmittance.dds",
            refractive_index=1.42,
            transmittance_color=Float3D(0.5, 0.2, 0.7),
            transmittance_measurement_distance=0.492,
            thin_wall_thickness=3.1415,
            use_diffuse_layer=True,
        )

        mat_struct = mat.as_struct()

        self.assertEqual(mat_struct.sType, _STypes.MATERIAL_INFO)
        self.assertNotEqual(mat_struct.pNext, None)
        self.assertEqual(mat_struct.albedoTexture, "albedo.dds")
        self.assertEqual(mat_struct.normalTexture, "normal.dds")
        self.assertEqual(mat_struct.tangentTexture, "tangent.dds")
        self.assertEqual(mat_struct.emissiveTexture, "emissive.dds")
        self.assertEqual(mat_struct.emissiveIntensity, 1.5)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.x, 0.2, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.y, 0.6, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.z, 0.9, 4)
        self.assertEqual(mat_struct.spriteSheetRow, 2)
        self.assertEqual(mat_struct.spriteSheetCol, 5)
        self.assertEqual(mat_struct.spriteSheetFps, 7)
        self.assertEqual(mat_struct.filterMode, FilterModes.NEAREST)
        self.assertEqual(mat_struct.wrapModeU, WrapModes.CLAMP)
        self.assertEqual(mat_struct.wrapModeV, WrapModes.CLAMP)

        translucent_struct = ctypes.cast(mat_struct.pNext, ctypes.POINTER(_MaterialInfoTranslucentEXT))[0]
        self.assertEqual(translucent_struct.sType, _STypes.MATERIAL_INFO_TRANSLUCENT_EXT)
        self.assertEqual(translucent_struct.pNext, None)
        self.assertEqual(translucent_struct.transmittanceTexture, "transmittance.dds")
        self.assertAlmostEqual(translucent_struct.refractiveIndex, 1.42, 4)
        self.assertAlmostEqual(translucent_struct.transmittanceColor.x, 0.5, 4)
        self.assertAlmostEqual(translucent_struct.transmittanceColor.y, 0.2, 4)
        self.assertAlmostEqual(translucent_struct.transmittanceColor.z, 0.7, 4)
        self.assertAlmostEqual(translucent_struct.transmittanceMeasurementDistance, 0.492, 4)
        self.assertEqual(translucent_struct.thinWallThickness_hasvalue, 1)
        self.assertAlmostEqual(translucent_struct.thinWallThickness_value, 3.1415, 4)
        self.assertEqual(translucent_struct.useDiffuseLayer, 1)


class TestPortal(TestCase):
    def test_default_initialization(self):
        mat = Portal(mat_hash=ctypes.c_uint64(0x3))
        mat_struct = mat.as_struct()

        self.assertEqual(mat_struct.sType, _STypes.MATERIAL_INFO)
        self.assertNotEqual(mat_struct.pNext, None)
        self.assertEqual(mat_struct.albedoTexture, "")
        self.assertEqual(mat_struct.normalTexture, "")
        self.assertEqual(mat_struct.tangentTexture, "")
        self.assertEqual(mat_struct.emissiveTexture, "")
        self.assertEqual(mat_struct.emissiveIntensity, 0)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.x, 0, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.y, 0, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.z, 0, 4)
        self.assertEqual(mat_struct.spriteSheetRow, 0)
        self.assertEqual(mat_struct.spriteSheetCol, 0)
        self.assertEqual(mat_struct.spriteSheetFps, 0)
        self.assertEqual(mat_struct.filterMode, FilterModes.LINEAR)
        self.assertEqual(mat_struct.wrapModeU, WrapModes.REPEAT)
        self.assertEqual(mat_struct.wrapModeV, WrapModes.REPEAT)

        portal_struct = ctypes.cast(mat_struct.pNext, ctypes.POINTER(_MaterialInfoPortalEXT))[0]
        self.assertEqual(portal_struct.sType, _STypes.MATERIAL_INFO_PORTAL_EXT)
        self.assertEqual(portal_struct.pNext, None)
        self.assertEqual(portal_struct.rayPortalIndex, 0)
        self.assertAlmostEqual(portal_struct.rotationSpeed, 0, 4)

    def test_custom_initialization(self):
        mat = Portal(
            mat_hash=ctypes.c_uint64(0x3),
            albedo_texture="albedo.dds",
            normal_texture="normal.dds",
            tangent_texture="tangent.dds",
            emissive_texture="emissive.dds",
            emissive_intensity=1.5,
            emissive_color_constant=Float3D(0.2, 0.6, 0.9),
            sprite_sheet_row=2,
            sprite_sheet_col=5,
            sprite_sheet_fps=7,
            filter_mode=FilterModes.NEAREST,
            wrap_mode_u=WrapModes.CLAMP,
            wrap_mode_v=WrapModes.CLAMP,
            # Portal Parameters:
            ray_portal_index=17,
            rotation_speed=1.42,
        )

        mat_struct = mat.as_struct()

        self.assertEqual(mat_struct.sType, _STypes.MATERIAL_INFO)
        self.assertNotEqual(mat_struct.pNext, None)
        self.assertEqual(mat_struct.albedoTexture, "albedo.dds")
        self.assertEqual(mat_struct.normalTexture, "normal.dds")
        self.assertEqual(mat_struct.tangentTexture, "tangent.dds")
        self.assertEqual(mat_struct.emissiveTexture, "emissive.dds")
        self.assertEqual(mat_struct.emissiveIntensity, 1.5)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.x, 0.2, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.y, 0.6, 4)
        self.assertAlmostEqual(mat_struct.emissiveColorConstant.z, 0.9, 4)
        self.assertEqual(mat_struct.spriteSheetRow, 2)
        self.assertEqual(mat_struct.spriteSheetCol, 5)
        self.assertEqual(mat_struct.spriteSheetFps, 7)
        self.assertEqual(mat_struct.filterMode, FilterModes.NEAREST)
        self.assertEqual(mat_struct.wrapModeU, WrapModes.CLAMP)
        self.assertEqual(mat_struct.wrapModeV, WrapModes.CLAMP)

        portal_struct = ctypes.cast(mat_struct.pNext, ctypes.POINTER(_MaterialInfoPortalEXT))[0]
        self.assertEqual(portal_struct.sType, _STypes.MATERIAL_INFO_PORTAL_EXT)
        self.assertEqual(portal_struct.pNext, None)
        self.assertEqual(portal_struct.rayPortalIndex, 17)
        self.assertAlmostEqual(portal_struct.rotationSpeed, 1.42, 4)


# TODO: Add tests for Assets destructors and Destroy calls.
