const DEPENDENCIES_URL = "https://raw.githubusercontent.com/autopkg/almenscorner-recipes/refs/heads/main/dependencies.json";
    
async function fetchDependencies() {
    try {
        const response = await fetch(DEPENDENCIES_URL);
        if (!response.ok) throw new Error("Failed to load dependencies.");
        const dependencies = await response.json();

        renderDependencies(dependencies);
    } catch (error) {
        console.error("Error fetching dependencies:", error);
        document.getElementById("dependencies").innerHTML = `<p class="text-red-400 text-center mt-4">Failed to load dependencies.</p>`;
    }
}

function renderDependencies(dependencies) {
    const container = document.getElementById("dependencies");
    container.innerHTML = `
        <div class="max-w-5xl mx-auto mt-10 p-6 bg-gray-800 rounded-lg shadow-lg">
            <h2 class="text-2xl font-bold gradient-text mb-4">📦 Dependency Repositories</h2>
            <p class="mb-5">Most of the recipes in almenscorner-recipes have a dependency on a parent recipe for downloading the application. To add a dependency repository, click the copy button next to it and run the command in the terminal.</p>
            <input type="text" id="searchBox" placeholder="🔍 Search repositories..." class="w-full mb-4 p-2 border border-gray-600 rounded bg-gray-900 text-white focus:ring-1 focus:ring-green-400">
            <div class="max-h-[50rem] overflow-y-auto rounded-md p-2 scrollable-list"> <!-- Scrollable List -->
                <ul id="repoList" class="space-y-2"></ul>
            </div>
        </div>
    `;

    const searchBox = document.getElementById("searchBox");
    searchBox.addEventListener("keyup", () => filterDependencies(dependencies));

    renderDependencyList(dependencies);
}

function renderDependencyList(dependencies) {
    const listContainer = document.getElementById("repoList");
    listContainer.innerHTML = dependencies.map(dep => `
        <li class="p-3 bg-gray-700 rounded-md hover:bg-gray-600 flex justify-between items-center">
            <a href="${dep.recipe_url}" target="_blank" class="text-green-300 hover:underline flex-1 truncate">
                <i class="fab fa-github"></i> ${new URL(dep.recipe_url).pathname.replace('/autopkg/', '')}
            </a>
            <button data-command="${dep.repo_add_command}" onclick="copyCommand(this)" 
                class="copy-button text-gray-400 hover:text-green-300">
                <i class="fas fa-copy"></i>
            </button>
        </li>
    `).join('');
}

function filterDependencies(dependencies) {
    const searchTerm = document.getElementById("searchBox").value.toLowerCase();
    const filteredDeps = dependencies.filter(dep => dep.recipe_url.toLowerCase().includes(searchTerm));
    renderDependencyList(filteredDeps);
}

document.addEventListener("DOMContentLoaded", fetchDependencies);