
[app]

# App information
title = Jare Ooday
package.name = jareooday
package.domain = org.jareooday

# Source files
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

# Version
version = 1.0.0

# Python and Kivy dependencies
requirements = python3,kivy

# Screen settings
orientation = landscape
fullscreen = 0

# Android settings
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a

# Permissions
android.permissions =

# Android application settings
android.accept_sdk_license = True
android.allow_backup = True

# Build settings
[buildozer]

log_level = 2
warn_on_root = 1
