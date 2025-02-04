import ctypes
import tkinter as tk
from unittest import TestCase
import time

import numpy as np

from api_data_types import Float3D, Float2D
from components import Camera, Vertex, MeshSurface, Mesh, MeshInstance, Transform, SphereLight, RectLight, \
    CylinderLight, DiskLight, DistantLight, DomeLight
from core import RTXRemixAPI, StartupInfo
from PIL import Image, ImageGrab


def create_tk_window(width: int, height: int) -> tk.Tk:
    window = tk.Tk()
    window.title("PyRTXRemix")
    window.geometry(f"{width}x{height}")
    return window


def initialize_remix_api(window):
    remix_api = RTXRemixAPI()
    startup_info = StartupInfo(hwnd=window.winfo_id())
    remix_api.init(startup_info)
    return remix_api


def take_screenshot(window: tk.Tk) -> Image:
    x,y = window.winfo_rootx(), window.winfo_rooty()
    bbox = x, y, x + window.winfo_width(), y + window.winfo_height()
    return ImageGrab.grab(bbox)


def get_images_diff_mse(img1: Image, img2: Image) -> float:
    """Compute Mean Squared Error between two images."""
    arr1 = np.array(img1, dtype=np.float32)
    arr2 = np.array(img2, dtype=np.float32)
    return np.mean((arr1 - arr2) ** 2)


class TestLightOnTriangle(TestCase):
    def setUp(self):
        self.window_width = 150
        self.window_height = 150
        self.window: tk.Tk | None = create_tk_window(self.window_width, self.window_height)
        self.remix_api: RTXRemixAPI | None = initialize_remix_api(self.window)
        self.camera = Camera(
            position=Float3D(0, 0, 0), forward=Float3D(0, 0, 1), up=Float3D(0, 1, 0), right=Float3D(1, 0, 0), fov_y=70,
            aspect=float(self.window_width)/self.window_height, near_plane=0.1, far_plane=1000
        )
        vertices = [
            Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0, 0)).as_struct(),
            Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0, 1), color=0xFFFFFF).as_struct(),
            Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(1, 0)).as_struct()
        ]
        surface = MeshSurface(vertices=vertices, indices=[0, 1, 2])
        self.mesh = Mesh(surfaces=[surface.as_struct()])
        self.remix_api.create_mesh(self.mesh)
        self.mesh_instance = MeshInstance(mesh=self.mesh, category_flags=ctypes.c_uint32(0), transform=Transform(), double_sided=1)
        self.mse_comparison_threshold = 5
        self.created_lights = list()

    def tearDown(self):
        if self.remix_api:
            for light in self.created_lights:
                self.remix_api.destroy_light(light)
            self.created_lights = list()
            self.remix_api.destroy_mesh(self.mesh)
            self.remix_api.shutdown()

        if self.window:
            self.window.destroy()
            self.window = None

    def test_light_on_triangle(self):
        self.remix_api.setup_camera(self.camera)
        self.created_lights.append(SphereLight(
            position=Float3D(0, 8, 0),
            radius=0.1,
            light_hash=ctypes.c_uint64(0x3),
            radiance=Float3D(100, 200, 100)
        ))
        self.remix_api.create_light(self.created_lights[0])
        self.window.update_idletasks()
        self.window.update()
        time.sleep(0.5)  # Wait for the window fade in animation.

        for i in range(50):  # rendering a few frames to let the denoiser settle.
            self.remix_api.setup_camera(self.camera)
            self.remix_api.draw_instance(self.mesh_instance)
            self.remix_api.draw_light_instance(self.created_lights[0])
            self.remix_api.present()
            self.window.update_idletasks()
            self.window.update()
            time.sleep(0.016)

        img = take_screenshot(self.window)
        fixture_img = Image.open("tests/e2e/fixtures/light_on_triangle_01.png")
        mse = get_images_diff_mse(img, fixture_img)
        self.assertLess(mse, self.mse_comparison_threshold)

    def test_multiple_lights_on_triangle(self):
        self.remix_api.setup_camera(self.camera)
        self.created_lights.append(SphereLight(
            light_hash=ctypes.c_uint64(0x1),
            position=Float3D(0, 8, 0),
            radius=0.1,
            radiance=Float3D(100, 200, 100)
        ))
        self.created_lights.append(RectLight(
            light_hash=ctypes.c_uint64(0x2),
            position=Float3D(-2, -3, 9),
            direction=Float3D(0, 0, 1),
            x_axis=Float3D(1, 0, 0),
            y_axis=Float3D(0, 1, 0),
            y_size=3,
            radiance=Float3D(0.2, 0, 0.2)
        ))
        self.created_lights.append(CylinderLight(
            light_hash=ctypes.c_uint64(0x3),
            position=Float3D(2, -3, 9.8),
            radiance=Float3D(0, 0, 0.5),
            radius=0.1,
            axis=Float3D(0.7071, 0.7071, 0),
            axis_length=10
        ))
        self.created_lights.append(DiskLight(
            light_hash=ctypes.c_uint64(0x4),
            position=Float3D(0, 2, 9.95),
            direction=Float3D(0, 0, 1),
            x_axis=Float3D(1, 0, 0),
            y_axis=Float3D(0, 1, 0),
            x_size=1,
            y_size=0.3,
            radiance=Float3D(0.5, 0.5, 0),
        ))
        self.created_lights.append(DistantLight(
            light_hash=ctypes.c_uint64(0x5),
            radiance=Float3D(0.02, 0.02, 0.04),
            direction=Float3D(0.2, -0.7071, 0.7071).normalized(),
        ))
        self.created_lights.append(DomeLight(
            light_hash=ctypes.c_uint64(0x6),
            radiance=Float3D(0.02, 0.02, 0.02),
            color_texture="tests/e2e/fixtures/skybox.dds",
        ))
        [self.remix_api.create_light(light) for light in self.created_lights]
        self.window.update_idletasks()
        self.window.update()
        time.sleep(0.5)  # Wait for the window fade in animation.

        for i in range(50):  # rendering a few frames to let the denoiser settle.
            self.remix_api.setup_camera(self.camera)
            self.remix_api.draw_instance(self.mesh_instance)
            [self.remix_api.draw_light_instance(light) for light in self.created_lights]
            self.remix_api.present()
            self.window.update_idletasks()
            self.window.update()
            time.sleep(0.016)

        img = take_screenshot(self.window)
        fixture_img = Image.open("tests/e2e/fixtures/light_on_triangle_02.png")
        mse = get_images_diff_mse(img, fixture_img)
        self.assertLess(mse, self.mse_comparison_threshold)


def main():
    test = TestLightOnTriangle()
    test.setUp()
    test.test_multiple_lights_on_triangle()
    test.tearDown()
    test.setUp()
    test.test_light_on_triangle()
    test.tearDown()


if __name__ == '__main__':
    main()
