import os
import subprocess
import sys

PROJECT_NAME = "hello_uefi"
PROJECT_DIR = os.path.join(os.getcwd(), PROJECT_NAME)

CARGO_TOML_CONTENT = f"""[package]
name = "{PROJECT_NAME}"
version = "0.1.0"
edition = "2021"

[dependencies]
uefi = "0.24"

[profile.release]
opt-level = "z"
lto = true
codegen-units = 1
panic = "abort"
"""

MAIN_RS_CONTENT = """#![no_main]
#![no_std]

use uefi::prelude::*;
use core::fmt::Write;

// Implement panic handler for no_std environment
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}

#[entry]
fn efi_main(_image_handle: Handle, mut st: SystemTable<Boot>) -> Status {
    // Initialize the console for output
    let _ = st.stdout().reset(false);
    writeln!(st.stdout(), "Hello, UEFI world!").unwrap();
    
    Status::SUCCESS
}
"""


def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        sys.exit(result.returncode)

def create_project():
    if os.path.exists(PROJECT_DIR):
        print(f"❌ Project directory '{PROJECT_DIR}' already exists.")
        return

    print(f"📁 Creating Rust project: {PROJECT_NAME}")
    run(["cargo", "new", PROJECT_NAME, "--bin"])

    # Write Cargo.toml
    with open(os.path.join(PROJECT_DIR, "Cargo.toml"), "w") as f:
        f.write(CARGO_TOML_CONTENT)

    # Write src/main.rs
    with open(os.path.join(PROJECT_DIR, "src", "main.rs"), "w") as f:
        f.write(MAIN_RS_CONTENT)


    print("✅ Project created successfully.")

if __name__ == "__main__":
    create_project()
