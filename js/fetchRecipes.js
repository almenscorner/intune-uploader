const jsonUrl = "https://raw.githubusercontent.com/autopkg/almenscorner-recipes/refs/heads/main/recipes.json";

let apps = [];
let filteredApps = [];
let currentPage = 1;
const appsPerPage = 12;

// Base path for local icons
const iconBaseUrl = "https://almenscorner.github.io/intune-uploader/assets/icons/";

async function fetchRecipes() {
    try {
        const response = await fetch(jsonUrl);
        if (!response.ok) throw new Error("Failed to load app data.");

        apps = await response.json();
        filteredApps = [...apps];

        renderApps(); // Ensure this is running
        recipeCountUp(filteredApps.length);
    } catch (error) {
        console.error("Error fetching app list:", error);
        document.getElementById("appList").innerHTML = `<p class="text-red-400">Failed to load app list.</p>`;
    }
}

function renderApps() {
    const appList = document.getElementById("appList");
    appList.innerHTML = ""; // Clear previous results

    const startIndex = (currentPage - 1) * appsPerPage;
    const endIndex = startIndex + appsPerPage;
    const paginatedApps = filteredApps.slice(startIndex, endIndex);

    paginatedApps.forEach(app => {
        const formattedName = app.name.toLowerCase().replace(/\s+/g, "_") + ".png";
        const iconUrl = `${iconBaseUrl}${formattedName}`;

        // Create card container
        const appElement = document.createElement("div");
        appElement.className = "app-item relative bg-gray-800 p-4 rounded-lg shadow-md cursor-pointer transition-transform hover:scale-105";

        // App title
        const titleElement = document.createElement("p");
        titleElement.className = "text-white font-semibold text-center";
        titleElement.textContent = app.name;

        // Open URL button
        const openUrlButton = document.createElement("button");
        openUrlButton.className = "absolute top-2 right-2 text-gray-600 hover:text-gray-300 transition duration-200";
        openUrlButton.innerHTML = '<i class="fas fa-external-link-alt"></i>'; // FontAwesome icon
        openUrlButton.onclick = (event) => {
            event.stopPropagation(); // Prevent modal from opening
            window.open(app.recipe_url, "_blank");
        };

        // Check if the icon exists before appending it
        fetch(iconUrl, { method: "HEAD" })
            .then(response => {
                if (response.ok) {
                    const imgElement = document.createElement("img");
                    imgElement.src = iconUrl;
                    imgElement.alt = `${app.name} icon`;
                    imgElement.className = "w-12 h-12 mb-2 app-icon";
                    appElement.prepend(imgElement);
                }
            })
            .catch(() => {
                console.warn(`⚠️ No icon found for ${app.name}`);
            });

        // Append elements
        appElement.appendChild(titleElement);
        appElement.appendChild(openUrlButton);

        // Click to open popup/modal
        appElement.addEventListener("click", () => openAppPopup(app));

        appList.appendChild(appElement);
    });

    updatePagination();
}

function openAppPopup(app) {
    const modal = document.getElementById("appModal");
    const modalTitle = document.getElementById("modalTitle");
    const modalDescription = document.getElementById("modalDescription");
    const modalImage = document.getElementById("modalImage");
    const modalCommand = document.getElementById("modalCommand");

    modalTitle.textContent = app.name;
    modalDescription.textContent = app.description || "No description available.";

    // Construct the icon URL
    const formattedName = app.name.toLowerCase().replace(/\s+/g, "_") + ".png";
    const iconUrl = `${iconBaseUrl}${formattedName}`;

    // Check if image exists before setting it
    fetch(iconUrl, { method: "HEAD" })
        .then(response => {
            if (response.ok) {
                modalImage.src = iconUrl;
                modalImage.classList.remove("hidden"); // Show image if it exists
            } else {
                modalImage.classList.add("hidden"); // Hide image if it doesn't exist
            }
        })
        .catch(() => {
            modalImage.classList.add("hidden"); // Hide image on error
        });

    // Set the AutoPkg command for the selected app
    const recipe_name = app.recipe_url.split("/").pop();
    modalCommand.innerHTML = `
        <div class="command-block">
            <span class="command-symbol">$</span>
            <span class="command-text">autopkg make-override</span>
            <span class="command-highlight text-yellow-500">${recipe_name}</span>
            <button class="copy-button group" data-command="autopkg make-override ${recipe_name}" onclick="copyCommand(this)">
                <i class="fa-solid fa-copy h-5 w-5 text-gray-500 group-hover:text-white transition"></i>
            </button>
        </div>
    `;

    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden"); // Prevent background scrolling

    // Close modal when clicking outside content
    modal.addEventListener("click", (event) => {
        if (event.target === modal) closeModal();
    });

    // Listen for Escape key
    document.addEventListener("keydown", handleEscapeKey);
}

function closeModal() {
    const modal = document.getElementById("appModal");
    modal.classList.add("hidden");
    document.body.classList.remove("overflow-hidden"); // Restore scrolling

    // Remove event listener to prevent multiple bindings
    document.removeEventListener("keydown", handleEscapeKey);
}

// Handle Escape key press
function handleEscapeKey(event) {
    if (event.key === "Escape") {
        closeModal();
    }
}

// Attach close event listener
document.getElementById("closeModal").addEventListener("click", closeModal);

// Handle Escape key press
function handleEscapeKey(event) {
    if (event.key === "Escape") closeModal();
}

// Close modal
document.getElementById("closeModal").addEventListener("click", () => {
    document.getElementById("appModal").classList.add("hidden");
});

function updatePagination() {
    const pageInfo = document.getElementById("pageInfo");
    const prevButton = document.getElementById("prevButton");
    const nextButton = document.getElementById("nextButton");
    const firstPageButton = document.getElementById("startButton")
    const lastPageButton = document.getElementById("endButton")

    const totalPages = Math.ceil(filteredApps.length / appsPerPage)

    pageInfo.textContent = `Page ${currentPage} of ${Math.ceil(filteredApps.length / appsPerPage)}`;

    if (currentPage === 1) {
        prevButton.disabled = true;
        prevButton.classList.add("opacity-50", "pointer-events-none");
    
        firstPageButton.disabled = true;
        firstPageButton.classList.add("opacity-50", "pointer-events-none");
    } else {
        prevButton.disabled = false;
        prevButton.classList.remove("opacity-50", "pointer-events-none");
    
        firstPageButton.disabled = false;
        firstPageButton.classList.remove("opacity-50", "pointer-events-none");
    }
    
    if (currentPage >= totalPages) {
        nextButton.disabled = true;
        nextButton.classList.add("opacity-50", "pointer-events-none");
    
        lastPageButton.disabled = true;
        lastPageButton.classList.add("opacity-50", "pointer-events-none");
    } else {
        nextButton.disabled = false;
        nextButton.classList.remove("opacity-50", "pointer-events-none");
    
        lastPageButton.disabled = false;
        lastPageButton.classList.remove("opacity-50", "pointer-events-none");
    }
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

function firstPage() {
    if (currentPage > 1) {
        animatePageChange(() => {
            currentPage = 1;
            renderApps();
        });
    }
}

function lastPage() {
    if (currentPage < Math.ceil(filteredApps.length / appsPerPage)) {
        animatePageChange(() => {
            currentPage = Math.ceil(filteredApps.length / appsPerPage);
            renderApps();
        });
    }
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

let searchTimeout;

function filterApps() {
    clearTimeout(searchTimeout); // Reset timeout if user keeps typing

    searchTimeout = setTimeout(() => {
        const searchInput = document.getElementById("searchInput").value.toLowerCase().trim();
        const searchTerms = searchInput.split(/[ ,]+/).filter(term => term.length > 0);
        const appList = document.getElementById("appList");

        // Apply smooth exit animation
        appList.classList.add("opacity-50", "scale-95", "blur-sm", "transition-all", "duration-300");

        setTimeout(() => {
            if (searchTerms.length === 0) {
                filteredApps = [...apps];
            } else {
                filteredApps = apps.filter(app =>
                    searchTerms.some(term => app.name.toLowerCase().includes(term))
                );
            }

            currentPage = 1;
            renderApps();

            appList.classList.remove("opacity-50", "scale-95", "blur-sm");
            appList.classList.add("opacity-100", "scale-100");
        }, 200);
    }, 300);
}

function recipeCountUp(recipeCount) {
    const recipeCounter = new countUp.CountUp("recipeCounter", recipeCount, {
        duration: 2,
        separator: ",",
    });

    if (!recipeCounter.error) {
        recipeCounter.start();
    } else {
        console.error(recipeCounter.error);
    }
}

window.recipeCountUp = recipeCountUp;

document.addEventListener("DOMContentLoaded", fetchRecipes);