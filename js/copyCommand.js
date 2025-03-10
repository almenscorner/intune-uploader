function copyCommand(button) {
    const commandText = button.getAttribute("data-command");
    if (!commandText) {
        console.error("No command found to copy.");
        return;
    }

    console.log("Copying:", commandText);

    navigator.clipboard.writeText(commandText).then(() => {
        console.log("Copied successfully!");

        // Get the icon inside the button
        const icon = button.querySelector("i");
        if (icon) {
            // Change icon to a checkmark to indicate success
            icon.classList.replace("fa-copy", "fa-check");
            icon.classList.replace("text-gray-500", "text-green-400");

            // Restore icon after 2 seconds
            setTimeout(() => {
                icon.classList.replace("fa-check", "fa-copy");
                icon.classList.replace("text-green-400", "text-gray-500");
            }, 2000);
        }
    }).catch(err => {
        console.error("Failed to copy:", err);
    });
}