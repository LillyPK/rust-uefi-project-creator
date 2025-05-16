# build_project.py

import subprocess
from pathlib import Path

project_name = "hello_uefi"
project_dir = Path.cwd() / project_name
target = "x86_64-unknown-uefi"
efi_path = project_dir / "target" / target / "release" / f"{project_name}.efi"

print("Adding UEFI target...")
subprocess.run(["rustup", "target", "add", target], check=True)

print("Building project...")
result = subprocess.run([
    "cargo", "build",
    "--release",
    "--target", target
], cwd=project_dir)

if result.returncode == 0 and efi_path.exists():
    print(f"\n✅ Build successful! EFI file created at:\n{efi_path}")
else:
    print("\n❌ Build failed.")
