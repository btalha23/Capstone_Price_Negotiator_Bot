document.addEventListener('DOMContentLoaded', () => {
    // Base URL for the backend API
    const apiUrl = 'http://localhost:5000/api/users';

    // Sample product data
    const products = [
        { id: 1, name: 'Product 1', price: 100 },
        { id: 2, name: 'Product 2', price: 200 },
        { id: 3, name: 'Product 3', price: 300 },
    ];

    // References to HTML elements
    const productSection = document.getElementById('product-section');
    const productList = document.getElementById('product-list');
    const chatbotSection = document.getElementById('chatbot-section');
    const loginSection = document.getElementById('login-section');
    const signupSection = document.getElementById('signup-section');
    const historySection = document.getElementById('history-section');
    const chatContent = document.getElementById('chat-content');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const historyList = document.getElementById('history-list');

    // Find the account-info element in the DOM
    const accountInfo = document.getElementById('account-info');

    // Variables to store the current user and their authentication token
    let currentUser = null;
    let authToken = null;

    // Function to load products into the product list
    function loadProducts() {
        productList.innerHTML = ''; // Clear existing products
        products.forEach(product => {
            // Create a new product item element
            const productItem = document.createElement('div');
            productItem.classList.add('product-item');
            productItem.innerHTML = `
                <h3>${product.name}</h3>
                <p>Price: $${product.price}</p>
                <button class="negotiate-btn" data-id="${product.id}">Negotiate</button>
                <button class="add-to-cart-btn" data-id="${product.id}">Add to Cart</button>
            `;
            productList.appendChild(productItem);
        });
    }

    // Event listeners for navigation links to switch between different sections
    document.getElementById('home-link').addEventListener('click', () => {
        productSection.classList.remove('hidden');
        chatbotSection.classList.add('hidden');
        loginSection.classList.add('hidden');
        signupSection.classList.add('hidden');
        historySection.classList.add('hidden');
    });

    document.getElementById('login-link').addEventListener('click', () => {
        productSection.classList.add('hidden');
        chatbotSection.classList.add('hidden');
        loginSection.classList.remove('hidden');
        signupSection.classList.add('hidden');
        historySection.classList.add('hidden');
    });

    document.getElementById('signup-link').addEventListener('click', () => {
        productSection.classList.add('hidden');
        chatbotSection.classList.add('hidden');
        loginSection.classList.add('hidden');
        signupSection.classList.remove('hidden');
        historySection.classList.add('hidden');
    });

    document.getElementById('history-link').addEventListener('click', () => {
        if (currentUser) {
            productSection.classList.add('hidden');
            chatbotSection.classList.add('hidden');
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
            chatbotSection.classList.remove('hidden');
            productSection.classList.add('hidden');
            startChat(productId); // Start a chat for price negotiation
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

    // Function to start a chat for price negotiation (to be implemented)
    function startChat(productId) {
        chatContent.innerHTML = `Starting chat for product ${productId}`;
    }

    // Function to load purchase history (to be implemented)
    function loadPurchaseHistory() {
        historyList.innerHTML = 'Loading purchase history...';
    }

    // Load products on page load
    loadProducts();
});
