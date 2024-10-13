import ctypes
import hashlib
import time
from ctypes import wintypes


def HASH(value: int = 0) -> ctypes.c_uint64:
    """
    Helper function to create 64bit integer hashes.
    If no value is passed, it generates a new 64-bit integer as a hash.
    :param value: An integer value
    :return:
    """
    if value:
        return ctypes.c_uint64(value)

    value = int(hashlib.sha256(str(time.time()).encode()).hexdigest(), 16)
    return ctypes.c_uint64(value)


class CategoryFlags:
    NONE = 0
    WORLD_UI = 1 << 0
    WORLD_MATTE = 1 << 1
    SKY = 1 << 2
    IGNORE = 1 << 3
    IGNORE_LIGHTS = 1 << 4
    IGNORE_ANTI_CULLING = 1 << 5
    IGNORE_MOTION_BLUR = 1 << 6
    IGNORE_OPACITY_MICROMAP = 1 << 7
    HIDDEN = 1 << 8
    PARTICLE = 1 << 9
    BEAM = 1 << 10
    DECAL_STATIC = 1 << 11
    DECAL_DYNAMIC = 1 << 12
    DECAL_SINGLE_OFFSET = 1 << 13
    DECAL_NO_OFFSET = 1 << 14
    ALPHA_BLEND_TO_CUTOUT = 1 << 15
    TERRAIN = 1 << 16
    ANIMATED_WATER = 1 << 17
    THIRD_PERSON_PLAYER_MODEL = 1 << 18
    THIRD_PERSON_PLAYER_BODY = 1 << 19
    IGNORE_BAKED_LIGHTING = 1 << 20
    IGNORE_ALPHA_CHANNEL = 1 << 21


class ReturnCodes:
    SUCCESS = 0
    GENERAL_FAILURE = 1
    # WinAPI's LoadLibrary has failed
    LOAD_LIBRARY_FAILURE = 2
    INVALID_ARGUMENTS = 3
    # Couldn't find 'remixInitialize' function in the .dll
    GET_PROC_ADDRESS_FAILURE = 4
    # CreateD3D9 / RegisterD3D9Device can be called only once
    ALREADY_EXISTS = 5
    # RegisterD3D9Device requires the device that was created with IDirect3DDevice9Ex, returned by CreateD3D9
    REGISTERING_NON_REMIX_D3D9_DEVICE = 6
    # RegisterD3D9Device was not called
    REMIX_DEVICE_WAS_NOT_REGISTERED = 7
    INCOMPATIBLE_VERSION = 8
    # WinAPI's SetDllDirectory has failed
    SET_DLL_DIRECTORY_FAILURE = 9
    # WinAPI's GetFullPathName has failed
    GET_FULL_PATH_NAME_FAILURE = 10
    NOT_INITIALIZED = 11
    # Error codes that are encoded as HRESULT, i.e. returned from D3D9 functions.
    # Look MAKE_D3DHRESULT, but with _FACD3D=0x896, instead of D3D9's 0x876
    HRESULT_NO_REQUIRED_GPU_FEATURES = 0x88960001
    HRESULT_DRIVER_VERSION_BELOW_MINIMUM = 0x88960002
    HRESULT_DXVK_INSTANCE_EXTENSION_FAIL = 0x88960003
    HRESULT_VK_CREATE_INSTANCE_FAIL = 0x88960004
    HRESULT_VK_CREATE_DEVICE_FAIL = 0x88960005
    HRESULT_GRAPHICS_QUEUE_FAMILY_MISSING = 0x88960006

    @staticmethod
    def get_name(error_code: int) -> str:
        """Returns the error code name, for convenience."""
        return {
            ReturnCodes.SUCCESS: 'SUCCESS',
            ReturnCodes.GENERAL_FAILURE: 'GENERAL_FAILURE',
            ReturnCodes.LOAD_LIBRARY_FAILURE: 'LOAD_LIBRARY_FAILURE',
            ReturnCodes.INVALID_ARGUMENTS: 'INVALID_ARGUMENTS',
            ReturnCodes.GET_PROC_ADDRESS_FAILURE: 'GET_PROC_ADDRESS_FAILURE',
            ReturnCodes.ALREADY_EXISTS: 'ALREADY_EXISTS',
            ReturnCodes.REGISTERING_NON_REMIX_D3D9_DEVICE: 'REGISTERING_NON_REMIX_D3D9_DEVICE',
            ReturnCodes.REMIX_DEVICE_WAS_NOT_REGISTERED: 'REMIX_DEVICE_WAS_NOT_REGISTERED',
            ReturnCodes.INCOMPATIBLE_VERSION: 'INCOMPATIBLE_VERSION',
            ReturnCodes.SET_DLL_DIRECTORY_FAILURE: 'SET_DLL_DIRECTORY_FAILURE',
            ReturnCodes.GET_FULL_PATH_NAME_FAILURE: 'GET_FULL_PATH_NAME_FAILURE',
            ReturnCodes.NOT_INITIALIZED: 'NOT_INITIALIZED',
            ReturnCodes.HRESULT_NO_REQUIRED_GPU_FEATURES: 'HRESULT_NO_REQUIRED_GPU_FEATURES',
            ReturnCodes.HRESULT_DRIVER_VERSION_BELOW_MINIMUM: 'HRESULT_DRIVER_VERSION_BELOW_MINIMUM',
            ReturnCodes.HRESULT_DXVK_INSTANCE_EXTENSION_FAIL: 'HRESULT_DXVK_INSTANCE_EXTENSION_FAIL',
            ReturnCodes.HRESULT_VK_CREATE_INSTANCE_FAIL: 'HRESULT_VK_CREATE_INSTANCE_FAIL',
            ReturnCodes.HRESULT_VK_CREATE_DEVICE_FAIL: 'HRESULT_VK_CREATE_DEVICE_FAIL',
            ReturnCodes.HRESULT_GRAPHICS_QUEUE_FAMILY_MISSING: 'HRESULT_GRAPHICS_QUEUE_FAMILY_MISSING',
        }[error_code]


class _STypes:
    """
    "remixapi_StructType" enum values for "sType" fields in the Remix API Structs.
    Refer to the remix_c.h header.
    """
    NONE = 0
    INITIALIZE_LIBRARY_INFO = 1
    MATERIAL_INFO = 2
    MATERIAL_INFO_PORTAL_EXT = 3
    MATERIAL_INFO_TRANSLUCENT_EXT = 4
    MATERIAL_INFO_OPAQUE_EXT = 5
    LIGHT_INFO = 6
    LIGHT_INFO_DISTANT_EXT = 7
    LIGHT_INFO_CYLINDER_EXT = 8
    LIGHT_INFO_DISK_EXT = 9
    LIGHT_INFO_RECT_EXT = 10
    LIGHT_INFO_SPHERE_EXT = 11
    MESH_INFO = 12
    INSTANCE_INFO = 13
    INSTANCE_INFO_BONE_TRANSFORMS_EXT = 14
    INSTANCE_INFO_BLEND_EXT = 15
    CAMERA_INFO = 16
    CAMERA_INFO_PARAMETERIZED_EXT = 17
    MATERIAL_INFO_OPAQUE_SUBSURFACE_EXT = 18
    INSTANCE_INFO_OBJECT_PICKING_EXT = 19
    LIGHT_INFO_DOME_EXT = 20
    LIGHT_INFO_USD_EXT = 21
    STARTUP_INFO = 22
    PRESENT_INFO = 23


class _StartupInfo(ctypes.Structure):
    """Mapping to remixapi_StartupInfo C struct."""
    _fields_ = [
        ('sType', ctypes.c_int),
        ('pNext', ctypes.c_void_p),
        ('hwnd', wintypes.HWND),
        ('disableSrgbConversionForOutput', ctypes.c_int),
        ('forceNoVkSwapchain', ctypes.c_int),
        ('editorModeEnabled', ctypes.c_int),
    ]


class _PresentInfo(ctypes.Structure):
    """Mapping to remixapi_StartupInfo C struct."""
    _fields_ = [
        ('sType', ctypes.c_int),
        ('pNext', ctypes.c_void_p),
        ('hwndOverride', wintypes.HWND),
    ]


class Rect2D(ctypes.Structure):
    """ctypes direct mapping to remixapi_Rect2D struct"""
    _fields_ = [
        ("left", ctypes.c_int32),
        ("top", ctypes.c_int32),
        ("right", ctypes.c_int32),
        ("bottom", ctypes.c_int32),
    ]


class Float2D(ctypes.Structure):
    """ctypes direct mapping to remixapi_Float2D struct"""
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]


class Float3D(ctypes.Structure):
    """ctypes direct mapping to remixapi_Float3D struct"""
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
    ]


class Float4D(ctypes.Structure):
    """ctypes direct mapping to remixapi_Float4D struct"""
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float),
    ]


class _CameraInfoParameterizedEXT(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_CameraInfoParameterizedEXT.

    Remix API allows both parameterized data (fov, position, clipping planes distance, etc.) or transformation matrix.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("position", Float3D),
        ("forward", Float3D),
        ("up", Float3D),
        ("right", Float3D),
        ("fovYInDegrees", ctypes.c_float),
        ("aspect", ctypes.c_float),
        ("nearPlane", ctypes.c_float),
        ("farPlane", ctypes.c_float),
    ]


class _CameraInfo(ctypes.Structure):
    """
    ctpyes direct mapping to remixapi_CameraInfo.
        - Use pNext pointer to point to a _CameraInfoParameterizedEXT struct to use parametrized data.
        - Assign "view" and "projection" stack-allocated matrices to use your own computed matrices instead.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("type", ctypes.c_int),
        ("view", (ctypes.c_float * 4) * 4),
        ("projection", (ctypes.c_float * 4) * 4)
    ]


class _HardcodedVertex(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_HardcodedVertex.

    Vertex data featuring position, normal, texcoord and color.
    Graphics APIs allow users to define their own custom data for vertices but at the moment Remix only supports these hardcoded ones.
    """
    _fields_ = [
        ("position", ctypes.c_float * 3),
        ("normal", ctypes.c_float * 3),
        ("texcoord", ctypes.c_float * 2),
        ("color", ctypes.c_uint32),
        ("_pad0", ctypes.c_uint32),
        ("_pad1", ctypes.c_uint32),
        ("_pad2", ctypes.c_uint32),
        ("_pad3", ctypes.c_uint32),
        ("_pad4", ctypes.c_uint32),
        ("_pad5", ctypes.c_uint32),
        ("_pad6", ctypes.c_uint32),
    ]


class _MeshInfoSkinning(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_MeshInfoSkinning.

    Use this if your mesh surface has skinning data.
    Refer to _InstanceInfoBoneTransformsEXT to define the skeleton data.
    """
    _fields_ = [
        ("bonesPerVertex", ctypes.c_uint32),  # I.e. 2 bones per vertex.
        # Each tuple of 'bonesPerVertex' float-s defines a vertex.
        # I.e. the size must be (bonesPerVertex * vertexCount).
        ("blendWeights_values", ctypes.POINTER(ctypes.c_float)),  # [vert0-bone0, vert1-bone0, vert0-bone1, vert1-bone1, ...].
        ("blendWeights_count", ctypes.c_uint32),  # len(blendWeights_values).
        # Each tuple of 'bonesPerVertex' uint32_t-s defines a vertex.
        # I.e. the size must be (bonesPerVertex * vertexCount).
        ("blendIndices_values", ctypes.POINTER(ctypes.c_uint32)),  # Maps vertices to the bones array in _InstanceInfoBoneTransformsEXT. [vert0-bone0, vert0-bone1, vert1-bone0, vert1-bone1, ...]
        ("blendIndices_count", ctypes.c_uint32),  # len(blendIndices_values).
    ]


class _MeshInfoSurfaceTriangles(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_MeshInfoSurfaceTriangles.

    The bulk data to define your mesh with vertices, indices and materials.
    Make sure to dispose the data after calling CreateMesh.
    """
    _fields_ = [
        ("vertices_values", ctypes.POINTER(_HardcodedVertex)),
        ("vertices_count", ctypes.c_uint64),
        ("indices_values", ctypes.POINTER(ctypes.c_uint32)),
        ("indices_count", ctypes.c_uint64),
        ("skinning_hasvalue", ctypes.c_int),
        ("skinning_value", _MeshInfoSkinning),
        ("material", ctypes.c_void_p),
    ]


class _MeshInfo(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_MeshInfo.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("hash", ctypes.c_uint64),
        ("surfaces_values", ctypes.POINTER(_MeshInfoSurfaceTriangles)),
        ("surfaces_count", ctypes.c_uint32),
    ]


class _Transform(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_Transform.
    """
    _fields_ = [
        ("matrix", (ctypes.c_float * 4) * 3),
    ]


class _InstanceInfo(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_InstanceInfo.

    "mesh" should be assigned with the handle returned by CreateMesh call.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("categoryFlags", ctypes.c_uint32),
        ("mesh", ctypes.c_void_p),
        ("transform", _Transform),
        ("doubleSided", ctypes.c_uint32),
    ]


class _LightInfoLightShaping(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_LightInfoLightShaping.

    Defines a focal cone shaping for sphere, disk and rect lights.
    Assign to "remixapi_LightInfoSphereEXT.shaping_value" pointer, setting "shaping_hasvalue" to true.
    """
    _fields_ = [
        ("direction", Float3D),
        ("coneAngleDegrees", ctypes.c_float),
        ("coneSoftness", ctypes.c_float),
        ("focusExponent", ctypes.c_float),
    ]


class _LightInfoSphereEXT(ctypes.Structure):
    """
    ctpyes direct mapping to remixapi_LightInfoSphereEXT.

    Extension struct used to define a sphere light type in "remixapi_LightInfo.pNext" pointer.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("position", Float3D),
        ("radius", ctypes.c_float),
        ("shaping_hasvalue", ctypes.c_uint32),
        ("shaping_value", _LightInfoLightShaping),
    ]


class _LightInfoRectEXT(ctypes.Structure):
    """
    ctpyes direct mapping to remixapi_LightInfoRectEXT.

    Extension struct used to define a Rect light type in "remixapi_LightInfo.pNext" pointer.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("position", Float3D),
        ("xAxis", Float3D),
        ("xSize", ctypes.c_float),
        ("yAxis", Float3D),
        ("ySize", ctypes.c_float),
        ("direction", Float3D),
        ("shaping_hasvalue", ctypes.c_uint32),
        ("shaping_value", _LightInfoLightShaping),
    ]


class _LightInfoDiskEXT(ctypes.Structure):
    """
    ctpyes direct mapping to remixapi_LightInfoDiskEXT.

    Extension struct used to define a Disk light type in "remixapi_LightInfo.pNext" pointer.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("position", Float3D),
        ("xAxis", Float3D),
        ("xRadius", ctypes.c_float),
        ("yAxis", Float3D),
        ("yRadius", ctypes.c_float),
        ("direction", Float3D),
        ("shaping_hasvalue", ctypes.c_uint32),
        ("shaping_value", _LightInfoLightShaping),
    ]


class _LightInfoCylinderEXT(ctypes.Structure):
    """
    ctpyes direct mapping to remixapi_LightInfoCylinderEXT.

    Extension struct used to define a Cylinder light type in "remixapi_LightInfo.pNext" pointer.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("position", Float3D),
        ("radius", ctypes.c_float),
        ("axis", Float3D),
        ("axisLength", ctypes.c_float),
    ]


class _LightInfoDistantEXT(ctypes.Structure):
    """
    ctpyes direct mapping to remixapi_LightInfoDistantEXT.

    Extension struct used to define a Distant/Directional light type in "remixapi_LightInfo.pNext" pointer.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("direction", Float3D),
        ("angularDiameterDegrees", ctypes.c_float),
    ]


class _LightInfoDomeEXT(ctypes.Structure):
    """
    ctpyes direct mapping to remixapi_LightInfoDistantEXT.

    Extension struct used to define a Dome/Skybox/HDRI light type in "remixapi_LightInfo.pNext" pointer.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("transform", _Transform),
        ("colorTexture", ctypes.c_wchar_p),
    ]


class _LightInfo(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_LightInfo.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("hash", ctypes.c_uint64),
        ("radiance", Float3D),
    ]


class FilterModes:
    NEAREST = 0
    LINEAR = 1


class WrapModes:
    CLAMP = 0
    REPEAT = 1
    MIRRORED_REPEAT = 2
    CLIP = 3


class BlendTypes:
    """
    Blend type options. Refer to InstanceManager::calculateAlphaState in rtx_instance_manager.cpp.

    https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/src/dxvk/rtx_render/rtx_instance_manager.cpp
    """
    ALPHA = 0  # standard ONE_MINUS_SRC_ALPHA if invertedBlend is False, else SRC_ALPHA
    ALPHA_EMISSIVE = 1  # SRC_ALPHA
    REVERSE_ALPHA_EMISSIVE = 2
    COLOR = 3
    COLOR_EMISSIVE = 4
    REVERSE_COLOR_EMISSIVE = 5
    EMISSIVE = 6
    MULTIPLICATIVE = 7
    DOUBLE_MULTIPLICATIVE = 8
    REVERSE_ALPHA = 9
    REVERSE_COLOR = 10


class AlphaTestTypes:
    """
    Alpha blend operations. Refer to InstanceManager::calculateAlphaState in rtx_instance_manager.cpp.

    https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/src/dxvk/rtx_render/rtx_instance_manager.cpp
    """
    NEVER = 0
    LESS = 1
    EQUAL = 2
    LESS_OR_EQUAL = 3
    GREATER = 4
    NOT_EQUAL = 5
    GREATER_OR_EQUAL = 6
    ALWAYS = 7


class _MaterialInfo(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_MaterialInfo.

    Base struct with common data for all Remix material types.

    pNext should point to one of _MaterialInfoOpaqueEXT, _MaterialInfoTranslucentEXT or _MaterialInfoPortalEXT struct.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("albedoTexture", ctypes.c_wchar_p),
        ("normalTexture", ctypes.c_wchar_p),
        ("tangentTexture", ctypes.c_wchar_p),
        ("emissiveTexture", ctypes.c_wchar_p),
        ("emissiveIntensity", ctypes.c_float),
        ("emissiveColorConstant", Float3D),
        ("spriteSheetRow", ctypes.c_uint8),
        ("spriteSheetCol", ctypes.c_uint8),
        ("spriteSheetFps", ctypes.c_uint8),
        ("filterMode", ctypes.c_uint8),
        ("wrapModeU", ctypes.c_uint8),
        ("wrapModeV", ctypes.c_uint8),
    ]


class _MaterialInfoOpaqueEXT(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_MaterialInfoOpaqueEXT.

    Defines a material to use the OpacityPBR shader.

    pNext should point to _MaterialInfoOpaqueSubsurfaceEXT to support Subsurface Scattering features.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("roughnessTexture", ctypes.c_wchar_p),
        ("anisotropy", ctypes.c_float),
        ("albedoConstant", Float3D),
        ("opacityConstant", ctypes.c_float),
        ("roughnessConstant", ctypes.c_float),
        ("metallicConstant", ctypes.c_float),
        ("thinFilmThickness_hasvalue", ctypes.c_uint32),
        ("thinFilmThickness_value", ctypes.c_float),
        ("alphaIsThinFilmThickness", ctypes.c_uint32),
        ("heightTexture", ctypes.c_wchar_p),
        ("heightTextureStrength", ctypes.c_float),
        ("useDrawCallAlphaState", ctypes.c_uint32),
        ("blendType_hasvalue", ctypes.c_uint32),
        ("blendType_value", ctypes.c_uint32),
        ("invertedBlend", ctypes.c_uint32),
        ("alphaTestType", ctypes.c_uint32),
        ("alphaReferenceValue", ctypes.c_uint8),
    ]


class _MaterialInfoOpaqueSubsurfaceEXT(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_MaterialInfoOpaqueSubsurfaceEXT.

    Defines extended material data to enable Subsurface Scattering in an OpacityPBR material.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("subsurfaceTransmittanceTexture", ctypes.c_wchar_p),
        ("subsurfaceThicknessTexture", ctypes.c_wchar_p),
        ("subsurfaceSingleScatteringAlbedoTexture", ctypes.c_wchar_p),
        ("subsurfaceTransmittanceColor", Float3D),
        ("subsurfaceMeasurementDistance", ctypes.c_float),
        ("subsurfaceSingleScatteringAlbedo", Float3D),
        ("subsurfaceVolumetricAnisotropy", ctypes.c_float),
    ]


class _MaterialInfoTranslucentEXT(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_MaterialInfoTranslucentSubsurfaceEXT.

    Defines a material to use the TranslucentPBR shader.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("transmittanceTexture", ctypes.c_wchar_p),
        ("refractiveIndex", ctypes.c_float),
        ("transmittanceColor", Float3D),
        ("transmittanceMeasurementDistance", ctypes.c_float),
        ("thinWallThickness_hasvalue", ctypes.c_uint32),
        ("thinWallThickness_value", ctypes.c_float),
        ("useDiffuseLayer", ctypes.c_uint32),
    ]


class _MaterialInfoPortalEXT(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_MaterialInfoPortalEXT.

    Defines a material to use the Portal shader.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("rayPortalIndex", ctypes.c_uint8),
        ("rotationSpeed", ctypes.c_float),
    ]


class _InstanceInfoBoneTransformsEXT(ctypes.Structure):
    """
    ctypes direct mapping to remixapi_InstanceInfoBoneTransformsEXT.

    Defines an array of bone transforms in a skeleton.
    """
    _fields_ = [
        ("sType", ctypes.c_int),
        ("pNext", ctypes.c_void_p),
        ("boneTransforms_values", ctypes.POINTER(_Transform)),
        ("boneTransforms_count", ctypes.c_uint32),
    ]
