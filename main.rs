#![no_main]
#![no_main]
#![no_std]

use uefi::prelude::*;
use core::fmt::Write;
use uefi::proto::console::text::{Input, Key, ScanCode};

// Implement panic handler for no_std environment
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}

#[entry]
fn efi_main(_image_handle: Handle, mut st: SystemTable<Boot>) -> Status {
    // Initialize the console for output
    let _ = st.stdout().reset(false);
    
    // Display hello message
    writeln!(st.stdout(), "Hello, UEFI world!").unwrap();
    writeln!(st.stdout(), "").unwrap();
    writeln!(st.stdout(), "Press any key to exit...").unwrap();
    
    // Wait for a keypress before returning
    loop {
        // Check if there's a key in the buffer
        if let Some(key) = st.stdin().read_key().unwrap() {
            // Exit on any key press
            break;
        }
        
        // Give the CPU a chance to handle other tasks
        st.boot_services().stall(10_000); // 10 ms delay
    }
    
    Status::SUCCESS
}