#
# Copyright (C) 2019 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

DEVICE_PATH := device/blackberry/athena

# Inherit from BlackBerry sdm660-common
-include device/blackberry/sdm660-common/BoardConfigCommon.mk

# Architecture
TARGET_CPU_VARIANT_RUNTIME := cortex-a73
TARGET_2ND_CPU_VARIANT_RUNTIME := cortex-a73

# Audio
AUDIO_FEATURE_ENABLED_FM_POWER_OPT := true
AUDIO_FEATURE_ENABLED_GEF_SUPPORT := true
AUDIO_FEATURE_ENABLED_SSR := true
BOARD_SUPPORTS_SOUND_TRIGGER := true
BOARD_USES_ALSA_AUDIO := true

# Bootloader
TARGET_BOOTLOADER_BOARD_NAME := sdm660

# Display
TARGET_SCREEN_DENSITY := 420

# Kernel
TARGET_KERNEL_CONFIG := athena-perf_defconfig

# Properties
TARGET_VENDOR_PROP += $(DEVICE_PATH)/vendor.prop

