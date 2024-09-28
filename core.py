import ctypes

from components import Camera, Mesh, MeshInstance, Light
from api_data_types import _StartupInfo, _STypes, ReturnCodes, _PresentInfo


class StartupInfo:
    def __init__(
        self,
        hwnd: int = 0,
        disable_srgb_conversion_for_output: bool = False,
        force_no_vk_swapchain: bool = False,
        editor_mode_enabled: bool = False
    ):
        """
        Startup class used to setup Remix for initialization.

        :param int hwnd: Windows API's HWND window handle.

        :param bool disable_srgb_conversion_for_output: # TODO: Add docstring.

        :param bool force_no_vk_swapchain: Disables the frame presentation on the screen.
        'dxvk_GetExternalSwapchain' can be used to retrieve a raw VkImage so the application can decide what to do with it.
        i.e: Convert and present it using OpenGL.

        :param bool editor_mode_enabled: # TODO: Add docstring.
        """
        self.hwnd: int = hwnd
        self.disable_srgb_conversion_for_output = disable_srgb_conversion_for_output
        self.force_no_vk_swapchain = force_no_vk_swapchain
        self.editor_mode_enabled = editor_mode_enabled

    def as_struct(self) -> _StartupInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        startup_info = _StartupInfo()
        startup_info.sType = _STypes.STARTUP_INFO
        startup_info.hwnd = self.hwnd
        startup_info.disableSrgbConversionForOutput = self.disable_srgb_conversion_for_output
        startup_info.forceNoVkSwapchain = self.force_no_vk_swapchain
        startup_info.editorModeEnabled = self.editor_mode_enabled
        return startup_info


class RTXRemixAPI:
    def __init__(self, dll_path: str = './remixapi.dll'):
        """
        Main interface class to communicate with the RTX Remix API.
        """
        self.startup_info_struct: _StartupInfo | None = None
        self.remixapi_dll_handle = ctypes.CDLL(dll_path)

    def init(self, startup_info: StartupInfo) -> int:
        """
        Initializes RTX Remix API, properly loading its internal DLLs and starts up the engine.
        :param StartupInfo startup_info: Instance of a StartupInfo with basic settings for the API and Engine.
        :return: SUCCESS status code if succeeded, raises ValueError if not.
        """
        self.startup_info_struct = startup_info.as_struct()
        init_status = self.remixapi_dll_handle.init(ctypes.byref(self.startup_info_struct))
        if init_status != ReturnCodes.SUCCESS:
            raise ValueError(f"RTXRemixAPI.init failed with status code: {init_status}")

        return ReturnCodes.SUCCESS

    def setup_camera(self, camera: Camera) -> None:
        """
        Binds 'camera' as the current rendering camera. Must be called every frame.

        :param Camera camera: Instance of the Camera() component.
        """
        cam_info = camera.as_struct()
        self.remixapi_dll_handle.setup_camera(ctypes.byref(cam_info))

    def create_mesh(self, mesh: Mesh) -> None:
        """
        Registers a new mesh inside Remix engine. If successful, that mesh can later be used to call draw_instance.

        :param mesh: Instance of the Mesh class to create.
        """
        scene_mesh_handle: ctypes.c_void_p = ctypes.c_void_p(0)
        mesh_info = mesh.as_struct()
        self.remixapi_dll_handle.create_mesh(
            ctypes.byref(mesh_info),
            ctypes.byref(scene_mesh_handle)
        )
        mesh.handle = scene_mesh_handle

    def create_light(self, light: Light) -> None:
        """
        Registers a new light inside Remix engine. If successful, that light can later be used to call draw_light_instance.

        :param light: Instance of the Light class to create.
        """
        scene_light_handle: ctypes.c_void_p = ctypes.c_void_p(0)
        light_info = light.as_struct()
        self.remixapi_dll_handle.create_light(
            ctypes.byref(light_info),
            ctypes.byref(scene_light_handle)
        )
        light.handle = scene_light_handle

    def draw_instance(self, mesh_instance: MeshInstance) -> None:
        mesh_instance_struct = mesh_instance.as_struct()
        self.remixapi_dll_handle.draw_instance(ctypes.byref(mesh_instance_struct))

    def draw_light_instance(self, light: Light) -> None:
        self.remixapi_dll_handle.draw_light_instance(light.handle)

    def present(self, hwnd_override: int = None):
        """
        Triggers remix to render it's contents to the screen.
        :param str hwnd_override: Alternative hwnd Window handle to present. Useful for multi-window applications.
        """
        if not hwnd_override:
            self.remixapi_dll_handle.present(None)
            return

        present_info = _PresentInfo()
        present_info.hwndOverride = hwnd_override
        present_info.sType = _STypes.PRESENT_INFO
        present_info.pNext = 0
        self.remixapi_dll_handle.present(ctypes.byref(present_info))

    def __del__(self):
        self.remixapi_dll_handle.destroy()
