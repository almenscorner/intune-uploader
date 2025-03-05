document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".nav-link");

    links.forEach(link => {
        if (link.href === window.location.href || window.location.pathname === link.getAttribute("href")) {
            link.classList.add("text-green-300", "font-semibold");
        } else {
            link.classList.add("text-gray-400", "hover:text-green-300");
        }
    });

    // Handle anchor navigation (e.g., index.html#faq-container)
    const hash = window.location.hash;
    if (hash) {
        const targetElement = document.querySelector(hash);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: "smooth" });
        }
    }
});