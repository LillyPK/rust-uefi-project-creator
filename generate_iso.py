#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import tempfile
import argparse
from pathlib import Path

def check_dependencies():
    """Verify required tools are installed."""
    dependencies = ['grub-mkrescue', 'xorriso']
    missing = []
    
    for dep in dependencies:
        try:
            subprocess.run(['which', dep], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            missing.append(dep)
    
    if missing:
        print(f"Error: Missing required dependencies: {', '.join(missing)}")
        print("Please install them and try again.")
        sys.exit(1)
    
    print("✅ All dependencies are installed.")

def create_directory_structure(iso_root):
    """Create the necessary directory structure for the ISO."""
    dirs = [
        os.path.join(iso_root, "EFI", "BOOT"),
        os.path.join(iso_root, "boot", "grub")
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print(f"✅ Created directory structure at {iso_root}")

def copy_efi_file(efi_path, iso_root):
    """Copy the EFI file to the appropriate location in the ISO structure."""
    if not os.path.exists(efi_path):
        print(f"Error: EFI file not found at {efi_path}")
        return False
    
    dest_path = os.path.join(iso_root, "EFI", "BOOT", "BOOTX64.EFI")
    shutil.copy2(efi_path, dest_path)
    print(f"✅ Copied EFI file to {dest_path}")
    return True

def create_grub_config(iso_root):
    """Create a GRUB configuration file for booting the UEFI application."""
    grub_cfg_path = os.path.join(iso_root, "boot", "grub", "grub.cfg")
    
    grub_config = """set timeout=5
set default=0

menuentry "Boot UEFI Application" {
    insmod part_gpt
    insmod chain
    echo "Chainloading UEFI application..."
    chainloader /EFI/BOOT/BOOTX64.EFI
}

menuentry "UEFI Shell" {
    insmod chain
    echo "Launching UEFI Shell..."
    chainloader /EFI/BOOT/BOOTX64.EFI
}
"""
    
    with open(grub_cfg_path, 'w') as f:
        f.write(grub_config)
    
    print(f"✅ Created GRUB configuration at {grub_cfg_path}")
    return True

def generate_iso(iso_root, output_iso):
    """Generate a bootable ISO using grub-mkrescue."""
    try:
        print("Generating ISO file... (This may take a moment)")
        subprocess.run([
            'grub-mkrescue',
            '-o', output_iso,
            iso_root
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if os.path.exists(output_iso):
            print(f"✅ Successfully created bootable ISO at: {output_iso}")
            print(f"   ISO size: {os.path.getsize(output_iso) / (1024*1024):.2f} MB")
            return True
        else:
            print(f"Error: ISO generation failed - output file not found")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to generate ISO: {e}")
        print(f"STDERR: {e.stderr.decode() if e.stderr else 'None'}")
        return False

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Generate bootable ISO with GRUB and UEFI application')
    
    parser.add_argument(
        '--efi-path', 
        default='/home/lilly/Downloads/rustprojects/hello_uefi/target/x86_64-unknown-uefi/release/hello_uefi.efi',
        help='Path to the UEFI application (.efi file)'
    )
    
    parser.add_argument(
        '--output', 
        default='hello_uefi.iso',
        help='Path to the output ISO file'
    )
    
    return parser.parse_args()

def main():
    """Main function to coordinate the ISO generation process."""
    args = parse_args()
    
    # Convert to absolute paths
    efi_path = os.path.abspath(args.efi_path)
    output_iso = os.path.abspath(args.output)
    
    print(f"UEFI application: {efi_path}")
    print(f"Output ISO: {output_iso}")
    
    # Check if tools are installed
    check_dependencies()
    
    # Create a temporary directory for ISO structure
    with tempfile.TemporaryDirectory() as iso_root:
        try:
            # Create directory structure
            create_directory_structure(iso_root)
            
            # Copy EFI file
            if not copy_efi_file(efi_path, iso_root):
                return 1
            
            # Create GRUB configuration
            if not create_grub_config(iso_root):
                return 1
            
            # Generate ISO
            if not generate_iso(iso_root, output_iso):
                return 1
            
            print("You can boot this ISO in QEMU with:")
            print(f"qemu-system-x86_64 -cdrom {output_iso} -bios /usr/share/ovmf/OVMF.fd")
            
            return 0
            
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main())

