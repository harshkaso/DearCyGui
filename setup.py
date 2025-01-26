from setuptools import setup, find_packages, Distribution
from setuptools.command import build_py
from setuptools.extension import Extension
from Cython.Build import cythonize
import distutils.cmd
from codecs import open
import os
from os import path
import sys
from glob import glob
import numpy as np
import shutil
import subprocess

wip_version = "0.0.8"

def version_number():
    return wip_version

def get_platform():
    platforms = {
        'linux': 'Linux',
        'linux1': 'Linux', 
        'linux2': 'Linux',
        'darwin': 'OS X'
    }
    if sys.platform == 'darwin':
        return 'OS X'
    if "win" in sys.platform:
        return "Windows"
    if sys.platform not in platforms:
        return sys.platform
    return platforms[sys.platform]

# This few functions below were generated by copilot.
def is_mingw():
    try:
        # Check if gcc is being used and we're on Windows
        if get_platform() != "Windows":
            return False
        import subprocess
        result = subprocess.run(['gcc', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0 and (b'mingw' in result.stdout.lower() or b'mingw' in result.stderr.lower())
    except:
        return False

def is_msvc_compat():
    return "--msvc-compat" in sys.argv

def get_mingw_msvc_flags():
    if not is_msvc_compat():
        return []
    return ["-fms-extensions", "-fms-compatibility", "-fms-compatibility-version=19.29",
            "-fdeclspec", "-fpack-struct=8", "-mms-bitfields"]

def is_gcc_clang_compat():
    return "--gcc-clang-compat" in sys.argv

def get_gcc_clang_compat_flags():
    if not is_gcc_clang_compat():
        return []
    return [
        "-fno-strict-aliasing",      # Helps with type-punning issues
        "-ffunction-sections",       # Better optimization/compatibility
        "-fdata-sections",           # Better optimization/compatibility
        "-D__STDC_CONSTANT_MACROS", # Important for C++ code
        "-D__STDC_LIMIT_MACROS",    # Important for C++ code
        "-D__STDC_FORMAT_MACROS"    # Important for C++ code
    ]

def build_SDL3():
    src_path = os.path.dirname(os.path.abspath(__file__))
    cmake_config_args = [
        '-DCMAKE_BUILD_TYPE=Release',
        '-DSDL_SHARED=OFF',
        '-DSDL_STATIC=ON',
        '-DSDL_EXAMPLES=OFF',
        '-DSDL_TESTS=OFF',
        '-DSDL_TEST_LIBRARY=OFF',
        '-DSDL_DISABLE_INSTALL=ON',
        '-DSDL_DISABLE_INSTALL_DOCS=ON',
        '-DCMAKE_POSITION_INDEPENDENT_CODE=ON'
    ]
    if get_platform() == "Windows":
        cmake_config_args += ["-DSDL_JOYSTICK=OFF -DSDL_HAPTIC=OFF"]
        if is_mingw():
            # First, set up the generator
            generator_command = 'cmake -S thirdparty/SDL/ -B build_SDL -G "MinGW Makefiles"'
            subprocess.check_call(generator_command, shell=True)
            
            # Then configure with the rest of the arguments
            mingw_args = ["-DCMAKE_C_COMPILER=gcc", "-DCMAKE_CXX_COMPILER=g++"]
            if is_msvc_compat():
                mingw_args += [
                    "-DCMAKE_C_FLAGS=-fms-extensions -fms-compatibility -fms-compatibility-version=19.29",
                    "-DCMAKE_CXX_FLAGS=-fms-extensions -fms-compatibility -fms-compatibility-version=19.29 -fdeclspec"
                ]
            command = 'cmake -S thirdparty/SDL/ -B build_SDL ' + ' '.join(cmake_config_args + mingw_args)
            subprocess.check_call(command, shell=True)
        else:
            command = 'cmake -S thirdparty/SDL/ -B build_SDL ' + ' '.join(cmake_config_args)
            subprocess.check_call(command, shell=True)

    command = 'cmake --build build_SDL --config Release'
    subprocess.check_call(command, shell=True)
    
    if get_platform() == "Windows":
        if is_mingw():
            return os.path.abspath(os.path.join("build_SDL", "libSDL3.a"))
        return os.path.abspath(os.path.join("build_SDL", "Release/SDL3-static.lib"))
    return os.path.abspath(os.path.join("build_SDL", "libSDL3.a"))

def build_FREETYPE():
    src_path = os.path.dirname(os.path.abspath(__file__))
    cmake_config_args = [
        '-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_POSITION_INDEPENDENT_CODE=ON',
        '-D FT_DISABLE_ZLIB=TRUE',
        '-D FT_DISABLE_BZIP2=TRUE',
        '-D FT_DISABLE_PNG=TRUE',
        '-D FT_DISABLE_HARFBUZZ=TRUE',
        '-D FT_DISABLE_BROTLI=TRUE'
    ]
    
    if get_platform() == "Windows" and is_mingw():
        # First, set up the generator
        generator_command = 'cmake -S thirdparty/freetype/ -B build_FT -G "MinGW Makefiles"'
        subprocess.check_call(generator_command, shell=True)
        
        # Then configure with the rest of the arguments
        mingw_args = ["-DCMAKE_C_COMPILER=gcc", "-DCMAKE_CXX_COMPILER=g++"]
        if is_msvc_compat():
            mingw_args += [
                "-DCMAKE_C_FLAGS=-fms-extensions -fms-compatibility -fms-compatibility-version=19.29",
                "-DCMAKE_CXX_FLAGS=-fms-extensions -fms-compatibility -fms-compatibility-version=19.29 -fdeclspec"
            ]
        command = 'cmake -S thirdparty/freetype/ -B build_FT ' + ' '.join(cmake_config_args + mingw_args)
        subprocess.check_call(command, shell=True)
    else:
        command = 'cmake -S thirdparty/freetype/ -B build_FT ' + ' '.join(cmake_config_args)
        subprocess.check_call(command, shell=True)

    command = 'cmake --build build_FT --config Release'
    subprocess.check_call(command, shell=True)
    
    if get_platform() == "Windows":
        if is_mingw():
            return os.path.abspath(os.path.join("build_FT", "libfreetype.a"))
        return os.path.abspath(os.path.join("build_FT", "Release/freetype.lib"))
    return os.path.abspath(os.path.join("build_FT", "libfreetype.a"))

def setup_package():

    src_path = os.path.dirname(os.path.abspath(__file__))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    # Build dependencies
    sdl3_lib = build_SDL3()
    FT_lib = build_FREETYPE()

    # import readme content
    with open("./README.md", encoding='utf-8') as f:
        long_description = f.read()

    include_dirs = ["dearcygui",
                    "dearcygui/backends",
                    "thirdparty/imgui",
                    "thirdparty/imgui/backends",
                    "thirdparty/imnodes",
                    "thirdparty/implot",
                    "thirdparty/gl3w",
                    "thirdparty/freetype/include",
                    "thirdparty/SDL/include"]
    include_dirs += [np.get_include()]

    cpp_sources = [
        "dearcygui/backends/sdl3_gl3_backend.cpp",
        "thirdparty/imnodes/imnodes.cpp",
        "thirdparty/implot/implot.cpp",
        "thirdparty/implot/implot_items.cpp",
        "thirdparty/implot/implot_demo.cpp",
        "thirdparty/imgui/misc/cpp/imgui_stdlib.cpp",
        "thirdparty/imgui/imgui.cpp",
        "thirdparty/imgui/imgui_demo.cpp",
        "thirdparty/imgui/imgui_draw.cpp",
        "thirdparty/imgui/imgui_widgets.cpp",
        "thirdparty/imgui/imgui_tables.cpp",
        "dearcygui/backends/imgui_impl_sdl3.cpp",
        "dearcygui/backends/imgui_impl_opengl3.cpp",
        "thirdparty/imgui/misc/freetype/imgui_freetype.cpp",
        "thirdparty/gl3w/GL/gl3w.cpp"
    ]

    compile_args = ["-D_CRT_SECURE_NO_WARNINGS",
                    "-D_USE_MATH_DEFINES",
                    "-DIMGUI_IMPL_OPENGL_LOADER_SDL3",
                    "-DIMGUI_USER_CONFIG=\"imgui_config.h\""]
    linking_args = ['-O3']

    if get_platform() == "Linux":
        compile_args += ["-DNDEBUG", "-fwrapv", "-O3", "-DUNIX", "-DLINUX", "-g1", "-std=c++14"]
        compile_args += get_gcc_clang_compat_flags()
        libraries = ["crypt", "pthread", "dl", "util", "m", "GL"]
    elif get_platform() == "OS X":
        compile_args += [
            "-fobjc-arc", "-fno-common", "-dynamic", "-DNDEBUG",
            "-fwrapv", "-O3", "-DAPPLE", "-arch", "x86_64", "-std=c++14"
        ]
        compile_args += get_gcc_clang_compat_flags()
        libraries = []
        # Link against MacOS frameworks
        linking_args += [
            "-framework", "Cocoa",
            "-framework", "IOKit", 
            "-framework", "CoreFoundation",
            "-framework", "CoreVideo",
            "-framework", "OpenGL",
            "-arch", "x86_64"
        ]
    elif get_platform() == "Windows":
        if is_mingw():
            compile_args += ["-O2", "-DNDEBUG", "-D_WINDOWS", "-DWIN32_LEAN_AND_MEAN", "-std=c++14"]
            if is_msvc_compat():
                compile_args += get_mingw_msvc_flags()
            if is_gcc_clang_compat():
                compile_args += get_gcc_clang_compat_flags()
            libraries = ["user32", "gdi32", "shell32", "advapi32", "imm32", "ole32", "oleaut32", "uuid", "opengl32",
                        "setupapi", "version", "winmm"]
            linking_args += ["-static", "-static-libgcc", "-static-libstdc++"]
        else:
            compile_args += ["/O2", "/DNDEBUG", "/D_WINDOWS", "/D_UNICODE", "/DWIN32_LEAN_AND_MEAN", "/std:c++14", "/EHsc"]
            libraries = ["user32", "gdi32", "shell32", "advapi32", "ole32", "oleaut32", "uuid", "opengl32",
                        "setupapi", "cfgmgr32", "version", "winmm"]
            linking_args += ["/MACHINE:X64"]
    else:
        # Please test and tell us what changes are needed to the build
        raise ValueError("Unsupported platform")
    cython_sources = [
        "dearcygui/core.pyx",
        "dearcygui/draw.pyx",
        "dearcygui/font.pyx",
        "dearcygui/handler.pyx",
        "dearcygui/imgui.pyx",
        "dearcygui/imgui_types.pyx",
        "dearcygui/layout.pyx",
        "dearcygui/os.pyx",
        "dearcygui/plot.pyx",
        "dearcygui/table.pyx",
        "dearcygui/theme.pyx",
        "dearcygui/types.pyx",
        "dearcygui/widget.pyx",
    ]

    # We compile in a single extension because we want
    # to link to the same static libraries

    extensions = [
        Extension(
            "dearcygui.dearcygui",
            ["dearcygui/dearcygui.pyx"] + cython_sources + cpp_sources,
            language="c++",
            include_dirs=include_dirs,
            extra_compile_args=compile_args,
            libraries=libraries,
            extra_link_args=linking_args,
            extra_objects=[sdl3_lib, FT_lib]
        )
    ]

    # secondary extensions
    extensions += [
        Extension(
            "dearcygui.utils.draw",
            ["dearcygui/utils/draw.pyx"],
            language="c++",
            include_dirs=[np.get_include()],
            extra_compile_args=compile_args,
             libraries=libraries,
            extra_link_args=linking_args),
        Extension(
            "dearcygui.utils.image",
            ["dearcygui/utils/image.pyx"],
            language="c++",
            include_dirs=[np.get_include()],
            extra_compile_args=compile_args,
             libraries=libraries,
            extra_link_args=linking_args)
    ]

    shutil.copy("thirdparty/latin-modern-roman/lmsans17-regular.otf", "dearcygui/")
    shutil.copy("thirdparty/latin-modern-roman/lmromanslant17-regular.otf", "dearcygui/")
    shutil.copy("thirdparty/latin-modern-roman/lmsans10-bold.otf", "dearcygui/")
    shutil.copy("thirdparty/latin-modern-roman/lmromandemi10-oblique.otf", "dearcygui/")


    metadata = dict(
        name='dearcygui',                                      # Required
        version=version_number(),                              # Required
        author="Axel Davy",                                    # Optional
        description='DearCyGui: A simple and customizable Python GUI Toolkit coded in Cython',  # Required
        long_description=long_description,                     # Optional
        long_description_content_type='text/markdown',         # Optional
        url='https://github.com/axeldavy/DearCyGui',          # Optional
        license = 'MIT',
        python_requires='>=3.10',
        classifiers=[
                'Development Status :: 2 - Pre-Alpha',
                'Intended Audience :: Education',
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'License :: OSI Approved :: MIT License',
                'Operating System :: MacOS',
                'Operating System :: Microsoft :: Windows :: Windows 10',
                'Operating System :: POSIX',
                'Operating System :: Unix',
                'Programming Language :: Cython',
                'Programming Language :: Python :: 3',
                'Topic :: Software Development :: User Interfaces',
                'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        packages=['dearcygui', 'dearcygui.docs', 'dearcygui.utils', 'dearcygui.backends', 'dearcygui.wrapper'],
        install_requires=[
          'numpy',
          'freetype-py',
          'scipy'
        ],
        ext_modules = cythonize(extensions, compiler_directives={'language_level' : "3"}, nthreads=4),
        extras_require={
            'svg': ['skia-python'],  # For SVG rendering support in utils.image
        }
    )
    metadata["package_data"] = {}
    metadata["package_data"]['dearcygui'] = ['*.pxd', '*.py', '*.pyi', '*ttf', '*otf', '*typed']
    metadata["package_data"]['dearcygui.docs'] = ['*.py', '*.md']
    metadata["package_data"]['dearcygui.utils'] = ['*.pxd', '*.py', '*.pyi', '*ttf', '*otf', '*typed']
    metadata["package_data"]['dearcygui.backends'] = ['*.pxd', '*.py', '*.pyi', '*ttf', '*otf', '*typed']
    metadata["package_data"]['dearcygui.wrapper'] = ['*.pxd', '*.py', '*.pyi', '*ttf', '*otf', '*typed']

    if "--msvc-compat" in sys.argv:
        sys.argv.remove('--msvc-compat')

    if "--gcc-clang-compat" in sys.argv:
        sys.argv.remove('--gcc-clang-compat')

    if "--force" in sys.argv:
        sys.argv.remove('--force')

    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)
    return


if __name__ == '__main__':
    setup_package()
