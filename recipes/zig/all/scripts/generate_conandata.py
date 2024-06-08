import json
import yaml
import requests
from pathlib import Path


# Sample JSON data
json_data_example = '''{
    "0.13.0": {
        "date": "2024-06-07",
        "docs": "https://ziglang.org/documentation/0.13.0/",
        "stdDocs": "https://ziglang.org/documentation/0.13.0/std/",
        "notes": "https://ziglang.org/download/0.13.0/release-notes.html",
        "src": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-0.13.0.tar.xz",
            "shasum": "06c73596beeccb71cc073805bdb9c0e05764128f16478fa53bf17dfabc1d4318",
            "size": "17220728"
        },
        "bootstrap": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-bootstrap-0.13.0.tar.xz",
            "shasum": "cd446c084b5da7bc42e8ad9b4e1c910a957f2bf3f82bcc02888102cd0827c139",
            "size": "46440356"
        },
        "x86_64-freebsd": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-freebsd-x86_64-0.13.0.tar.xz",
            "shasum": "adc1ffc9be56533b2f1c7191f9e435ad55db00414ff2829d951ef63d95aaad8c",
            "size": "47177744"
        },
        "x86_64-macos": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-macos-x86_64-0.13.0.tar.xz",
            "shasum": "8b06ed1091b2269b700b3b07f8e3be3b833000841bae5aa6a09b1a8b4773effd",
            "size": "48857012"
        },
        "aarch64-macos": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-macos-aarch64-0.13.0.tar.xz",
            "shasum": "46fae219656545dfaf4dce12fb4e8685cec5b51d721beee9389ab4194d43394c",
            "size": "44892040"
        },
        "x86_64-linux": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-linux-x86_64-0.13.0.tar.xz",
            "shasum": "d45312e61ebcc48032b77bc4cf7fd6915c11fa16e4aad116b66c9468211230ea",
            "size": "47082308"
        },
        "aarch64-linux": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-linux-aarch64-0.13.0.tar.xz",
            "shasum": "041ac42323837eb5624068acd8b00cd5777dac4cf91179e8dad7a7e90dd0c556",
            "size": "43090688"
        },
        "armv7a-linux": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-linux-armv7a-0.13.0.tar.xz",
            "shasum": "4b0550239c2cd884cc03ddeb2b9934708f4b073ad59a96fccbfe09f7e4f54233",
            "size": "43998916"
        },
        "riscv64-linux": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-linux-riscv64-0.13.0.tar.xz",
            "shasum": "9f7f3c685894ff80f43eaf3cad1598f4844ac46f4308374237c7f912f7907bb3",
            "size": "45540956"
        },
        "powerpc64le-linux": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-linux-powerpc64le-0.13.0.tar.xz",
            "shasum": "6a467622448e830e8f85d20cabed151498af2b0a62f87b8c083b2fe127e60417",
            "size": "46574596"
        },
        "x86-linux": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-linux-x86-0.13.0.tar.xz",
            "shasum": "876159cc1e15efb571e61843b39a2327f8925951d48b9a7a03048c36f72180f7",
            "size": "52062336"
        },
        "x86_64-windows": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-windows-x86_64-0.13.0.zip",
            "shasum": "d859994725ef9402381e557c60bb57497215682e355204d754ee3df75ee3c158",
            "size": "79163968"
        },
        "aarch64-windows": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-windows-aarch64-0.13.0.zip",
            "shasum": "95ff88427af7ba2b4f312f45d2377ce7a033e5e3c620c8caaa396a9aba20efda",
            "size": "75119033"
        },
        "x86-windows": {
            "tarball": "https://ziglang.org/download/0.13.0/zig-windows-x86-0.13.0.zip",
            "shasum": "eb3d533c3cf868bff7e74455dc005d18fd836c42e50b27106b31e9fec6dffc4a",
            "size": "83274739"
        }
    }
}'''

zig_os_to_conan = {
    "linux": "Linux",
    "windows": "Windows",
    "macos": "Macos",
    "freebsd": "FreeBSD",
}

zig_arch_to_conan = {
    "aarch64": "armv8",
    "powerpc64le": "ppc64le",
    "powerpc": "ppc32",
    "armv6kz": "armv6",
    "armv7a": "armv7",
    "riscv64": "riscv64",
    "x86": "x86",
    "i386": "x86",
    "x86_64": "x86_64"
}

zig_download_matrix = "https://ziglang.org/download/index.json"

# Get Zig's binaries matrix
response = requests.get(zig_download_matrix)
assert response.status_code == 200, f"Faild to download Zig's binaries matrix file from '{zig_download_matrix}' . error code: {response.status_code}"
json_data = response.text

# Load JSON data
data = json.loads(json_data)

# Initialize the YAML structure
sources = "sources"
yaml_data = {sources: {}}

# Process the JSON data
for version, details in data.items():
    yaml_data[sources][version] = {}
    for key, value in details.items():
        if '-' in key:
            arch, os = key.split('-')
            os = zig_os_to_conan[os]
            arch = zig_arch_to_conan[arch]
            if os not in yaml_data[sources][version]:
                yaml_data[sources][version][os] = {}
            yaml_data[sources][version][os][arch] = {
                'url': value['tarball'],
                'sha256': value['shasum']
            }

# Convert to YAML
conandata = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)

# Print the YAML output
folder = Path(__file__).resolve().parent
with open(folder / "conandata.yml", "w") as f:
    f.write(conandata)
