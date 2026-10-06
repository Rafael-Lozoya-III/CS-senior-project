const searchInput = document.querySelector("#project-search");
const projectCards = document.querySelectorAll(".searchable-project");
const noResults = document.querySelector("#no-project-results");

searchInput.addEventListener("input", () => {
    const searchTerm = searchInput.value.toLowerCase().trim();
    let visibleProjects = 0;

    projectCards.forEach((card) => {
        const projectText = card.textContent.toLowerCase();
        const matches = projectText.includes(searchTerm);

        card.hidden = !matches;

        if (matches) {
            visibleProjects++;
        }
    });

    noResults.hidden = visibleProjects !== 0;
});