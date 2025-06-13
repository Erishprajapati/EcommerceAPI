document.addEventListener("DOMContentLoaded", fetchProducts);

function fetchProducts() {
    fetch('http://127.0.0.1:8000/all_products')  // Adjust port if different
        .then(response => response.json())
        .then(data => {
            const main = document.querySelector(".main-content");
            main.innerHTML = "";  // Clear default welcome text

            if (data.length === 0) {
                main.innerHTML = "<p>No products found.</p>";
                return;
            }

            const productContainer = document.createElement("div");
            productContainer.className = "product-container";

            data.forEach(product => {
                const productCard = document.createElement("div");
                productCard.className = "product-card";

                productCard.innerHTML = `
                    <img src="${product.image_url || '/static/images/placeholder.jpg'}" alt="${product.name}" class="product-image">
                    <h3>${product.name}</h3>
                    <p>${product.description || 'No description available.'}</p>
                    <p><strong>Price:</strong> $${product.price || 'N/A'}</p>
                `;

                productContainer.appendChild(productCard);
            });

            main.appendChild(productContainer);
        })
        .catch(err => {
            console.error("Error fetching products:", err);
            document.querySelector(".main-content").innerHTML = "<p>Failed to load products.</p>";
        });
}
