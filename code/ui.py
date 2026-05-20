import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from importlib import util

MODULE_PATH = os.path.join(os.path.dirname(__file__), 'gestor_segurança.py')

if not os.path.exists(MODULE_PATH):
    raise FileNotFoundError(f"Arquivo de dados não encontrado: {MODULE_PATH}")

spec = util.spec_from_file_location('gestor_seguranca', MODULE_PATH)
gestor_mod = util.module_from_spec(spec)
spec.loader.exec_module(gestor_mod)
GestorSeguranca = gestor_mod.GestorSeguranca


class GestorApp:
    def __init__(self, root):
        self.gestor = GestorSeguranca()
        self.root = root
        self.root.title('Gestor de Estoque, Orçamento e Vendas')
        self.root.geometry('1040x720')
        self.root.configure(bg='#111827')

        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TLabel', background='#111827', foreground='#f8fafc', font=('Segoe UI', 10))
        style.configure('TButton', background='#0f172a', foreground='#f8fafc', font=('Segoe UI', 10, 'bold'), padding=8)
        style.map('TButton', background=[('active', '#2563eb')])
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#38bdf8')
        style.configure('Accent.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#a5f3fc')

        self.build_header()
        self.build_left_panel()
        self.build_right_panel()
        self.build_output_panel()
        self.mostrar_intro()

    def build_header(self):
        header = ttk.Label(self.root, text='Microempresa Inteligente de Vendas e Estoque', style='Header.TLabel')
        header.place(x=24, y=16)

        subtitle = ttk.Label(
            self.root,
            text='Controle de estoque, orçamento de projetos e dicas para vender mais usando tecnologia.',
            style='TLabel'
        )
        subtitle.place(x=24, y=52)

    def build_left_panel(self):
        painel = tk.Frame(self.root, bg='#0f172a', bd=0, highlightthickness=0)
        painel.place(x=24, y=100, width=480, height=360)

        ttk.Label(painel, text='Cadastro de Produto', style='Accent.TLabel').place(x=20, y=16)

        campos = [
            ('Nome do produto', 'nome'),
            ('Tipo', 'tipo'),
            ('Valor unitário (R$)', 'valor'),
            ('Unidade', 'unidade'),
            ('Estoque atual', 'estoque'),
            ('Descrição', 'descricao')
        ]

        self.inputs = {}
        y = 56
        for label_text, key in campos:
            ttk.Label(painel, text=label_text).place(x=20, y=y)
            entry = ttk.Entry(painel, width=34)
            entry.place(x=20, y=y+24)
            self.inputs[key] = entry
            y += 72

        botao = ttk.Button(painel, text='Adicionar ao estoque', command=self.adicionar_produto)
        botao.place(x=20, y=320)

    def build_right_panel(self):
        painel = tk.Frame(self.root, bg='#0f172a', bd=0, highlightthickness=0)
        painel.place(x=520, y=100, width=500, height=360)

        ttk.Label(painel, text='Orçamento e Dicas de Venda', style='Accent.TLabel').place(x=20, y=16)

        ttk.Label(painel, text='Nome do projeto').place(x=20, y=58)
        self.projeto_nome = ttk.Entry(painel, width=30)
        self.projeto_nome.place(x=20, y=82)

        ttk.Label(painel, text='Cliente').place(x=20, y=116)
        self.projeto_cliente = ttk.Entry(painel, width=30)
        self.projeto_cliente.place(x=20, y=140)

        ttk.Label(painel, text='Produtos do projeto (nome:quantidade)').place(x=20, y=174)
        self.projeto_produtos = tk.Text(painel, width=28, height=6, bg='#1e293b', fg='#e2e8f0', insertbackground='#f8fafc', bd=1, relief='solid')
        self.projeto_produtos.place(x=20, y=198)

        ttk.Label(painel, text='Tipo de ambiente').place(x=20, y=320)
        self.ambiente_tipo = ttk.Combobox(painel, values=['interno', 'externo'], state='readonly', width=16)
        self.ambiente_tipo.set('interno')
        self.ambiente_tipo.place(x=20, y=344)

        botao_orcamento = ttk.Button(painel, text='Gerar Orçamento', command=self.gerar_orcamento)
        botao_orcamento.place(x=20, y=390)

        self.projeto_status = tk.Label(painel, text='Nenhum projeto gerado ainda.', bg='#0f172a', fg='#94a3b8', font=('Segoe UI', 9, 'italic'))
        self.projeto_status.place(x=20, y=430)

        ttk.Label(painel, text='Busca por produto para dicas').place(x=260, y=236)
        self.produto_busca = ttk.Entry(painel, width=20)
        self.produto_busca.place(x=260, y=260)

        botao_dicas = ttk.Button(painel, text='Gerar Dicas de Vendas', command=self.gerar_dicas)
        botao_dicas.place(x=260, y=310)

    def build_output_panel(self):
        painel = tk.Frame(self.root, bg='#0f172a', bd=0)
        painel.place(x=24, y=480, width=996, height=220)

        ttk.Label(painel, text='Relatório', style='Accent.TLabel').place(x=20, y=16)
        self.output_text = ScrolledText(painel, bg='#0d1117', fg='#e2e8f0', insertbackground='#f8fafc', font=('Segoe UI', 10), bd=0)
        self.output_text.place(x=20, y=48, width=956, height=156)
        self.output_text.configure(state='disabled')

    def mostrar_intro(self):
        self.mostrar_texto(
            'Bem-vindo ao sistema de gestão para microempresas!\n'
            'Use a interface à esquerda para cadastrar produtos e estoque.\n'
            'No lado direito, gere orçamentos automáticos e dicas de vendas tecno-friendly.\n'
            'A cada ação, o sistema calcula estoque, orçamento e sugestões de vendas realisticamente.'
        )

    def adicionar_produto(self):
        nome = self.inputs['nome'].get().strip()
        tipo = self.inputs['tipo'].get().strip()
        valor = self.inputs['valor'].get().strip()
        unidade = self.inputs['unidade'].get().strip()
        descricao = self.inputs['descricao'].get().strip()
        estoque = self.inputs['estoque'].get().strip()

        if not nome or not tipo or not valor or not unidade:
            messagebox.showwarning('Atenção', 'Preencha nome, tipo, valor e unidade.')
            return

        try:
            valor = float(valor.replace(',', '.'))
            estoque = float(estoque.replace(',', '.')) if estoque else 0
        except ValueError:
            messagebox.showerror('Erro', 'Informe valores numéricos válidos para valor e estoque.')
            return

        self.gestor.adicionar_equipamento(nome, tipo, valor, unidade, descricao, estoque)
        self.mostrar_texto(f'✅ Produto cadastrado: {nome} | Estoque: {estoque} {unidade} | Valor R$ {valor:.2f}')
        for field in self.inputs.values():
            field.delete(0, tk.END)

    def parse_project_products(self, raw_text):
        itens = []
        for parte in raw_text.split(','):
            texto = parte.strip()
            if not texto:
                continue
            if ':' in texto:
                nome, qtd = texto.split(':', 1)
                try:
                    quantidade = float(qtd.strip().replace(',', '.'))
                except ValueError:
                    quantidade = 1
                itens.append((nome.strip(), quantidade))
            else:
                itens.append((texto, 1))
        return itens

    def gerar_orcamento(self):
        nome_projeto = self.projeto_nome.get().strip() or 'Projeto Comercial'
        cliente = self.projeto_cliente.get().strip() or 'Cliente Oculto'
        produtos_texto = self.projeto_produtos.get('1.0', tk.END).strip()
        tipo = self.ambiente_tipo.get()

        if not produtos_texto:
            messagebox.showwarning('Atenção', 'Informe os produtos que serão utilizados no projeto.')
            return

        produtos = self.parse_project_products(produtos_texto)
        if not produtos:
            messagebox.showwarning('Atenção', 'Informe ao menos um produto válido para o projeto.')
            return

        equipamentos = self.gestor.listar_equipamentos()
        produtos_encontrados = []
        produtos_faltando = []
        total_estimado = 0

        projeto_id = self.gestor.criar_projeto(nome_projeto, cliente)

        for nome, quantidade in produtos:
            equipamento = next((item for item in equipamentos if item['nome'].lower() == nome.lower()), None)
            if equipamento:
                self.gestor.adicionar_item_projeto(projeto_id, equipamento['id'], quantidade)
                produtos_encontrados.append(f'{equipamento["nome"]} x{quantidade}')
                total_estimado += equipamento['valor'] * quantidade
            else:
                produtos_faltando.append(nome)

        if not produtos_encontrados:
            self.projeto_status.config(text='Projeto não adicionado: nenhum produto cadastrado foi encontrado.')
            self.mostrar_texto('⚠️ Projeto não gerado. Nenhum dos produtos informados está cadastrado no estoque.')
            return

        status_text = f'Projeto adicionado: {nome_projeto}'
        if produtos_faltando:
            status_text += f' (produto(s) não encontrado(s): {", ".join(produtos_faltando)})'
        self.projeto_status.config(text=status_text)

        self.mostrar_texto(
            f'📌 Projeto "{nome_projeto}" adicionado!\n'
            f'Cliente: {cliente}\n'
            f'Tipo de ambiente: {tipo}\n'
            f'Produtos utilizados:\n  - {"\n  - ".join(produtos_encontrados)}\n'
            f'\nValor total estimado: R$ {total_estimado:.2f}'
        )

    def gerar_dicas(self):
        produto = self.produto_busca.get().strip()
        resultado = self.gestor.gerar_dicas_venda(produto)
        texto = f'💡 Dicas de vendas para: {resultado["produto"]}\n\n'
        for dica in resultado['dicas']:
            texto += f'• {dica}\n'
        self.mostrar_texto(texto)

    def mostrar_texto(self, texto):
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, texto)
        self.output_text.configure(state='disabled')


def run_app():
    root = tk.Tk()
    app = GestorApp(root)
    root.mainloop()
