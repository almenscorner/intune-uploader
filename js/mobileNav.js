document.addEventListener("DOMContentLoaded", function () {
    const mobileMenuButton = document.getElementById("mobileMenuButton");
    const mobileNav = document.getElementById("mobileNav");

    function toggleMenu() {
        mobileNav.classList.toggle("hidden");
        mobileMenuButton.classList.toggle("open");
    }

    mobileMenuButton.addEventListener("click", toggleMenu);

    document.querySelectorAll("#mobileNav a").forEach(link => {
        link.addEventListener("click", () => {
            mobileNav.classList.add("hidden");
            mobileMenuButton.classList.remove("open");
        });
    });
});