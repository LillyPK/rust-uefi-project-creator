#!/bin/bash

# ---------------------------------------------------------------
# setup.sh - Setup script for UEFI Rust project
# ---------------------------------------------------------------
# This script automates the setup process for UEFI Rust projects:
# - Installs Rust nightly toolchain
# - Installs system dependencies (xorriso)
# - Builds the UEFI application
# - Sets up the required directory structure
# ---------------------------------------------------------------

# Exit on any error
set -e

# Set text colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print messages with color
print_step() {
    echo -e "${BLUE}==> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Setup trap to handle errors
trap 'echo -e "${RED}❌ An error occurred. Setup failed.${NC}"; exit 1' ERR

# Directory setup - using $HOME instead of hardcoded paths
RUST_PROJECTS_DIR="$HOME/Downloads/rustprojects"
SCRIPT_DIR="$(pwd)"

print_step "Starting UEFI Rust project setup..."

# Step 1: Check and install Rust nightly
print_step "Checking Rust installation..."
if ! command_exists rustup; then
    print_step "Installing Rust using rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

print_step "Installing Rust nightly toolchain..."
rustup toolchain install nightly

print_step "Adding UEFI target..."
rustup target add x86_64-unknown-uefi --toolchain nightly

# Step 2: Check and install system dependencies
print_step "Checking system dependencies..."

if ! command_exists xorriso; then
    print_step "Installing xorriso dependency..."
    # Check if we can use sudo without password (already authenticated)
    if sudo -n true 2>/dev/null; then
        sudo apt-get update -y
        sudo apt-get install -y xorriso
    else
        echo "We need to install xorriso. This requires sudo privileges."
        sudo apt-get update -y
        sudo apt-get install -y xorriso
    fi
    print_success "Installed xorriso successfully."
else
    print_success "xorriso is already installed."
fi

# Step 3: Create and build the UEFI project
if [ ! -d "hello_uefi" ]; then
    print_step "Creating Rust UEFI project..."
    python3 create_project.py
else
    print_success "Project already exists, skipping creation."
fi

print_step "Building UEFI application..."
cd hello_uefi
# Make sure Cargo.toml has the right settings for UEFI
if ! grep -q "uefi" Cargo.toml; then
    # Add UEFI-specific configurations to Cargo.toml
    cat << EOF >> Cargo.toml

[profile.release]
lto = true

[package.metadata.bootimage]
run-command = ["qemu-system-x86_64", "-drive", "format=raw,file={}"]

[target.'cfg(target_os = "uefi")'.dependencies]
uefi = "0.15.0"
uefi-services = "0.12.0"
EOF
    print_success "Updated Cargo.toml with UEFI dependencies."
fi

# Build the project
cargo +nightly build --target x86_64-unknown-uefi --release
print_success "Built UEFI application successfully."

# Return to the script directory
cd "$SCRIPT_DIR"

# Step 4: Set up directory structure
print_step "Setting up required directory structure..."
mkdir -p "$RUST_PROJECTS_DIR"
cp -r hello_uefi "$RUST_PROJECTS_DIR/"
print_success "Copied project to $RUST_PROJECTS_DIR/hello_uefi"

# Step 5: Final validation
if [ -f "$RUST_PROJECTS_DIR/hello_uefi/target/x86_64-unknown-uefi/release/hello_uefi.efi" ]; then
    print_success "Setup completed successfully!"
    echo -e "${GREEN}You can now run the generate_iso.py script to create a bootable ISO:${NC}"
    echo -e "  python3 generate_iso.py"
    
    # Show QEMU command for testing
    echo -e "${BLUE}After creating the ISO, you can test it using:${NC}"
    echo -e "  qemu-system-x86_64 -cdrom hello_uefi.iso -bios /usr/share/ovmf/OVMF.fd"
else
    print_error "Setup incomplete. EFI file was not created correctly."
    exit 1
fi

