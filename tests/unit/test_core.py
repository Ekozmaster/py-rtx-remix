from unittest import TestCase

from core import StartupInfo
from api_data_types import _STypes


class TestStartupInfo(TestCase):
    def test_default_initialization(self):
        startup_info = StartupInfo()
        struct = startup_info.as_struct()

        self.assertEqual(struct.hwnd, None)
        self.assertEqual(struct.disableSrgbConversionForOutput, 0)
        self.assertEqual(struct.forceNoVkSwapchain, 0)
        self.assertEqual(struct.editorModeEnabled, 0)
        self.assertEqual(struct.sType, _STypes.STARTUP_INFO)

    def test_custom_initialization(self):
        hwnd = 100
        disable_srgb = True
        force_no_vk_swapchain = True
        editor_mode_enabled = True

        startup_info = StartupInfo(
            hwnd=hwnd,
            disable_srgb_conversion_for_output=disable_srgb,
            force_no_vk_swapchain=force_no_vk_swapchain,
            editor_mode_enabled=editor_mode_enabled
        )
        struct = startup_info.as_struct()

        self.assertEqual(struct.hwnd, hwnd)
        self.assertEqual(struct.disableSrgbConversionForOutput, int(disable_srgb))
        self.assertEqual(struct.forceNoVkSwapchain, int(force_no_vk_swapchain))
        self.assertEqual(struct.editorModeEnabled, int(editor_mode_enabled))

    def test_boolean_to_integer_conversion(self):
        startup_info = StartupInfo(
            disable_srgb_conversion_for_output=True,
            force_no_vk_swapchain=False,
            editor_mode_enabled=True
        )
        struct = startup_info.as_struct()

        self.assertEqual(struct.disableSrgbConversionForOutput, 1)
        self.assertEqual(struct.forceNoVkSwapchain, 0)
        self.assertEqual(struct.editorModeEnabled, 1)
