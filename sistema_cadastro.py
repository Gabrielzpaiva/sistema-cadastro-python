"""
Sistema de Cadastro - clientes, produtos e pedidos.

Programa de terminal que guarda tudo em um arquivo JSON (dados.json).
O pedido liga um cliente a um ou alguns produtos a mais usando apenas os ids.
"""

import json
import os

ARQUIVO = "dados.json"

clientes = []
produtos = []
pedidos = []
contadores = []

# Contador de ids: nunca reaproveita um id, mesmo depois de excluir.
contadores = {"clientes": 1, "produtos": 1, "pedidos": 1}


# ---------------------------------------------------------------
# Persistência (salvar / carregar)
# ---------------------------------------------------------------

def salvar():
    dados = {
        "clientes": clientes,
        "produtos": produtos,
        "pedidos": pedidos,
        "contadores": contadores,
    }
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar():
    if not os.path.exists(ARQUIVO):
        return
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        dados = json.load(f)
    clientes.extend(dados.get("clientes", []))
    produtos.extend(dados.get("produtos", []))
    pedidos.extend(dados.get("pedidos", []))
    contadores.update(dados.get("contadores", {}))


# ---------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------

def novo_id(tipo):
    """Devolve o próximo id disponível para 'clientes', 'produtos' ou 'pedidos'."""
    id_atual = contadores[tipo]
    contadores[tipo] += 1
    return id_atual


def buscar_por_id(lista, item_id):
    for item in lista:
        if item["id"] == item_id:
            return item
    return None


def formatar_preco(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def ler_texto(mensagem):
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print("Campo obrigatório. Tente de novo.")


def ler_inteiro(mensagem, minimo=None):
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Digite um número inteiro.")
            continue
        if minimo is not None and valor < minimo:
            print(f"O valor deve ser pelo menos {minimo}.")
            continue
        return valor


def ler_decimal(mensagem):
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))
        except ValueError:
            print("Digite um número válido (ex: 2,50).")
            continue
        if valor < 0:
            print("O valor não pode ser negativo.")
            continue
        return valor


def confirmar(mensagem):
    resposta = input(f"{mensagem} (s/n): ").strip().lower()
    return resposta == "s"


# ---------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------

def cadastrar_cliente():
    print("\n--- Novo cliente ---")
    nome = ler_texto("Nome: ")
    telefone = ler_texto("Telefone: ")
    cliente = {"id": novo_id("clientes"), "nome": nome, "telefone": telefone}
    clientes.append(cliente)
    salvar()
    print(f"Cliente cadastrado com id {cliente['id']}.")


def listar_clientes():
    print("\n--- Clientes ---")
    if not clientes:
        print("Nenhum cliente cadastrado.")
        return
    for c in clientes:
        print(f"{c['id']} - {c['nome']} ({c['telefone']})")


def excluir_cliente():
    listar_clientes()
    if not clientes:
        return
    cliente_id = ler_inteiro("\nId do cliente a excluir: ")
    cliente = buscar_por_id(clientes, cliente_id)
    if cliente is None:
        print("Cliente não encontrado.")
        return
    # Não deixa excluir quem tem pedidos, para não quebrar o histórico.
    if any(p["cliente_id"] == cliente_id for p in pedidos):
        print("Este cliente tem pedidos. Exclua os pedidos dele primeiro.")
        return
    if confirmar(f"Excluir '{cliente['nome']}'?"):
        clientes.remove(cliente)
        salvar()
        print("Cliente excluído.")
    else:
        print("Operação cancelada.")


# ---------------------------------------------------------------
# Produtos
# ---------------------------------------------------------------

def cadastrar_produto():
    print("\n--- Novo produto ---")
    nome = ler_texto("Nome: ")
    preco = ler_decimal("Preço (ex: 2,50): ")
    estoque = ler_inteiro("Quantidade em estoque: ", minimo=0)
    produto = {
        "id": novo_id("produtos"),
        "nome": nome,
        "preco": preco,
        "estoque": estoque,
    }
    produtos.append(produto)
    salvar()
    print(f"Produto cadastrado com id {produto['id']}.")


def listar_produtos():
    print("\n--- Produtos ---")
    if not produtos:
        print("Nenhum produto cadastrado.")
        return
    for p in produtos:
        print(f"{p['id']} - {p['nome']} | {formatar_preco(p['preco'])} | estoque: {p['estoque']}")


def repor_estoque():
    listar_produtos()
    if not produtos:
        return
    produto_id = ler_inteiro("\nId do produto: ")
    produto = buscar_por_id(produtos, produto_id)
    if produto is None:
        print("Produto não encontrado.")
        return
    quantidade = ler_inteiro("Quantidade a adicionar: ", minimo=1)
    produto["estoque"] += quantidade
    salvar()
    print(f"Novo estoque de '{produto['nome']}': {produto['estoque']}.")


def excluir_produto():
    listar_produtos()
    if not produtos:
        return
    produto_id = ler_inteiro("\nId do produto a excluir: ")
    produto = buscar_por_id(produtos, produto_id)
    if produto is None:
        print("Produto não encontrado.")
        return
    em_pedido = any(
        item["produto_id"] == produto_id for p in pedidos for item in p["itens"]
    )
    if em_pedido:
        print("Este produto aparece em pedidos. Exclua os pedidos primeiro.")
        return
    if confirmar(f"Excluir '{produto['nome']}'?"):
        produtos.remove(produto)
        salvar()
        print("Produto excluído.")
    else:
        print("Operação cancelada.")


# ---------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------

def total_do_pedido(pedido):
    return sum(i["quantidade"] * i["preco_unitario"] for i in pedido["itens"])


def criar_pedido():
    print("\n--- Novo pedido ---")
    if not clientes or not produtos:
        print("Cadastre ao menos um cliente e um produto antes.")
        return

    listar_clientes()
    cliente_id = ler_inteiro("\nId do cliente: ")
    cliente = buscar_por_id(clientes, cliente_id)
    if cliente is None:
        print("Cliente não encontrado.")
        return

    itens = []
    while True:
        listar_produtos()
        produto_id = ler_inteiro("\nId do produto (0 para finalizar): ")
        if produto_id == 0:
            break
        produto = buscar_por_id(produtos, produto_id)
        if produto is None:
            print("Produto não encontrado.")
            continue

        # Considera o que já foi colocado deste produto neste mesmo pedido.
        ja_no_pedido = sum(i["quantidade"] for i in itens if i["produto_id"] == produto_id)
        disponivel = produto["estoque"] - ja_no_pedido
        quantidade = ler_inteiro("Quantidade: ", minimo=1)
        if quantidade > disponivel:
            print(f"Estoque insuficiente (disponível: {disponivel}).")
            continue

        itens.append({
            "produto_id": produto_id,
            "quantidade": quantidade,
            "preco_unitario": produto["preco"],  # guarda o preço da hora da venda
        })
        print("Item adicionado.")

    if not itens:
        print("Pedido vazio, nada foi criado.")
        return

    # Só mexe no estoque quando o pedido é realmente confirmado.
    for item in itens:
        buscar_por_id(produtos, item["produto_id"])["estoque"] -= item["quantidade"]

    pedido = {"id": novo_id("pedidos"), "cliente_id": cliente_id, "itens": itens}
    pedidos.append(pedido)
    salvar()
    print(f"Pedido {pedido['id']} criado. Total: {formatar_preco(total_do_pedido(pedido))}")


def mostrar_pedido(pedido):
    cliente = buscar_por_id(clientes, pedido["cliente_id"])
    nome_cliente = cliente["nome"] if cliente else "(cliente removido)"
    print(f"\nPedido {pedido['id']} - Cliente: {nome_cliente}")
    for item in pedido["itens"]:
        produto = buscar_por_id(produtos, item["produto_id"])
        nome_produto = produto["nome"] if produto else "(produto removido)"
        subtotal = item["quantidade"] * item["preco_unitario"]
        print(f"   {item['quantidade']}x {nome_produto} - {formatar_preco(subtotal)}")
    print(f"   Total: {formatar_preco(total_do_pedido(pedido))}")


def listar_pedidos():
    print("\n--- Pedidos ---")
    if not pedidos:
        print("Nenhum pedido registrado.")
        return
    for pedido in pedidos:
        mostrar_pedido(pedido)


def excluir_pedido():
    listar_pedidos()
    if not pedidos:
        return
    pedido_id = ler_inteiro("\nId do pedido a excluir: ")
    pedido = buscar_por_id(pedidos, pedido_id)
    if pedido is None:
        print("Pedido não encontrado.")
        return
    if confirmar(f"Excluir o pedido {pedido_id}? Os produtos voltam para o estoque."):
        for item in pedido["itens"]:
            produto = buscar_por_id(produtos, item["produto_id"])
            if produto:
                produto["estoque"] += item["quantidade"]
        pedidos.remove(pedido)
        salvar()
        print("Pedido excluído e estoque devolvido.")
    else:
        print("Operação cancelada.")


# ---------------------------------------------------------------
# Relatórios
# ---------------------------------------------------------------

def pedidos_de_um_cliente():
    listar_clientes()
    if not clientes:
        return
    cliente_id = ler_inteiro("\nId do cliente: ")
    cliente = buscar_por_id(clientes, cliente_id)
    if cliente is None:
        print("Cliente não encontrado.")
        return
    dele = [p for p in pedidos if p["cliente_id"] == cliente_id]
    if not dele:
        print(f"{cliente['nome']} ainda não fez pedidos.")
        return
    for pedido in dele:
        mostrar_pedido(pedido)
    gasto = sum(total_do_pedido(p) for p in dele)
    print(f"\nTotal gasto por {cliente['nome']}: {formatar_preco(gasto)}")


def produtos_mais_vendidos():
    print("\n--- Produtos mais vendidos ---")
    vendas = {}
    for pedido in pedidos:
        for item in pedido["itens"]:
            vendas[item["produto_id"]] = vendas.get(item["produto_id"], 0) + item["quantidade"]
    if not vendas:
        print("Ainda não há vendas.")
        return
    ranking = sorted(vendas.items(), key=lambda par: par[1], reverse=True)
    for produto_id, quantidade in ranking:
        produto = buscar_por_id(produtos, produto_id)
        nome = produto["nome"] if produto else f"(produto {produto_id} removido)"
        print(f"{nome}: {quantidade} unidade(s)")


def total_vendido():
    total = sum(total_do_pedido(p) for p in pedidos)
    print(f"\nTotal vendido: {formatar_preco(total)} em {len(pedidos)} pedido(s).")


# ---------------------------------------------------------------
# Menus
# ---------------------------------------------------------------

def menu_clientes():
    while True:
        print("\n=== CLIENTES ===")
        print("1 - Cadastrar cliente")
        print("2 - Listar clientes")
        print("3 - Excluir cliente")
        print("0 - Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            cadastrar_cliente()
        elif opcao == "2":
            listar_clientes()
        elif opcao == "3":
            excluir_cliente()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def menu_produtos():
    while True:
        print("\n=== PRODUTOS ===")
        print("1 - Cadastrar produto")
        print("2 - Listar produtos")
        print("3 - Repor estoque")
        print("4 - Excluir produto")
        print("0 - Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            listar_produtos()
        elif opcao == "3":
            repor_estoque()
        elif opcao == "4":
            excluir_produto()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def menu_pedidos():
    while True:
        print("\n=== PEDIDOS ===")
        print("1 - Criar pedido")
        print("2 - Listar pedidos")
        print("3 - Excluir pedido")
        print("0 - Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            criar_pedido()
        elif opcao == "2":
            listar_pedidos()
        elif opcao == "3":
            excluir_pedido()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def menu_relatorios():
    while True:
        print("\n=== RELATÓRIOS ===")
        print("1 - Pedidos de um cliente")
        print("2 - Produtos mais vendidos")
        print("3 - Total vendido")
        print("0 - Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            pedidos_de_um_cliente()
        elif opcao == "2":
            produtos_mais_vendidos()
        elif opcao == "3":
            total_vendido()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def main():
    carregar()
    while True:
        print("\n===== SISTEMA DE CADASTRO =====")
        print("1 - Clientes")
        print("2 - Produtos")
        print("3 - Pedidos")
        print("4 - Relatórios")
        print("0 - Sair")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            menu_clientes()
        elif opcao == "2":
            menu_produtos()
        elif opcao == "3":
            menu_pedidos()
        elif opcao == "4":
            menu_relatorios()
        elif opcao == "0":
            print("Até mais!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
