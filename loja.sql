create database if not exists loja;

use loja;

CREATE TABLE grupos_usuarios (
  IDGrupo INT PRIMARY KEY AUTO_INCREMENT,
  NomeGrupo VARCHAR(60) NOT NULL UNIQUE,     -- 'GERENCIA', 'FUNCIONARIO', 'CLIENTE'...
  Descricao VARCHAR(255)
);

CREATE TABLE usuarios (
  IDUsuario INT PRIMARY KEY AUTO_INCREMENT,
  Nome VARCHAR(120) NOT NULL,
  IDGrupo INT NOT NULL,
  CriadoEm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_usuario_grupo
    FOREIGN KEY (IDGrupo) REFERENCES grupos_usuarios(IDGrupo)
      ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Clientes (
  IDCliente INT PRIMARY KEY AUTO_INCREMENT,
  Nome VARCHAR(120) NOT NULL,
  CPF CHAR(11) UNIQUE,
  CriadoEm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Funcionarios (
  IDFuncionario INT PRIMARY KEY AUTO_INCREMENT,
  Nome VARCHAR(120) NOT NULL,
  CPF CHAR(11) UNIQUE,
  Cargo VARCHAR(60),
  Salario DOUBLE,
  CriadoEm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Produtos (
  IDProduto INT PRIMARY KEY AUTO_INCREMENT,
  Nome VARCHAR(120) NOT NULL,
  Descricao TEXT,
  Preco DOUBLE NOT NULL,
  Estoque INT NOT NULL DEFAULT 0,
  CriadoEm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

alter table Produtos drop column CriadoEm;

CREATE TABLE Vendas (
  IDVenda INT PRIMARY KEY AUTO_INCREMENT,
  IDCliente INT NOT NULL,
  IDFuncionario INT NOT NULL,
  DataVenda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Total DOUBLE NOT NULL DEFAULT 0,
  CONSTRAINT fk_venda_cliente
    FOREIGN KEY (IDCliente) REFERENCES Clientes(IDCliente)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_venda_funcionario
    FOREIGN KEY (IDFuncionario) REFERENCES Funcionarios(IDFuncionario)
      ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE ItensVenda (
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

CREATE TABLE MovimentacoesEstoque ( 
  IDMovimentacao INT PRIMARY KEY AUTO_INCREMENT,
  IDProduto INT NOT NULL,
  TipoMovimentacao ENUM('Entrada', 'Saída') NOT NULL,
  Quantidade INT NOT NULL,
  DataMovimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (IDProduto) REFERENCES Produtos(IDProduto)
);

CREATE TABLE IF NOT EXISTS AvisosEstoque (
  IDAviso INT PRIMARY KEY AUTO_INCREMENT,
  IDProduto INT NOT NULL,
  Mensagem VARCHAR(255) NOT NULL,
  DataAviso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (IDProduto) REFERENCES Produtos(IDProduto)
);

ALTER TABLE Produtos
  ADD COLUMN Categoria VARCHAR(80) NULL AFTER Nome;
  
ALTER TABLE usuarios
  ADD COLUMN Email VARCHAR(150) NULL AFTER Nome;
  
ALTER TABLE usuarios
  ADD CONSTRAINT uk_usuarios_email UNIQUE (Email);
  
ALTER TABLE usuarios
  ADD COLUMN SenhaHash VARCHAR(255) NULL AFTER Email;

CREATE INDEX idx_clientes_nome      ON Clientes(Nome);
CREATE INDEX idx_funcionarios_nome  ON Funcionarios(Nome);
CREATE INDEX idx_produtos_nome      ON Produtos(Nome);
CREATE INDEX idx_vendas_data        ON Vendas(DataVenda);
CREATE INDEX idx_itens_venda_venda  ON ItensVenda(IDVenda);
CREATE INDEX idx_produtos_categoria ON Produtos(Categoria);

DELIMITER //

CREATE FUNCTION fn_total_vendas_dia()
RETURNS DOUBLE
DETERMINISTIC
BEGIN
  RETURN (
    SELECT IFNULL(SUM(Total), 0)
    FROM Vendas
    WHERE DATE(DataVenda) = CURDATE()
  );
END//


CREATE FUNCTION fn_qtd_produtos_disponiveis()
RETURNS INT
DETERMINISTIC
BEGIN
  RETURN (
    SELECT IFNULL(SUM(Estoque), 0)
    FROM Produtos
  );
END//


-- 3) Aplica desconto percentual (com limites de 0 a 90%)
CREATE FUNCTION fn_preco_com_desconto(p_preco DOUBLE, p_pct DOUBLE)
RETURNS DOUBLE
DETERMINISTIC
BEGIN
  IF p_pct < 0 THEN SET p_pct = 0; END IF;
  IF p_pct > 90 THEN SET p_pct = 90; END IF;
  RETURN ROUND(p_preco * (1 - p_pct/100), 2);
END//

DELIMITER ;

DELIMITER //
  
-- TRIGGERS (estoque)[
DROP TRIGGER IF EXISTS trg_itensvenda_before_insert//
DROP TRIGGER IF EXISTS trg_itensvenda_after_insert//
  
  CREATE TRIGGER trg_itensvenda_after_insert
AFTER INSERT ON ItensVenda
FOR EACH ROW
BEGIN
  -- baixa estoque do produto
  UPDATE Produtos
  SET Estoque = Estoque - NEW.Quantidade
  WHERE IDProduto = NEW.IDProduto;

  -- registra movimentação de saída
  INSERT INTO MovimentacoesEstoque (IDProduto, TipoMovimentacao, Quantidade)
  VALUES (NEW.IDProduto, 'Saída', NEW.Quantidade);
END//

/* 2) NOVA: avisa quando o estoque acabar (zerar) */
DROP TRIGGER IF EXISTS trg_produtos_after_update//
CREATE TRIGGER trg_produtos_after_update
AFTER UPDATE ON Produtos
FOR EACH ROW
BEGIN
  -- quando sair de >0 para <=0, gera um alerta
  IF OLD.Estoque > 0 AND NEW.Estoque <= 0 THEN
    INSERT INTO AvisosEstoque (IDProduto, Mensagem)
    VALUES (NEW.IDProduto, CONCAT('Estoque zerado do produto ID ', NEW.IDProduto));
  END IF;
END//

DELIMITER ;

-- 1) Cadastrar produto
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

-- 2) Deletar produto
DROP PROCEDURE IF EXISTS deletar_produto//
CREATE PROCEDURE deletar_produto (
  IN p_IDProduto INT
)
BEGIN
  DELETE FROM Produtos
  WHERE IDProduto = p_IDProduto;

  SELECT CONCAT('Produto ID ', p_IDProduto, ' deletado!') AS Mensagem;
END//

-- 3) Editar produto completo (nome, descrição, preço, estoque)
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

-- 4) Editar somente a descrição do produto
DROP PROCEDURE IF EXISTS editar_descricao//
CREATE PROCEDURE editar_descricao (
  IN p_IDProduto INT,
  IN p_Descricao TEXT
)
BEGIN
  UPDATE Produtos
  SET Descricao = p_Descricao
  WHERE IDProduto = p_IDProduto;

  SELECT CONCAT('Descrição do produto ID ', p_IDProduto, ' atualizada!') AS Mensagem;
END//

DELIMITER ;

-- Views de acesso (cliente e funcionário)


CREATE VIEW vw_produtos_cliente AS
SELECT IDProduto, Nome, Preco, Estoque
FROM Produtos;

CREATE VIEW vw_produtos_funcionario AS
SELECT IDProduto, Nome, Preco, Estoque
FROM Produtos;

CREATE USER 'gerencia'@'localhost' IDENTIFIED BY 'gerencia';
CREATE USER 'funcionario'@'localhost' IDENTIFIED BY 'funcionario';
CREATE USER 'cliente'@'localhost' IDENTIFIED BY 'cliente';

create user 'pedro'@'26.102.205.190' identified by 'pedro1234ger';
grant all on loja.* to 'pedro'@'26.102.205.190';

create user 'david'@'26.4.235.12' identified by 'beckgerencia!';
grant all on loja.* to 'david'@'26.4.235.12';

create user 'note'@'26.133.40.164' identified by 'noteger123';
grant all on loja.* to 'note'@'26.133.40.164';

CREATE USER 'gerencia'@'192.168.1.%' IDENTIFIED BY 'gerencia';
CREATE USER 'funcionario'@'192.168.1.%' IDENTIFIED BY 'funcionario';
CREATE USER 'cliente'@'192.168.1.%' IDENTIFIED BY 'cliente';

grant all on loja.* to gerencia@localhost;
grant select on loja.vw_produtos_funcionario TO funcionario@localhost ;
grant select on loja.Clientes TO funcionario@localhost;
grant select on loja.Funcionarios TO funcionario@localhost;
grant select , INSERT, UPDATE, DELETE ON loja.Vendas    TO funcionario@localhost;
grant select , INSERT, UPDATE, DELETE ON loja.ItensVenda TO funcionario@localhost;
grant select on loja.vw_produtos_cliente TO cliente@localhost;


insert into grupos_usuarios (NomeGrupo, Descricao)
values ('Administrador','Acesso administrativo'),
       ('Vendedor','Equipe de vendas'),
       ('Gerente','Gestão e liderança')
ON DUPLICATE KEY UPDATE Descricao = VALUES(Descricao);


CREATE OR REPLACE VIEW vw_front_produtos AS
SELECT  p.IDProduto   AS id,
        p.Nome        AS nome,
        p.Categoria   AS categoria,
        p.Preco       AS preco
FROM Produtos p;

CREATE OR REPLACE VIEW vw_front_usuarios AS
SELECT  u.IDUsuario   AS id,
        u.Nome        AS nome,
        u.Email       AS email,
        g.NomeGrupo   AS grupo
FROM usuarios u
JOIN grupos_usuarios g ON g.IDGrupo = u.IDGrupo;

CREATE OR REPLACE VIEW vw_front_grupos AS
SELECT g.IDGrupo AS id, g.NomeGrupo AS nome, g.Descricao AS descricao
FROM grupos_usuarios g;

grant select on loja.vw_front_produtos to 'funcionario'@'localhost', 'cliente'@'localhost';
grant select on loja.vw_front_usuarios to 'gerencia'@'localhost';   -- geralmente só gerência enxerga usuários
grant select on loja.vw_front_grupos   to 'gerencia'@'localhost', 'funcionario'@'localhost', 'cliente'@'localhost';

flush privileges;
