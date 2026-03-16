import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import sys
import os
import json
import datetime
import time
import subprocess
import webbrowser
from src.bot_pyautogui import executar_consulta_em_lote, executar_consulta_individual, resource_path

class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FGTS Digital RPA")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Variáveis de controle globais
        self.caminho_excel = tk.StringVar()
        self.modo_consulta = tk.StringVar(value="lote") # 'lote' ou 'individual'
        self.cnpj_individual = tk.StringVar()
        self.nome_individual = tk.StringVar()
        self.codigo_individual = tk.StringVar()
        self.competencia_individual = tk.StringVar()
        self.grupo_individual = tk.StringVar()
        
        # Variáveis MySQL
        self.db_host = tk.StringVar(value="mysql831.umbler.com")
        self.db_port = tk.StringVar(value="41890")
        self.db_user = tk.StringVar()
        self.db_pass = tk.StringVar()
        self.db_name = tk.StringVar()
        
        # Configurações por serviço
        self.servicos = {
            "fgts_digital": {
                "nome": "FGTS Digital",
                "pasta": tk.StringVar(),
                "ativo": tk.BooleanVar(value=True),
                "intervalo": tk.StringVar(value="30"),
                "prox_execucao": None
            },
            "fgts_digital_site": {
                "nome": "FGTS Digital Site",
                "pasta": tk.StringVar(),
                "ativo": tk.BooleanVar(value=True),
                "intervalo": tk.StringVar(value="30"),
                "prox_execucao": None
            },
            "onvio": {
                "nome": "ONVIO",
                "pasta": tk.StringVar(),
                "ativo": tk.BooleanVar(value=True),
                "intervalo": tk.StringVar(value="30"),
                "prox_execucao": None
            }
        }

        self.is_running = False
        self.is_paused = False
        self.thread = None
        self.server_process = None
        self.config_file = "config_multi.json"
        
        # Configurar interface
        self.criar_interface()
        
        # Carregar configurações salvas
        self.carregar_config()

        # Estilização das Abas (Bordas e Separação)
        style = ttk.Style()
        try:
            style.theme_use('clam') # Tema que permite maior customização de bordas
        except: pass
        
        style.configure("TNotebook.Tab", 
                        padding=[12, 5], 
                        font=("Arial", 9, "bold"),
                        borderwidth=1,
                        relief="raised")
        
        style.map("TNotebook.Tab",
                  background=[("selected", "#ffffff"), ("active", "#e1e1e1")],
                  foreground=[("selected", "#000000")],
                  expand=[("selected", [1, 1, 1, 0])]) # Expande levemente a aba selecionada

    def salvar_config(self):
        """Salva as configurações atuais em um arquivo JSON"""
        config = {
            "excel_path": self.caminho_excel.get(),
            "fgts_digital": {
                "dest_path": self.servicos["fgts_digital"]["pasta"].get(),
                "active": self.servicos["fgts_digital"]["ativo"].get(),
                "interval": self.servicos["fgts_digital"]["intervalo"].get(),
                "next_run": self.servicos["fgts_digital"]["prox_execucao"].isoformat() if self.servicos["fgts_digital"]["prox_execucao"] else None
            },
            "fgts_digital_site": {
                "dest_path": self.servicos["fgts_digital_site"]["pasta"].get(),
                "active": self.servicos["fgts_digital_site"]["ativo"].get(),
                "interval": self.servicos["fgts_digital_site"]["intervalo"].get(),
                "next_run": self.servicos["fgts_digital_site"]["prox_execucao"].isoformat() if self.servicos["fgts_digital_site"]["prox_execucao"] else None
            },
            "onvio": {
                "dest_path": self.servicos["onvio"]["pasta"].get(),
                "active": self.servicos["onvio"]["ativo"].get(),
                "interval": self.servicos["onvio"]["intervalo"].get(),
                "next_run": self.servicos["onvio"]["prox_execucao"].isoformat() if self.servicos["onvio"]["prox_execucao"] else None
            },
            "mysql_config": {
                "host": self.db_host.get(),
                "port": self.db_port.get(),
                "user": self.db_user.get(),
                "pass": self.db_pass.get(),
                "database": self.db_name.get()
            }
        }
        
        # Adicionar modo atual
        config["consulta_mode"] = self.modo_consulta.get()
        
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def carregar_config(self):
        """Carrega as configurações salvas"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.caminho_excel.set(config.get("excel_path", ""))
                    
                    fgts_digital_conf = config.get("fgts_digital", {})
                    self.servicos["fgts_digital"]["pasta"].set(fgts_digital_conf.get("dest_path", ""))
                    self.servicos["fgts_digital"]["ativo"].set(fgts_digital_conf.get("active", True))
                    self.servicos["fgts_digital"]["intervalo"].set(fgts_digital_conf.get("interval", "30"))
                    if fgts_digital_conf.get("next_run"):
                        try:
                            self.servicos["fgts_digital"]["prox_execucao"] = datetime.datetime.fromisoformat(fgts_digital_conf.get("next_run"))
                        except: pass

                    fgts_digital_site_conf = config.get("fgts_digital_site", {})
                    self.servicos["fgts_digital_site"]["pasta"].set(fgts_digital_site_conf.get("dest_path", ""))
                    self.servicos["fgts_digital_site"]["ativo"].set(fgts_digital_site_conf.get("active", True))
                    self.servicos["fgts_digital_site"]["intervalo"].set(fgts_digital_site_conf.get("interval", "30"))
                    if fgts_digital_site_conf.get("next_run"):
                        try:
                            self.servicos["fgts_digital_site"]["prox_execucao"] = datetime.datetime.fromisoformat(fgts_digital_site_conf.get("next_run"))
                        except: pass

                    onvio_conf = config.get("onvio", {})
                    self.servicos["onvio"]["pasta"].set(onvio_conf.get("dest_path", ""))
                    self.servicos["onvio"]["ativo"].set(onvio_conf.get("active", True))
                    self.servicos["onvio"]["intervalo"].set(onvio_conf.get("interval", "30"))
                    if onvio_conf.get("next_run"):
                        try:
                            self.servicos["onvio"]["prox_execucao"] = datetime.datetime.fromisoformat(onvio_conf.get("next_run"))
                        except: pass

                    # Carregar dados individuais (opcional para facilitar re-teste)
                    self.cnpj_individual.set(config.get("cnpj_individual", ""))
                    self.nome_individual.set(config.get("nome_individual", ""))
                    self.codigo_individual.set(config.get("codigo_individual", ""))
                    self.competencia_individual.set(config.get("competencia_individual", ""))
                    self.grupo_individual.set(config.get("grupo_individual", ""))

                    # Carregar último modo usado se houver (opcional) ou manter padrão
                    self.modo_consulta.set(config.get("consulta_mode", "lote"))
                    
                    mysql_config = config.get("mysql_config", {})
                    if mysql_config:
                        self.db_host.set(mysql_config.get("host", "mysql831.umbler.com"))
                        self.db_port.set(mysql_config.get("port", "41890"))
                        self.db_user.set(mysql_config.get("user", ""))
                        self.db_pass.set(mysql_config.get("pass", ""))
                        self.db_name.set(mysql_config.get("database", ""))
                        
                    self.toggle_modo_consulta() # Atualiza UI
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")

    def salvar_alteracoes_manual(self):
        """Salva as alterações manualmente e avisa o usuário"""
        self.salvar_config()
        messagebox.showinfo("Sucesso", "Configurações salvas e aplicadas para a próxima execução!")
        self.log("💾 Configurações atualizadas pelo usuário.")

    def executar_individual(self, key):
        """Executa apenas um serviço imediatamente"""
        if self.is_running:
            messagebox.showwarning("Atenção", "O robô já está em execução! Pare ou pause antes de iniciar uma execução manual.")
            return

        servico = self.servicos[key]
        if not servico["pasta"].get():
            messagebox.showerror("Erro", f"Selecione uma pasta de destino para {servico['nome']}!")
            return
        
        # Validação conforme o modo
        modo = self.modo_consulta.get()
        if modo == "lote":
            if not self.caminho_excel.get() or not os.path.exists(self.caminho_excel.get()):
                messagebox.showerror("Erro", "Selecione um arquivo Excel válido!")
                return
        elif modo == "mysql":
            if not self.db_user.get().strip() or not self.db_name.get().strip():
                messagebox.showerror("Erro", "Preencha o Usuário e o Banco de Dados!")
                return
        else: # individual
            if not self.cnpj_individual.get().strip():
                messagebox.showerror("Erro", "Digite um CNPJ válido!")
                return
            if not self.nome_individual.get().strip():
                messagebox.showerror("Erro", "Digite o Nome da Empresa!")
                return

        # Preparar UI
        self.is_running = True
        self.is_paused = False
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_finalizar.config(state=tk.NORMAL)
        
        self.log(f"\n⚡ Iniciando execução MANUAL de: {servico['nome']}")
        self.atualizar_status(f"Executando manual: {servico['nome']}...")
        
        # Thread dedicada para execução única
        self.thread = threading.Thread(target=self.executar_bot_individual, args=(key,), daemon=True)
        self.thread.start()

    def executar_bot_individual(self, key):
        """Wrapper para execução única"""
        
        original_stdout = sys.stdout
        try:
             # Redirecionar stdout (reutilizando a classe se possível ou redefinindo)
            class LogRedirector:
                def __init__(self, gui): self.gui = gui
                def write(self, m): 
                    if m.strip(): self.gui.log(m.strip())
                def flush(self): pass
            sys.stdout = LogRedirector(self)

            servico = self.servicos[key]
            
            if self.modo_consulta.get() == "lote":
                executar_consulta_em_lote(
                    self.caminho_excel.get(),
                    servico["pasta"].get(),
                    tipo_consulta=servico["nome"],
                    check_stop_callback=lambda: not self.is_running
                )
            else:
                executar_consulta_individual(
                    self.cnpj_individual.get(),
                    self.nome_individual.get(),
                    self.codigo_individual.get(),
                    servico["pasta"].get(),
                    competencia=self.competencia_individual.get(),
                    grupo=self.grupo_individual.get(),
                    tipo_consulta=servico["nome"],
                    check_stop_callback=lambda: not self.is_running
                )
            
            self.log(f"✅ Execução manual de {servico['nome']} concluída!")

        except Exception as e:
            self.log(f"❌ Erro na execução manual: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}")
        finally:
            sys.stdout = original_stdout
            self.resetar_botoes()

    def criar_aba_servico(self, notebook, key, titulo):
        frame = tk.Frame(notebook, padx=10, pady=10)
        notebook.add(frame, text=titulo)
        
        # Configurações Manuais (Box)
        man_frame = tk.LabelFrame(frame, text="Execução Manual & Configuração", padx=10, pady=10)
        man_frame.pack(fill=tk.X, pady=(0, 10))

        # Configuração de Pasta
        tk.Label(man_frame, text="Pasta de Destino:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        p_frame = tk.Frame(man_frame)
        p_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Entry(p_frame, textvariable=self.servicos[key]["pasta"], width=45).pack(side=tk.LEFT, padx=(0,5))
        tk.Button(p_frame, text="Selecionar", 
                 command=lambda k=key: self.selecionar_pasta(k)).pack(side=tk.LEFT)
        
        # Botão EXECUÇÃO MANUAL
        tk.Button(man_frame, text=f"⚡ Executar {titulo} Agora", 
                 command=lambda k=key: self.executar_individual(k),
                 bg="#607D8B", fg="white", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(0, 10))

        # Configuração de Agendamento
        ag_frame = tk.LabelFrame(frame, text="Agendamento Automático", padx=10, pady=10)
        ag_frame.pack(fill=tk.X)
        
        tk.Checkbutton(ag_frame, text="Ativar execução automática", 
                      variable=self.servicos[key]["ativo"], font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        i_frame = tk.Frame(ag_frame)
        i_frame.pack(fill=tk.X, pady=5)
        tk.Label(i_frame, text="Executar a cada:").pack(side=tk.LEFT)
        tk.Entry(i_frame, textvariable=self.servicos[key]["intervalo"], width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(i_frame, text="dias").pack(side=tk.LEFT)
        
        # Label de status da próxima execução
        self.servicos[key]["lbl_status"] = tk.Label(ag_frame, text="Status: Aguardando início", fg="gray")
        self.servicos[key]["lbl_status"].pack(anchor=tk.W, pady=(5,0))
        
    def selecionar_excel(self):
        filename = filedialog.askopenfilename(
            title="Selecione o arquivo Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.caminho_excel.set(filename)
            self.log(f"📄 Arquivo selecionado: {os.path.basename(filename)}")
    
    def selecionar_pasta(self, key):
        foldername = filedialog.askdirectory(title=f"Selecione a pasta de destino para {self.servicos[key]['nome']}")
        if foldername:
            self.servicos[key]["pasta"].set(foldername)
            self.log(f"📁 Pasta selecionada para {self.servicos[key]['nome']}: {foldername}")
    
    def log(self, mensagem):
        """Adiciona mensagem ao log (Thread-Safe)"""
        def _update():
            try:
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, mensagem + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
            except: pass
        self.root.after(0, _update)
    
    def atualizar_status(self, texto):
        """Atualiza a barra de status (Thread-Safe)"""
        def _update():
            try:
                self.status_label.config(text=texto)
            except: pass
        self.root.after(0, _update)

    def criar_interface(self):
        # --- STATUS BAR ---
        # Criado antes para garantir que fique no rodapé (pack side=BOTTOM)
        self.status_label = tk.Label(self.root, text="Pronto para iniciar", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # --- SCROLL CONTAINER ---
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # ID da janela no canvas para redimensionamento
        window_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Ajustar largura do frame interno ao redimensionar a janela
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(window_id, width=e.width))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.root.bind_all("<MouseWheel>", _on_mousewheel)

        # Frame principal (agora dentro do scrollable)
        main_frame = tk.Frame(self.scrollable_frame, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- HEADER (LOGO e TÍTULO) ---
        try:
            logo_path = resource_path("src/assets/logo.png")
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                self.root.iconphoto(False, self.logo_img)
                
                header_frame = tk.Frame(main_frame)
                header_frame.pack(pady=(0, 10))
                
                lbl_logo = tk.Label(header_frame, image=self.logo_img)
                lbl_logo.pack(side=tk.LEFT, padx=10)
                
                titulo = tk.Label(header_frame, text="FGTS Digital RPA", 
                                font=("Arial", 18, "bold"), fg="#2c3e50")
                titulo.pack(side=tk.LEFT)
            else:
                titulo = tk.Label(main_frame, text="Consultas Automáticas", 
                                font=("Arial", 16, "bold"))
                titulo.pack(pady=(0, 10))
        except Exception:
            pass
        
        # --- FONTE DE DADOS (Tabs ou Radio) ---
        data_frame = tk.LabelFrame(main_frame, text="Fonte de Dados", padx=10, pady=5)
        data_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Seletor de Modo
        mode_frame = tk.Frame(data_frame)
        mode_frame.pack(fill=tk.X, pady=(0,5))
        tk.Radiobutton(mode_frame, text="Consulta em Lote (Excel)", variable=self.modo_consulta, 
                       value="lote", command=self.toggle_modo_consulta).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Consulta Individual", variable=self.modo_consulta, 
                       value="individual", command=self.toggle_modo_consulta).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Banco de Dados (MySQL)", variable=self.modo_consulta, 
                       value="mysql", command=self.toggle_modo_consulta).pack(side=tk.LEFT, padx=10)

        # Container para Excel
        self.frame_excel = tk.Frame(data_frame)
        self.frame_excel.pack(fill=tk.X)
        
        tk.Entry(self.frame_excel, textvariable=self.caminho_excel, width=50).pack(side=tk.LEFT, padx=5)
        self.btn_procurar_excel = tk.Button(self.frame_excel, text="Procurar", command=self.selecionar_excel)
        self.btn_procurar_excel.pack(side=tk.LEFT)

        # Container para os campos MySQL (será gerenciado no toggle)
        self.frame_mysql_fields = tk.Frame(data_frame)
        self.frame_mysql_fields.pack_forget() # Inicialmente oculto
        
        # Grid para os campos MySQL
        row_idx = 0
        tk.Label(self.frame_mysql_fields, text="Host:").grid(row=row_idx, column=0, sticky=tk.W)
        tk.Entry(self.frame_mysql_fields, textvariable=self.db_host, width=30).grid(row=row_idx, column=1, padx=5, pady=2)
        tk.Label(self.frame_mysql_fields, text="Port:").grid(row=row_idx, column=2, sticky=tk.W)
        tk.Entry(self.frame_mysql_fields, textvariable=self.db_port, width=10).grid(row=row_idx, column=3, padx=5, pady=2)
        
        row_idx += 1
        tk.Label(self.frame_mysql_fields, text="User:").grid(row=row_idx, column=0, sticky=tk.W)
        tk.Entry(self.frame_mysql_fields, textvariable=self.db_user, width=30).grid(row=row_idx, column=1, padx=5, pady=2)
        tk.Label(self.frame_mysql_fields, text="Pass:").grid(row=row_idx, column=2, sticky=tk.W)
        tk.Entry(self.frame_mysql_fields, textvariable=self.db_pass, width=10, show="*").grid(row=row_idx, column=3, padx=5, pady=2)
        
        row_idx += 1
        tk.Label(self.frame_mysql_fields, text="Banco (DB):").grid(row=row_idx, column=0, sticky=tk.W)
        tk.Entry(self.frame_mysql_fields, textvariable=self.db_name, width=30).grid(row=row_idx, column=1, padx=5, pady=2, columnspan=3, sticky=tk.W)

        # Container para Individual
        self.frame_individual = tk.Frame(data_frame)
        # Não damos pack agora, o toggle fará isso
        
        tk.Label(self.frame_individual, text="CNPJ:").pack(side=tk.LEFT)
        tk.Entry(self.frame_individual, textvariable=self.cnpj_individual, width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.frame_individual, text="Nome:").pack(side=tk.LEFT)
        tk.Entry(self.frame_individual, textvariable=self.nome_individual, width=20).pack(side=tk.LEFT, padx=5)

        tk.Label(self.frame_individual, text="Código:").pack(side=tk.LEFT)
        tk.Entry(self.frame_individual, textvariable=self.codigo_individual, width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.frame_individual, text="Comp:").pack(side=tk.LEFT)
        tk.Entry(self.frame_individual, textvariable=self.competencia_individual, width=10).pack(side=tk.LEFT, padx=5)

        tk.Label(self.frame_individual, text="Grupo:").pack(side=tk.LEFT)
        tk.Entry(self.frame_individual, textvariable=self.grupo_individual, width=15).pack(side=tk.LEFT, padx=5)

        # Inicializa estado correto
        self.toggle_modo_consulta()

        # --- ABAS DE SERVIÇOS ---
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Criar abas
        self.criar_aba_servico(notebook, "fgts_digital", "FGTS Digital")
        self.criar_aba_servico(notebook, "fgts_digital_site", "FGTS Digital Site")
        self.criar_aba_servico(notebook, "onvio", "ONVIO")

        # --- CONTROLES ---
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_iniciar = tk.Button(control_frame, text="▶ Iniciar", 
                                     command=self.iniciar, bg="#4CAF50", fg="white",
                                     font=("Arial", 10, "bold"), width=15, height=2)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        
        self.btn_pausar = tk.Button(control_frame, text="⏸ Pausar", 
                                    command=self.pausar, bg="#FF9800", fg="white",
                                    font=("Arial", 10, "bold"), width=12, height=2,
                                    state=tk.NORMAL)
        self.btn_pausar.pack(side=tk.LEFT, padx=5)
        
        self.btn_finalizar = tk.Button(control_frame, text="⏹ Parar", 
                                       command=self.finalizar, bg="#F44336", fg="white",
                                       font=("Arial", 10, "bold"), width=12, height=2,
                                       state=tk.NORMAL)
        self.btn_finalizar.pack(side=tk.LEFT, padx=5)

        self.btn_salvar = tk.Button(control_frame, text="💾 Salvar", 
                                    command=self.salvar_alteracoes_manual, bg="#2196F3", fg="white",
                                    font=("Arial", 10, "bold"), width=12, height=2)
        self.btn_salvar.pack(side=tk.LEFT, padx=5)

        self.btn_web = tk.Button(control_frame, text="🌐 Abrir Dashboard", 
                                  command=self.iniciar_servidor_web, bg="#9C27B0", fg="white",
                                  font=("Arial", 10, "bold"), width=15, height=2)
        self.btn_web.pack(side=tk.LEFT, padx=5)

        # --- LOG ---
        log_frame = tk.LabelFrame(main_frame, text="Log de Execução", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        

    
    def iniciar(self):
        """Inicia o processamento"""
        # Salvar configurações atuais
        self.salvar_config()
        
        # Validação Excel
        # Validação conforme o modo
        modo = self.modo_consulta.get()
        if modo == "lote":
            if not self.caminho_excel.get() or not os.path.exists(self.caminho_excel.get()):
                messagebox.showerror("Erro", "Selecione um arquivo Excel válido para consulta em lote!")
                return
        elif modo == "mysql":
            if not self.db_user.get().strip() or not self.db_name.get().strip():
                messagebox.showerror("Erro", "Configure os dados de acesso ao Banco de Dados (Usuário e Banco)!")
                return
        else: # individual
            # Validação simples
            if not self.cnpj_individual.get().strip():
                messagebox.showerror("Erro", "Digite um CNPJ válido!")
                return
            if not self.nome_individual.get().strip():
                messagebox.showerror("Erro", "Digite o Nome da Empresa!")
                return
        
        # Validação Serviços
        servicos_para_executar = []
        algum_agendado = False

        for key, servico in self.servicos.items():
            # Considera selecionado se tiver pasta definida
            if servico["pasta"].get():
                try:
                    # Valida intervalo se estiver marcado como ativo
                    if servico["ativo"].get():
                        float(servico["intervalo"].get())
                        algum_agendado = True
                except ValueError:
                    messagebox.showerror("Erro", f"Intervalo inválido para {servico['nome']}!")
                    return
                
                servicos_para_executar.append(servico)
        
        if not servicos_para_executar:
            messagebox.showwarning(
                "Nenhum Serviço Configurado", 
                "Nenhum serviço tem pasta de destino definida!\n\n"
                "• Selecione uma pasta para o serviço que deseja executar."
            )
            return
        
        # Confirmação
        msg_lista = []
        for servico in servicos_para_executar:
            nome = servico["nome"]
            if servico["ativo"].get():
                dias = servico["intervalo"].get()
                msg_lista.append(f"• {nome}: Executar AGORA e repetir a cada {dias} dias")
            else:
                msg_lista.append(f"• {nome}: Executar APENAS UMA VEZ agora")

        msg_final = "\n".join(msg_lista)
        
        resposta = messagebox.askyesno(
            "Confirmar Início",
            f"Resumo da Operação:\n\n{msg_final}\n\n"
            "⚠️ IMPORTANTE:\n"
            "• Feche navegadores Chrome abertos\n"
            "• NÃO mexa no mouse/teclado durante a execução\n\n"
            "Deseja iniciar?"
        )
        
        if not resposta:
            return
        
        # Limpar log e resetar status
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Atualizar estado
        self.is_running = True
        self.is_paused = False
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_pausar.config(state=tk.NORMAL)
        self.btn_finalizar.config(state=tk.NORMAL)
        
        self.log("🚀 Iniciando agendador de tarefas...")
        self.atualizar_status("Iniciando...")
        
        # Executar em thread separada
        self.thread = threading.Thread(target=self.executar_bot, daemon=True)
        self.thread.start()

    def pausar(self):
        """Pausa/Resume o processamento"""
        if self.is_paused:
            self.is_paused = False
            self.btn_pausar.config(text="⏸ Pausar")
            self.log("▶ Processamento retomado")
        else:
            self.is_paused = True
            self.btn_pausar.config(text="▶ Retomar")
            self.log("⏸ Processamento pausado")

    def finalizar(self):
        """Finaliza o processamento"""
        resposta = messagebox.askyesno("Confirmar", "Deseja parar todas as execuções?")
        if resposta:
            self.is_running = False
            self.log("⏹ Parando execuções...")
            self.resetar_botoes()

    def resetar_botoes(self):
        """Reseta o estado dos botões (Thread-Safe)"""
        def _update():
            self.btn_iniciar.config(state=tk.NORMAL)
            self.btn_pausar.config(state=tk.DISABLED, text="⏸ Pausar")
            self.btn_finalizar.config(state=tk.DISABLED)
            self.is_running = False
            self.is_paused = False
            self.atualizar_status("Parado")
        self.root.after(0, _update)
    
    def executar_bot(self):
        """Executa o bot com agendamento múltiplo e execução manual inicial"""

        try:
            # Redirecionar stdout
            class LogRedirector:
                def __init__(self, gui): self.gui = gui
                def write(self, m): 
                    if m.strip(): self.gui.log(m.strip())
                def flush(self): pass
            
            original_stdout = sys.stdout
            sys.stdout = LogRedirector(self)

            # Inicializar agendamentos
            agora = datetime.datetime.now()
            
            # Dicionário para controlar execução imediata ("run_now")
            # Se tem pasta, deve rodar imediatamente
            run_now_flags = {} 

            tem_agendamento_ativo = False

            for key, servico in self.servicos.items():
                if servico["pasta"].get():
                    # Marca para rodar agora
                    run_now_flags[key] = True
                    
                    # Se for ativo (agendado), define a próxima execução também (após a manual/imediata)
                    # Mas a lógica abaixo vai tratar isso.
                    if servico["ativo"].get():
                        servico["prox_execucao"] = agora # Vai cair na verificação de tempo
                        tem_agendamento_ativo = True
                        self.atualizar_label_prox(key, agora)
                    else:
                        servico["prox_execucao"] = None # Sem agendamento, só manual
                        self.atualizar_label_simples(key, "Execução única pendente", "orange")
                else:
                    run_now_flags[key] = False
                    servico["prox_execucao"] = None

            while self.is_running:
                # Verificar pausas
                while self.is_paused and self.is_running:
                    time.sleep(1)
                
                if not self.is_running: break

                executou_algo = False
                agora = datetime.datetime.now()
                
                # Verificar se ainda tem algo para fazer (se não tem agendamento e nem run_now, para)
                alguma_pendencia = False
                for k, s in self.servicos.items():
                    if run_now_flags.get(k) or (s["ativo"].get() and s["prox_execucao"]):
                        alguma_pendencia = True
                        break
                
                if not alguma_pendencia:
                    self.log("\n✅ Todas as execuções manuais concluídas e nenhum agendamento ativo.")
                    self.is_running = False
                    break

                # Verificar cada serviço
                for key, servico in self.servicos.items():
                    # Condição para executar:
                    # 1. Flag run_now está True (execução manual inicial)
                    # 2. OU (Ativo E Hora Chegou)
                    
                    deve_executar = False
                    
                    if run_now_flags.get(key):
                        deve_executar = True
                        motivo = "Manual/Inicial"
                    elif servico["ativo"].get() and servico["prox_execucao"] and agora >= servico["prox_execucao"]:
                        deve_executar = True
                        motivo = "Agendamento"
                    
                    if deve_executar:
                        self.log(f"\n⚡ Iniciando execução ({motivo}) de: {servico['nome']}")
                        self.atualizar_status(f"Executando {servico['nome']}...")
                        
                        # Executa
                        if self.modo_consulta.get() == "lote":
                            executar_consulta_em_lote(
                                self.caminho_excel.get(),
                                servico["pasta"].get(),
                                tipo_consulta=servico["nome"],
                                check_stop_callback=lambda: not self.is_running
                            )
                        elif self.modo_consulta.get() == "mysql":
                            # Passa o dicionário de configuração
                            mysql_conf = {
                                'host': self.db_host.get(),
                                'port': int(self.db_port.get()) if self.db_port.get().isdigit() else 3306,
                                'user': self.db_user.get(),
                                'password': self.db_pass.get(),
                                'database': self.db_name.get()
                            }
                            executar_consulta_em_lote(
                                mysql_conf,
                                servico["pasta"].get(),
                                tipo_consulta=servico["nome"],
                                check_stop_callback=lambda: not self.is_running
                            )
                        else:
                            executar_consulta_individual(
                                self.cnpj_individual.get(),
                                self.nome_individual.get(),
                                self.codigo_individual.get(),
                                servico["pasta"].get(),
                                competencia=self.competencia_individual.get(),
                                grupo=self.grupo_individual.get(),
                                tipo_consulta=servico["nome"],
                                check_stop_callback=lambda: not self.is_running
                            )
                        
                        # Pós-execução
                        run_now_flags[key] = False # Consome o flag de execução imediata
                        
                        # Se for agendado, calcula próxima
                        # Se for agendado, calcula próxima
                        if servico["ativo"].get():
                            try:
                                dias = float(servico["intervalo"].get())
                                delta = datetime.timedelta(days=dias)
                                servico["prox_execucao"] = datetime.datetime.now() + delta
                                self.atualizar_label_prox(key, servico["prox_execucao"])
                                self.log(f"📅 Próxima execução de {servico['nome']} reagendada para: {servico['prox_execucao'].strftime('%d/%m %H:%M')}")
                            except Exception as e:
                                self.log(f"Erro ao reagendar {servico['nome']}: {e}")
                                servico["ativo"].set(False)
                        
                        if not servico["ativo"].get():
                            # Se não é agendado (ou falhou), limpa status
                            servico["prox_execucao"] = None
                            self.atualizar_label_simples(key, "Concluído", "green")

                        executou_algo = True
                        
                        # Se for execução INDIVIDUAL, paramos após a primeira execução bem sucedida de cada serviço marcado?
                        # No código atual, run_now_flags consome a flag. 
                        # Se modo == individual, talvez devêssemos parar o loop principal se não houver agendamentos?
                        # O loop já checa 'alguma_pendencia'. Se não é agendado, prox_execucao fica None.
                        # Logo, vai parar naturalmente se não houver agendamentos ativos.
                        
                        # Se parou no meio da execução
                        if not self.is_running: break

                if not self.is_running: break
                
                # Se não executou nada, espera um pouco e atualiza status
                if not executou_algo:
                    min_prox = None
                    nome_prox = ""
                    
                    # Descobre qual é o próximo mais próximo
                    for servico in self.servicos.values():
                        if servico["ativo"].get() and servico["prox_execucao"]:
                            if min_prox is None or servico["prox_execucao"] < min_prox:
                                min_prox = servico["prox_execucao"]
                                nome_prox = servico["nome"]
                    
                    if min_prox:
                        restante = min_prox - datetime.datetime.now()
                        minutos = int(restante.total_seconds() / 60)
                        self.atualizar_status(f"Próxima: {nome_prox} em {minutos} min ({min_prox.strftime('%H:%M')})")
                    else:
                        self.atualizar_status("Aguardando...")
                        
                    time.sleep(1)

        except Exception as e:
            self.log(f"\n❌ Erro fatal: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro fatal:\n{str(e)}")
        finally:
            sys.stdout = original_stdout
            if not self.is_running:
                self.log("\n⏹ Processamento finalizado.")
            self.resetar_botoes()

    def atualizar_label_prox(self, key, data):
        """Atualiza o label de próxima execução na aba correspondente (Thread-Safe)"""
        def _update():
            if "lbl_status" in self.servicos[key]:
                fmt = data.strftime("%d/%m %H:%M")
                self.servicos[key]["lbl_status"].config(text=f"Próxima execução: {fmt}", fg="blue")
        self.root.after(0, _update)

    def toggle_modo_consulta(self):
        """Alterna a visibilidade dos frames baseado no modo"""
        modo = self.modo_consulta.get()
        if modo == "lote":
            self.frame_individual.pack_forget()
            self.frame_mysql_fields.pack_forget()
            self.frame_excel.pack(fill=tk.X, pady=5)
            self.btn_procurar_excel.pack(side=tk.LEFT)
            # Limpa labels antigos se existirem
            for child in self.frame_excel.winfo_children():
                if isinstance(child, tk.Label): child.destroy()
            tk.Label(self.frame_excel, text="Planilha Excel:").pack(side=tk.LEFT, before=self.frame_excel.winfo_children()[0])
        elif modo == "mysql":
            self.frame_individual.pack_forget()
            self.frame_excel.pack_forget()
            self.frame_mysql_fields.pack(fill=tk.X, pady=5)
        else: # individual
            self.frame_excel.pack_forget()
            self.frame_mysql_fields.pack_forget()
            self.frame_individual.pack(fill=tk.X, pady=5)

    def atualizar_label_simples(self, key, texto, cor):
        """Atualiza o texto do label de status (Thread-Safe)"""
        def _update():
            if "lbl_status" in self.servicos[key]:
                self.servicos[key]["lbl_status"].config(text=texto, fg=cor)
        self.root.after(0, _update)

        
    def iniciar_servidor_web(self):
        """Inicia o servidor Flask em uma thread separada e abre o navegador"""
        def run_server():
            try:
                self.log("🌐 Iniciando servidor do dashboard (webapp/app.py)...")
                # Caminho absoluto para o app.py
                app_path = os.path.join(os.path.dirname(__file__), 'webapp', 'app.py')
                
                # Inicia o processo do servidor
                # Usamos sys.executable para garantir que use o mesmo interpretador Python
                self.server_process = subprocess.Popen(
                    [sys.executable, app_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.log("✅ Servidor web iniciado! Aguardando 3 segundos para abrir o navegador...")
                time.sleep(3)
                webbrowser.open("http://127.0.0.1:5000")
                
                # Monitora a saída se necessário (opcional)
                # stdout, stderr = self.server_process.communicate()
                
            except Exception as e:
                self.log(f"❌ Erro ao iniciar servidor web: {e}")
                messagebox.showerror("Erro", f"Não foi possível iniciar o servidor web:\n{e}")

        # Executa em thread para não travar a GUI
        thread_web = threading.Thread(target=run_server, daemon=True)
        thread_web.start()

def main():
    root = tk.Tk()
    app = BotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
