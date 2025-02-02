import ctypes
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from api_data_types import _STypes, Float3D, _CameraInfoParameterizedEXT, _CameraInfo, Float2D, _HardcodedVertex, \
    _MeshInfoSkinning, _MeshInfoSurfaceTriangles, _MeshInfo, _Transform, _InstanceInfo, _LightInfoLightShaping, \
    _LightInfo, _LightInfoSphereEXT, CategoryFlags, FilterModes, WrapModes, _MaterialInfo, BlendTypes, \
    _MaterialInfoOpaqueEXT, AlphaTestTypes, _MaterialInfoOpaqueSubsurfaceEXT, _MaterialInfoTranslucentEXT, \
    _MaterialInfoPortalEXT, _InstanceInfoBoneTransformsEXT, _LightInfoRectEXT, _LightInfoDiskEXT, _LightInfoCylinderEXT, \
    _LightInfoDistantEXT, _LightInfoDomeEXT
from exceptions import WrongSkinningDataCount, ResourceNotInitialized, SkinningDataOutOfSkeletonRange, \
    InvalidSkinningData


class CameraTypes:
    WORLD = 0
    SKY = 1
    VIEW_MODEL = 2


class Camera:
    def __init__(
        self,
        cam_type: int = CameraTypes.WORLD,
        position: Float3D = Float3D(0, 0, 0),
        forward: Float3D = Float3D(0, 0, 1),
        up: Float3D = Float3D(0, 1, 0),
        right: Float3D = Float3D(1, 0, 0),
        fov_y: float = 70,
        aspect: float = 16.0/9.0,
        near_plane: float = 0.1,
        far_plane: float = 1000.0,
    ):
        """
        General camera class used to render in World, View Model or Sky mode.

        :param cam_type: Sets the camera mode/purpose. One of CameraTypes values: WORLD, VIEW_MODEL or SKY.
        :param position: Position vector. i.e: Float3D(0, 0, 0)
        :param forward: Forward vector. i.e: Float3D(0, 0, 1)
        :param up: Up vector. i.e: Float3D(0, 1, 0)
        :param right: Right vector. i.e: Float3D(1, 0, 0)
        :param fov_y: FOV angle in degrees from the Y axis.
        :param aspect: Aspect ratio of the screen. i.e: 16.0/9.0 for FHD screens.
        :param near_plane: Nearest clipping plane to render. Anything behind it won't render.
        :param far_plane: Farthest clipping plane to render. Anything further it won't render.
        """
        self.cam_type = cam_type
        self.position = position
        self.forward = forward
        self.up = up
        self.right = right
        self.fov_y = fov_y
        self.aspect = aspect
        self.near_plane = near_plane
        self.far_plane = far_plane
        self.cam_params_info: _CameraInfoParameterizedEXT | None = None

    def as_struct(self) -> _CameraInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.cam_params_info = _CameraInfoParameterizedEXT()
        self.cam_params_info.sType = _STypes.CAMERA_INFO_PARAMETERIZED_EXT
        self.cam_params_info.pNext = 0
        self.cam_params_info.position = self.position
        self.cam_params_info.forward = self.forward
        self.cam_params_info.up = self.up
        self.cam_params_info.right = self.right
        self.cam_params_info.fovYInDegrees = self.fov_y
        self.cam_params_info.aspect = self.aspect
        self.cam_params_info.nearPlane = self.near_plane
        self.cam_params_info.farPlane = self.far_plane

        cam_info = _CameraInfo()
        cam_info.sType = _STypes.CAMERA_INFO
        cam_info.type = self.cam_type
        cam_info.pNext = ctypes.cast(ctypes.byref(self.cam_params_info), ctypes.c_void_p)
        return cam_info


class Vertex:
    def __init__(
        self,
        position: Float3D = Float3D(0, 0, 0),
        normal: Float3D = Float3D(0, 0, 1),
        texcoord: Float2D = Float2D(0, 0),
        color: int = 0xFFFFFFFF
    ):
        """
        Vertex class featuring position, normal, 1 UV/tex coord and 1 color.
        Manipulating data from python to C is very slow. For real scenarios consider using an asset loader in C instead.
        :param position: Position vector.
        :param normal: Normal vector.
        :param texcoord: UV coordinate.
        :param color: Vertex color packed into a 32bit unsigned int.
        """
        self.position: Float3D = position
        self.normal: Float3D = normal
        self.texcoord: Float2D = texcoord
        self.color: int = color

    def as_struct(self) -> _HardcodedVertex:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        vertex = _HardcodedVertex()
        vertex.position[0] = self.position.x
        vertex.position[1] = self.position.y
        vertex.position[2] = self.position.z
        vertex.normal[0] = self.normal.x
        vertex.normal[1] = self.normal.y
        vertex.normal[2] = self.normal.z
        vertex.texcoord[0] = self.texcoord.x
        vertex.texcoord[1] = self.texcoord.y
        vertex.color = ctypes.c_uint32(self.color)
        return vertex


class SkinningData:
    def __init__(
        self,
        bones_per_vertex: int,
        blend_weights: List[float],
        blend_indices: List[int],
    ):
        """
        Defines skinning data for deforming a MeshSurface based on the MeshInstance's Skeleton transforms array.
        The layout of Weights and Indices are dependent on 'bones_per_vertex'.

        I.e: For 2 bones per vertex:
            Weights: [v0-bone0, v1-bone0, v0-bone1, v1-bone1, ...].

            Indices: [v0-bone0, v0-bone1, v1-bone0, v1-bone1, ...].

        Make sure to normalize your weights per vertex, or else a "budget" weight of 1.0 will be consumed in order of bones.

        I.e: 4 bones: [0.3, 0.5, 200, 0.3] -> 0.3 for bone0, 0.5 for bone1, 0.2 for bone2, 0 for bone3.

        :param bones_per_vertex: How many bones influence each vertex. 4 is a common value.
        :param blend_weights: Influence weight of each bone over each vertex.
        :param blend_indices: Per vertex bones indices in the MeshInstance skeleton array.
        """
        self.bones_per_vertex = bones_per_vertex
        self.blend_weights = blend_weights
        self.blend_indices = blend_indices
        self.blend_weights_array = None
        self.blend_index_array = None
        self.skinning_struct: _MeshInfoSkinning | None = None
        self.check_for_errors()

    def check_for_errors(self, should_raise: bool = True):
        """Checks for potential errors in the SkinningData."""
        errors = list()
        def raise_or_append(error_msg: str):
            if should_raise:
                raise InvalidSkinningData(error_msg)
            errors.append(error_msg)

        if not self.blend_weights:
            raise_or_append(f"Invalid blend_weights: {self.blend_weights}")

        elif len(self.blend_weights) % self.bones_per_vertex != 0:
            raise_or_append(f"blend_weights (length {len(self.blend_weights)}) should be multiple of bones_per_vertex.")

        if not self.blend_indices:
            raise_or_append(f"Invalid blend_indices: {self.blend_indices}")

        elif len(self.blend_indices) % self.bones_per_vertex != 0:
            raise_or_append(f"blend_indices (length {len(self.blend_indices)}) should be multiple of bones_per_vertex.")

        return errors

    def as_struct(self) -> _MeshInfoSkinning:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.check_for_errors()

        blend_weights_count = len(self.blend_weights)
        self.blend_weights_array = (ctypes.c_float * blend_weights_count)()
        for i, weight in enumerate(self.blend_weights):
            self.blend_weights_array[i] = weight

        index_count = len(self.blend_indices)
        self.blend_index_array = (ctypes.c_uint32 * index_count)()
        for i, idx in enumerate(self.blend_indices):
            self.blend_index_array[i] = idx

        self.skinning_struct = _MeshInfoSkinning()
        self.skinning_struct.bonesPerVertex = self.bones_per_vertex
        self.skinning_struct.blendWeights_values = ctypes.cast(self.blend_weights_array, ctypes.POINTER(ctypes.c_float))
        self.skinning_struct.blendWeights_count = blend_weights_count
        self.skinning_struct.blendIndices_values = ctypes.cast(self.blend_index_array, ctypes.POINTER(ctypes.c_uint32))
        self.skinning_struct.blendIndices_count = index_count
        return self.skinning_struct


class Material(ABC):
    @abstractmethod
    def __init__(
        self,
        mat_hash: ctypes.c_uint64,
        albedo_texture: str | Path = "",
        normal_texture: str | Path = "",
        tangent_texture: str | Path = "",
        emissive_texture: str | Path = "",
        emissive_intensity: float = 0,
        emissive_color_constant: Float3D = Float3D(0, 0, 0),
        sprite_sheet_row: int = 0,
        sprite_sheet_col: int = 0,
        sprite_sheet_fps: int = 0,
        filter_mode: int = FilterModes.LINEAR,
        wrap_mode_u: int = WrapModes.REPEAT,
        wrap_mode_v: int = WrapModes.REPEAT,
    ):
        """
        Abstract class to define materials like OpacityPBR, TranslucentPBR or Portal.

        :param mat_hash: 64bit uint HASH to uniquely identify this material. You should manage your own hashes.
        :param albedo_texture: Path to the .dds (BC7) albedo texture.
        :param normal_texture: Path to the .dds (BC5 - Octahedral) normal texture.
        :param tangent_texture: Path to the .dds (BC5, I guess?) tangent texture.
        :param emissive_texture: Path to the .dds (BC7) emissive texture.
        :param emissive_intensity: Emissive intensity
        :param emissive_color_constant: Color constant to use as emissive if no texture is provided.
        :param sprite_sheet_row: Row count for the animation sprite sheet grid.
        :param sprite_sheet_col: Column count for the animation sprite sheet grid.
        :param sprite_sheet_fps: Sprite sheet frames per second to play.
        :param filter_mode: Which filter to apply to the textures.
        :param wrap_mode_u: What to do with UV coordinates outside 0-1 range in U/X direction.
        :param wrap_mode_v: What to do with UV coordinates outside 0-1 range in V/Y direction.
        """
        self.handle: ctypes.c_void_p = ctypes.c_void_p(0)
        self.mat_hash = mat_hash
        self.albedo_texture = albedo_texture
        self.normal_texture = normal_texture
        self.tangent_texture = tangent_texture
        self.emissive_texture = emissive_texture
        self.emissive_intensity = emissive_intensity
        self.emissive_color_constant = emissive_color_constant
        self.sprite_sheet_row = sprite_sheet_row
        self.sprite_sheet_col = sprite_sheet_col
        self.sprite_sheet_fps = sprite_sheet_fps
        self.filter_mode = filter_mode
        self.wrap_mode_u = wrap_mode_u
        self.wrap_mode_v = wrap_mode_v
        self.material_info: _MaterialInfo | None = None

    @abstractmethod
    def as_struct(self, _child_struct_pointer: ctypes.c_void_p | None = None) -> _MaterialInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.material_info = _MaterialInfo()
        self.material_info.sType = _STypes.MATERIAL_INFO
        self.material_info.pNext = _child_struct_pointer
        self.material_info.hash = self.mat_hash
        self.material_info.albedoTexture = str(self.albedo_texture)
        self.material_info.normalTexture = str(self.normal_texture)
        self.material_info.tangentTexture = str(self.tangent_texture)
        self.material_info.emissiveTexture = str(self.emissive_texture)
        self.material_info.emissiveIntensity = self.emissive_intensity
        self.material_info.emissiveColorConstant = self.emissive_color_constant
        self.material_info.spriteSheetRow = self.sprite_sheet_row
        self.material_info.spriteSheetCol = self.sprite_sheet_col
        self.material_info.spriteSheetFps = self.sprite_sheet_fps
        self.material_info.filterMode = self.filter_mode
        self.material_info.wrapModeU = self.wrap_mode_u
        self.material_info.wrapModeV = self.wrap_mode_v
        return self.material_info


class OpacitySSSData:
    def __init__(
        self,
        transmittance_texture: str | Path = "",
        thickness_texture: str | Path = "",
        single_scattering_albedo_texture: str | Path = "",
        transmittance_color: Float3D = Float3D(0, 0, 0),
        measurement_distance: float = 0.1,
        single_scattering_albedo: Float3D = Float3D(0, 0, 0),
        volumetric_anisotropy: float = 0,
    ):
        # TODO: Add docstring.
        self.transmittance_texture = transmittance_texture
        self.thickness_texture = thickness_texture
        self.single_scattering_albedo_texture = single_scattering_albedo_texture
        self.transmittance_color = transmittance_color
        self.measurement_distance = measurement_distance
        self.single_scattering_albedo = single_scattering_albedo
        self.volumetric_anisotropy = volumetric_anisotropy
        self.sss_info: _MaterialInfoOpaqueSubsurfaceEXT | None = None

    def as_struct(self):
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.sss_info = _MaterialInfoOpaqueSubsurfaceEXT()
        self.sss_info.sType = _STypes.MATERIAL_INFO_OPAQUE_SUBSURFACE_EXT
        self.sss_info.pNext = None
        self.sss_info.subsurfaceTransmittanceTexture = str(self.transmittance_texture)
        self.sss_info.subsurfaceThicknessTexture = str(self.thickness_texture)
        self.sss_info.subsurfaceSingleScatteringAlbedoTexture = str(self.single_scattering_albedo_texture)
        self.sss_info.subsurfaceTransmittanceColor = self.transmittance_color
        self.sss_info.subsurfaceMeasurementDistance = self.measurement_distance
        self.sss_info.subsurfaceSingleScatteringAlbedo = self.single_scattering_albedo
        self.sss_info.subsurfaceVolumetricAnisotropy = self.volumetric_anisotropy
        return self.sss_info


class OpacityPBR(Material):
    def __init__(
        self,
        # Base Material Parameters:
        mat_hash: ctypes.c_uint64,
        albedo_texture: str | Path = "",
        normal_texture: str | Path = "",
        tangent_texture: str | Path = "",
        emissive_texture: str | Path = "",
        emissive_intensity: float = 0,
        emissive_color_constant: Float3D = Float3D(0, 0, 0),
        sprite_sheet_row: int = 0,
        sprite_sheet_col: int = 0,
        sprite_sheet_fps: int = 0,
        filter_mode: int = FilterModes.LINEAR,
        wrap_mode_u: int = WrapModes.REPEAT,
        wrap_mode_v: int = WrapModes.REPEAT,

        # OpacityPBR Parameters:
        roughness_texture: str | Path = "",
        metallic_texture: str | Path = "",
        anisotropy: float = 0,
        albedo_constant: Float3D = Float3D(1, 1, 1),
        opacity_constant: float = 1,
        roughness_constant: float = 1,
        metallic_constant: float = 0,
        thin_film_thickness_value: float | None = None,
        alpha_is_thin_film_thickness: bool = False,
        height_texture: str | Path = "",
        displace_in: float = 0,
        use_draw_call_alpha_state: bool = True,
        blend_type_value: int | None = None,
        inverted_blend: bool = False,
        alpha_test_type: int = AlphaTestTypes.NEVER,
        alpha_reference_value: int = 0,
        displace_out: float = 0,
        subsurface_data: OpacitySSSData | None = None,
    ):
        """
        Define an OpacityPBR material.

        :param mat_hash: 64bit uint HASH to uniquely identify this material. You should manage your own hashes.
        :param albedo_texture: Path to the .dds (BC7) albedo texture.
        :param normal_texture: Path to the .dds (BC5 - Octahedral) normal texture.
        :param tangent_texture: Path to the .dds (BC5, I guess?) tangent texture.
        :param emissive_texture: Path to the .dds (BC7) emissive texture.
        :param emissive_intensity: Emissive intensity
        :param emissive_color_constant: Color constant to use as emissive if no texture is provided.
        :param sprite_sheet_row: Row count for the animation sprite sheet grid.
        :param sprite_sheet_col: Column count for the animation sprite sheet grid.
        :param sprite_sheet_fps: Sprite sheet frames per second to play.
        :param filter_mode: Which filter to apply to the textures.
        :param wrap_mode_u: What to do with UV coordinates outside 0-1 range in U/X direction.
        :param wrap_mode_v: What to do with UV coordinates outside 0-1 range in V/Y direction.

        :param roughness_texture: Path to the .dds (BC4) roughness map texture.
        :param metallic_texture: Path to the .dds (BC4) metallic map texture.
        :param anisotropy: Anisotropy roughness effect intensity (0-1 range).
        :param albedo_constant: Anisotropy roughness effect intensity (0-1 range).
        :param opacity_constant: Opacity constant, if not provided by albedo_texture.
        :param roughness_constant: Roughness constant to use if there is no roughness_texture.
        :param metallic_constant: Metallic constant to use if there is no roughness_texture.
        :param thin_film_thickness_value: Thickness of the thin film effect (colorful distortions on oil or bubbles).
        :param alpha_is_thin_film_thickness: Use alpha channel do drive thin thickness instead.
        :param height_texture: Path to the .dds (BC4) Height/Displacement (POM) texture.
        :param displace_in: POM max. depth in world-space texture size. i.e: A value of 0.1 for a 1sqr meter texture = 10cm max. depth.
        :param use_draw_call_alpha_state: When injected in a dx9 game, whether it should use alpha flags from original draw call or not.
        :param blend_type_value: Which blend type to use. Check BlendTypes class for more info.
        :param inverted_blend: Should the alpha blending operation be inverted?
        :param alpha_test_type: Type of alpha test operation to perform.
        :param alpha_reference_value: The reference value to compute transparency from alpha channel.
        :param displace_out: Same as displace_in, but for outwards protrusion.
        """
        super().__init__(
            mat_hash=mat_hash,
            albedo_texture=albedo_texture,
            normal_texture=normal_texture,
            tangent_texture=tangent_texture,
            emissive_texture=emissive_texture,
            emissive_intensity=emissive_intensity,
            emissive_color_constant=emissive_color_constant,
            sprite_sheet_row=sprite_sheet_row,
            sprite_sheet_col=sprite_sheet_col,
            sprite_sheet_fps=sprite_sheet_fps,
            filter_mode=filter_mode,
            wrap_mode_u=wrap_mode_u,
            wrap_mode_v=wrap_mode_v,
        )
        self.roughness_texture = roughness_texture
        self.metallic_texture = metallic_texture
        self.anisotropy = anisotropy
        self.albedo_constant = albedo_constant
        self.opacity_constant = opacity_constant
        self.roughness_constant = roughness_constant
        self.metallic_constant = metallic_constant
        self.thin_film_thickness_value = thin_film_thickness_value
        self.alpha_is_thin_film_thickness = alpha_is_thin_film_thickness
        self.height_texture = height_texture
        self.displace_in = displace_in
        self.use_draw_call_alpha_state = use_draw_call_alpha_state
        self.blend_type_value = blend_type_value
        self.inverted_blend = inverted_blend
        self.alpha_test_type = alpha_test_type
        self.alpha_reference_value = alpha_reference_value
        self.displace_out = displace_out
        self.subsurface_data = subsurface_data
        self.subsurface_data_struct: ctypes.Structure | None = None
        self.opaque_mat: _MaterialInfoOpaqueEXT | None = None

    def as_struct(self, _: None = None) -> _MaterialInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.opaque_mat = _MaterialInfoOpaqueEXT()
        self.opaque_mat.sType = _STypes.MATERIAL_INFO_OPAQUE_EXT
        self.opaque_mat.pNext = None
        if self.subsurface_data:
            self.subsurface_data_struct = self.subsurface_data.as_struct()
            self.opaque_mat.pNext = ctypes.cast(ctypes.byref(self.subsurface_data_struct), ctypes.c_void_p)
        self.opaque_mat.roughnessTexture = str(self.roughness_texture)
        self.opaque_mat.metallicTexture = str(self.metallic_texture)
        self.opaque_mat.anisotropy = self.anisotropy
        self.opaque_mat.albedoConstant = self.albedo_constant
        self.opaque_mat.opacityConstant = self.opacity_constant
        self.opaque_mat.roughnessConstant = self.roughness_constant
        self.opaque_mat.metallicConstant = self.metallic_constant
        self.opaque_mat.thinFilmThickness_hasvalue = 1 if self.thin_film_thickness_value is not None else 0
        self.opaque_mat.thinFilmThickness_value = self.thin_film_thickness_value or 0
        self.opaque_mat.alphaIsThinFilmThickness = self.alpha_is_thin_film_thickness
        self.opaque_mat.heightTexture = str(self.height_texture)
        self.opaque_mat.displaceIn = self.displace_in
        self.opaque_mat.useDrawCallAlphaState = self.use_draw_call_alpha_state
        self.opaque_mat.blendType_hasvalue = 1 if self.blend_type_value is not None else 0
        self.opaque_mat.blendType_value = self.blend_type_value or BlendTypes.ALPHA
        self.opaque_mat.invertedBlend = self.inverted_blend
        self.opaque_mat.alphaTestType = self.alpha_test_type
        self.opaque_mat.alphaReferenceValue = self.alpha_reference_value
        self.opaque_mat.displaceOut = self.displace_out
        self_pointer = ctypes.cast(ctypes.byref(self.opaque_mat), ctypes.c_void_p)
        return super().as_struct(self_pointer)


class TranslucentPBR(Material):
    def __init__(
        self,
        # Base Material Parameters:
        mat_hash: ctypes.c_uint64,
        albedo_texture: str | Path = "",
        normal_texture: str | Path = "",
        tangent_texture: str | Path = "",
        emissive_texture: str | Path = "",
        emissive_intensity: float = 0,
        emissive_color_constant: Float3D = Float3D(0, 0, 0),
        sprite_sheet_row: int = 0,
        sprite_sheet_col: int = 0,
        sprite_sheet_fps: int = 0,
        filter_mode: int = FilterModes.LINEAR,
        wrap_mode_u: int = WrapModes.REPEAT,
        wrap_mode_v: int = WrapModes.REPEAT,

        # TranslucentPBR Parameters:
        transmittance_texture: str | Path = "",
        refractive_index: float = 0,
        transmittance_color: Float3D = Float3D(0, 0, 0),
        transmittance_measurement_distance: float = 0.1,
        thin_wall_thickness: float | None = None,
        use_diffuse_layer: bool = False,
    ):
        # TODO: Add docstring.
        super().__init__(
            mat_hash=mat_hash,
            albedo_texture=albedo_texture,
            normal_texture=normal_texture,
            tangent_texture=tangent_texture,
            emissive_texture=emissive_texture,
            emissive_intensity=emissive_intensity,
            emissive_color_constant=emissive_color_constant,
            sprite_sheet_row=sprite_sheet_row,
            sprite_sheet_col=sprite_sheet_col,
            sprite_sheet_fps=sprite_sheet_fps,
            filter_mode=filter_mode,
            wrap_mode_u=wrap_mode_u,
            wrap_mode_v=wrap_mode_v,
        )
        self.transmittance_texture = transmittance_texture
        self.refractive_index = refractive_index
        self.transmittance_color = transmittance_color
        self.transmittance_measurement_distance = transmittance_measurement_distance
        self.thin_wall_thickness = thin_wall_thickness
        self.use_diffuse_layer = use_diffuse_layer
        self.tranlucent_mat: _MaterialInfoTranslucentEXT | None = None

    def as_struct(self, _: None = None) -> _MaterialInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.tranlucent_mat = _MaterialInfoTranslucentEXT()
        self.tranlucent_mat.sType = _STypes.MATERIAL_INFO_TRANSLUCENT_EXT
        self.tranlucent_mat.pNext = None
        self.tranlucent_mat.transmittanceTexture = str(self.transmittance_texture)
        self.tranlucent_mat.refractiveIndex = self.refractive_index
        self.tranlucent_mat.transmittanceColor = self.transmittance_color
        self.tranlucent_mat.transmittanceMeasurementDistance = self.transmittance_measurement_distance
        self.tranlucent_mat.thinWallThickness_hasvalue = 1 if self.thin_wall_thickness is not None else 0
        self.tranlucent_mat.thinWallThickness_value = self.thin_wall_thickness or 0
        self.tranlucent_mat.useDiffuseLayer = self.use_diffuse_layer
        self_pointer = ctypes.cast(ctypes.byref(self.tranlucent_mat), ctypes.c_void_p)
        return super().as_struct(self_pointer)


class Portal(Material):
    def __init__(
        self,
        # Base Material Parameters:
        mat_hash: ctypes.c_uint64,
        albedo_texture: str | Path = "",
        normal_texture: str | Path = "",
        tangent_texture: str | Path = "",
        emissive_texture: str | Path = "",
        emissive_intensity: float = 0,
        emissive_color_constant: Float3D = Float3D(0, 0, 0),
        sprite_sheet_row: int = 0,
        sprite_sheet_col: int = 0,
        sprite_sheet_fps: int = 0,
        filter_mode: int = FilterModes.LINEAR,
        wrap_mode_u: int = WrapModes.REPEAT,
        wrap_mode_v: int = WrapModes.REPEAT,
        # Portal Parameters:
        ray_portal_index: int = 0,
        rotation_speed: float = 0,
    ):
        # TODO: Add docstring.
        super().__init__(
            mat_hash=mat_hash,
            albedo_texture=albedo_texture,
            normal_texture=normal_texture,
            tangent_texture=tangent_texture,
            emissive_texture=emissive_texture,
            emissive_intensity=emissive_intensity,
            emissive_color_constant=emissive_color_constant,
            sprite_sheet_row=sprite_sheet_row,
            sprite_sheet_col=sprite_sheet_col,
            sprite_sheet_fps=sprite_sheet_fps,
            filter_mode=filter_mode,
            wrap_mode_u=wrap_mode_u,
            wrap_mode_v=wrap_mode_v,
        )
        self.ray_portal_index = ray_portal_index
        self.rotation_speed = rotation_speed
        self.portal_mat: _MaterialInfoPortalEXT | None = None

    def as_struct(self, _: None = None) -> _MaterialInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.portal_mat = _MaterialInfoPortalEXT()
        self.portal_mat.sType = _STypes.MATERIAL_INFO_PORTAL_EXT
        self.portal_mat.pNext = None
        self.portal_mat.rayPortalIndex = self.ray_portal_index
        self.portal_mat.rotationSpeed = self.rotation_speed
        self_pointer = ctypes.cast(ctypes.byref(self.portal_mat), ctypes.c_void_p)
        return super().as_struct(self_pointer)


class MeshSurface:
    def __init__(
        self,
        vertices: List[_HardcodedVertex],
        indices: List[int],
        skinning_data: SkinningData | None = None,
        material: Material | None = None,
    ):
        """
        Defines a mesh "surface".

        Meshes can have multiple surfaces, i.e. to assign different materials or skinning info in a single mesh.

        :param vertices: A list of ctypes-ready vertices struct.
        :param indices: A list of indices to define triangles out of the vertices.
        """
        self.vertices = vertices
        self.indices = indices
        self.vertex_array = None
        self.index_array = None
        self.skinning_data = skinning_data
        self.material = material
        self.check_for_errors()

    def check_for_errors(self):
        """Checks for potential errors in the MeshSurface."""
        if self.skinning_data:
            blend_vertices = len(self.skinning_data.blend_weights) / self.skinning_data.bones_per_vertex
            if blend_vertices != len(self.vertices):
                raise WrongSkinningDataCount("SkinningData.blend_weights don't match MeshSurface.vertices count.")

        if self.material and not self.material.handle:
            raise ResourceNotInitialized("MeshSurface.material is not initialized (handle is 0). Forgot to call create_material?")

    def as_struct(self) -> _MeshInfoSurfaceTriangles:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.check_for_errors()

        self.vertex_array = (_HardcodedVertex * len(self.vertices))()
        vertex_count = len(self.vertices)
        for i, vertex in enumerate(self.vertices):
            self.vertex_array[i] = vertex

        self.index_array = (ctypes.c_uint32 * len(self.indices))()
        index_count = len(self.indices)
        for i, idx in enumerate(self.indices):
            self.index_array[i] = idx

        mesh_surface_info = _MeshInfoSurfaceTriangles()
        mesh_surface_info.vertices_values = ctypes.cast(self.vertex_array, ctypes.POINTER(_HardcodedVertex))
        mesh_surface_info.vertices_count = vertex_count
        mesh_surface_info.indices_values = ctypes.cast(self.index_array, ctypes.POINTER(ctypes.c_uint32))
        mesh_surface_info.indices_count = index_count
        mesh_surface_info.skinning_hasvalue = 1 if self.skinning_data is not None else 0
        mesh_surface_info.skinning_value = self.skinning_data.as_struct() if self.skinning_data else _MeshInfoSkinning()
        mesh_surface_info.material = self.material.handle if self.material else None
        return mesh_surface_info


class Mesh:
    def __init__(self, surfaces: List[_MeshInfoSurfaceTriangles], mesh_hash: int = 0x1):
        """
        Defines and manages a Mesh Asset (not instance) within Remix engine.

        :param surfaces: A list of surfaces composing the mesh in ctypes-ready format.
        :param mesh_hash: A 64bit uint HASH to uniquely identify this mesh asset. You should manage your own hashes.
        """
        self.handle: ctypes.c_void_p = ctypes.c_void_p(0)
        self.mesh_hash = mesh_hash
        self.num_surfaces = len(surfaces)
        self.surfaces_array = (_MeshInfoSurfaceTriangles * self.num_surfaces)()
        for i, surface in enumerate(surfaces):
            self.surfaces_array[i] = surface

    def as_struct(self) -> _MeshInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        mesh_info = _MeshInfo()
        mesh_info.sType = _STypes.MESH_INFO
        mesh_info.pNext = None
        mesh_info.hash = self.mesh_hash
        mesh_info.surfaces_values = ctypes.cast(self.surfaces_array, ctypes.POINTER(_MeshInfoSurfaceTriangles))
        mesh_info.surfaces_count = self.num_surfaces
        return mesh_info


class Transform:
    def __init__(self, matrix: List[List[float]] | None = None):
        """
        Transform class that holds a 3x4 matrix allowing for position, rotation, scaling and shear transformations.

        :param matrix: The 3x4 matrix values in Row-Major format per DirectX convention. i.e: Move 3 units to the right:
            [
                [1, 0, 0, 3],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
            ]
        """
        self.matrix = matrix
        if not self.matrix:
            self.reset()

    def as_struct(self):
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        transform = _Transform()

        for n, row in enumerate(self.matrix):
            for m, column in enumerate(row):
                transform.matrix[n][m] = column

        return transform

    def reset(self):
        self.matrix = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0]
        ]


class Skeleton:
    def __init__(self, bone_count: int):
        """
        Defines a flat array of Transforms representing each bone deformation in a Skeleton.

        :param bone_count: Length of the Transform array.
        """
        self.bone_count = bone_count
        self.bone_transforms = (_Transform * bone_count)()
        self.bones_struct: _InstanceInfoBoneTransformsEXT | None = None

    def set_bone_transforms(self, transform_data: ctypes.POINTER(_Transform)):
        """
        Copies data from transform_data to an internal _Transform array.

        :param transform_data: ctypes Pointer to an array of _Transform structs to copy from.
        """
        ctypes.memmove(
            ctypes.byref(self.bone_transforms),
            transform_data,
            ctypes.sizeof(_Transform) * self.bone_count
        )

    def as_struct(self) -> _InstanceInfoBoneTransformsEXT:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.bones_struct = _InstanceInfoBoneTransformsEXT()
        self.bones_struct.sType = _STypes.INSTANCE_INFO_BONE_TRANSFORMS_EXT
        self.bones_struct.pNext = None
        self.bones_struct.boneTransforms_values = self.bone_transforms
        self.bones_struct.boneTransforms_count = self.bone_count
        return self.bones_struct


class MeshInstance:
    def __init__(
        self,
        mesh: Mesh,
        category_flags: ctypes.c_uint32 = CategoryFlags.NONE,
        transform: Transform = Transform(),
        double_sided: int = 1,
        skeleton: Skeleton | None = None,
    ):
        """
        Defines and manages a Mesh Instance out of a Mesh Asset.
        One mesh can appear in multiple times (instances) with different properties in a scene.

        :param mesh: The mesh asset this instance refers to.
        :param category_flags: Bitwise OR'd Remix category flags like Sky, Ignore, Decal or Terrain.
        :param transform: The transform for positioning this mesh instance in the scene.
        :param double_sided: If the backface of the surfaces/polygons are visible.
        :param skeleton: Instance of a Skeleton if it is a skinned mesh.
        """
        self.mesh = mesh
        self.category_flags = category_flags
        self.transform = transform
        self.transform_struct = transform.as_struct()
        self.double_sided = double_sided
        self.skeleton = skeleton

        if not self.mesh.handle:
            msg = "MeshInstance.mesh is not initialized (handle is 0). Forgot to call create_mesh?"
            raise ResourceNotInitialized(msg)

    def check_for_errors(self):
        """Checks for potential errors in the MeshInstance. This method is expensive so use only when necessary."""
        if self.skeleton:
            for i in range(self.mesh.num_surfaces):
                surface = self.mesh.surfaces_array[i]
                if not surface.skinning_hasvalue:
                    continue

                for j in range(surface.skinning_value.blendIndices_count):
                    if surface.skinning_value.blendIndices_values[j] >= self.skeleton.bone_count:
                        msg = f"MeshSurface {i} has SkinningData out of the assigned Skeleton bone range."
                        raise SkinningDataOutOfSkeletonRange(msg)

    def as_struct(self):
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        if not self.mesh.handle:
            msg = "MeshInstance.mesh is not initialized (handle is 0). Forgot to call create_mesh?"
            raise ResourceNotInitialized(msg)

        instance_info = _InstanceInfo()
        instance_info.sType = _STypes.INSTANCE_INFO
        instance_info.pNext = None
        if self.skeleton:
            self.skeleton.as_struct()
            instance_info.pNext = ctypes.cast(ctypes.byref(self.skeleton.bones_struct), ctypes.c_void_p)
        instance_info.mesh = ctypes.cast(self.mesh.handle, ctypes.c_void_p)
        instance_info.transform = self.transform_struct
        instance_info.doubleSided = self.double_sided
        return instance_info


class Light(ABC):
    @abstractmethod
    def __init__(
        self,
        light_hash: ctypes.c_uint64,
        radiance: Float3D = Float3D(1, 1, 1),
    ):
        """
        Abstract class for all light types common logic.

        :param light_hash: 64bit hash for uniquely representing the light within Remix engine.
        :param radiance: Intensity and color of the light.
        """
        self.handle: ctypes.c_void_p = ctypes.c_void_p(0)
        if not light_hash:
            raise ValueError(f"Light hash must be a value bigger than 0. Got {light_hash} instead.")
        self.light_hash = light_hash
        self.radiance = radiance
        self.light_info: _LightInfo | None = None

    @abstractmethod
    def as_struct(self, _child_struct_pointer: ctypes.c_void_p | None = None) -> _LightInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.light_info = _LightInfo()
        self.light_info.sType = _STypes.LIGHT_INFO
        self.light_info.pNext = _child_struct_pointer
        self.light_info.hash = self.light_hash
        self.light_info.radiance = self.radiance
        return self.light_info


class LightShapingInfo:
    def __init__(
        self,
        direction: Float3D = Float3D(0, -1, 0),
        cone_angle: float = 0,
        cone_softness: float = 0,
        focus_exponent: float = 0,
    ):
        # TODO: Add docstring.
        self.direction = direction
        self.cone_angle = cone_angle
        self.cone_softness = cone_softness
        self.focus_exponent = focus_exponent

    def as_struct(self) -> _LightInfoLightShaping:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        light_shaping_struct = _LightInfoLightShaping()
        light_shaping_struct.direction = self.direction
        light_shaping_struct.coneAngleDegrees = self.cone_angle
        light_shaping_struct.coneSoftness = self.cone_softness
        light_shaping_struct.focusExponent = self.focus_exponent
        return light_shaping_struct


class SphereLight(Light):
    def __init__(
        self,
        light_hash: ctypes.c_uint64,
        radiance: Float3D = Float3D(1, 1, 1),
        position: Float3D = Float3D(0, 0, 0),
        radius: float = 0.1,
        shaping_value: LightShapingInfo = None,
    ):
        """
        Defines a Sphere light type.

        :param light_hash: A 64bit uint HASH to uniquely identify this light. You should manage your own hashes.
        :param radiance: RGB Color+Intensity of the light encoded in Float3D format.
        :param position: The light position.
        :param radius: The radius of the sphere light. Anything inside it won't be lit by it.
        :param shaping_value: The focal cone shaping for the Light.
        """
        self.position = position
        self.radius = radius
        self.shaping_value = shaping_value
        self.sphere_light_info: _LightInfoSphereEXT | None = None
        super().__init__(light_hash, radiance)

    def as_struct(self, _: None = None) -> _LightInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.sphere_light_info = _LightInfoSphereEXT()
        self.sphere_light_info.sType = _STypes.LIGHT_INFO_SPHERE_EXT
        self.sphere_light_info.pNext = None
        self.sphere_light_info.position = self.position
        self.sphere_light_info.radius = self.radius
        self.sphere_light_info.shaping_hasvalue = 1 if self.shaping_value else 0
        if self.shaping_value:
            self.sphere_light_info.shaping_value = self.shaping_value.as_struct()

        self_pointer = ctypes.cast(ctypes.byref(self.sphere_light_info), ctypes.c_void_p)
        return super().as_struct(self_pointer)


class RectLight(Light):
    def __init__(
        self,
        light_hash: ctypes.c_uint64,
        radiance: Float3D = Float3D(1, 1, 1),
        position: Float3D = Float3D(0, 0, 0),
        x_axis: Float3D = Float3D(1, 0, 0),
        x_size: float = 1.0,
        y_axis: Float3D = Float3D(0, 1, 0),
        y_size: float = 1.0,
        direction: Float3D = Float3D(0, 0, 1),
        shaping_value: LightShapingInfo = None,
    ):
        """
        Defines a Rect light type.

        :param light_hash: A 64bit uint HASH to uniquely identify this light. You should manage your own hashes.
        :param radiance: RGB Color+Intensity of the light encoded in Float3D format.
        :param position: The light position.
        :param x_axis: A unit Vector pointing to the horizontal direction of the rect shape.
        :param x_size: Rect's horizontal length.
        :param y_axis: A unit Vector pointing to the vertical direction of the rect shape.
        :param y_size: Rect's Vertical length.
        :param direction: Where the rect shape is facing at.
        :param shaping_value: The focal cone shaping for the Light.
        """
        self.position = position
        self.x_axis = x_axis
        self.x_size = x_size
        self.y_axis = y_axis
        self.y_size = y_size
        self.direction = direction
        self.shaping_value = shaping_value
        self.rect_light_info: _LightInfoRectEXT | None = None
        super().__init__(light_hash, radiance)

    def as_struct(self, _: None = None) -> _LightInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.rect_light_info = _LightInfoRectEXT()
        self.rect_light_info.sType = _STypes.LIGHT_INFO_RECT_EXT
        self.rect_light_info.pNext = None
        self.rect_light_info.position = self.position
        self.rect_light_info.xAxis = self.x_axis
        self.rect_light_info.xSize = self.x_size
        self.rect_light_info.yAxis = self.y_axis
        self.rect_light_info.ySize = self.y_size
        self.rect_light_info.direction = self.direction
        self.rect_light_info.shaping_hasvalue = 1 if self.shaping_value else 0
        if self.shaping_value:
            self.rect_light_info.shaping_value = self.shaping_value.as_struct()

        self_pointer = ctypes.cast(ctypes.byref(self.rect_light_info), ctypes.c_void_p)
        return super().as_struct(self_pointer)


class DiskLight(Light):
    def __init__(
        self,
        light_hash: ctypes.c_uint64,
        radiance: Float3D = Float3D(1, 1, 1),
        position: Float3D = Float3D(0, 0, 0),
        x_axis: Float3D = Float3D(1, 0, 0),
        x_size: float = 1.0,
        y_axis: Float3D = Float3D(0, 1, 0),
        y_size: float = 1.0,
        direction: Float3D = Float3D(0, 0, 1),
        shaping_value: LightShapingInfo = None,
    ):
        """
        Defines a Disk light type. Similar to Rect lights with separate X and Y axis, they're Ellipse-shaped.

        :param light_hash: A 64bit uint HASH to uniquely identify this light. You should manage your own hashes.
        :param radiance: RGB Color+Intensity of the light encoded in Float3D format.
        :param position: The light position.
        :param x_axis: A unit Vector pointing to the horizontal direction of the disk shape.
        :param x_size: Disk's horizontal length.
        :param y_axis: A unit Vector pointing to the vertical direction of the disk shape.
        :param y_size: Disk's Vertical length.
        :param direction: Where the rect shape is facing at.
        :param shaping_value: The focal cone shaping for the Light.
        """
        self.position = position
        self.x_axis = x_axis
        self.x_size = x_size
        self.y_axis = y_axis
        self.y_size = y_size
        self.direction = direction
        self.shaping_value = shaping_value
        self.disk_light_info: _LightInfoDiskEXT | None = None
        super().__init__(light_hash, radiance)

    def as_struct(self, _: None = None) -> _LightInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.disk_light_info = _LightInfoDiskEXT()
        self.disk_light_info.sType = _STypes.LIGHT_INFO_DISK_EXT
        self.disk_light_info.pNext = None
        self.disk_light_info.position = self.position
        self.disk_light_info.xAxis = self.x_axis
        self.disk_light_info.xRadius = self.x_size
        self.disk_light_info.yAxis = self.y_axis
        self.disk_light_info.yRadius = self.y_size
        self.disk_light_info.direction = self.direction
        self.disk_light_info.shaping_hasvalue = 1 if self.shaping_value else 0
        if self.shaping_value:
            self.disk_light_info.shaping_value = self.shaping_value.as_struct()

        self_pointer = ctypes.cast(ctypes.byref(self.disk_light_info), ctypes.c_void_p)
        return super().as_struct(self_pointer)


class CylinderLight(Light):
    def __init__(
        self,
        light_hash: ctypes.c_uint64,
        radiance: Float3D = Float3D(1, 1, 1),
        position: Float3D = Float3D(0, 0, 0),
        radius: float = 0.1,
        axis: Float3D = Float3D(0, 1, 0),
        axis_length: float = 1.0,
    ):
        """
        Defines a Cylinder light type. Good for Tube-shaped, neon or fluorescent lamps.

        :param light_hash: A 64bit uint HASH to uniquely identify this light. You should manage your own hashes.
        :param radiance: RGB Color+Intensity of the light encoded in Float3D format.
        :param position: The light position.
        :param radius: The tube radius or Thickness.
        :param axis: Direction vector for the tube.
        :param axis_length: Half-length of the tube.
        """
        self.position = position
        self.radius = radius
        self.axis = axis
        self.axis_length = axis_length
        self.cylinder_light_info: _LightInfoCylinderEXT | None = None
        super().__init__(light_hash, radiance)

    def as_struct(self, _: None = None) -> _LightInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.cylinder_light_info = _LightInfoCylinderEXT()
        self.cylinder_light_info.sType = _STypes.LIGHT_INFO_CYLINDER_EXT
        self.cylinder_light_info.pNext = None
        self.cylinder_light_info.position = self.position
        self.cylinder_light_info.radius = self.radius
        self.cylinder_light_info.axis = self.axis
        self.cylinder_light_info.axisLength = self.axis_length
        self_pointer = ctypes.cast(ctypes.byref(self.cylinder_light_info), ctypes.c_void_p)
        return super().as_struct(self_pointer)


class DistantLight(Light):
    def __init__(
        self,
        light_hash: ctypes.c_uint64,
        radiance: Float3D = Float3D(1, 1, 1),
        direction: Float3D = Float3D(0, -1, 0),
        angular_diameter: float = 0.1,
    ):
        """
        Defines a Distant/Directional light type. Like Sun, or Moon. Lights so far away that position doesn't matter.

        angular_diameter maps to the light source's size, producing soft shadows.

        I.e: sin(angular_diameter) == sun's radius in view space (BRDF ray sampling angle).

        :param light_hash: A 64bit uint HASH to uniquely identify this light. You should manage your own hashes.
        :param radiance: RGB Color+Intensity of the light encoded in Float3D format.
        :param direction: Direction the light source is point to.
        :param angular_diameter: In degrees, maps to the light source's diameter to produce soft shadows.
        """
        self.light_hash = light_hash
        self.radiance = radiance
        self.direction = direction
        self.angular_diameter = angular_diameter
        self.distant_light_info: _LightInfoDistantEXT | None = None
        super().__init__(light_hash, radiance)

    def as_struct(self, _: None = None) -> _LightInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.distant_light_info = _LightInfoDistantEXT()
        self.distant_light_info.sType = _STypes.LIGHT_INFO_DISTANT_EXT
        self.distant_light_info.pNext = None
        self.distant_light_info.direction = self.direction
        self.distant_light_info.angularDiameterDegrees = self.angular_diameter
        self_pointer = ctypes.cast(ctypes.byref(self.distant_light_info), ctypes.c_void_p)
        return super().as_struct(self_pointer)


class DomeLight(Light):
    def __init__(
        self,
        light_hash: ctypes.c_uint64,
        radiance: Float3D = Float3D(1, 1, 1),
        transform: Transform = Transform(),
        color_texture: str | Path = "",
    ):
        """
        Defines a Dome/Skybox/HDRI light type. You can assign DDS BC6U HDR Textures for colorTexture.

        :param light_hash: A 64bit uint HASH to uniquely identify this light. You should manage your own hashes.
        :param radiance: RGB Color+Intensity of the light encoded in Float3D format.
        :param transform: Transform for orienting the sky dome texture.
        :param color_texture: Path to the .dds texture.
        """
        self.light_hash = light_hash
        self.radiance = radiance
        self.transform = transform
        self.color_texture = color_texture
        self.dome_light_info: _LightInfoDomeEXT | None = None
        super().__init__(light_hash, radiance)

    def as_struct(self, _: None = None) -> _LightInfo:
        """Returns the internal structure form suitable for DLL interop via ctypes."""
        self.dome_light_info = _LightInfoDomeEXT()
        self.dome_light_info.sType = _STypes.LIGHT_INFO_DOME_EXT
        self.dome_light_info.pNext = None
        self.dome_light_info.transform = self.transform.as_struct()
        self.dome_light_info.colorTexture = str(self.color_texture)
        self_pointer = ctypes.cast(ctypes.byref(self.dome_light_info), ctypes.c_void_p)
        return super().as_struct(self_pointer)
