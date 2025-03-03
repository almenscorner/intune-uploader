const REPO_URL = "https://api.github.com/repos/almenscorner/intune-uploader";

async function fetchGitHubStats() {
    try {
        const response = await fetch(REPO_URL);

        if (!response.ok) throw new Error("GitHub API request failed");
        const data = await response.json();

        // Insert data into HTML
        document.getElementById("stars-count").textContent = data.stargazers_count.toLocaleString();
        document.getElementById("forks-count").textContent = data.forks.toLocaleString();
        document.getElementById("license").textContent = data.license.name;

    } catch (error) {
        console.error("Error fetching GitHub stats:", error);
    }
}

// Fetch data on page load
document.addEventListener("DOMContentLoaded", fetchGitHubStats);

const contributorsUrl = "https://api.github.com/repos/almenscorner/intune-uploader/contributors";

async function fetchContributors() {
    try {
        const response = await fetch(contributorsUrl);

        if (!response.ok) throw new Error("Failed to fetch contributors");

        const contributors = await response.json();
        const contributorsContainer = document.getElementById("contributors");

        contributorsContainer.innerHTML = ""; // Clear previous content

        contributors.slice(0, 10).forEach(contributor => {
            const avatar = document.createElement("a");
            avatar.href = contributor.html_url;
            avatar.target = "_blank";
            avatar.className = "w-7 h-7 rounded-full border-2 border-gray-700 hover:border-green-400 transition";
            avatar.innerHTML = `<img src="${contributor.avatar_url}" class="w-full h-full rounded-full">`;

            contributorsContainer.appendChild(avatar);
        });
    } catch (error) {
        console.error("Error fetching contributors:", error);
        document.getElementById("contributors").innerHTML = `<p class="text-red-400">Failed to load contributors.</p>`;
    }
}

// Load contributors when page loads
document.addEventListener("DOMContentLoaded", fetchContributors);
