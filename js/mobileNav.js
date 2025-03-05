document.addEventListener("DOMContentLoaded", function () {
    const mobileMenuButton = document.getElementById("mobileMenuButton");
    const mobileNav = document.getElementById("mobileNav");

    mobileMenuButton.addEventListener("click", () => {
        mobileNav.classList.toggle("hidden");
    });

    // Close mobile menu when a link is clicked
    document.querySelectorAll("#mobileNav a").forEach(link => {
        link.addEventListener("click", () => {
            mobileNav.classList.add("hidden");
        });
    });
});