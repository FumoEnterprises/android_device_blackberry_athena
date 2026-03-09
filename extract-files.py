#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

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
    # Audio
    ('vendor/lib/libwebrtc_audio_preprocessing.so',
     'vendor/lib64/libwebrtc_audio_preprocessing.so'
     ): blob_fixup()
        .replace_needed('libprotobuf-cpp-lite.so', 'libprotobuf-cpp-lite-v29.so'),

    # Fingerprint
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
        .add_needed('libhidl_shim_full.so')
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
        .add_needed('libfakelogprint.so')
        .binary_regex_replace(b'/system/etc/firmware', b'/vendor/firmware\x00\x00\x00\x00'),

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
        .replace_needed('libhidlbase.so', 'libhidl_shim_full.so')
        .add_needed('libbinder_shim.so')
        .add_needed('libfakelogprint.so'),

    'vendor/lib/hw/camera.sdm660.so': blob_fixup()
        .replace_needed('libskia.so', 'libskia_shim.so'),

    # Cams - libmmcamera_interface: skip Main+AUX virtual camera (ID 3) creation
    # sort_camera_info() BEQ.W → B.W at 0x678e: unconditionally skip dual-camera muxer loops
    # This seems to be related to portrait-mode stuff as the aux camera works okay without it.
    'vendor/lib/libmmcamera_interface.so': blob_fixup()
        .binary_regex_replace(
            b'\x00\xf0\x58\x82',
            b'\x00\xf0\x58\xba'),

    # Cams - iface_modules 0x400 frame drop bug (uses i=0 instead of bufq_idx)
    'vendor/lib/libmmcamera2_iface_modules.so': blob_fixup()
        .binary_regex_replace(b'\xed\xf7\xb2\xeb\x4f\xf0\xff\x30\x05\xb0\xbd\xe8',
                              b'\xed\xf7\xb2\xeb\x00\x20\x00\xbf\x05\xb0\xbd\xe8'),

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
