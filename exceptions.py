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
