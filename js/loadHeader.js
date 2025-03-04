async function loadHeader() {
    try {
        const response = await fetch("includes/header.html");
        if (!response.ok) throw new Error("Header file not found");

        document.getElementById("header-container").innerHTML = await response.text();

        // Attach mobile menu toggle function after loading
        const mobileMenuButton = document.getElementById("mobileMenuButton");
        const mobileNav = document.getElementById("mobileNav");

        if (mobileMenuButton && mobileNav) {
            mobileMenuButton.addEventListener("click", () => {
                mobileNav.classList.toggle("hidden");
            });
        }

        // ✅ Check if Quickstart & FAQ exist before adding smooth scrolling
        const quickstartLink = document.querySelector('a[href="#quickstart"]');
        const faqLink = document.querySelector('a[href="#faq"]');
        const quickstartSection = document.getElementById("quickstart");
        const faqSection = document.getElementById("faq-container");

        if (quickstartLink && quickstartSection) {
            quickstartLink.addEventListener("click", (e) => {
                e.preventDefault();
                quickstartSection.scrollIntoView({ behavior: "smooth" });
            });
        }

        if (faqLink && faqSection) {
            faqLink.addEventListener("click", (e) => {
                e.preventDefault();
                faqSection.scrollIntoView({ behavior: "smooth" });
            });
        }

    } catch (error) {
        console.error("Error loading header:", error);
    }
}

// Load header only if the div exists
document.addEventListener("DOMContentLoaded", function () {
    const currentPath = window.location.pathname.split("/").pop(); // Get current filename

    const navLinks = [
        { name: "Home", url: "index.html" },
        { name: "Quick Start", url: "index.html#quickstart" },
        { name: "FAQ", url: "index.html#faq-container" },
        { name: "Dependencies", url: "dependencies.html" },
        { name: "Join Slack", url: "https://macadmins.slack.com/archives/C05EDN7P337" }
    ];

    // Generate navigation dynamically
    const navHTML = navLinks.map(link => {
        const isActive = (link.url === currentPath || window.location.hash === link.url.split("#")[1]) 
            ? "text-green-300 font-semibold" 
            : "text-gray-400 hover:text-green-300";

        return `<a href="${link.url}" class="${isActive} block py-2 px-4 md:inline">${link.name}</a>`;
    }).join("");

    // Insert the header with a mobile toggle button
    document.getElementById("header-container").innerHTML = `
        <header class="w-full py-4 px-6 flex justify-between items-center border-b border-gray-700 bg-gray-900/90 backdrop-blur-md sticky top-0 z-50">
            <div class="flex items-center space-x-3">
                <h1 class="text-2xl font-extrabold gradient-text tracking-tight">Intune Uploader</h1>
            </div>
            <button id="mobile-nav-toggle" class="text-gray-400 md:hidden">
                <i class="fas fa-bars text-2xl"></i> <!-- Hamburger Icon -->
            </button>
            <nav id="mobile-nav" class="hidden md:flex flex-col md:flex-row absolute md:static top-16 left-0 w-full md:w-auto bg-gray-900 md:bg-transparent shadow-lg md:shadow-none rounded-md md:rounded-none">
                ${navHTML}
            </nav>
        </header>
    `;

    // Add event listener for mobile menu toggle
    document.getElementById("mobile-nav-toggle").addEventListener("click", function () {
        document.getElementById("mobile-nav").classList.toggle("hidden");
    });
});