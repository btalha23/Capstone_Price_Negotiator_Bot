// Ensure the DOM content is loaded before accessing elements
document.addEventListener('DOMContentLoaded', () => {
    // Base URL for the backend API
    const apiUrl = 'http://localhost:5000/api/users';

    // References to HTML elements
    const productSection = document.getElementById('product-section');
    const productList = document.getElementById('product-list');
    const loginSection = document.getElementById('login-section');
    const signupSection = document.getElementById('signup-section');
    const historySection = document.getElementById('history-section');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const historyList = document.getElementById('history-list');

    // Checkout/Negotiate elements
    const cartSection = document.getElementById('cart-section');
    const checkoutSection = document.getElementById('checkout-section');
    const cartItemsDiv = document.getElementById('cart-items');
    const checkoutItemsDiv = document.getElementById('checkout-items');
    const checkoutButton = document.getElementById('checkout-button');
    const negotiateButton = document.getElementById('negotiate-button');
    const finalizeButton = document.getElementById('finalize-button');

    // Find the account-info element in the DOM
    const accountInfo = document.getElementById('account-info');

    // Variables to store the current user and their authentication token
    let currentUser = null;
    let authToken = null;
    let cartItems = [];

    // Handle adding items to cart
    function addToCart(product) {
        cartItems.push(product);
        updateCart();
    }

    // Handle checkout button click
    checkoutButton.addEventListener('click', () => {
        checkoutItemsDiv.innerHTML = '';
        cartItems.forEach((item) => {
            const itemDiv = document.createElement('div');
            itemDiv.textContent = `${item.name} - $${item.price}`;
            checkoutItemsDiv.appendChild(itemDiv);
        });
        cartSection.classList.add('hidden');
        checkoutSection.classList.remove('hidden');
    });

    // Handle negotiation process
    negotiateButton.addEventListener('click', () => {
        // Example negotiation logic
        const total = cartItems.reduce((sum, item) => sum + item.price, 0);
        const negotiatedTotal = total * 0.9; // Assume a 10% discount
        alert(`Negotiated Price: $${negotiatedTotal.toFixed(2)}`);
        finalizeButton.classList.remove('hidden');
    });

    // Handle finalize purchase button click
    finalizeButton.addEventListener('click', () => {
        alert('Purchase finalized!');
        // Clear cart and reset UI
        cartItems = [];
        updateCart();
        checkoutSection.classList.add('hidden');
        productSection.classList.remove('hidden');
    });

    // Dynamically Adding Products
    const products = [
        { id: 1, name: 'Product 1', price: 100 },
        { id: 2, name: 'Product 2', price: 200 },
        { id: 3, name: 'Product 3', price: 300 },
    ];

    // Instantiate our product items & interactions
    products.forEach((product) => {
        const productDiv = document.createElement('div');
        productDiv.textContent = `${product.name} - $${product.price}`;
        const addButton = document.createElement('button');
        addButton.textContent = 'Add to Cart';
        addButton.addEventListener('click', () => addToCart(product));
        productDiv.appendChild(addButton);
        productList.appendChild(productDiv);
    });

    // Make products visible
    productSection.classList.remove('hidden');

    // Update cart display
    function updateCart() {
        cartItemsDiv.innerHTML = '';
        cartItems.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.textContent = `${item.name} - $${item.price}`;
            cartItemsDiv.appendChild(itemDiv);
        });
        cartSection.classList.remove('hidden');
    }

    // Event listeners for navigation links to switch between different sections
    document.getElementById('home-link').addEventListener('click', () => {
        productSection.classList.remove('hidden');
        loginSection.classList.add('hidden');
        signupSection.classList.add('hidden');
        historySection.classList.add('hidden');
    });

    document.getElementById('login-link').addEventListener('click', () => {
        productSection.classList.add('hidden');
        loginSection.classList.remove('hidden');
        signupSection.classList.add('hidden');
        historySection.classList.add('hidden');
    });

    document.getElementById('signup-link').addEventListener('click', () => {
        productSection.classList.add('hidden');
        loginSection.classList.add('hidden');
        signupSection.classList.remove('hidden');
        historySection.classList.add('hidden');
    });

    document.getElementById('history-link').addEventListener('click', () => {
        if (currentUser) {
            productSection.classList.add('hidden');
            loginSection.classList.add('hidden');
            signupSection.classList.add('hidden');
            historySection.classList.remove('hidden');
            loadPurchaseHistory(); // Load the purchase history if the user is logged in
        } else {
            alert('Please login to view purchase history.');
        }
    });

    // Handle login form submission
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent the default form submission behavior
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            // Send a login request to the backend
            const response = await fetch(`${apiUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            if (response.ok) {
                authToken = data.token; // Store the received token
                currentUser = username; // Store the current user's username
                alert('Login successful');
                productSection.classList.remove('hidden');
                loginSection.classList.add('hidden');
                // Update navigation bar
                updateNavbar();
            } else {
                if (data.msg) {
                    alert(data.msg); // Display server error message
                } else {
                    alert('Server error');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Network error'); // Display network error message
        }
    });

    // Function to update the navigation bar based on authentication status
    function updateNavbar() {
        const loginNavItem = document.getElementById('login-nav-item');
        const signupNavItem = document.getElementById('signup-nav-item');

        if (currentUser) {
            // If user is logged in, replace the "Login" button with the account name
            loginNavItem.innerHTML = `<a href="#">${currentUser}</a>`;
            // Hide the "Sign-up" navigation item
            signupNavItem.style.display = 'none';
        }
    }

    // Handle sign-up form submission
    signupForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent the default form submission behavior
        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;

        try {
            // Send a registration request to the backend
            const response = await fetch(`${apiUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            if (response.ok) {
                alert('Sign-up successful');
                signupSection.classList.add('hidden');
                loginSection.classList.remove('hidden');
            } else {
                alert(data.msg);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Server error');
        }
    });

    // Event listener for negotiation buttons
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('negotiate-btn')) {
            const productId = event.target.getAttribute('data-id');
            alert(`Starting chat for product ${productId}`);
        }
    });

    // Event listener for add-to-cart buttons
    document.addEventListener('click', async (event) => {
        if (event.target.classList.contains('add-to-cart-btn')) {
            const productId = event.target.getAttribute('data-id');
            const product = products.find(p => p.id == productId);
            if (currentUser && authToken) {
                try {
                    // Send a request to add the product to the cart
                    const response = await fetch(`${apiUrl}/add-to-cart`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${authToken}`
                        },
                        body: JSON.stringify({ product })
                    });
                    const data = await response.json();
                    if (response.ok) {
                        alert('Product added to cart');
                    } else {
                        alert(data.msg);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Server error');
                }
            } else {
                alert('Please login to add products to the cart.');
            }
        }
    });

    // Function to load purchase history (to be implemented)
    function loadPurchaseHistory() {
        historyList.innerHTML = 'Loading purchase history...';
    }

    // Load products on page load
    loadProducts();
});
