from conans import ConanFile, CMake, tools
import os
import subprocess


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake"]

    def build(self):
        cmake = CMake(self)
        cmake.definitions["PROJECT_SOURCE_DIR"] = "."
        cmake.definitions["Java_JAVA_EXECUTABLE"] = "java"
        cmake.definitions["ANTLR_JAR_LOCATION"] = self.env["ANTLR_EXECUTABLE"]
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            os.chdir("bin")
            self.run(".{}antlr4-demo".format(os.sep))
