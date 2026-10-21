# Sistema de Cadastro em Python

Programa de terminal para gerenciar **clientes, produtos e pedidos**, feito para praticar listas, dicionários, funções e persistência de dados em JSON.

## Funcionalidades

- **Clientes:** cadastrar, listar e excluir
- **Produtos:** cadastrar, listar, repor estoque e excluir
- **Pedidos:** criar (com vários itens e controle de estoque), listar e excluir (devolve o estoque)
- **Relatórios:** pedidos de um cliente, produtos mais vendidos e total vendido
- **Persistência:** tudo é salvo automaticamente em `dados.json`

## Como rodar

Precisa apenas do Python 3 instalado.

```bash
python sistema_cadastro.py
```

## Como funciona

Cada registro é um dicionário, e cada grupo fica numa lista:

```python
cliente = {"id": 1, "nome": "Maria", "telefone": "91 99999-0000"}
pedido  = {"id": 1, "cliente_id": 1,
           "itens": [{"produto_id": 1, "quantidade": 10, "preco_unitario": 0.5}]}
```

O pedido guarda só o **id** do cliente e dos produtos, então os dados não ficam duplicados.

## Regras de negócio

- Os ids **nunca são reaproveitados**, mesmo depois de excluir um registro.
- Não é possível excluir um cliente ou produto que já tenha pedidos, para não quebrar o histórico.
- Ao excluir um pedido, os produtos voltam para o estoque.
- O preço é guardado no pedido, então mudar o preço depois não altera vendas antigas.

## Próximos passos

- [ ] Editar cliente e produto
- [ ] Trocar o JSON por SQLite
- [ ] Exportar relatórios para CSV
- [ ] Gráficos com matplotlib
