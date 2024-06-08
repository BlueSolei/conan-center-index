from conan import ConanFile, conan_version
from conan.tools.files import get
from conan.tools.scm import Version
import os


class ZigConan(ConanFile):
    name = "zig"
    package_type = "application"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ziglang.org/"
    description = "General-purpose programming language and toolchain for maintaining robust, optimal, and reusable software."
    license = "MIT"
    topics = ("language", "compiler", "zig",)

    settings = "os", "arch", "compiler", "build_type"

    # not needed but supress warning message from conan commands
    def layout(self):
        pass

    # specific compiler and build type, usually are not distributed by vendors
    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    # in case some configuration is not supported
    def validate(self):
        pass
        # if self.settings.os == "Macos" and Version(self.settings.os.version) < 11:
        #     raise ConanInvalidConfiguration(f"{self.ref} requires OSX >=11.")

    def source(self):
        # do not cache as source, instead, use build folder
        pass

    def build(self):
        # download zig directly to the package folder
        get(
            self,
            **self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)],
            strip_root=True,
            destination=self.package_folder
        )

    def package(self):
        # no need to copy selectivly, as we copy zig's distribution as is
        pass

    def package_info(self):
        # folders not used for pre-built binaries
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        self.cpp_info.bindirs.append(self.package_folder)

        triplet = "native-native-musl"
        self.conf_info.update(
            "tools.build:compiler_executables", {"zig": "zig"})
        self.buildenv_info.define(
            "ZIG_LOCAL_CACHE_DIR", f"/tmp/zig-cache")  # TODO remove this
        self.buildenv_info.define("CC", f"zig cc -target {triplet}")
        self.buildenv_info.define("CXX", f"zig c++ -target {triplet}")
        self.buildenv_info.define("AR", "zig ar")
        self.buildenv_info.define("RANLIB", "zig ranlib")
        self.buildenv_info.define("USE_JEMALLOC", "no")
        self.buildenv_info.define("USE_SYSTEMD", "no")

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, ".")
        if Version(conan_version).major < 2:
            self.env_info.PATH.append(bin_folder)
            self.env_info.CC = self.buildenv_info["CC"]
            self.env_info.CXX = self.buildenv_info["CXX"]
            self.env_info.AR = self.buildenv_info["AR"]
            self.env_info.RANLIB = self.buildenv_info["RANLIB"]
