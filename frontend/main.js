// frontend/main.js
const API_URL = "http://127.0.0.1:8000/api";

/* ============================================================
   FUNÇÃO AUXILIAR DE FETCH
   ============================================================ */
async function apiRequest(url, options = {}) {
    try {
        const resposta = await fetch(url, {
            headers: { "Content-Type": "application/json", ...(options.headers || {}) },
            ...options
        });

        const data = await resposta.json().catch(() => null);

        if (!resposta.ok) {
            throw new Error(data?.detail || "Erro na requisição.");
        }

        return data;
    } catch (erro) {
        console.error("API ERROR:", erro);
        alert(erro.message || "Erro inesperado.");
        return null;
    }
}

/* ============================================================
   LISTAR PRODUTOS
   ============================================================ */
async function carregarProdutos() {
    const tabela = document.querySelector("#lista-produtos tbody");
    if (!tabela) return;

    const produtos = await apiRequest(`${API_URL}/produtos`);
    if (!produtos) return;

    tabela.innerHTML = "";

    if (!Array.isArray(produtos) || produtos.length === 0) {
        tabela.innerHTML = "<tr><td colspan='4'>Nenhum produto encontrado.</td></tr>";
        return;
    }

    const linhas = produtos.map(prod => `
        <tr>
            <td>${prod.id}</td>
            <td>${prod.nome}</td>
            <td>${prod.categoria}</td>
            <td>${prod.preco?.toFixed?.(2) ?? "0.00"}</td>
        </tr>
    `).join("");

    tabela.innerHTML = linhas;
}

/* ============================================================
   CADASTRAR PRODUTO
   ============================================================ */
async function cadastrarProduto(event) {
    event.preventDefault();

    const nome = document.querySelector("#nome-produto").value.trim();
    const categoria = document.querySelector("#categoria-produto").value.trim();
    const preco = parseFloat(document.querySelector("#preco-produto").value);

    if (!nome || !categoria || isNaN(preco)) {
        alert("Preencha todos os campos corretamente.");
        return;
    }

    const data = await apiRequest(`${API_URL}/produtos`, {
        method: "POST",
        body: JSON.stringify({ nome, categoria, preco })
    });

    if (!data) return;

    alert("Produto cadastrado com sucesso!");
    event.target.reset();
    carregarProdutos();
}

/* ============================================================
   LISTAR USUÁRIOS
   ============================================================ */
async function carregarUsuarios() {
    const tabela = document.querySelector("#tabela-usuarios");
    if (!tabela) return;

    const usuarios = await apiRequest(`${API_URL}/usuarios`);
    if (!usuarios) return;

    tabela.innerHTML = "";

    if (!Array.isArray(usuarios) || usuarios.length === 0) {
        tabela.innerHTML = "<tr><td colspan='4'>Nenhum usuário encontrado.</td></tr>";
        return;
    }

    usuarios.forEach(usuario => {
        const linha = document.createElement("tr");
        linha.innerHTML = `
            <td>${usuario.nome}</td>
            <td>${usuario.email}</td>
            <td>${usuario.grupo_id}</td>
            <td>
                <button class="btn small danger" data-id="${usuario.id}">Excluir</button>
            </td>
        `;
        tabela.appendChild(linha);
    });
}

/* ============================================================
   CADASTRAR USUÁRIO
   ============================================================ */
async function cadastrarUsuario(event) {
    event.preventDefault();

    const nome = document.getElementById("nome").value.trim();
    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value.trim();
    const grupo_id = parseInt(document.getElementById("grupo").value, 10);

    if (!nome || !email || !senha || isNaN(grupo_id)) {
        alert("Preencha todos os campos corretamente.");
        return;
    }

    const data = await apiRequest(`${API_URL}/usuarios`, {
        method: "POST",
        body: JSON.stringify({ nome, email, senha, grupo_id })
    });

    if (!data) return;

    alert(data.message || "Usuário cadastrado!");
    document.getElementById("formUsuario").reset();
    carregarUsuarios();
}

/* ============================================================
   EXCLUIR USUÁRIO
   ============================================================ */
async function excluirUsuarioPorId(id) {
    const data = await apiRequest(`${API_URL}/usuarios/${id}`, {
        method: "DELETE"
    });

    if (!data) return;

    alert(data.message || "Usuário excluído.");
    carregarUsuarios();
}

/* ============================================================
   INICIALIZAÇÃO
   ============================================================ */
document.addEventListener("DOMContentLoaded", () => {

    if (document.querySelector("#lista-produtos")) carregarProdutos();
    if (document.querySelector("#tabela-usuarios")) carregarUsuarios();

    const formProduto = document.querySelector("#form-produto");
    if (formProduto) formProduto.addEventListener("submit", cadastrarProduto);

    const formUsuario = document.getElementById("formUsuario");
    if (formUsuario) formUsuario.addEventListener("submit", cadastrarUsuario);

    const tabela = document.getElementById("tabela-usuarios");
    if (tabela) {
        tabela.addEventListener("click", (e) => {
            if (e.target.classList.contains("danger")) {
                const id = e.target.dataset.id;
                if (confirm("Confirma exclusão do usuário?")) {
                    excluirUsuarioPorId(id);
                }
            }
        });
    }

    document.querySelectorAll(".logout").forEach(link => {
        link.addEventListener("click", () => {
            localStorage.removeItem("usuarioLogado");
            window.location.href = "index.html";
        });
    });
});
