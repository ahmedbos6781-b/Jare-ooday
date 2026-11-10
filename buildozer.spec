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

# Screen settings (Landscape sidaad rabtay)
orientation = landscape
fullscreen = 0

# Android settings (Waxaan ka dhignay API 34 iyo NDK 25b si uusan GitHub Actions u qaladin)
android.api = 34
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Permissions
android.permissions =

# Android application settings
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
