import sqlite3
from datetime import datetime
from typing import Dict, List

class GestorSeguranca:
    """Sistema de IA para gerenciar equipamentos de segurança e orçamentos"""
    
    def __init__(self, db_name='seguranca.db'):
        self.db_name = db_name
        self.conexao = sqlite3.connect(db_name)
        self.cursor = self.conexao.cursor()
        self.criar_tabelas()
    
    def criar_tabelas(self):
        """Cria as tabelas do banco de dados"""
        # Tabela de equipamentos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                tipo TEXT NOT NULL,
                valor_unitario REAL NOT NULL,
                unidade TEXT NOT NULL,
                descricao TEXT,
                estoque REAL DEFAULT 0
            )
        ''')

        # Adiciona coluna de estoque em bancos antigos, se necessário
        self.cursor.execute('PRAGMA table_info(equipamentos)')
        colunas_equipamentos = [row[1] for row in self.cursor.fetchall()]
        if 'estoque' not in colunas_equipamentos:
            try:
                self.cursor.execute('ALTER TABLE equipamentos ADD COLUMN estoque REAL DEFAULT 0')
            except sqlite3.OperationalError:
                pass

        # Tabela de ambientes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ambientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                area_m2 REAL NOT NULL,
                tipo TEXT NOT NULL
            )
        ''')
        
        # Tabela de projetos/orçamentos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projetos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cliente TEXT,
                data_criacao TEXT,
                total REAL DEFAULT 0
            )
        ''')
        
        # Tabela de itens do projeto
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_projeto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                projeto_id INTEGER,
                equipamento_id INTEGER,
                quantidade REAL,
                valor_subtotal REAL,
                FOREIGN KEY(projeto_id) REFERENCES projetos(id),
                FOREIGN KEY(equipamento_id) REFERENCES equipamentos(id)
            )
        ''')
        
        self.conexao.commit()
    
    # ===== GERENCIAMENTO DE EQUIPAMENTOS =====
    
    def adicionar_equipamento(self, nome: str, tipo: str, valor_unitario: float, 
                             unidade: str, descricao: str = "", estoque: float = 0):
        """Adiciona um novo equipamento ao sistema ou soma ao estoque existente"""
        # Verifica se o equipamento já existe
        self.cursor.execute('SELECT id, estoque FROM equipamentos WHERE nome = ?', (nome,))
        resultado = self.cursor.fetchone()
        
        if resultado:
            # Equipamento existe - atualiza estoque
            equipamento_id, estoque_atual = resultado
            novo_estoque = estoque_atual + estoque
            self.cursor.execute('''
                UPDATE equipamentos SET estoque = ? WHERE id = ?
            ''', (novo_estoque, equipamento_id))
            self.conexao.commit()
            print(f"✅ Equipamento '{nome}' atualizado! Estoque anterior: {estoque_atual}, adicionado: {estoque}, novo total: {novo_estoque}")
        else:
            # Novo equipamento
            try:
                self.cursor.execute('''
                    INSERT INTO equipamentos (nome, tipo, valor_unitario, unidade, descricao, estoque)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (nome, tipo, valor_unitario, unidade, descricao, estoque))
                self.conexao.commit()
                print(f"✅ Equipamento '{nome}' adicionado com sucesso!")
            except sqlite3.IntegrityError:
                print(f"❌ Erro ao adicionar equipamento '{nome}'")
    
    def listar_equipamentos(self) -> List[Dict]:
        """Lista todos os equipamentos cadastrados"""
        self.cursor.execute('SELECT * FROM equipamentos')
        equipamentos = []
        for row in self.cursor.fetchall():
            equipamentos.append({
                'id': row[0],
                'nome': row[1],
                'tipo': row[2],
                'valor': row[3],
                'unidade': row[4],
                'descricao': row[5],
                'estoque': row[6] if len(row) > 6 else 0
            })
        return equipamentos

    def atualizar_estoque(self, equipamento_id: int, quantidade: float):
        """Atualiza o estoque de um equipamento"""
        self.cursor.execute('''
            UPDATE equipamentos SET estoque = estoque + ? WHERE id = ?
        ''', (quantidade, equipamento_id))
        self.conexao.commit()
        print(f"✅ Estoque atualizado para o equipamento {equipamento_id}.")

    def calcular_valor_estoque(self) -> float:
        """Calcula o valor total do estoque"""
        self.cursor.execute('SELECT valor_unitario, estoque FROM equipamentos')
        total = 0.0
        for valor_unitario, estoque in self.cursor.fetchall():
            total += valor_unitario * (estoque or 0)
        return round(total, 2)

    def gerar_dicas_venda(self, produto_nome: str = "", tipo_negocio: str = "microempresa") -> Dict:
        """Gera dicas de vendas personalizadas para o negócio"""
        self.cursor.execute('SELECT nome, tipo, valor_unitario, descricao FROM equipamentos')
        equipamentos = self.cursor.fetchall()
        dicas = []

        if produto_nome:
            itens = [item for item in equipamentos if produto_nome.lower() in item[0].lower()]
        else:
            itens = equipamentos

        if not itens:
            dicas.append("Cadastre produtos e equipamentos para receber dicas de vendas melhores.")
        else:
            dicas.append("Conheça seu cliente: ofereça soluções que resolvam dores reais de segurança e conforto.")
            dicas.append("Use promoções por pacote: combine câmeras, sensores e instalação em um orçamento único.")
            dicas.append("Destaque a tecnologia: mostre benefícios como imagem nítida, monitoramento remoto e instalação rápida.")

            for nome, tipo, valor, descricao in itens[:3]:
                dicas.append(f"Para '{nome}', sugira um pacote com garantia estendida e manutenção preventiva.")
                if valor < 200:
                    dicas.append(f"Produto econômico: ofereça este item como upgrade para muitos clientes.")
                elif valor > 700:
                    dicas.append(f"Produto premium: destaque qualidade, durabilidade e retorno sobre investimento.")

        return {
            'produto': produto_nome or 'Geral',
            'tipo_negocio': tipo_negocio,
            'dicas': dicas
        }

    def listar_projetos(self) -> List[Dict]:
        """Lista todos os orçamentos e projetos"""
        self.cursor.execute('SELECT id, nome, cliente, data_criacao, total FROM projetos')
        projetos = []
        for row in self.cursor.fetchall():
            projetos.append({
                'id': row[0],
                'nome': row[1],
                'cliente': row[2],
                'data_criacao': row[3],
                'total': row[4]
            })
        return projetos
    
    # ===== GERENCIAMENTO DE AMBIENTES =====
    
    def adicionar_ambiente(self, nome: str, area_m2: float, tipo: str):
        """Adiciona um novo ambiente"""
        try:
            self.cursor.execute('''
                INSERT INTO ambientes (nome, area_m2, tipo)
                VALUES (?, ?, ?)
            ''', (nome, area_m2, tipo))
            self.conexao.commit()
            print(f"✅ Ambiente '{nome}' adicionado com sucesso!")
        except sqlite3.IntegrityError:
            print(f"❌ Ambiente '{nome}' já existe!")
    
    # ===== CÁLCULOS INTELIGENTES =====
    
    def calcular_cameras_recomendadas(self, area_m2: float, tipo_ambiente: str = "interno") -> int:
        """
        Calcula a quantidade recomendada de câmeras
        Regra: 1 câmera a cada 25-40 m² para interno, 15-20 m² para externo
        """
        if tipo_ambiente.lower() == "externo":
            cameras = max(1, round(area_m2 / 20))
        else:
            cameras = max(1, round(area_m2 / 30))
        return cameras
    
    def calcular_fios_necessarios(self, area_m2: float, num_cameras: int, 
                                  num_alarmes: int) -> float:
        """
        Calcula a metragem aproximada de fio necessário
        Fórmula: perímetro da área + (metragem por câmera e sensor)
        """
        # Perímetro estimado (considerando forma retangular)
        perimetro = 2 * (area_m2 ** 0.5) * 2
        
        # Adicionar metragem por câmera (média 15-20 metros)
        metragem_cameras = num_cameras * 20
        
        # Adicionar metragem por sensor de alarme (média 10-15 metros)
        metragem_sensores = num_alarmes * 15
        
        # Margem de segurança (20%)
        total = (perimetro + metragem_cameras + metragem_sensores) * 1.2
        
        return round(total, 2)
    
    def calcular_sensores_alarme(self, num_portas: int, num_janelas: int) -> int:
        """Calcula quantidade recomendada de sensores de alarme"""
        # Um sensor por porta e janela + sensores adicionais
        return num_portas + num_janelas
    
    # ===== ORÇAMENTO E PROJETOS =====
    
    def criar_projeto(self, nome: str, cliente: str = "") -> int:
        """Cria um novo projeto/orçamento"""
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT INTO projetos (nome, cliente, data_criacao)
            VALUES (?, ?, ?)
        ''', (nome, cliente, data))
        self.conexao.commit()
        return self.cursor.lastrowid
    
    def adicionar_item_projeto(self, projeto_id: int, equipamento_id: int, quantidade: float):
        """Adiciona um equipamento ao projeto"""
        # Buscar valor do equipamento
        self.cursor.execute('SELECT valor_unitario FROM equipamentos WHERE id = ?', 
                           (equipamento_id,))
        resultado = self.cursor.fetchone()
        
        if not resultado:
            print("❌ Equipamento não encontrado!")
            return
        
        valor_unitario = resultado[0]
        subtotal = quantidade * valor_unitario
        
        self.cursor.execute('''
            INSERT INTO itens_projeto (projeto_id, equipamento_id, quantidade, valor_subtotal)
            VALUES (?, ?, ?, ?)
        ''', (projeto_id, equipamento_id, quantidade, subtotal))
        
        # Atualizar total do projeto
        self.atualizar_total_projeto(projeto_id)
        self.conexao.commit()
        print(f"✅ Item adicionado ao projeto!")
    
    def atualizar_total_projeto(self, projeto_id: int):
        """Atualiza o valor total do projeto"""
        self.cursor.execute('''
            SELECT SUM(valor_subtotal) FROM itens_projeto WHERE projeto_id = ?
        ''', (projeto_id,))
        
        resultado = self.cursor.fetchone()
        total = resultado[0] if resultado[0] else 0
        
        self.cursor.execute('''
            UPDATE projetos SET total = ? WHERE id = ?
        ''', (total, projeto_id))
        self.conexao.commit()
    
    def gerar_orcamento_automatico(self, projeto_id: int, area_m2: float, 
                                   num_portas: int, num_janelas: int, 
                                   tipo_ambiente: str = "interno") -> Dict:
        """
        Gera automaticamente um orçamento baseado nos parâmetros do ambiente
        """
        print("\n" + "="*50)
        print(f"📋 GERANDO ORÇAMENTO AUTOMÁTICO")
        print("="*50)
        
        # Cálculos recomendados
        num_cameras = self.calcular_cameras_recomendadas(area_m2, tipo_ambiente)
        num_sensores = self.calcular_sensores_alarme(num_portas, num_janelas)
        metragem_fios = self.calcular_fios_necessarios(area_m2, num_cameras, num_sensores)
        
        print(f"\n📊 RECOMENDAÇÕES:")
        print(f"   • Câmeras necessárias: {num_cameras}")
        print(f"   • Sensores de alarme: {num_sensores}")
        print(f"   • Metragem de fio: {metragem_fios}m")
        
        # Buscar equipamentos padrão
        equipamentos_padrao = {
            'Câmera IP 1080P': 1,
            'Alarme Sensor Porta/Janela': 2,
            'Cabo Coaxial (por 100m)': (metragem_fios / 100)
        }
        
        # Adicionar itens ao projeto
        for equip_nome, quantidade in equipamentos_padrao.items():
            self.cursor.execute('SELECT id FROM equipamentos WHERE nome = ?', (equip_nome,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                equip_id = resultado[0]
                self.adicionar_item_projeto(projeto_id, equip_id, quantidade * num_cameras 
                                           if equip_nome == "Câmera IP 1080P" 
                                           else quantidade)
        
        # Retornar resumo
        self.cursor.execute('''
            SELECT p.nome, p.cliente, p.total FROM projetos WHERE id = ?
        ''', (projeto_id,))
        
        projeto = self.cursor.fetchone()
        
        return {
            'projeto': projeto[0],
            'cliente': projeto[1],
            'cameras': num_cameras,
            'sensores': num_sensores,
            'fios_metros': metragem_fios,
            'valor_total': projeto[2] if projeto[2] else 0
        }
    
    def exibir_orcamento(self, projeto_id: int):
        """Exibe um orçamento completo"""
        self.cursor.execute('SELECT * FROM projetos WHERE id = ?', (projeto_id,))
        projeto = self.cursor.fetchone()
        
        if not projeto:
            print("❌ Projeto não encontrado!")
            return
        
        print("\n" + "="*60)
        print(f"📄 ORÇAMENTO: {projeto[1]}")
        print(f"Cliente: {projeto[2] or 'N/A'}")
        print(f"Data: {projeto[3]}")
        print("="*60)
        
        self.cursor.execute('''
            SELECT e.nome, e.unidade, ip.quantidade, e.valor_unitario, ip.valor_subtotal
            FROM itens_projeto ip
            JOIN equipamentos e ON ip.equipamento_id = e.id
            WHERE ip.projeto_id = ?
        ''', (projeto_id,))
        
        items = self.cursor.fetchall()
        
        print(f"\n{'Equipamento':<25} {'Qtd':<8} {'Unidade':<10} {'Valor Unit.':<12} {'Subtotal':<12}")
        print("-" * 67)
        
        total = 0
        for item in items:
            nome, unidade, qtd, valor_unit, subtotal = item
            print(f"{nome:<25} {qtd:<8.2f} {unidade:<10} R$ {valor_unit:<11.2f} R$ {subtotal:<11.2f}")
            total += subtotal
        
        print("-" * 67)
        print(f"{'TOTAL':<25} {'':<8} {'':<10} {'':<12} R$ {total:<11.2f}")
        print("="*60 + "\n")
    
    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados"""
        self.conexao.close()
    