function filterApps() {
    const searchTerm = document.getElementById("searchInput").value.toLowerCase();
    filteredApps = apps.filter(app => app.name.toLowerCase().includes(searchTerm));

    const appList = document.getElementById("appList");
    appList.classList.add("fade-out");

    setTimeout(() => {
        currentPage = 1;
        renderApps();

        appList.classList.remove("fade-out");
        appList.classList.add("fade-in");

        setTimeout(() => {
            appList.classList.remove("fade-in");
        }, 300);
    }, 200);
}
