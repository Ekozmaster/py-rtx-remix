import ctypes

from components import Camera, Float3D, Vertex, MeshSurface, Mesh, MeshInstance, Transform, SphereLight
from core import RTXRemixAPI, StartupInfo
from windowing import WinAPIWindow


def main():
    window_width = 1600
    window_height = 900
    window = WinAPIWindow("PyRTXRemix", window_width, window_height)
    window.show()
    window.update()

    remix_api = RTXRemixAPI()
    startup_info = StartupInfo(hwnd=window.hwnd)
    remix_api.init(startup_info)

    # Creating a Camera
    camera = Camera(
         position=Float3D(0, 0, 0), forward=Float3D(0, 0, 1), up=Float3D(0, 1, 0), right=Float3D(1, 0, 0), fov_y=70,
         aspect=float(window_width)/window_height, near_plane=0.1, far_plane=1000
    )
    # Creating a Mesh Asset and a MeshInstance
    vertices = [
        Vertex(position=Float3D(5, -5, 10), normal=Float3D(0, 0, -1)).as_struct(),
        Vertex(position=Float3D(0, 5, 10), normal=Float3D(0, 0, -1), color=0x0).as_struct(),
        Vertex(position=Float3D(-5, -5, 10), normal=Float3D(0, 0, -1)).as_struct()
    ]
    surface = MeshSurface(vertices=vertices, indices=[0, 1, 2])
    mesh = Mesh(surfaces=[surface.as_struct()])
    remix_api.create_mesh(mesh)
    mesh_instance = MeshInstance(mesh=mesh, category_flags=ctypes.c_uint32(0), transform=Transform(), double_sided=1)

    # Creating a Sphere Light
    light = SphereLight(position=Float3D(0, 8, 0), radius=0.1, light_hash=ctypes.c_uint64(0x3), radiance=Float3D(100, 200, 100))
    remix_api.create_light(light)

    while not window.should_quit:
        has_messages = window.process_window_messages()
        if not has_messages:
            remix_api.setup_camera(camera)
            remix_api.draw_instance(mesh_instance)
            remix_api.draw_light_instance(light)
            remix_api.present(window.hwnd)


if __name__ == '__main__':
    main()
