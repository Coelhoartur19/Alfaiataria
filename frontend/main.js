const API_URL = "http://127.0.0.1:8000/api";


// ============================================================
// HELPER CENTRAL DE REQUISIÇÕES
// ============================================================
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: { "Content-Type": "application/json", ...(options.headers || {}) },
            ...options
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(data?.detail || data?.message || "Erro na requisição.");
        }

        return data;
    } catch (error) {
        console.error("API ERROR:", error);
        alert(error.message || "Erro inesperado.");
        return null;
    }
}


// ============================================================
// SESSÃO / PERMISSÕES
// ============================================================
function getCurrentUser() {
    try {
        return JSON.parse(localStorage.getItem("usuario") || "null");
    } catch {
        return null;
    }
}

const isAdmin = (u) => u && u.grupo_id === 1;
const isSeller = (u) => u && u.grupo_id === 2;
const isClient = (u) => u && u.grupo_id === 3;


// ============================================================
// PRODUTOS
// ============================================================

async function carregarProdutos() {
    let tbody = document.querySelector("#lista-produtos");

    if (tbody?.tagName.toLowerCase() === "table")
        tbody = tbody.querySelector("tbody");

    if (!tbody)
        tbody = document.querySelector("#lista-produtos tbody");

    if (!tbody) return;

    const user = getCurrentUser();
    const produtos = await apiRequest(`${API_URL}/produtos`);
    if (!produtos) return;

    tbody.innerHTML = "";

    if (produtos.length === 0) {
        tbody.innerHTML = "<tr><td colspan='5'>Nenhum produto encontrado.</td></tr>";
        return;
    }

    produtos.forEach(p => {
        const tr = document.createElement("tr");

        let acoes = "";
        if (isAdmin(user) || isSeller(user)) {
            acoes = `
                <button class="btn small editar" data-id="${p.id}">Editar</button>
                <button class="btn small danger excluir" data-id="${p.id}">Excluir</button>
            `;
        } else if (isClient(user)) {
            acoes = `<button class="btn small comprar" data-id="${p.id}">Comprar</button>`;
        }

        tr.innerHTML = `
            <td>${p.id}</td>
            <td>${p.nome}</td>
            <td>${p.categoria ?? ""}</td>
            <td>R$ ${Number(p.preco).toFixed(2)}</td>
            <td>${acoes}</td>
        `;
        tbody.appendChild(tr);
    });
}


// ------------------------------------------------------------
// CADASTRAR PRODUTO
// ------------------------------------------------------------
async function cadastrarProduto(event) {
    event.preventDefault();

    const user = getCurrentUser();
    if (!isAdmin(user) && !isSeller(user)) {
        alert("Sem permissão.");
        return;
    }

    const nome = document.querySelector("#nome-produto").value.trim();
    const categoria = document.querySelector("#categoria-produto").value.trim();
    const preco = parseFloat(document.querySelector("#preco-produto").value);

    if (!nome || !categoria || Number.isNaN(preco)) {
        alert("Preencha todos os campos corretamente.");
        return;
    }

    const data = await apiRequest(`${API_URL}/produtos`, {
        method: "POST",
        body: JSON.stringify({ nome, categoria, preco })
    });

    if (!data) return;

    alert("Produto cadastrado!");
    event.target.reset();
    carregarProdutos();
}


// ------------------------------------------------------------
// EDITAR PRODUTO
// ------------------------------------------------------------
async function editarProduto(id) {
    const user = getCurrentUser();
    if (!isAdmin(user) && !isSeller(user)) {
        alert("Sem permissão para editar.");
        return;
    }

    const lista = await apiRequest(`${API_URL}/produtos`);
    const produto = lista?.find(p => Number(p.id) === Number(id));

    if (!produto) {
        alert("Produto não encontrado.");
        return;
    }

    const novoNome = prompt("Nome:", produto.nome);
    if (novoNome === null) return;

    const novaCat = prompt("Categoria:", produto.categoria ?? "");
    if (novaCat === null) return;

    const precoStr = prompt("Preço:", produto.preco);
    if (precoStr === null) return;

    const novoPreco = parseFloat(precoStr.replace(",", "."));
    if (Number.isNaN(novoPreco)) {
        alert("Preço inválido.");
        return;
    }

    const data = await apiRequest(`${API_URL}/produtos/${id}`, {
        method: "PUT",
        body: JSON.stringify({ nome: novoNome, categoria: novaCat, preco: novoPreco })
    });

    if (!data) return;

    alert("Produto atualizado!");
    carregarProdutos();
}


// ------------------------------------------------------------
// EXCLUIR PRODUTO
// ------------------------------------------------------------
async function excluirProduto(id) {
    const user = getCurrentUser();
    if (!isAdmin(user) && !isSeller(user)) {
        alert("Sem permissão.");
        return;
    }

    if (!confirm("Tem certeza que deseja excluir?")) return;

    const data = await apiRequest(`${API_URL}/produtos/${id}`, {
        method: "DELETE"
    });

    if (!data) return;

    alert(data.message || "Produto excluído!");
    carregarProdutos();
}


// ============================================================
// USUÁRIOS
// ============================================================

async function carregarUsuarios() {
    const tabela = document.querySelector("#tabela-usuarios");
    if (!tabela) return;

    const user = getCurrentUser();
    const usuarios = await apiRequest(`${API_URL}/usuarios`);
    if (!usuarios) return;

    tabela.innerHTML = "";

    usuarios.forEach(u => {
        const tr = document.createElement("tr");

        let acoes = "";
        if (isAdmin(user)) {
            acoes = `<button class="btn small danger excluir-usuario" data-id="${u.id}">Excluir</button>`;
        } else {
            acoes = `<span style="color:#777;">Sem permissão</span>`;
        }

        tr.innerHTML = `
            <td>${u.id}</td>
            <td>${u.nome}</td>
            <td>${u.email}</td>
            <td>${u.grupo_id}</td>
            <td>${acoes}</td>
        `;
        tabela.appendChild(tr);
    });
}


// ------------------------------------------------------------
// CADASTRAR USUÁRIO
// ------------------------------------------------------------
async function cadastrarUsuario(event) {
    event.preventDefault();

    const user = getCurrentUser();
    if (!isAdmin(user) && !isSeller(user)) {
        alert("Sem permissão.");
        return;
    }

    const nome = document.querySelector("#nome").value.trim();
    const email = document.querySelector("#email").value.trim();
    const senha = document.querySelector("#senha").value.trim();
    const grupo_id = parseInt(document.querySelector("#grupo").value, 10);

    const data = await apiRequest(`${API_URL}/usuarios`, {
        method: "POST",
        body: JSON.stringify({ nome, email, senha, grupo_id })
    });

    if (!data) return;

    alert(data.message || "Usuário cadastrado!");
    event.target.reset();
    carregarUsuarios();
}


// ------------------------------------------------------------
// EXCLUIR USUÁRIO
// ------------------------------------------------------------
async function excluirUsuarioPorId(id) {
    const user = getCurrentUser();
    if (!isAdmin(user)) {
        alert("Somente administradores podem excluir usuários.");
        return;
    }

    if (!confirm("Deseja excluir este usuário?")) return;

    const data = await apiRequest(`${API_URL}/usuarios/${id}`, {
        method: "DELETE"
    });

    if (!data) return;

    alert(data.message || "Usuário excluído!");
    carregarUsuarios();
}


// ============================================================
// GRUPOS
// ============================================================

async function carregarGrupos() {
    const lista = document.getElementById("lista-grupos");
    if (!lista) return;

    lista.innerHTML = "<li>Carregando grupos...</li>";

    const data = await apiRequest(`${API_URL}/grupos`);
    if (!data) {
        lista.innerHTML = "<li>Erro ao carregar grupos.</li>";
        return;
    }

    const grupos = data.grupos; // API retorna assim

    if (!grupos || grupos.length === 0) {
        lista.innerHTML = "<li>Nenhum grupo encontrado.</li>";
        return;
    }

    lista.innerHTML = "";

    grupos.forEach(g => {
        const li = document.createElement("li");
        li.textContent = `${g.nome} — ID: ${g.id} — ${g.descricao ?? ""}`;
        lista.appendChild(li);
    });
}


// ============================================================
// INICIALIZAÇÃO GLOBAL
// ============================================================
document.addEventListener("DOMContentLoaded", () => {

    const user = getCurrentUser();
    if (!user) {
        window.location.href = "index.html";
        return;
    }

    // produtos
    if (document.querySelector("#lista-produtos")) {
        carregarProdutos();

        const form = document.querySelector("#form-produto");
        if (form && !isClient(user)) form.addEventListener("submit", cadastrarProduto);
        if (form && isClient(user)) form.style.display = "none";
    }

    // usuários
    if (document.querySelector("#tabela-usuarios")) {
        if (!isAdmin(user)) {
            alert("Apenas administradores podem acessar usuários.");
            window.location.href = "dashboard.html";
            return;
        }

        carregarUsuarios();
        document.querySelector("#formUsuario")?.addEventListener("submit", cadastrarUsuario);
    }

    // grupos
    if (document.querySelector("#lista-grupos")) {
        if (!isAdmin(user)) {
            alert("Somente administradores podem acessar grupos.");
            window.location.href = "dashboard.html";
            return;
        }

        carregarGrupos();
    }

    // eventos globais de clique
    document.addEventListener("click", (e) => {
        if (e.target.classList.contains("editar")) editarProduto(e.target.dataset.id);
        if (e.target.classList.contains("excluir")) excluirProduto(e.target.dataset.id);
        if (e.target.classList.contains("excluir-usuario")) excluirUsuarioPorId(e.target.dataset.id);
        if (e.target.classList.contains("comprar")) alert("Carrinho será implementado futuramente!");
    });

    // logout
    document.querySelectorAll(".logout").forEach(btn => {
        btn.addEventListener("click", () => {
            localStorage.removeItem("usuario");
            window.location.href = "index.html";
        });
    });
});
