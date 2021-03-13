from conans import ConanFile, CMake, tools
import os


class Antlr4Conan(ConanFile):
    name = "antlr4"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.antlr.org/"
    topics = ("conan", "antlr", "parsers")
    description = "C++ runtime support for ANTLR"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    version = "4.9.1"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version]["sources"],
                  destination=self._source_subfolder)
        filename = os.path.join(self._source_subfolder, "antlr.jar")
        tools.download(
            **self.conan_data["sources"][self.version]["jar"], filename=filename)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(
            target="antlr4_shared" if self.options.shared else "antlr4_static")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_LIBCXX"] = "OFF"
        self._cmake.configure(build_folder=self._build_subfolder,
                              source_folder=self._source_subfolder)
        return self._cmake

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses",
                  src=self._source_subfolder)
        self.copy("*.h", dst="include",
                  src=os.path.join(self._source_subfolder, "runtime", "src"))
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.jar", dst="bin",
                  src=self._source_subfolder, keep_path=False)
        self.copy(
            pattern="*.so*",
            dst="lib",
            src=os.path.join(self._source_subfolder, "dist"),
            keep_path=False,
            symlinks=True,
        )

    def package_info(self):
        self.cpp_info.libs = ["antlr4-runtime"]
        self.env_info.ANTLR_EXECUTABLE = os.path.join(
            self.package_folder, "bin", "antlr.jar")
