class InvalidSkinningData(ValueError):
    """For general skinning data errors like None checks of empty lists."""
    ...


class WrongSkinningDataCount(ValueError):
    """For when SkinningData and MeshSurface arrays don't match."""
    ...


class SkinningDataOutOfSkeletonRange(ValueError):
    """For when SkinningData and MeshInstance Skeleton arrays don't match."""
    ...


class ResourceNotInitialized(ValueError):
    """For any resource (Mesh, Material, Light...) being used before initialization within Remix API."""
    ...


class APINotInitialized(ValueError):
    """Using the Remix API without initializing it?"""
    ...


class FailedToInitializeAPI(ValueError):
    """For when the Remix API failed to initialize. Usually due to wrong paths."""
    ...


class FailedToSetupCamera(ValueError):
    """For when the Remix API failed to setup a camera for any reason."""
    ...


class FailedToCreateMesh(ValueError):
    """For when the Remix API failed to create a mesh."""
    ...


class FailedToCreateLight(ValueError):
    """For when the Remix API failed to create a light."""
    ...
