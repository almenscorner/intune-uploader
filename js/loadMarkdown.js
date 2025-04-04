async function loadMarkdown(url, targetElement) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to load FAQ file.");

        const markdown = await response.text();
        const faqContainer = document.getElementById(targetElement);

        // Ensure header remains intact
        faqContainer.innerHTML = `<h2 class="text-2xl font-bold gradient-flow mb-6 tracking-wide">❓ FAQ</h2>`;

        // Split into questions and answers
        const faqItems = markdown.split("### ➤").slice(1);

        faqItems.forEach((item, index) => {
            const lines = item.split("\n");
            const question = lines.shift().trim();
            const answer = lines.join("\n").trim().replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="text-green-300 hover:underline">$1</a>');

            // Create FAQ item
            const faqItem = document.createElement("div");
            faqItem.className = "border-b border-gray-700 pb-3";

            // Create question button
            const faqButton = document.createElement("button");
            faqButton.className = "w-full text-left text-gray-300 font-medium flex items-center gap-2 py-3";
            faqButton.innerHTML = `<p id="arrow${index}" class="transition-transform">➤</p><span>${question}</span>`;
            faqButton.onclick = () => toggleFAQ(index);

            // Create answer paragraph (hidden by default)
            const faqAnswer = document.createElement("p");
            faqAnswer.id = `faq${index}`;
            faqAnswer.className = "faq-content text-gray-400 font-light hidden mt-2";
            faqAnswer.innerHTML = answer;

            faqItem.appendChild(faqButton);
            faqItem.appendChild(faqAnswer);
            faqContainer.appendChild(faqItem);
        });

    } catch (error) {
        console.error("Error loading FAQ:", error);
        document.getElementById(targetElement).innerHTML = `<p class="text-red-400">Failed to load FAQ.</p>`;
    }
}

// Toggle FAQ expand/collapse
function toggleFAQ(id) {
    const content = document.getElementById(`faq${id}`);
    const arrow = document.getElementById(`arrow${id}`);

    if (content.classList.contains("hidden")) {
        content.classList.remove("hidden");
        arrow.style.transform = "rotate(90deg)";
    } else {
        content.classList.add("hidden");
        arrow.style.transform = "rotate(0deg)";
    }
}

// Load FAQ on page load
document.addEventListener("DOMContentLoaded", () => {
    loadMarkdown("data/faq.md", "faq");
});
