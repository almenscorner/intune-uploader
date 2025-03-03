function copyCommand(button) {
    const commandBlock = button.closest(".command-block");
    if (!commandBlock) {
        console.error("No command block found");
        return;
    }

    const commandText = Array.from(commandBlock.querySelectorAll(".command-text, .command-highlight"))
        .map(child => child.innerText.trim())
        .join(" ");

    console.log("Copying:", commandText);

    navigator.clipboard.writeText(commandText).then(() => {
        console.log("Copied successfully!");

        const icon = button.querySelector("i.fa-copy, i.fa-clone");
        if (icon) {
            icon.classList.remove("text-gray-500");
            icon.classList.add("text-green-400");

            setTimeout(() => {
                icon.classList.remove("text-green-400");
                icon.classList.add("text-gray-500");
            }, 2000);
        }
    }).catch(err => {
        console.error("Failed to copy:", err);
    });
}
