function toggleFAQ(id) {
    const faq = document.getElementById(`faq${id}`);
    const arrow = document.getElementById(`arrow${id}`);

    if (faq.classList.contains("hidden")) {
        faq.classList.remove("hidden");
        arrow.style.transform = "rotate(90deg)"; // Rotates arrow when expanded
    } else {
        faq.classList.add("hidden");
        arrow.style.transform = "rotate(0deg)"; // Resets arrow rotation
    }
}
