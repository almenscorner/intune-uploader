document.querySelectorAll('a[href^="/#"]').forEach(anchor => {
    anchor.addEventListener("click", function (event) {
        event.preventDefault();
        const targetId = this.getAttribute("href").split("#")[1];
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: "smooth" });
            window.history.pushState(null, null, `/#${targetId}`); // Update URL
        }
    });
});