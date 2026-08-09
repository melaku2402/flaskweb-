let cart = [];

//  DOM 
const addButtons = document.querySelectorAll('.add-btn');
const countLabel = document.getElementById('itemCount');
const totalLabel = document.getElementById('totalPrice');
const listContainer = document.getElementById('orderList');
const clearBtn = document.getElementById('clearOrderBtn');
const toast = document.getElementById('notification');
const clockDisplay = document.getElementById('clock');
const cartBtn = document.getElementById('cartIcon');
const badge = document.getElementById('cartCount');
const panel = document.getElementById('orderSummary');
const headerBar = document.querySelector('header');
const submitBtn = document.getElementById('submitOrderBtn');
const orderMessage = document.getElementById('orderMessage');

// 
addButtons.forEach(button => {
  button.onclick = function () {
    const itemName = this.getAttribute('data-name');
    const itemPrice = Number(this.getAttribute('data-price'));

    addItem(itemName, itemPrice);
    popToast();
  };
});

// Locate
const findCartItem = name => cart.find(item => item.name === name) || null;

function addItem(name, price) {
  const item = findCartItem(name);

  if (item) {
    item.qty++;
  } else {
    cart.push({ name, price, qty: 1 });
  }

  updateUI();
}

function increaseQty(name) {
  const item = findCartItem(name);
  if (item) {
    item.qty++;
  }
  updateUI();
}

function decreaseQty(name) {
  const item = findCartItem(name);
  if (!item) return;

  item.qty--;

  if (item.qty <= 0) {
    removeItem(name);
    return;
  }

  updateUI();
}

function removeItem(name) {
  cart = cart.filter(item => item.name !== name);
  updateUI();
}

// 
function updateUI() {
  listContainer.innerHTML = '';

  const itemsCount = cart.reduce((acc, entry) => acc + entry.qty, 0);
  const sumPrice = cart.reduce((acc, entry) => acc + entry.qty * entry.price, 0);

  cart.forEach(entry => {
    const row = document.createElement('li');
    row.className = 'order-item';
    row.innerHTML = `
      <div class="order-item-info">
        <span class="order-item-name">${entry.name}</span>
        <p>You have ${entry.qty} items at ${entry.price} birr each.</p>
      </div>
      <div class="order-item-actions">
        <button class="qty-btn" onclick="decreaseQty('${entry.name}')">decrease</button>
        <span class="qty-value">${entry.qty}</span>
        <button class="qty-btn" onclick="increaseQty('${entry.name}')">increase</button>
        <button class="remove-btn" onclick="removeItem('${entry.name}')">Remove</button>
      </div>
    `;

    listContainer.appendChild(row);
  });

  countLabel.textContent = itemsCount;
  totalLabel.textContent = sumPrice;
  badge.textContent = itemsCount;
}

clearBtn.onclick = () => {
  cart = [];
  updateUI();
};


function popToast() {
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 1500);
}

function startClock() {
  const now = new Date();
  clockDisplay.textContent = `${now.toLocaleDateString()} ${now.toLocaleTimeString()}`;
}

startClock();
setInterval(startClock, 1000);

cartBtn.onclick = () => {
  panel.classList.toggle('hidden');

  if (!panel.classList.contains('hidden')) {
    panel.scrollIntoView({ behavior: 'smooth' });
  }
};


window.onscroll = () => {
  if (window.scrollY > 80) {
    headerBar.classList.add('sticky');
    document.body.classList.add('header-fixed');
  } else {
    headerBar.classList.remove('sticky');
    document.body.classList.remove('header-fixed');
  }
};

// async/await 
submitBtn.onclick = async () => {
  if (cart.length === 0) {
    orderMessage.textContent = 'add something to your cart first';
    return;
  }

  const total = cart.reduce((acc, item) => acc + item.qty * item.price, 0);

  try {
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: cart, total })
    });

    const data = await res.json();

    if (data.error) {
      orderMessage.textContent = data.error;
    } else {
      orderMessage.textContent = 'order placed, thanks!';
      cart = [];
      updateUI();
    }
  } catch (err) {
    orderMessage.textContent = 'could not reach server';
    console.error(err);
  }
};
