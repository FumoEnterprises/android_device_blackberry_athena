#
# Copyright (C) 2020 The LineageOS Project
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

DEVICE_PATH := device/blackberry/athena

# Set Shipping API level
PRODUCT_SHIPPING_API_LEVEL := 27

# Overlays
DEVICE_PACKAGE_OVERLAYS += \
    $(LOCAL_PATH)/overlay

# Setup dalvik vm configs
$(call inherit-product, frameworks/native/build/phone-xhdpi-4096-dalvik-heap.mk)

# Get non-open-source specific aspects
$(call inherit-product, vendor/blackberry/athena/athena-vendor.mk)

# AAPT
PRODUCT_AAPT_CONFIG := normal
PRODUCT_AAPT_PREF_CONFIG := xxhdpi

# Boot Animation
TARGET_SCREEN_HEIGHT := 1620
TARGET_SCREEN_WIDTH := 1080

# Athena audio configs
PRODUCT_COPY_FILES += \
    $(call find-copy-subdir-files,*,$(DEVICE_PATH)/configs/audio/,$(TARGET_COPY_OUT_VENDOR)/etc)

# Athena camera configs
PRODUCT_COPY_FILES += \
    $(call find-copy-subdir-files,*,$(DEVICE_PATH)/configs/camera/,$(TARGET_COPY_OUT_VENDOR)/etc/camera)

# GMS
PRODUCT_GMS_CLIENTID_BASE := android-blackberry

# Goodix - libbinder shim
PRODUCT_PACKAGES += \
    libbinder_shim.vendor \
    libfakelogprint

# Camera - Shims for OREO camera HAL
PRODUCT_PACKAGES += \
    libskia_shim \
    libjnigraphics_shim

# Inherit from BlackBerry sdm660-common
$(call inherit-product, device/blackberry/sdm660-common/common.mk)
