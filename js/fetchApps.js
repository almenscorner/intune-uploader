const jsonUrl = "https://raw.githubusercontent.com/autopkg/almenscorner-recipes/refs/heads/main/recipes.json";

let apps = [];
let filteredApps = [];
let currentPage = 1;
const appsPerPage = 12;

// Base path for local icons
const iconBaseUrl = "assets/icons/";

async function fetchApps() {
    try {
        const response = await fetch(jsonUrl);
        if (!response.ok) throw new Error("Failed to load app data.");

        apps = await response.json();
        filteredApps = [...apps];

        document.getElementById("searchInput").placeholder = `🔍 Search among ${apps.length} supported recipes...`;

        renderApps(); // Ensure this is running
    } catch (error) {
        console.error("Error fetching app list:", error);
        document.getElementById("appList").innerHTML = `<p class="text-red-400">Failed to load app list.</p>`;
    }
}

function renderApps() {
    const appList = document.getElementById("appList");
    if (!appList) {
        console.error("❌ Error: #appList not found in the DOM");
        return;
    }

    appList.innerHTML = ""; // Clear existing content

    const startIndex = (currentPage - 1) * appsPerPage;
    const endIndex = startIndex + appsPerPage;
    const paginatedApps = filteredApps.slice(startIndex, endIndex);

    paginatedApps.forEach(app => {
        const formattedName = app.name.replace(/\s+/g, "_");
        const iconUrl = `data/icons/${formattedName}.png`;

        const appElement = document.createElement("div");
        appElement.className = "app-item shadow-md flex flex-col items-center p-4 transition hover:bg-gray-700 rounded-lg cursor-pointer";
        appElement.onclick = () => window.open(app.recipe_url, "_blank");

        const nameElement = document.createElement("span");
        nameElement.className = "text-white font-medium mt-2";
        nameElement.textContent = app.name;

        const imgElement = document.createElement("img");
        imgElement.src = iconUrl;
        imgElement.alt = `${app.name} icon`;
        imgElement.className = "w-12 h-12 mb-2 hidden";

        fetch(iconUrl, { method: "HEAD" })
            .then(response => {
                if (response.ok) {
                    imgElement.classList.remove("hidden");
                } else {
                    console.warn(`⚠️ No icon found for ${app.name}, skipping.`);
                }
            })
            .catch(() => {
                console.warn(`⚠️ Error checking ${iconUrl}, skipping icon.`);
            });

        appElement.appendChild(imgElement);
        appElement.appendChild(nameElement);

        appList.appendChild(appElement);
    });

    updatePagination();
}

function updatePagination() {
    const pageInfo = document.getElementById("pageInfo");
    const prevButton = document.getElementById("prevButton");
    const nextButton = document.getElementById("nextButton");

    pageInfo.textContent = `Page ${currentPage} of ${Math.ceil(filteredApps.length / appsPerPage)}`;
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = currentPage >= Math.ceil(filteredApps.length / appsPerPage);
}

function nextPage() {
    if (currentPage * appsPerPage < filteredApps.length) {
        animatePageChange(() => {
            currentPage++;
            renderApps();
        });
    }
}

function prevPage() {
    if (currentPage > 1) {
        animatePageChange(() => {
            currentPage--;
            renderApps();
        });
    }
}

function filterApps() {
    const searchTerm = document.getElementById("searchInput").value.toLowerCase();
    filteredApps = apps.filter(app => app.name.toLowerCase().includes(searchTerm));
    currentPage = 1;
    renderApps();
}

function animatePageChange(callback) {
    const appList = document.getElementById("appList");
    appList.classList.add("fade-out");

    setTimeout(() => {
        callback();
        appList.classList.remove("fade-out");
        appList.classList.add("fade-in");

        setTimeout(() => {
            appList.classList.remove("fade-in");
        }, 300);
    }, 200);
}

document.addEventListener("DOMContentLoaded", fetchApps);
