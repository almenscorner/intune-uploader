document.addEventListener("DOMContentLoaded", () => {
    const mobileMenuButton = document.getElementById("mobileMenuButton");
    const mobileNav = document.getElementById("mobileNav");
    const bars = mobileMenuButton.querySelectorAll(".block");

    // Ensure we have exactly 3 bars
    if (bars.length !== 3) {
        console.error("Error: Expected 3 bars (.block) inside #mobileMenuButton, but found", bars.length);
        return; // Stop script execution if the expected elements are missing
    }

    function toggleMenu() {
        mobileNav.classList.toggle("hidden");
        mobileMenuButton.classList.toggle("open");

        if (mobileMenuButton.classList.contains("open")) {
            bars[0].style.transform = "rotate(45deg) translateY(7px)";
            bars[1].style.opacity = "0"; // Hide middle bar
            bars[2].style.transform = "rotate(-45deg) translateY(-7px)";
        } else {
            bars[0].style.transform = "rotate(0) translateY(0)";
            bars[1].style.opacity = "1"; // Show middle bar
            bars[2].style.transform = "rotate(0) translateY(0)";
        }
    }

    // Toggle menu when clicking the button
    mobileMenuButton.addEventListener("click", toggleMenu);

    // Close menu when clicking a link inside mobileNav
    document.querySelectorAll("#mobileNav a").forEach(link => {
        link.addEventListener("click", () => {
            mobileNav.classList.add("hidden");
            mobileMenuButton.classList.remove("open");

            // Reset bars to default state when menu closes
            bars[0].style.transform = "rotate(0) translateY(0)";
            bars[1].style.opacity = "1"; // Show middle bar
            bars[2].style.transform = "rotate(0) translateY(0)";
        });
    });
});