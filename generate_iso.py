# generate_iso.py

import shutil
from pathlib import Path
import subprocess

project_name = "hello_uefi"
target = "x86_64-unknown-uefi"
project_dir = Path.cwd() / project_name
efi_file = project_dir / "target" / target / "release" / f"{project_name}.efi"
iso_dir = Path.cwd() / "iso_root"
efi_boot_path = iso_dir / "EFI" / "BOOT"
boot_efi = efi_boot_path / "BOOTX64.EFI"
iso_path = Path.cwd() / f"{project_name}.iso"

if not efi_file.exists():
    print("❌ EFI file not found. Please run build_project.py first.")
    exit(1)

# Prepare ISO directory
print("Preparing ISO structure...")
efi_boot_path.mkdir(parents=True, exist_ok=True)
shutil.copy2(efi_file, boot_efi)

# Generate ISO using xorriso or genisoimage
print("Generating ISO...")
try:
    subprocess.run([
        "xorriso",
        "-as", "mkisofs",
        "-R",
        "-J",
        "-efi-boot", "EFI/BOOT/BOOTX64.EFI",
        "-no-emul-boot",
        "-o", str(iso_path),
        str(iso_dir)
    ], check=True)
    print(f"✅ ISO created at: {iso_path}")
except FileNotFoundError:
    print("❌ xorriso not found. Please install it (Debian: sudo apt install xorriso)")
