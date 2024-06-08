ext = "bat" if self.settings.os == "Windows" else "sh"
params = "%*" if self.settings.os == "Windows" else "$@"
execs = {
    "c": {"name": f"zig-cc.{ext}", "code": f"zig cc {params}"},
    "cpp": {"name": f"zig-cpp.{ext}", "code": f"zig c++ {params}"},
    "ar": {"name": f"zig-ar.{ext}", "code": f"zig ar {params}"},
    "runlib": {"name": f"zig-runlib.{ext}", "code": f"zig runlib {params}"}
}

for exec in execs:
    path = os.path.join(self.package_folder, exec["name"])
