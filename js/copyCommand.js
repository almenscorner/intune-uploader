function copyCommand(button) {
    const commandText = button.getAttribute("data-command");
    if (!commandText) {
        console.error("No command found to copy.");
        return;
    }

    console.log("Copying:", commandText);

    navigator.clipboard.writeText(commandText).then(() => {
        console.log("Copied successfully!");

        // Change icon color to indicate success
        const icon = button.querySelector("i.fa-copy");
        if (icon) {
            icon.classList.replace("text-gray-400", "text-green-400");

            setTimeout(() => {
                icon.classList.replace("text-green-400", "text-gray-400");
            }, 2000);
        }
    }).catch(err => {
        console.error("Failed to copy:", err);
    });
}