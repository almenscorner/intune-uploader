document.addEventListener("DOMContentLoaded", () => {
    const mobileMenuButton = document.getElementById("mobileMenuButton");
    const bars = mobileMenuButton.querySelectorAll(".block");

    mobileMenuButton.addEventListener("click", () => {
        // Toggle active state
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
    });
});