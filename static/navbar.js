function isLoggedIn() {
    return localStorage.getItem('loggedIn') === 'true';
}

function renderNavbar() {
    const navbar = document.getElementById('navbar');
    navbar.innerHTML = '';

    if (isLoggedIn()) {
        navbar.innerHTML = `
            <li><a href="/static/index.html">Home</a></li>
            <li><a href="/static/products.html">Products</a></li>
            <li><a href="/static/add_product.html">Add Product</a></li>
            <li><a href="#" id="logout-link">Logout</a></li>
        `;
        document.getElementById('logout-link').addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm("Are you sure you want to logout?")) {
                localStorage.removeItem('loggedIn');
                localStorage.removeItem('token');
                alert("Logout successful!");
                window.location.href = '/static/login.html';
            }
        });
    } else {
        navbar.innerHTML = `
            <li><a href="/static/index.html">Home</a></li>
            <li><a href="/static/products.html">Products</a></li>
            <li><a href="/static/login.html">Login</a></li>
            <li><a href="/static/register.html">Register</a></li>
        `;
    }
}

document.addEventListener('DOMContentLoaded', renderNavbar);
