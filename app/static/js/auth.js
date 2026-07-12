const errorEl = document.getElementById("error");

function showError(msg) {
    errorEl.textContent = msg;
    errorEl.classList.remove("hidden");
}

async function submitAuth(url, payload) {
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (res.ok) {
        window.location = "/";
        return;
    }
    let detail = "Something went wrong";
    try {
        detail = (await res.json()).detail || detail;
    } catch (_) { /* keep default */ }
    showError(detail);
}

const loginForm = document.getElementById("login-form");
if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        submitAuth("/api/auth/login", {
            account: document.getElementById("account").value.trim(),
            password: document.getElementById("password").value,
        });
    });
}

const registerForm = document.getElementById("register-form");
if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
        e.preventDefault();
        submitAuth("/api/auth/register", {
            name: document.getElementById("name").value.trim(),
            account: document.getElementById("account").value.trim(),
            password: document.getElementById("password").value,
        });
    });
}
