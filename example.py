import ctypes
import tkinter as tk

from api_data_types import HASH, Float2D
from components import Camera, Float3D, Vertex, MeshSurface, Mesh, MeshInstance, Transform, SphereLight, OpacityPBR
from core import RTXRemixAPI, StartupInfo


def main():
    window_width = 1600
    window_height = 900
    window = tk.Tk()
    window.title("PyRTXRemix")
    window.geometry(f"{window_width}x{window_height}")

    remix_api = RTXRemixAPI()
    startup_info = StartupInfo(hwnd=window.winfo_id())
    remix_api.init(startup_info)

    mat = OpacityPBR(mat_hash=HASH(0x1))
    remix_api.create_material(mat)

    # Creating a Camera
    camera = Camera(
         position=Float3D(0, 0.3, 0), forward=Float3D(0, 0, 1), up=Float3D(0, 1, 0), right=Float3D(1, 0, 0), fov_y=70,
         aspect=float(window_width)/window_height, near_plane=0.1, far_plane=1000
    )
    # Creating a Mesh Asset and a MeshInstance
    vertices = [
        Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0,0)).as_struct(),
        Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(0,1), color=0xFFFFFF).as_struct(),
        Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1), texcoord=Float2D(1,0)).as_struct()
    ]
    surface = MeshSurface(vertices=vertices, indices=[0, 1, 2], material=mat)
    mesh = Mesh(surfaces=[surface.as_struct()])
    remix_api.create_mesh(mesh)

    mesh_instance = MeshInstance(
        mesh=mesh, category_flags=ctypes.c_uint32(0), transform=Transform(), double_sided=1
    )

    # Creating a Sphere Light
    light = SphereLight(position=Float3D(3, 8, -5), radius=0.1, light_hash=HASH(0x3), radiance=Float3D(100, 200, 100))
    remix_api.create_light(light)

    window.update_idletasks()
    window.update()
    while True:
        if not window.winfo_exists():
            break

        remix_api.setup_camera(camera)
        remix_api.draw_instance(mesh_instance)
        remix_api.draw_light_instance(light)
        remix_api.present(window.winfo_id())
        window.update_idletasks()
        window.update()

    remix_api.destroy_material(mat)
    remix_api.destroy_mesh(mesh)
    remix_api.destroy_light(light)
    window.destroy()
    remix_api.shutdown()


if __name__ == '__main__':
    main()
