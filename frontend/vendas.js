const API = "http://127.0.0.1:8000/api";

let produtos = [];
let itens = [];

// ===================================
// Proteção de acesso + carregamento inicial
// ===================================
document.addEventListener("DOMContentLoaded", () => {

    let usuario = null;
    try {
        usuario = JSON.parse(localStorage.getItem("usuario"));
    } catch {
        usuario = null;
    }

    if (!usuario) {
        alert("Você precisa estar logado!");
        window.location.href = "index.html";
        return;
    }

    // Só administradores (1) e vendedores (2) podem acessar vendas
    if (usuario.grupo_id === 3) {
        alert("Clientes não podem acessar vendas.");
        window.location.href = "dashboard.html";
        return;
    }

    console.log("Usuário logado:", usuario);

    carregarProdutos();

    // Botão vendas 
    const menuVendas = document.getElementById("menu-vendas");
    if (menuVendas) menuVendas.style.display = "block";

    // Eventos da página
    document.getElementById("add-item").addEventListener("click", adicionarItem);
    document.getElementById("finalizar-venda").addEventListener("click", finalizarVenda);
});

// ===================================
// Carregar produtos
// ===================================
async function carregarProdutos() {
    const resp = await fetch(`${API}/produtos`);
    produtos = await resp.json();

    const select = document.getElementById("produto-select");
    select.innerHTML = '<option value="">Selecione um produto</option>';

    produtos.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = `${p.nome} — R$ ${p.preco.toFixed(2)}`;
        select.appendChild(opt);
    });
}

// ===================================
// Adicionar item
// ===================================
function adicionarItem() {
    const idProd = Number(document.getElementById("produto-select").value);
    const qtd = Number(document.getElementById("quantidade").value);

    if (!idProd || qtd <= 0) {
        alert("Selecione o produto e quantidade válida!");
        return;
    }

    const produto = produtos.find(p => p.id === idProd);

    itens.push({
        id: produto.id,
        nome: produto.nome,
        quantidade: qtd,
        preco: produto.preco,
        total: produto.preco * qtd
    });

    renderTabela();
}

// ===================================
// Atualiza tabela
// ===================================
function renderTabela() {
    const tabela = document.getElementById("itens-venda");
    tabela.innerHTML = "";

    let totalGeral = 0;

    itens.forEach((i, idx) => {
        totalGeral += i.total;

        tabela.innerHTML += `
            <tr>
                <td>${i.nome}</td>
                <td>${i.quantidade}</td>
                <td>R$ ${i.preco.toFixed(2)}</td>
                <td>R$ ${i.total.toFixed(2)}</td>
                <td><button class="btn danger" onclick="removerItem(${idx})">Remover</button></td>
            </tr>
        `;
    });

    document.getElementById("total-geral").textContent = totalGeral.toFixed(2);
}

// ===================================
// Remover item
// ===================================
function removerItem(index) {
    itens.splice(index, 1);
    renderTabela();
}

// ===================================
// Finalizar venda
// ===================================
async function finalizarVenda() {

    let usuario = JSON.parse(localStorage.getItem("usuario"));

    if (!usuario) {
        alert("Erro: usuário não encontrado.");
        return;
    }

    if (itens.length === 0) {
        alert("Nenhum item na venda.");
        return;
    }

    const payload = {
        id_usuario: usuario.id,
        itens: itens
    };

    const resp = await fetch(`${API}/vendas`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await resp.json();

    if (resp.ok) {
        alert("Venda registrada com sucesso!");
        itens = [];
        renderTabela();
    } else {
        alert("Erro ao registrar venda: " + (data.detail || "desconhecido"));
    }
}
