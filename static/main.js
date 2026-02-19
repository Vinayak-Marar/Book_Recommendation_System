const searchInput = document.getElementById("searchInput");
const suggestionsBox = document.getElementById("suggestions");
const tagContainer = document.getElementById("tagContainer");
const selectedIsbnsInput = document.getElementById("selectedIsbns");

let selectedBooks = [];

// Focus input when clicking container
tagContainer.addEventListener("click", () => {
    searchInput.focus();
});

// Autocomplete
searchInput.addEventListener("input", function() {
    const query = this.value;

    if (query.length < 2) {
        suggestionsBox.innerHTML = "";
        return;
    }

    fetch(`/search?q=${query}`)
        .then(res => res.json())
        .then(data => {
            suggestionsBox.innerHTML = "";

            data.forEach(book => {
                const item = document.createElement("a");
                item.classList.add("list-group-item", "list-group-item-action");
                item.innerHTML = `
                    <strong>${book.Title}</strong><br>
                    <small>${book.Author}</small>
                `;

                item.addEventListener("click", function() {
                    addTag(book);
                    suggestionsBox.innerHTML = "";
                    searchInput.value = "";
                });

                suggestionsBox.appendChild(item);
            });
        });
});

// Add floating tag
function addTag(book) {

    // Avoid duplicates
    if (selectedBooks.some(b => b.ISBN === book.ISBN)) return;

    selectedBooks.push(book);
    updateHiddenInput();

    const tag = document.createElement("span");
    tag.classList.add(
        "badge",
        "bg-primary",
        "me-2",
        "mb-2",
        "d-flex",
        "align-items-center"
    );

    tag.style.padding = "8px 10px";
    tag.style.fontSize = "0.9rem";

    tag.innerHTML = `
        ${book.Title}
        <span style="margin-left:8px; cursor:pointer;">&times;</span>
    `;

    // Remove tag
    tag.querySelector("span").addEventListener("click", function() {
        tag.remove();
        selectedBooks = selectedBooks.filter(b => b.ISBN !== book.ISBN);
        updateHiddenInput();
    });

    tagContainer.insertBefore(tag, searchInput);
}

// Update hidden input
function updateHiddenInput() {
    const isbns = selectedBooks.map(b => b.ISBN);
    selectedIsbnsInput.value = isbns.join(",");
}