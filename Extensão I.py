import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, END, filedialog
import datetime
import os
import pickle
import tkinter as tk
import tkinter.ttk as ttk
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

class Venda:
    def __init__(self, marca, nome, preco, quantidade, tele_entrega, valor_tele, data):
        self.marca = marca
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade
        self.tele_entrega = tele_entrega
        self.valor_tele = valor_tele
        self.data = data

    def __str__(self):
        entrega = "Sim" if self.tele_entrega else "Não"
        valor_tele = f"R$ {self.valor_tele:.2f}" if self.tele_entrega else "-"
        return (f"Data: {self.data.strftime('%d/%m/%Y')} | Marca: {self.marca} | Nome: {self.nome} | "
                f"Preço: R$ {self.preco:.2f} | Quantidade: {self.quantidade} | Tele-entrega: {entrega} | "
                f"Valor Tele-entrega: {valor_tele}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciamento de Vendas de Bebidas")
        self.vendas = []

        self.arquivo_vendas = "vendas_todas.pkl"
        self.carregar_vendas()

        frame = tb.Frame(root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        # Permite que as colunas cresçam proporcionalmente
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=3)

        tb.Label(frame, text="Marca:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky=W+E, pady=5)
        self.marca_entry = tb.Entry(frame, width=30, bootstyle="success")
        self.marca_entry.grid(row=0, column=1, pady=5, sticky="ew")

        tb.Label(frame, text="Nome:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky=W+E, pady=5)
        self.nome_entry = tb.Entry(frame, width=30)
        self.nome_entry.grid(row=1, column=1, pady=5, sticky="ew")

        tb.Label(frame, text="Preço (R$):", font=("Segoe UI", 12)).grid(row=2, column=0, sticky=W+E, pady=5)
        self.preco_entry = tb.Entry(frame, width=30)
        self.preco_entry.grid(row=2, column=1, pady=5, sticky="ew")

        tb.Label(frame, text="Quantidade:", font=("Segoe UI", 12)).grid(row=3, column=0, sticky=W+E, pady=5)
        self.quantidade_entry = tb.Entry(frame, width=30)
        self.quantidade_entry.grid(row=3, column=1, pady=5, sticky="ew")

        # Checkbox Tele-entrega (acima do campo de valor e alinhado à esquerda)
        tb.Label(frame, text="").grid(row=4, column=0, sticky=W+E)
        self.tele_var = tb.BooleanVar()
        self.tele_check = tb.Checkbutton(
            frame, text="Tele-entrega", variable=self.tele_var, bootstyle="success", command=self.toggle_tele_entry
        )
        self.tele_check.grid(row=4, column=1, sticky="w", padx=0, pady=(0, 0))

        tb.Label(frame, text="Valor Tele-entrega (R$):", font=("Segoe UI", 12)).grid(row=5, column=0, sticky=W+E, pady=5)
        self.valor_tele_entry = tb.Entry(frame, width=30)
        self.valor_tele_entry.grid(row=5, column=1, pady=5, sticky="ew")
        self.valor_tele_entry.bind("<KeyRelease>", self.on_valor_tele_change)

        # Botão para registrar venda
        self.btn_vender = tb.Button(
            frame,
            text="Registrar Venda",
            bootstyle="primary",
            command=self.registrar_venda
        )
        self.btn_vender.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky=EW)

        # Botão para emitir relatório
        self.btn_relatorio = tb.Button(
            frame,
            text="Emitir Relatório do Mês Atual",
            bootstyle="info",
            command=self.emitir_relatorio
        )
        self.btn_relatorio.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky=EW)

        # Botão para editar item selecionado (verde claro)
        self.btn_editar = tb.Button(
            frame,
            text="Editar Item Selecionado",
            bootstyle="success",
            command=self.editar_item_relatorio
        )
        self.btn_editar.grid(row=8, column=0, columnspan=2, pady=(10, 0), sticky=EW)

        # Botão para excluir item selecionado (laranja claro)
        self.btn_excluir = tb.Button(
            frame,
            text="Excluir Item Selecionado",
            bootstyle="warning",
            command=self.excluir_item_relatorio
        )
        self.btn_excluir.grid(row=9, column=0, columnspan=2, pady=(10, 0), sticky=EW)

        # Label e área do relatório mais para baixo e maior
        tb.Label(frame, text="Vendas do mês:", font=("Segoe UI", 12, "bold")).grid(
            row=10, column=0, columnspan=2, pady=(30, 0), sticky=EW
        )
        self.lista_vendas = tb.ScrolledText(frame, width=60, height=16, font=("Consolas", 10))
        self.lista_vendas.grid(row=11, column=0, columnspan=2, pady=5, sticky="nsew")

        # Destacar linha selecionada em azul claro
        self.lista_vendas.bind("<ButtonRelease-1>", self.destacar_linha_selecionada)
        self.lista_vendas.bind("<KeyRelease-Up>", self.destacar_linha_selecionada)
        self.lista_vendas.bind("<KeyRelease-Down>", self.destacar_linha_selecionada)

        # Botão para limpar relatório (vermelho)
        self.btn_limpar_relatorio = tb.Button(
            frame,
            text="Limpar Relatório do Mês",
            bootstyle="danger",
            command=self.confirmar_limpar_relatorio
        )
        self.btn_limpar_relatorio.grid(row=12, column=0, columnspan=2, pady=(10, 0), sticky=EW)

        # Não há métodos get_pedido_selecionado, alterar_pedido, excluir_pedido, destacar_linha_selecionada

    def salvar_vendas(self):
        with open(self.arquivo_vendas, "wb") as f:
            pickle.dump(self.vendas, f)

    def carregar_vendas(self):
        if os.path.exists(self.arquivo_vendas):
            with open(self.arquivo_vendas, "rb") as f:
                self.vendas = pickle.load(f)
        else:
            self.vendas = []

    def fechar_app(self):
        self.salvar_vendas()
        self.root.destroy()

    def atualizar_lista_vendas_mes_atual(self):
        # Mostra apenas vendas do mês atual na tela principal
        self.lista_vendas.delete(1.0, END)
        agora = datetime.datetime.now()
        total_vendido = 0
        header = (
            f"{'Data':<12} | {'Marca':<15} | {'Nome':<25} | {'Preço':>12} | {'Qtd':>8} | {'Tele-entrega':^13} | {'Valor Tele-entrega':>18}"
        )
        self.lista_vendas.insert(END, header + "\n")
        self.lista_vendas.insert(END, "-" * len(header) + "\n")
        for venda in self.vendas:
            if venda.data.month == agora.month and venda.data.year == agora.year:
                self.lista_vendas.insert(
                    END,
                    f"{venda.data.strftime('%d/%m/%Y'):<12} | "
                    f"{venda.marca:<15} | "
                    f"{venda.nome:<25} | "
                    f"R$ {venda.preco:>10,.2f} | "
                    f"{venda.quantidade:>8,} | "
                    f"{'Sim' if venda.tele_entrega else 'Não':^13} | "
                    f"{(f'R$ {venda.valor_tele:>6,.2f}' if venda.tele_entrega else '-'):>18}\n"
                )
                total_vendido += venda.preco * venda.quantidade + (venda.valor_tele if venda.tele_entrega else 0)
        self.lista_vendas.insert(END, "-" * len(header) + "\n")
        self.lista_vendas.insert(END, f"{'TOTAL VENDIDO NO MÊS:':<80} R$ {total_vendido:,.2f}\n")

    def registrar_venda(self):
        marca = self.marca_entry.get().strip()
        nome = self.nome_entry.get().strip()
        try:
            preco = float(self.preco_entry.get())
            quantidade = int(self.quantidade_entry.get())
            valor_tele = float(self.valor_tele_entry.get()) if self.tele_var.get() else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Preço, quantidade e valor de tele-entrega devem ser numéricos.")
            return

        if not marca or not nome or preco <= 0 or quantidade <= 0 or (self.tele_var.get() and valor_tele <= 0):
            messagebox.showerror("Erro", "Preencha todos os campos corretamente.")
            return

        tele_entrega = self.tele_var.get()
        data = datetime.datetime.now()
        venda = Venda(marca, nome, preco, quantidade, tele_entrega, valor_tele, data)
        self.vendas.append(venda)
        self.atualizar_lista_vendas_mes_atual()
        self.salvar_vendas()
        self.limpar_campos()

    def emitir_relatorio(self):
        if not self.vendas:
            messagebox.showinfo("Relatório", "Nenhuma venda registrada.")
            return

        agora = datetime.datetime.now()
        vendas_mes = [
            v for v in self.vendas
            if v.data.month == agora.month and v.data.year == agora.year
        ]

        if not vendas_mes:
            messagebox.showinfo("Relatório", "Nenhuma venda registrada para o mês atual.")
            return

        # Cabeçalho com largura fixa para cada coluna
        header = (
            f"{'Data':<12} | {'Marca':<15} | {'Nome':<25} | {'Preço':>12} | {'Qtd':>8} | {'Tele-entrega':^13} | {'Valor Tele-entrega':>18}"
        )
        relatorio = [header]
        relatorio.append("-" * len(header))
        for v in vendas_mes:
            relatorio.append(
                f"{v.data.strftime('%d/%m/%Y'):<12} | "
                f"{v.marca:<15} | "
                f"{v.nome:<25} | "
                f"R$ {v.preco:>10,.2f} | "
                f"{v.quantidade:>8,} | "
                f"{'Sim' if v.tele_entrega else 'Não':^13} | "
                f"{(f'R$ {v.valor_tele:>6,.2f}' if v.tele_entrega else '-'):>18}"
            )
        total_vendido = sum(v.preco * v.quantidade + (v.valor_tele if v.tele_entrega else 0) for v in vendas_mes)
        relatorio.append("-" * len(header))
        # Linha final: total apenas na última coluna
        relatorio.append(
            f"{'':<12} | {'':<15} | {'':<25} | {'':>12} | {'':>8} | {'':^13} | {'TOTAL: R$ ' + format(total_vendido, ',.2f'):>18}"
        )

        # Pergunta onde salvar o PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Salvar relatório em PDF"
        )
        if not file_path:
            return

        # Cria o PDF em modo paisagem (horizontal)
        c = canvas.Canvas(file_path, pagesize=landscape(A4))
        width, height = landscape(A4)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 50, f"Relatório de Vendas - {agora.strftime('%m/%Y')}")
        c.setFont("Courier", 10)  # Fonte monoespaçada para alinhamento

        y = height - 80
        for linha in relatorio:
            c.drawString(40, y, linha)
            y -= 15
            if y < 40:
                c.showPage()
                c.setFont("Courier", 10)
                y = height - 40

        c.save()
        messagebox.showinfo("Relatório", f"Relatório salvo em:\n{file_path}")

        # Também mostra o total vendido na interface
        messagebox.showinfo("Total Vendido", f"Total vendido no mês: R$ {total_vendido:,.2f}")

    def confirmar_limpar_relatorio(self):
        resposta = messagebox.askyesno(
            "Confirmação",
            "Tem certeza que deseja limpar TODOS os dados do relatório do mês atual?\nEssa ação não pode ser desfeita."
        )
        if resposta:
            self.limpar_relatorio_mes_atual()

    def limpar_relatorio_mes_atual(self):
        agora = datetime.datetime.now()
        # Remove apenas as vendas do mês atual
        self.vendas = [
            v for v in self.vendas
            if not (v.data.month == agora.month and v.data.year == agora.year)
        ]
        self.salvar_vendas()
        self.atualizar_lista_vendas_mes_atual()
        messagebox.showinfo("Relatório", "Relatório do mês atual limpo com sucesso!")

    def toggle_tele_entry(self):
        if self.tele_var.get():
            self.valor_tele_entry.config(state="normal")
        else:
            self.valor_tele_entry.delete(0, END)
            self.valor_tele_entry.config(state="disabled")

    def on_valor_tele_change(self, event=None):
        valor = self.valor_tele_entry.get()
        try:
            if float(valor) > 0:
                self.tele_var.set(True)
                self.valor_tele_entry.config(state="normal")
            else:
                self.tele_var.set(False)
                self.valor_tele_entry.delete(0, END)
                self.valor_tele_entry.config(state="disabled")
        except ValueError:
            if valor.strip() == "":
                self.tele_var.set(False)
                self.valor_tele_entry.config(state="disabled")

    def limpar_campos(self):
        self.marca_entry.delete(0, END)
        self.nome_entry.delete(0, END)
        self.preco_entry.delete(0, END)
        self.quantidade_entry.delete(0, END)
        self.valor_tele_entry.delete(0, END)
        self.valor_tele_entry.config(state="disabled")
        self.tele_var.set(False)

    def get_linha_selecionada(self):
        try:
            linha = int(self.lista_vendas.index("insert").split('.')[0])
            index = linha - 3  # Desconta cabeçalho e separador
            if index < 0:
                return None
            agora = datetime.datetime.now()
            vendas_mes = [
                v for v in self.vendas
                if v.data.month == agora.month and v.data.year == agora.year
            ]
            if index >= len(vendas_mes):
                return None
            return index, vendas_mes
        except Exception:
            return None

    def destacar_linha_selecionada(self, event=None):
        self.lista_vendas.tag_remove("destaque", "1.0", END)
        try:
            linha = int(self.lista_vendas.index("insert").split('.')[0])
            if linha > 2:
                self.lista_vendas.tag_add("destaque", f"{linha}.0", f"{linha}.end")
                self.lista_vendas.tag_config("destaque", background="#add8e6")  # azul claro
        except Exception:
            pass

    def editar_item_relatorio(self):
        resultado = self.get_linha_selecionada()
        if not resultado:
            messagebox.showwarning("Atenção", "Selecione um item válido para editar.")
            return
        index, vendas_mes = resultado
        venda = vendas_mes[index]
        # Preenche os campos para edição
        self.marca_entry.delete(0, END)
        self.marca_entry.insert(0, venda.marca)
        self.nome_entry.delete(0, END)
        self.nome_entry.insert(0, venda.nome)
        self.preco_entry.delete(0, END)
        self.preco_entry.insert(0, str(venda.preco))
        self.quantidade_entry.delete(0, END)
        self.quantidade_entry.insert(0, str(venda.quantidade))
        self.tele_var.set(venda.tele_entrega)
        if venda.tele_entrega:
            self.valor_tele_entry.config(state="normal")
            self.valor_tele_entry.delete(0, END)
            self.valor_tele_entry.insert(0, str(venda.valor_tele))
        else:
            self.valor_tele_entry.delete(0, END)
            self.valor_tele_entry.config(state="disabled")
        # Remove o item antigo
        self.vendas.remove(venda)
        self.atualizar_lista_vendas_mes_atual()
        self.salvar_vendas()
        messagebox.showinfo("Alteração", "Item alterado! Confirme os dados e clique em 'Registrar Venda' para salvar as alterações.")

    def excluir_item_relatorio(self):
        resultado = self.get_linha_selecionada()
        if not resultado:
            messagebox.showwarning("Atenção", "Selecione um item válido para excluir.")
            return
        index, vendas_mes = resultado
        venda = vendas_mes[index]
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este item?"):
            self.vendas.remove(venda)
            self.atualizar_lista_vendas_mes_atual()
            self.salvar_vendas()
            messagebox.showinfo("Excluído", "Item excluído com sucesso.")

if __name__ == "__main__":
    root = tk.Tk()
    tb.Style("darkly")
    application = App(root)
    application.toggle_tele_entry()
    root.mainloop()