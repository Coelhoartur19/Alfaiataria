create database alfaiataria;

use alfaiataria;

create table grupos_usuarios (
  IDGrupo INT PRIMARY KEY AUTO_INCREMENT,
  NomeGrupo VARCHAR(60) NOT NULL UNIQUE,     -- 'GERENCIA','FUNCIONARIO','CLIENTE'
  Descricao VARCHAR(255)
);

create table usuarios (
  IDUsuario INT PRIMARY KEY AUTO_INCREMENT,
  Nome VARCHAR(120) NOT NULL,
  Email VARCHAR(150) NULL,
  SenhaHash VARCHAR(255) NULL,
  IDGrupo INT NOT NULL,
  CriadoEm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_usuarios_email UNIQUE (Email),
  CONSTRAINT fk_usuario_grupo
    FOREIGN KEY (IDGrupo) REFERENCES grupos_usuarios(IDGrupo)
      ON UPDATE CASCADE ON DELETE RESTRICT
);

create table Produtos (
  IDProduto INT PRIMARY KEY AUTO_INCREMENT,
  Nome VARCHAR(120) NOT NULL,
  Categoria VARCHAR(80) NULL,
  Descricao TEXT,
  Preco DOUBLE NOT NULL,
  Estoque INT NOT NULL DEFAULT 0
);

create table Vendas (
  IDVenda INT PRIMARY KEY AUTO_INCREMENT,
  IDUsuarioCliente   INT NOT NULL,
  IDUsuarioAtendente INT NOT NULL,
  DataVenda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Total DOUBLE NOT NULL DEFAULT 0,
  CONSTRAINT fk_venda_cliente_usuario
    FOREIGN KEY (IDUsuarioCliente) REFERENCES usuarios(IDUsuario)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_venda_atendente_usuario
    FOREIGN KEY (IDUsuarioAtendente) REFERENCES usuarios(IDUsuario)
      ON UPDATE CASCADE ON DELETE RESTRICT
);

create table ItensVenda (
  IDItem INT PRIMARY KEY AUTO_INCREMENT,
  IDVenda INT NOT NULL,
  IDProduto INT NOT NULL,
  Quantidade INT NOT NULL,
  PrecoUnitario DOUBLE NOT NULL,
  CONSTRAINT fk_item_venda
    FOREIGN KEY (IDVenda) REFERENCES Vendas(IDVenda)
      ON DELETE CASCADE,
  CONSTRAINT fk_item_produto
    FOREIGN KEY (IDProduto) REFERENCES Produtos(IDProduto)
      ON DELETE RESTRICT
);

create table MovimentacoesEstoque ( 
  IDMovimentacao INT PRIMARY KEY AUTO_INCREMENT,
  IDProduto INT NOT NULL,
  TipoMovimentacao ENUM('Entrada', 'Saída') NOT NULL,
  Quantidade INT NOT NULL,
  DataMovimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (IDProduto) REFERENCES Produtos(IDProduto)
);

create table AvisosEstoque (
  IDAviso INT PRIMARY KEY AUTO_INCREMENT,
  IDProduto INT NOT NULL,
  Mensagem VARCHAR(255) NOT NULL,
  DataAviso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (IDProduto) REFERENCES Produtos(IDProduto)
);


create index idx_usuarios_nome      on usuarios(Nome);
create index idx_produtos_nome      on Produtos(Nome);
create index idx_produtos_categoria on Produtos(Categoria);
create index idx_vendas_data        on Vendas(DataVenda);
create index idx_itens_venda_venda  on ItensVenda(IDVenda);

DELIMITER //

	create function total_vendas_dia()
    returns double 
    DETERMINISTIC
		BEGIN
			return (
            select ifnull(SUM(Total),0)
            from Vendas
            Where date(DataVenda) = Curdate()
            );
        END//
				
	Create function qtd_produtos_disponivel()
    returns INT
    DETERMINISTIC
	BEGIN
		RETURN (
		SELECT IFNULL(SUM(Estoque), 0)
		FROM Produtos
  );
	END//
    
    
	CREATE FUNCTION preco_com_desconto(p_preco DOUBLE, p_pct DOUBLE)
	RETURNS DOUBLE
	DETERMINISTIC
		BEGIN
			IF p_pct < 0 THEN SET p_pct = 0; END IF;
			IF p_pct > 90 THEN SET p_pct = 90; END IF;
			RETURN ROUND(p_preco * (1 - p_pct/100), 2);
END//

DELIMITER ;

DELIMITER //

-- 1) após inserir item: baixa estoque, registra saída e atualiza total da venda
DROP TRIGGER IF EXISTS trg_itensvenda_after_insert//
CREATE TRIGGER trg_itensvenda_after_insert
AFTER INSERT ON ItensVenda
FOR EACH ROW
BEGIN
  UPDATE Produtos
  SET Estoque = Estoque - NEW.Quantidade
  WHERE IDProduto = NEW.IDProduto;

  INSERT INTO MovimentacoesEstoque (IDProduto, TipoMovimentacao, Quantidade)
  VALUES (NEW.IDProduto, 'Saída', NEW.Quantidade);

  UPDATE Vendas
  SET Total = Total + (NEW.Quantidade * NEW.PrecoUnitario)
  WHERE IDVenda = NEW.IDVenda;
END//

-- 2) após atualizar produto: se estoque zerar, gera aviso
DROP TRIGGER IF EXISTS trg_produtos_after_update//
CREATE TRIGGER trg_produtos_after_update
AFTER UPDATE ON Produtos
FOR EACH ROW
BEGIN
  IF OLD.Estoque > 0 AND NEW.Estoque <= 0 THEN
    INSERT INTO AvisosEstoque (IDProduto, Mensagem)
    VALUES (NEW.IDProduto, CONCAT('Estoque zerado do produto ID ', NEW.IDProduto));
  END IF;
END//

DELIMITER ;

DELIMITER //

DROP PROCEDURE IF EXISTS cadastrar_produto//
CREATE PROCEDURE cadastrar_produto (
  IN p_Nome VARCHAR(120),
  IN p_Descricao TEXT,
  IN p_Preco DOUBLE,
  IN p_Estoque INT
)
BEGIN
  INSERT INTO Produtos (Nome, Descricao, Preco, Estoque)
  VALUES (p_Nome, p_Descricao, p_Preco, p_Estoque);
  SELECT LAST_INSERT_ID() AS IDProduto, 'Produto cadastrado com sucesso!' AS Mensagem;
END//

DROP PROCEDURE IF EXISTS editar_produto//
CREATE PROCEDURE editar_produto (
  IN p_IDProduto INT,
  IN p_Nome VARCHAR(120),
  IN p_Descricao TEXT,
  IN p_Preco DOUBLE,
  IN p_Estoque INT
)
BEGIN
  UPDATE Produtos
  SET Nome = p_Nome,
      Descricao = p_Descricao,
      Preco = p_Preco,
      Estoque = p_Estoque
  WHERE IDProduto = p_IDProduto;
  SELECT CONCAT('Produto ID ', p_IDProduto, ' atualizado!') AS Mensagem;
END//

DROP PROCEDURE IF EXISTS deletar_produto//
CREATE PROCEDURE deletar_produto (
  IN p_IDProduto INT
)
BEGIN
  DELETE FROM Produtos
  WHERE IDProduto = p_IDProduto;
  SELECT CONCAT('Produto ID ', p_IDProduto, ' deletado!') AS Mensagem;
END//

DELIMITER ;

create view  vw_produtos_cliente AS
SELECT IDProduto, Nome, Preco, Estoque
FROM Produtos;

create view  vw_produtos_funcionario AS
SELECT IDProduto, Nome, Preco, Estoque
FROM Produtos;

-- Cabeçalho dos pedidos
create view vw_pedidos AS
SELECT
  v.IDVenda,
  v.DataVenda,
  uc.Nome AS Cliente,
  ua.Nome AS Atendente,
  v.Total
FROM Vendas v
JOIN usuarios uc ON uc.IDUsuario = v.IDUsuarioCliente
JOIN usuarios ua ON ua.IDUsuario = v.IDUsuarioAtendente;

-- Itens por pedido
create view  vw_itens_pedido AS
SELECT
  i.IDVenda,
  p.Nome      AS Produto,
  i.Quantidade,
  i.PrecoUnitario,
  (i.Quantidade * i.PrecoUnitario) AS Subtotal
FROM ItensVenda i
JOIN Produtos p ON p.IDProduto = i.IDProduto;

-- Avisos de estoque (zerado)
create view  vw_avisos_estoque AS
SELECT a.IDAviso, a.DataAviso, a.IDProduto, p.Nome AS Produto, a.Mensagem
FROM AvisosEstoque a
JOIN Produtos p ON p.IDProduto = a.IDProduto;

-- Views “front”
create view vw_front_produtos AS
SELECT  p.IDProduto   AS id,
        p.Nome        AS nome,
        p.Categoria   AS categoria,
        p.Preco       AS preco
FROM Produtos p;

create view  vw_front_usuarios AS
SELECT  u.IDUsuario   AS id,
        u.Nome        AS nome,
        u.Email       AS email,
        g.NomeGrupo   AS grupo
FROM usuarios u
JOIN grupos_usuarios g ON g.IDGrupo = u.IDGrupo;

create view  vw_front_grupos AS
SELECT g.IDGrupo AS id, g.NomeGrupo AS nome, g.Descricao AS descricao
FROM grupos_usuarios g;

-- (Opcional) Views por grupo
create view vw_usuarios_clientes AS
SELECT u.IDUsuario, u.Nome, u.Email, u.CriadoEm
FROM usuarios u
JOIN grupos_usuarios g ON g.IDGrupo = u.IDGrupo
WHERE g.NomeGrupo = 'CLIENTE';

create view  vw_usuarios_atendentes AS
SELECT u.IDUsuario, u.Nome, u.Email, u.CriadoEm
FROM usuarios u
JOIN grupos_usuarios g ON g.IDGrupo = u.IDGrupo
WHERE g.NomeGrupo IN ('FUNCIONARIO','ATENDENTE','VENDEDOR','GERENCIA');

INSERT IGNORE INTO grupos_usuarios (NomeGrupo, Descricao) VALUES
('GERENCIA','Acesso total'), ('FUNCIONARIO','Cria vendas'),
('CLIENTE','Consulta produtos');

INSERT INTO usuarios (Nome, Email, IDGrupo)
VALUES ('Maria Gerente','maria@exemplo.com',(SELECT IDGrupo FROM grupos_usuarios WHERE NomeGrupo='GERENCIA')),
       ('João Vendedor','joao@exemplo.com',(SELECT IDGrupo FROM grupos_usuarios WHERE NomeGrupo='FUNCIONARIO')),
       ('Gustavo Cliente','gustavo@exemplo.com',(SELECT IDGrupo FROM grupos_usuarios WHERE NomeGrupo='CLIENTE'))
ON DUPLICATE KEY UPDATE Email=VALUES(Email);


-- Localhost


create user 'gerencia'@'localhost'   identified by 'SenhaGerencia!';
create user 'funcionario'@'localhost' identified by 'SenhaFunc!';
create user 'cliente'@'localhost'     identified by 'SenhaCliente!';

GRANT ALL PRIVILEGES ON loja.*                 to 'gerencia'@'localhost';
grant select on loja.vw_produtos_funcionario   to 'funcionario'@'localhost';
grant select on loja.vw_usuarios_clientes      to 'funcionario'@'localhost';
grant select on loja.vw_pedidos                to 'funcionario'@'localhost';
grant select on loja.vw_itens_pedido           to 'funcionario'@'localhost';
grant select, INSERT, UPDATE, DELETE ON loja.Vendas     to 'funcionario'@'localhost';
grant select, INSERT, UPDATE, DELETE ON loja.ItensVenda to 'funcionario'@'localhost';
grant select on loja.vw_produtos_cliente       to 'cliente'@'localhost';
grant select on loja.vw_front_produtos         to 'cliente'@'localhost';

-- Rede local (ex.: 192.168.1.x) — ajuste conforme sua rede
CREATE USER IF NOT EXISTS 'gerencia'@'192.168.1.%'   identified by 'SenhaGerencia!';
CREATE USER IF NOT EXISTS 'funcionario'@'192.168.1.%' identified by 'SenhaFunc!';
CREATE USER IF NOT EXISTS 'cliente'@'192.168.1.%'     IDENTIFIED BY 'SenhaCliente!';

GRANT ALL PRIVILEGES ON loja.*                 TO 'gerencia'@'192.168.1.%';
grant select on  loja.vw_produtos_funcionario   TO 'funcionario'@'192.168.1.%';
grant select on  loja.vw_usuarios_clientes      TO 'funcionario'@'192.168.1.%';
grant select on  loja.vw_pedidos                TO 'funcionario'@'192.168.1.%';
grant select on  loja.vw_itens_pedido           TO 'funcionario'@'192.168.1.%';
grant select, INSERT, UPDATE, DELETE ON loja.Vendas     TO 'funcionario'@'192.168.1.%';
grant select, INSERT, UPDATE, DELETE ON loja.ItensVenda TO 'funcionario'@'192.168.1.%';
grant select on loja.vw_produtos_cliente       TO 'cliente'@'192.168.1.%';
grant select on loja.vw_front_produtos         TO 'cliente'@'192.168.1.%';

create user 'note'@'26.133.40.164' identified by 'noteger123';
grant all on loja.* to 'note'@'26.133.40.164';

create user 'david'@'26.4.235.12' identified by 'beckgerencia!';
grant all on loja.* to 'david'@'26.4.235.12';

flush privileges;
