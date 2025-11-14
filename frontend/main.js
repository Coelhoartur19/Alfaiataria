document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector(".login-form");

    // ===== Simulação de login =====
    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();

            const email = loginForm.querySelector("input[type='email']").value;
            const password = loginForm.querySelector("input[type='password']").value;

            if (email && password) {
                localStorage.setItem("usuarioLogado", email);
                window.location.href = "dashboard.html";
            } else {
                alert("Preencha todos os campos!");
            }
        });
    }

    // ===== Mensagem de boas-vindas no dashboard =====
    const user = localStorage.getItem("usuarioLogado");
    const dashboard = document.querySelector(".content");

    if (dashboard && user) {
        const msg = document.createElement("p");
        msg.textContent = `👋 Bem-vindo, ${user.split("@")[0]}!`;
        msg.style.marginTop = "10px";
        msg.style.fontWeight = "500";
        msg.classList.add("fade-in");
        dashboard.prepend(msg);
    }

    // ===== Botão de sair =====
    const logoutLinks = document.querySelectorAll(".logout");
    logoutLinks.forEach((link) => {
        link.addEventListener("click", () => {
            localStorage.removeItem("usuarioLogado");
        });
    });

    // ===== Simulação dos CRUDs =====
    const forms = document.querySelectorAll(".crud-form");
    forms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            alert("Item adicionado! (Simulação)");
            form.reset();
        });
    });

    const deleteButtons = document.querySelectorAll(".btn.danger");
    deleteButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            alert("Item excluído! (Simulação)");
        });
    });
});
