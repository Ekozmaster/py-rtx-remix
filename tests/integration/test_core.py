import ctypes
import os
from unittest import TestCase
import tkinter as tk

from api_data_types import ReturnCodes, Float3D
from components import Camera, Vertex, MeshSurface, Mesh, SphereLight
from core import StartupInfo, RTXRemixAPI
from exceptions import FailedToInitializeAPI, APINotInitialized


class TestRemixAPIInit(TestCase):
    def setUp(self):
        if not hasattr(self, 'remix_api'):
            self.remix_api: RTXRemixAPI | None = None

        if self.remix_api:
            self.remix_api.shutdown()

    def tearDown(self):
        self.remix_api.shutdown()

        if os.path.exists('not_bin/'):
            os.rename('not_bin', 'bin')

    def test_wrong_remixapi_dll_path_should_raise_exception(self):
        self.remix_api = RTXRemixAPI('some_wrong_path.dll')
        with self.assertRaises(FailedToInitializeAPI):
            self.remix_api.init(StartupInfo(hwnd=0))

    def test_regular_init_should_return_success_code(self):
        window_width = 400
        window_height = 300
        window = tk.Tk()
        window.title("PyRTXRemix")
        window.geometry(f"{window_width}x{window_height}")

        self.remix_api = RTXRemixAPI('remixapi.dll')
        startup_info = StartupInfo(hwnd=window.winfo_id())
        return_code = self.remix_api.init(startup_info)
        self.assertEqual(return_code, ReturnCodes.SUCCESS)

    def test_calling_init_twice_should_return_success(self):
        window = tk.Tk()
        window.title("PyRTXRemix")
        window.geometry(f"400x300")

        self.remix_api = RTXRemixAPI('remixapi.dll')
        startup_info = StartupInfo(hwnd=window.winfo_id())
        return_code = self.remix_api.init(startup_info)
        self.assertEqual(return_code, ReturnCodes.SUCCESS)

        return_code = self.remix_api.init(startup_info)
        self.assertEqual(return_code, ReturnCodes.SUCCESS)

    def test_init_without_remix_in_bin_folder_should_raise_exception(self):
        window_width = 400
        window_height = 300
        window = tk.Tk()
        window.title("PyRTXRemix")
        window.geometry(f"{window_width}x{window_height}")

        self.remix_api = RTXRemixAPI('remixapi.dll')
        startup_info = StartupInfo(hwnd=window.winfo_id())

        os.rename('bin', 'not_bin')
        with self.assertRaises(FailedToInitializeAPI):
            self.remix_api.init(startup_info)

        os.rename('not_bin', 'bin')


class TestRemixAPICameraAPI(TestCase):
    @classmethod
    def setUpClass(self):
        self.window_width = 400
        self.window_height = 300
        self.window = tk.Tk()
        self.window.title("PyRTXRemix")
        self.window.geometry(f"{self.window_width}x{self.window_height}")
        self.remix_api = RTXRemixAPI('remixapi.dll')
        startup_info = StartupInfo(hwnd=self.window.winfo_id())
        self.remix_api.init(startup_info)

    def setUp(self):
        self.remix_api._initialized = True

    @classmethod
    def tearDownClass(self):
        self.remix_api.shutdown()

        if self.window:
            self.window.destroy()
            self.window = None

    def test_setup_camera_without_initializing_remix_should_raise_exception(self):
        # TODO: Actually call Shutdown to make sure the API can be shutdown and reinitialized just fine.
        self.remix_api._initialized = False

        camera = Camera(
            position=Float3D(0, 0, 0), forward=Float3D(0, 0, 1), up=Float3D(0, 1, 0), right=Float3D(1, 0, 0), fov_y=70,
            aspect=float(self.window_width) / self.window_height, near_plane=0.1, far_plane=1000
        )
        with self.assertRaises(APINotInitialized):
            self.remix_api.setup_camera(camera)

    def test_setup_basic_camera_should_return_success(self):
        camera = Camera(
            position=Float3D(0, 0, 0), forward=Float3D(0, 0, 1), up=Float3D(0, 1, 0), right=Float3D(1, 0, 0), fov_y=70,
            aspect=float(self.window_width) / self.window_height, near_plane=0.1, far_plane=1000
        )
        return_code = self.remix_api.setup_camera(camera)
        self.assertEqual(return_code, ReturnCodes.SUCCESS)


class TestRemixAPIMeshAPI(TestCase):
    @classmethod
    def setUpClass(self):
        self.window_width = 400
        self.window_height = 300
        self.window = tk.Tk()
        self.window.title("PyRTXRemix")
        self.window.geometry(f"{self.window_width}x{self.window_height}")
        self.remix_api = RTXRemixAPI('remixapi.dll')
        startup_info = StartupInfo(hwnd=self.window.winfo_id())
        self.remix_api.init(startup_info)

    def setUp(self):
        self.remix_api._initialized = True

    @classmethod
    def tearDownClass(self):
        self.remix_api.shutdown()

        if self.window:
            self.window.destroy()
            self.window = None

    def test_create_mesh_without_initializing_remix_should_raise_exception(self):
        # TODO: Actually call Shutdown to make sure the API can be shutdown and reinitialized just fine.
        self.remix_api._initialized = False

        vertices = [
            Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1)).as_struct(),
            Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), color=0x0).as_struct(),
            Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1)).as_struct()
        ]
        surface = MeshSurface(vertices=vertices, indices=[0, 1, 2])
        mesh = Mesh(surfaces=[surface.as_struct()])
        with self.assertRaises(APINotInitialized):
            self.remix_api.create_mesh(mesh)
            self.remix_api = None

    def test_create_basic_mesh_should_return_success(self):
        vertices = [
            Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1)).as_struct(),
            Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), color=0x0).as_struct(),
            Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1)).as_struct()
        ]
        surface = MeshSurface(vertices=vertices, indices=[0, 1, 2])
        mesh = Mesh(surfaces=[surface.as_struct()])
        return_code = self.remix_api.create_mesh(mesh)
        self.assertEqual(return_code, ReturnCodes.SUCCESS)


class TestRemixAPILightAPI(TestCase):
    @classmethod
    def setUpClass(self):
        self.window_width = 400
        self.window_height = 300
        self.window = tk.Tk()
        self.window.title("PyRTXRemix")
        self.window.geometry(f"{self.window_width}x{self.window_height}")
        self.remix_api = RTXRemixAPI('remixapi.dll')
        startup_info = StartupInfo(hwnd=self.window.winfo_id())
        self.remix_api.init(startup_info)

    def setUp(self):
        self.remix_api._initialized = True

    @classmethod
    def tearDownClass(self):
        self.remix_api.shutdown()

        if self.window:
            self.window.destroy()
            self.window = None

    def test_create_light_without_initializing_remix_should_raise_exception(self):
        # TODO: Actually call Shutdown to make sure the API can be shutdown and reinitialized just fine.
        self.remix_api._initialized = False

        light = SphereLight(position=Float3D(0, 8, 0), radius=0.1, light_hash=ctypes.c_uint64(0x3), radiance=Float3D(100, 200, 100))
        with self.assertRaises(APINotInitialized):
            self.remix_api.create_light(light)

    def test_create_basic_light_should_return_success(self):
        light = SphereLight(position=Float3D(0, 8, 0), radius=0.1, light_hash=ctypes.c_uint64(0x3), radiance=Float3D(100, 200, 100))
        return_code = self.remix_api.create_light(light)
        self.assertEqual(return_code, ReturnCodes.SUCCESS)
