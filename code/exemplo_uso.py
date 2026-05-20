from gestor_segurança import GestorSeguranca

# Inicializar o sistema
gestor = GestorSeguranca()

# ===== CADASTRAR EQUIPAMENTOS =====
print("\nCADASTRANDO EQUIPAMENTOS...\n")

gestor.adicionar_equipamento(
    nome="Câmera IP 1080P",
    tipo="câmera",
    valor_unitario=450.00,
    descricao="Câmera IP 1080P Full HD"
)

gestor.adicionar_equipamento(
    nome="Câmera IP 4K",
    tipo="câmera",
    valor_unitario=800.00,

    descricao="Câmera IP 4K Ultra HD"
)

gestor.adicionar_equipamento(
    nome="Alarme Sensor Porta/Janela",
    tipo="sensor",
    valor_unitario=120.00,

    descricao="Sensor de abertura porta/janela"
)

gestor.adicionar_equipamento(
    nome="Cabo Coaxial (por 100m)",
    tipo="cabo",
    valor_unitario=250.00,
    unidade="100 metros",
    descricao="Cabo coaxial RG6 para CFTV"
)

gestor.adicionar_equipamento(
    nome="DVR 8 Canais",
    tipo="gravador",
    valor_unitario=1200.00,

    descricao="Gravador digital de vídeo"
)

# ===== CRIAR PROJETO =====
print("\n📋 CRIANDO PROJETO...\n")

projeto_id = gestor.criar_projeto(
    nome="Sistema de Segurança - Loja Centro",
    cliente="Loja Center Mall"
)

# ===== GERAR ORÇAMENTO AUTOMÁTICO =====
print("\n🤖 APLICANDO IA PARA CALCULAR EQUIPAMENTOS...\n")

orcamento = gestor.gerar_orcamento_automatico(
    projeto_id=projeto_id,
    area_m2=150,  # Loja com 150 m²
    num_portas=2,
    num_janelas=4,
    tipo_ambiente="interno"
)

print(f"\n✨ RESUMO GERADO PELA IA:")
print(f"   • Câmeras recomendadas: {orcamento['cameras']}")
print(f"   • Sensores de alarme: {orcamento['sensores']}")
print(f"   • Metragem de fio: {orcamento['fios_metros']}m")
print(f"   • VALOR TOTAL DO ORÇAMENTO: R$ {orcamento['valor_total']:.2f}")

# ===== EXIBIR ORÇAMENTO COMPLETO =====
gestor.exibir_orcamento(projeto_id)

# ===== LISTAR EQUIPAMENTOS =====
print("📦 EQUIPAMENTOS CADASTRADOS:\n")
for eq in gestor.listar_equipamentos():
    print(f"  • {eq['nome']:<30} R$ {eq['valor']:.2f} ({eq['unidade']})")

# Fechar conex��o
gestor.fechar_conexao()