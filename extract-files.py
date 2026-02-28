#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import re

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

import extract_utils.tools
extract_utils.tools.DEFAULT_PATCHELF_VERSION = '0_9'

namespace_imports = [
    'hardware/qcom-caf/sdm660',
    'vendor/qcom/opensource/display',
    'hardware/qcom-caf/wlan',
    'vendor/blackberry/sdm660-common',
]

blob_fixups: blob_fixups_user_type =        {
    # Protobuf for audio and goodix
    ('vendor/lib/libwebrtc_audio_preprocessing.so',
     'vendor/lib64/libwebrtc_audio_preprocessing.so'
     ): blob_fixup()
        .replace_needed('libprotobuf-cpp-lite.so', 'libprotobuf-cpp-lite-v29.so'),

    'vendor/bin/gx_fpd': blob_fixup()
        .replace_needed('libprotobuf-cpp-lite.so', 'libprotobuf-cpp-lite-v29.so')
        .remove_needed('libandroid_runtime.so')
        .remove_needed('libkeystore_binder.so')
        .remove_needed('libbacktrace.so')
        .remove_needed('libunwind.so')
        .remove_needed('libkeystore_binder.so')
        .remove_needed('libsoftkeymasterdevice.so')
        .remove_needed('libsoftkeymaster.so')
        .remove_needed('libkeymaster_messages.so')
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so')
        .add_needed('libbinder_shim.so')
        .add_needed('libfakelogprint.so'),

    'vendor/lib64/hw/gxfingerprint.default.so': blob_fixup()
        .replace_needed('libprotobuf-cpp-lite.so', 'libprotobuf-cpp-lite-v29.so')
        .remove_needed('libandroid_runtime.so')
        .remove_needed('libkeystore_binder.so')
        .remove_needed('libbacktrace.so')
        .remove_needed('libunwind.so')
        .remove_needed('libkeystore_binder.so')
        .remove_needed('libsoftkeymasterdevice.so')
        .remove_needed('libsoftkeymaster.so')
        .remove_needed('libkeymaster_messages.so')
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so')
        .add_needed('libbinder_shim.so')
        .binary_regex_replace(b'/system/etc/firmware', b'/vendor/firmware\x00\x00\x00\x00'),

    # Fingerprint
    ('vendor/lib64/hw/fingerprint.goodix.so',
     'vendor/lib64/libfp_client.so',
     'vendor/lib64/libfpservice.so',
     'vendor/lib64/libvendor.goodix.hardware.fingerprint.hwbinder@2.1.so'): blob_fixup()
        .remove_needed('libandroid_runtime.so')
        .remove_needed('libkeystore_binder.so')
        .remove_needed('libbacktrace.so')
        .remove_needed('libunwind.so')
        .remove_needed('libkeystore_binder.so')
        .remove_needed('libsoftkeymasterdevice.so')
        .remove_needed('libsoftkeymaster.so')
        .remove_needed('libkeymaster_messages.so')
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so')
        .add_needed('libbinder_shim.so')
        .add_needed('libfakelogprint.so'),

    # Cams - OREO HAL needs libskia shim
    'vendor/lib/hw/camera.sdm660.so': blob_fixup()
        .replace_needed('libskia.so', 'libskia_shim.so'),

    # Cams - OREO iface_modules 0x400 frame drop bug (uses i=0 instead of bufq_idx)
    'vendor/lib/libmmcamera2_iface_modules.so': blob_fixup()
        .binary_regex_replace(b'\xed\xf7\xb2\xeb\x4f\xf0\xff\x30\x05\xb0\xbd\xe8',
                              b'\xed\xf7\xb2\xeb\x00\x20\x00\xbf\x05\xb0\xbd\xe8'),

    # Cams - OREO stats_modules PDAF depth: inject default actuator_sensitivity=1.0
    # When EEPROM driver doesn't provide sensitivity, the zero value disables PDAF depth
    # processing entirely (skips to alt path). This injects 1.0 as fallback.
    'vendor/lib/libmmcamera2_stats_modules.so': blob_fixup()
        .binary_regex_replace(
            b'\x14\xd1\x0d\xf5\x40\x5e\xbe\xf8\x2c\x40\x05\xe1',
            b'\x14\xd1\xb7\xee\x00\x8a\x00\xbf\x00\xbf\x14\xe0'),

    # Cams - OREO q3a_core AF AUTO mode fix
    # NOP range-check branches that skip AF_INIT for non-CAF modes (AUTO=1, MACRO=2)
    # Patch 1: af_core_set_param case 5 — bhi.w at 0x8321e
    # Patch 2: af_state=1 safety net at 0x83b3c (reproducibility of manual patch)
    # Patch 3: af_util_focus_mode_change — bhi at 0x958da
    # Patch 4: Force fullsweep AF for telephoto — NOP cbz+blt at 0x89648/0x89658
    # HJ hill-climbing gets trapped in local FV minimum on telephoto (only scans half range).
    # This forces the secondary (fullsweep) search handler to always trigger, enabling
    # full 0-240 step scan so near objects are reliably found on first tap.
    # Patch 5: PDAF direction passthrough to HJ prescan — trampoline at 0x8c116 + code cave
    # Qualcomm bug: af_single_set_start_pos loads PDAF direction from depth_info but only
    # uses it for debug log string selection. The actual prescan direction (r7[0x10]) is set
    # by position-based heuristic, ignoring PDAF. This trampoline to code cave at 0xb69ba
    # checks depth_status != 0 (PDAF data available), and if so, uses the PDAF direction
    # value directly for r7[0x10], giving HJ the correct initial scan direction.
    'vendor/lib/libmmcamera2_q3a_core.so': blob_fixup()
        .binary_regex_replace(
            re.escape(b'\x03\x38\x02\x28\x00\xf2\x17\x82\x28\x46\x84\xf7'),
            b'\x03\x38\x02\x28\x00\xbf\x00\xbf\x28\x46\x84\xf7')
        .binary_regex_replace(
            re.escape(b'\x30\x68\x61\x68\xd0\xf8\x64\x01\x00\x29\x75\xd0\x60\xb1'),
            b'\x30\x68\x61\x68\xd0\xf8\x64\x01\x01\x21\x61\x60\x60\xb1')
        .binary_regex_replace(
            re.escape(b'\x41\x58\x03\x39\x02\x29\x0e\xd8\x72\xf7\x4a\xe8'),
            b'\x41\x58\x03\x39\x02\x29\x00\xbf\x72\xf7\x4a\xe8')
        .binary_regex_replace(
            re.escape(b'\x20\x58\x41\x58\x99\xb1\x41\xf2\xd0\x31\x40\x58\x44\xf2\x40\x21\x61\x58\x81\x42\x0b\xdb'),
            b'\x20\x58\x41\x58\x00\xbf\x41\xf2\xd0\x31\x40\x58\x44\xf2\x40\x21\x61\x58\x81\x42\x00\xbf')
        .binary_regex_replace(
            re.escape(b'\x38\x74\xc8\xbf\x01\x23'),
            b'\x2a\xf0\x50\xbc\x00\xbf')
        .binary_regex_replace(
            re.escape(b'\x4c\x3e\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),
            b'\x4c\x3e\x00\x00\x00\x00\x00\x01\x06\xb4\x41\xf2\xb0\x51\x79\x58\x0a\x69\x12\x68\x02\x2a\x02\xd1\x89\x68\x08\x68\x38\x74\x06\xbc\xca\x45\xc8\xbf\x01\x23\xd5\xf7\xa0\xbb'),

    ('vendor/lib/libdualcameraddm.so',
     'vendor/lib/libarcsoft_dualcam_refocus.so',
     'vendor/lib/libarcsoft_low_light_shot.so',
     'vendor/lib/libarcsoft_nighthawk.so',
     'vendor/lib/liboptizoom.so',
     'vendor/lib/libchromaflash.so',
     'vendor/lib/libseemore.so',
     'vendor/lib/libubifocus.so'): blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),

    'vendor/lib/libcamera_imgproc.so': blob_fixup()
        .remove_needed('libjnigraphics.so')
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),

    'vendor/lib/libopencv_java3.so': blob_fixup()
        .replace_needed('libjnigraphics.so', 'libjnigraphics_shim.so')
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),

    'vendor/lib/libVDSuperPhotoAPI.so': blob_fixup()
        .replace_needed('libjnigraphics.so', 'libjnigraphics_shim.so')
        .remove_needed('libandroid.so')
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
}  # fmt: skip

module = ExtractUtilsModule(
    'athena',
    'blackberry',
    namespace_imports=namespace_imports,
    blob_fixups=blob_fixups,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sdm660-common', module.vendor
    )
    utils.run()
