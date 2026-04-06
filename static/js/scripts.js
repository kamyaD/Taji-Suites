let cart = {};
let total = 0;
let selectedCategory = "all";

function addToCart(id, name, price) {
    if (!cart[id]) {
        cart[id] = {item: name, rate: price, qty: 1};
    } else {
        cart[id].qty += 1;
    }
    renderCart();
}

function increaseQty(id) {
    cart[id].qty += 1;
    renderCart();
}

function decreaseQty(id) {
    cart[id].qty -= 1;
    if (cart[id].qty <= 0) delete cart[id];
    renderCart();
}

function renderCart() {
    let cartDiv = document.getElementById("cartItems");
    cartDiv.innerHTML = "";
    total = 0;
    for (let id in cart) {
        let item = cart[id];
        let subtotal = item.qty * item.rate;
        total += subtotal;
        cartDiv.innerHTML += `
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                <div>
                    <strong>${item.item}</strong><br>
                    <small>KES ${item.rate.toFixed(2)}</small>
                </div>
                <div class="d-flex align-items-center">
                    <button type="button" class="btn btn-sm btn-danger" onclick="decreaseQty('${id}')">-</button>
                    <span class="mx-2">${item.qty}</span>
                    <button type="button" class="btn btn-sm btn-success" onclick="increaseQty('${id}')">+</button>
                </div>
                <div>
                    <strong>KES ${subtotal.toFixed(2)}</strong>
                </div>
            </div>
            <input type="hidden" name="product_${id}" value="${item.qty}">
        `;
    }
    document.getElementById("total").innerText = total.toFixed(2);
}

// 🔹 Set category
function setCategory(category, event) {
    selectedCategory = category;
    document.querySelectorAll(".category-btn").forEach(btn => {
        btn.classList.remove("btn-dark");
        btn.classList.add("btn-outline-secondary");
    });
    event.target.classList.remove("btn-outline-secondary");
    event.target.classList.add("btn-dark");
    searchProducts();
}

// 🔹 Search + Category filter combined
function searchProducts() {
    let input = document.getElementById('productSearch').value.toLowerCase();
    let activeTab = document.querySelector('.tab-pane.active');
    if (!activeTab) return;
    let products = activeTab.querySelectorAll('.product-item');
    products.forEach(p => {
        let name = p.querySelector('h6').textContent.toLowerCase();
        let category = (p.dataset.category || "").toLowerCase();
        let matchCategory = (selectedCategory === "all" || category === selectedCategory);
        if ((name.includes(input) || category.includes(input)) && matchCategory) {
            p.style.display = "block";
        } else {
            p.style.display = "none";
        }
    });
}

