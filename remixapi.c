#include <remix/remix_c.h>

#include <assert.h>
#include <stdio.h>

#define DllExport   __declspec( dllexport )

remixapi_Interface g_remix = { 0 };
HMODULE g_remix_dll = NULL;


DllExport remixapi_ErrorCode init(remixapi_StartupInfo* startupInfo) {
    const wchar_t* path = L"d3d9.dll";
    if (GetFileAttributesW(path) == INVALID_FILE_ATTRIBUTES) {
        path = L"bin\\d3d9.dll";
        if (GetFileAttributesW(path) == INVALID_FILE_ATTRIBUTES) {
          printf("Counldn't find d3d9.dll.\nIs the SDK installed properly?");
        }
    }

    {
        remixapi_ErrorCode status = remixapi_lib_loadRemixDllAndInitialize(path, &g_remix, &g_remix_dll);
        if (status != REMIXAPI_ERROR_CODE_SUCCESS) {
            printf("remixapi_lib_loadRemixDllAndInitialize failed: %d", status);
            return status;
        }
    }

    {
        remixapi_ErrorCode r = g_remix.Startup(startupInfo);
        if (r != REMIXAPI_ERROR_CODE_SUCCESS) {
          printf("remix::Startup() failed: %d", r);
          return r;
        }
    }
    return REMIXAPI_ERROR_CODE_SUCCESS;
}

DllExport void setup_camera(remixapi_CameraInfo* cam_info) {
    g_remix.SetupCamera(cam_info);
}

DllExport void present(remixapi_PresentInfo* info) {
    g_remix.Present(info);
}

DllExport remixapi_ErrorCode create_mesh(remixapi_MeshInfo* info, remixapi_MeshHandle* handle) {
    remixapi_ErrorCode r = g_remix.CreateMesh(info, handle);
    if (r != REMIXAPI_ERROR_CODE_SUCCESS) {
        printf("remix::CreateMesh() failed: %d", r);
        return r;
    }
    return REMIXAPI_ERROR_CODE_SUCCESS;
}

DllExport remixapi_ErrorCode create_light(remixapi_LightInfo* info, remixapi_LightHandle* handle) {
    remixapi_ErrorCode r = g_remix.CreateLight(info, handle);
    if (r != REMIXAPI_ERROR_CODE_SUCCESS) {
        printf("remix::CreateLight() failed: %d", r);
        return r;
    }
    return REMIXAPI_ERROR_CODE_SUCCESS;
}

DllExport void draw_instance(remixapi_InstanceInfo* info) {
    g_remix.DrawInstance(info);
}

DllExport void draw_light_instance(remixapi_LightHandle handle) {
    g_remix.DrawLightInstance(handle);
}

DllExport void destroy(void) {
  if (g_remix.Shutdown) {
    remixapi_lib_shutdownAndUnloadRemixDll(&g_remix, g_remix_dll);
  }
}
