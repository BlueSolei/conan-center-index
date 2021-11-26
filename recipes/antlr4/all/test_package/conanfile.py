from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake"]

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
      self.copy("*.dll", src="bin", dst="bin", keep_path=False)
      self.copy("*.dylib", src="lib", dst="lib", keep_path=False)
      
    def test(self):
        if not tools.cross_building(self.settings):
            os.chdir("bin")
            self.run(".{}antlr4-demo".format(os.sep))
