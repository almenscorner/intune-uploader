document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".nav-link");

    function updateActiveLink() {
        const currentPath = window.location.pathname;

        links.forEach(link => {
            const linkPath = new URL(link.href).pathname;

            // Ignore Quick Start and FAQ
            if (link.href.includes("#quickstart") || link.href.includes("#faq-container")) {
                return;
            }

            // Ensure only the correct link is active
            if (currentPath === "/" || currentPath.endsWith("intune-uploader")) {
                if (linkPath === "/" || linkPath.endsWith("intune-uploader")) {
                    link.classList.add("text-green-300", "font-semibold");
                } else {
                    link.classList.remove("text-green-300", "font-semibold");
                }
            } else if (linkPath === currentPath) {
                link.classList.add("text-green-300", "font-semibold");
            } else {
                link.classList.remove("text-green-300", "font-semibold");
            }
        });
    }

    // Run on page load
    updateActiveLink();

    // Handle smooth scrolling for section links
    document.querySelectorAll('a[href*="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (event) {
            const targetId = this.getAttribute("href").split("#")[1];
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                event.preventDefault();
                targetElement.scrollIntoView({ behavior: "smooth" });

                // Update URL without reloading
                window.history.pushState(null, null, `#${targetId}`);
            }
        });
    });

    // Update active link when navigating
    window.addEventListener("popstate", updateActiveLink);
});