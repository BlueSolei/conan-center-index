from conans import ConanFile, CMake, tools
import os


class Antlr4Conan(ConanFile):
    name = "antlr4"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.antlr.org/"
    topics = ("parse", "parsing", "parser-generator", "grammar", "antlr", "antlr4", "language-recognition")
    description = "C++ runtime support for ANTLR"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports = "Antlr4.cmake"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return os.path.join("source_subfolder", f"antlr4-{self.version}", "runtime", "Cpp")

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        src = self.conan_data["sources"][self.version]
        tools.get(**src["code"], destination="source_subfolder")
        antlr_executable = os.path.join(self._source_subfolder, "antlr.jar")
        tools.download(**src["jar"], filename=antlr_executable)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(
            target="antlr4_shared" if self.options.shared else "antlr4_static")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        try:
            use_static_crt = self.settings.compiler.runtime in ["MT", "MTd"]
        except Exception:
            use_static_crt = None

        try:
            use_libcpp = self.settings.compiler.libcxx == "libc++"
        except Exception:
            use_libcpp = None

        self._cmake = CMake(self)
        self._cmake.definitions["WITH_LIBCXX"] = "ON" if use_libcpp else "OFF"
        self._cmake.definitions["WITH_STATIC_CRT"] = "ON" if use_static_crt else "OFF"

        # this is SUPPOSE to be done automatically. 
        # for some wired bug, this is needed to be set explicitly        
        self._cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type 
        
        self._cmake.configure(build_folder=self._build_subfolder,
                              source_folder=self._source_subfolder)
        return self._cmake

    def package(self):
        dist = os.path.join(self._source_subfolder, "dist")
        include = os.path.join(self._source_subfolder, "runtime", "src")

        # antlr tool
        self.copy("*/antlr.jar", dst="bin", keep_path=False)

        # antlr runtime
        self.copy("*/LICENSE.txt", dst="licenses", keep_path=False)
        self.copy("*.h", dst="include", src=include)
        self.copy("*.a", dst="lib", src=dist, keep_path=False)
        self.copy("*.lib", dst="lib", src=dist, keep_path=False)
        self.copy("*.so*", dst="lib", src=dist, keep_path=False)
        self.copy("*.dylib", dst="lib", src=dist, keep_path=False)
        self.copy("*.dll", dst="bin", src=dist, keep_path=False)

        # antlr utils (generate parsers\lexers in CMake scripts)
        self.copy("*/FindANTLR.cmake", dst="bin/cmake", keep_path=False)
        self.copy("Antlr4.cmake", dst="bin/cmake",  keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows" and not self.options.shared:
          libname = f"antlr4-runtime-static"
        else:
          libname = "antlr4-runtime"
          
        self.cpp_info.libs = [libname]
        self.cpp_info.builddirs = ["bin/cmake"]
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("bin", "cmake", "Antlr4.cmake")])
        antlr_executable = os.path.join(
            self.package_folder, "bin", "antlr.jar")
        self.user_info.antlr_executable = antlr_executable
        self.env_info.ANTLR_EXECUTABLE = antlr_executable
