const items = Array.from({ length: 100 }, (_, i) => `Item ${i + 1}`); // 100 items
const itemsPerPage = 10; // Number of items per page
let currentPage = 1; // Current page

// Function to display items
function displayItems(page) {
    const start = (page - 1) * itemsPerPage; // Calculate start index
    const end = start + itemsPerPage; // Calculate end index
    const paginatedItems = items.slice(start, end); // Get current page items

    const itemContainer = document.getElementById('itemContainer');
    itemContainer.innerHTML = ''; // Clear previous items
    paginatedItems.forEach(item => {
        const div = document.createElement('div');
        div.classList.add('item');
        div.textContent = item;
        itemContainer.appendChild(div);
    });
}

// Function to create pagination
function setupPagination() {
    const pageCount = Math.ceil(items.length / itemsPerPage); // Total number of pages
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = ''; // Clear previous pagination

    for (let i = 1; i <= pageCount; i++) {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.textContent = i;
        a.href = '#';
        a.className = i === currentPage ? 'active' : ''; // Highlight current page
        a.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent link default behavior
            currentPage = i; // Set current page
            displayItems(currentPage); // Display items for the current page
            setupPagination(); // Update pagination
        });
        li.appendChild(a);
        pagination.appendChild(li);
    }
}

// Initial display
displayItems(currentPage);
setupPagination();