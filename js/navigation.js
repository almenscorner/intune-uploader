document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".nav-link");

    function updateActiveLink() {
        const basePath = "/intune-uploader";
        const currentPath = window.location.pathname.replace(/\/$/, "");
    
        links.forEach(link => {
            const linkPath = new URL(link.href).pathname.replace(/\/$/, "");
    
            // Ignore Quick Start and FAQ links
            if (link.href.includes("#quickstart") || link.href.includes("#faq-container")) {
                return;
            }
    
            // Reset classes before setting active state
            link.classList.remove("text-green-300", "font-semibold");
    
            // Handle the Home page correctly
            if (currentPath === basePath) {
                if (linkPath === basePath) {
                    link.classList.add("text-green-300", "font-semibold");
                }
            } 
            // Check for exact path match
            else if (linkPath === currentPath) {
                link.classList.add("text-green-300", "font-semibold");
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