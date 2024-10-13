import ctypes
from pathlib import Path

from components import Camera, Mesh, MeshInstance, Light
from api_data_types import _StartupInfo, _STypes, ReturnCodes, _PresentInfo
from exceptions import FailedToInitializeAPI, FailedToCreateMesh, APINotInitialized, FailedToSetupCamera, \
    FailedToCreateLight


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

        With force_no_vk_swapchain=False, 'dxvk_GetExternalSwapchain' can be used to retrieve a raw VkImage so the
        application can decide what to do with it. i.e: Convert and present it using OpenGL.

        :param int hwnd: Windows API's HWND window handle.
        :param bool disable_srgb_conversion_for_output: # TODO: Add docstring.
        :param bool force_no_vk_swapchain: Disables the frame presentation on the screen.
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
        self.dll_path: Path = Path(dll_path).resolve()
        self._remixapi_dll_handle: ctypes.CDLL | None = None
        self._initialized: bool = False

    def init(self, startup_info: StartupInfo) -> int:
        """
        Initializes RTX Remix API, properly loading its internal DLLs and starts up the engine.
        :param StartupInfo startup_info: Instance of a StartupInfo with basic settings for the API and Engine.
        :return: SUCCESS status code if succeeded, raises ValueError if not.
        """
        if self._initialized:
            print("Remix API already initialized.")
            return ReturnCodes.SUCCESS

        try:
            self._remixapi_dll_handle = ctypes.CDLL(str(self.dll_path))
        except FileNotFoundError:
            raise FailedToInitializeAPI(f"Failed to initialize remixapi.dll with path '{self.dll_path}'")

        self.startup_info_struct = startup_info.as_struct()
        init_status = self._remixapi_dll_handle.init(ctypes.byref(self.startup_info_struct))
        if init_status == ReturnCodes.ALREADY_EXISTS:
            # TODO: Why we get this return code from remixapi? How should it be handled?
            print("Remix API already initialized.")

        elif init_status != ReturnCodes.SUCCESS:
            raise FailedToInitializeAPI(f"Failed to startup Remix. Error code: {init_status} - {ReturnCodes.get_name(init_status)}")

        self._initialized = True
        return ReturnCodes.SUCCESS

    def setup_camera(self, camera: Camera) -> int:
        """
        Binds 'camera' as the current rendering camera. Must be called every frame.

        :param Camera camera: Instance of the Camera() component.
        """
        if not self._initialized:
            raise APINotInitialized(f"Can't call setup_camera without initializing the API first.")

        cam_info = camera.as_struct()
        return_code = self._remixapi_dll_handle.setup_camera(ctypes.byref(cam_info))

        if return_code == ReturnCodes.REMIX_DEVICE_WAS_NOT_REGISTERED:
            raise APINotInitialized(f"Can't call setup_camera without initializing the API first.")

        elif return_code != ReturnCodes.SUCCESS:
            raise FailedToSetupCamera(f"Failed to call setup_camera. Error code: {return_code} - {ReturnCodes.get_name(return_code)}")

        return return_code

    def create_mesh(self, mesh: Mesh) -> int:
        """
        Registers a new mesh inside Remix engine. If successful, that mesh can later be used to call draw_instance.
        Make sure to call destroy_mesh when you're done with it.

        :param mesh: Instance of the Mesh class to create.
        """
        if not self._initialized:
            raise APINotInitialized(f"Can't call setup_camera without initializing the API first.")

        scene_mesh_handle: ctypes.c_void_p = ctypes.c_void_p(0)
        mesh_info = mesh.as_struct()
        return_code = self._remixapi_dll_handle.create_mesh(
            ctypes.byref(mesh_info),
            ctypes.byref(scene_mesh_handle)
        )
        if return_code == ReturnCodes.REMIX_DEVICE_WAS_NOT_REGISTERED:
            raise APINotInitialized(f"Can't call create_mesh without initializing the API first.")

        elif return_code != ReturnCodes.SUCCESS:
            raise FailedToCreateMesh(f"Failed to call create_mesh. Error code: {return_code} - {ReturnCodes.get_name(return_code)}")

        mesh.handle = scene_mesh_handle

        return return_code

    def create_light(self, light: Light) -> int:
        """
        Registers a new light inside Remix engine. If successful, that light can later be used to call draw_light_instance.
        Make sure to call destroy_mesh when you're done with it.

        :param light: Instance of the Light class to create.
        """
        if not self._initialized:
            raise APINotInitialized(f"Can't call create_light without initializing the API first.")

        scene_light_handle: ctypes.c_void_p = ctypes.c_void_p(0)
        light_info = light.as_struct()
        return_code = self._remixapi_dll_handle.create_light(
            ctypes.byref(light_info),
            ctypes.byref(scene_light_handle)
        )
        if return_code == ReturnCodes.REMIX_DEVICE_WAS_NOT_REGISTERED:
            raise APINotInitialized(f"Can't call create_mesh without initializing the API first.")

        elif return_code != ReturnCodes.SUCCESS:
            raise FailedToCreateLight(f"Failed to call create_light. Error code: {return_code} - {ReturnCodes.get_name(return_code)}")

        light.handle = scene_light_handle
        return return_code

    def draw_instance(self, mesh_instance: MeshInstance) -> None:
        if not self._initialized:
            raise APINotInitialized(f"Can't call draw_instance without initializing the API first.")

        mesh_instance_struct = mesh_instance.as_struct()
        self._remixapi_dll_handle.draw_instance(ctypes.byref(mesh_instance_struct))

    def draw_light_instance(self, light: Light) -> None:
        if not self._initialized:
            raise APINotInitialized(f"Can't call draw_light_instance without initializing the API first.")
        self._remixapi_dll_handle.draw_light_instance(light.handle)

    def present(self, hwnd_override: int = None):
        """
        Triggers remix to render its contents to the screen.
        :param str hwnd_override: Alternative hwnd Window handle to present. Useful for multi-window applications.
        """
        if not self._initialized:
            raise APINotInitialized(f"Can't call present without initializing the API first.")

        if not hwnd_override:
            self._remixapi_dll_handle.present(None)
            return

        present_info = _PresentInfo()
        present_info.hwndOverride = hwnd_override
        present_info.sType = _STypes.PRESENT_INFO
        present_info.pNext = 0
        self._remixapi_dll_handle.present(ctypes.byref(present_info))

    def shutdown(self):
        if self._remixapi_dll_handle and self._initialized:
            return_code = self._remixapi_dll_handle.destroy()
            if return_code != ReturnCodes.SUCCESS:
                raise ValueError(f"RemixAPI didn't shutdown happily. Return code {return_code} - {ReturnCodes.get_name(return_code)}")

        self._remixapi_dll_handle = None
        self._initialized = False

    def __del__(self):
        self.shutdown()
