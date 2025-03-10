document.querySelectorAll('a[href*="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (event) {
        // Prevent default only for in-page links
        if (this.getAttribute("href").includes("#")) {
            event.preventDefault();
            const targetId = this.getAttribute("href").split("#")[1];
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: "smooth" });
                window.history.pushState(null, null, `#${targetId}`); // Update URL

                // If inside mobile nav, close menu
                if (document.getElementById("mobileNav").contains(this)) {
                    document.getElementById("mobileNav").classList.add("hidden");
                    document.getElementById("mobileMenuButton").classList.remove("open");
                }
            }
        }
    });
});