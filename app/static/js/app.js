const app = document.getElementById('app');

function renderLogin() {
  app.innerHTML = `
    <div class="space-y-4">
      <h2 class="text-xl font-bold">Login</h2>
      <input id="email" type="email" placeholder="Email" class="border p-2 w-full" />
      <input id="password" type="password" placeholder="Password" class="border p-2 w-full" />
      <button id="loginBtn" class="bg-blue-500 text-white px-4 py-2 rounded">Login</button>
    </div>`;
  document.getElementById('loginBtn').addEventListener('click', login);
}

async function login() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const resp = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, password})
  });
  if (resp.ok) {
    const data = await resp.json();
    localStorage.setItem('token', data.token);
    renderDashboard();
  } else {
    alert('Login failed');
  }
}

async function renderDashboard() {
  const token = localStorage.getItem('token');
  const resp = await fetch('/health', {
    headers: {'Authorization': 'Bearer ' + token}
  });
  const status = resp.ok ? (await resp.json()).status : 'error';
  app.innerHTML = `<h2 class="text-xl font-bold">Dashboard</h2><p>Health: ${status}</p>`;
}

if (localStorage.getItem('token')) {
  renderDashboard();
} else {
  renderLogin();
}
