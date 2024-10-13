## Features
- [ ] Faster input data structures to MeshSurface and SkinningData.
  - [ ] VERTEX_ARRAY & INDEX_ARRAY storing raw _HardcodedVertex & int array pointer + size as optional arguments to MeshSurface.
  - [ ] BLEND_WEIGHT_ARRAY & BLEND_INDEX_ARRAY storing raw data array pointers + size as optional argument types.
- [ ] Break resource types in separate modules (meshes, materials, lighting...).
- [ ] Protect the API for thread safety.

## ctypes mappings
- [ ] remixapi_LightInfoUSDEXT
- [ ] remixapi_InstanceInfoObjectPickingEXT
- [ ] remixapi_InstanceInfoBlendEXT
- [ ] remixapi_InstanceInfoBoneTransformsEXT

## API Interface
- [ ] Shutdown
- [ ] CreateMaterial
- [ ] DestroyMaterial
- [ ] CreateMesh
- [ ] DestroyMesh
- [ ] SetupCamera
- [ ] DrawInstance
- [ ] CreateLight
- [ ] DestroyLight
- [ ] DrawLightInstance
- [ ] SetConfigVariable
- [ ] Present
- [ ] Startup

DXVK interoperability
- [ ] dxvk_CreateD3D9
- [ ] dxvk_RegisterD3D9Device
- [ ] dxvk_GetExternalSwapchain
- [ ] dxvk_GetVkImage
- [ ] dxvk_CopyRenderingOutput
- [ ] dxvk_SetDefaultOutput

Object picking utils
- [ ] pick_RequestObjectPicking
- [ ] pick_HighlightObjects

## Tests
### Unit Tests:
-[ ] Lights
- [ ] Test MeshInstance with uninitialized material

### Integration Tests
- [ ] Creation and deletion of materials.
- [ ] Updating and Recreating materials.
- [x] Creation and deletion of meshes.
- [ ] Updating and Recreating meshes.
- [x] Creation and deletion of lights.
- [ ] Updating and Recreating lights.
- [ ] Creation and deletion of cameras.
- [ ] Updating and Recreating cameras.

### E2E Tests:
- [ ] Capture screenshots of the Remix window.
- [ ] Render Result of test scene with all light types.
- [ ] Render Result of lights with different settings.
