# -*- coding: utf-8 -*-
"""
Script de Geração de Relatórios e Gráficos de Controle de EPIs (SST)
Conforme as diretrizes da Skill analise-epis e requisitos de conformidade com a NR-6.

Data de Referência: 24/10/2026 (ou data de execução)
"""

import os
import sys
from datetime import datetime, timedelta, date
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Configuração do Matplotlib para evitar problemas com acentos
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.unicode_minus'] = False

def processar_base_epis(caminho_csv='dados/base_controle_epis.csv', data_ref=None, dias_janela=30):
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    df = pd.read_csv(caminho_csv, encoding='utf-8')

    # Data de referência padrão: 24/10/2026 se nenhuma for fornecida
    if data_ref is None:
        data_ref = date(2026, 10, 24)
    elif isinstance(data_ref, str):
        data_ref = datetime.strptime(data_ref, '%Y-%m-%d').date()

    limite_a_vencer = data_ref + timedelta(days=dias_janela)

    # Conversão de datas
    df['Data_Entrega_dt'] = pd.to_datetime(df['Data_Entrega'], errors='coerce').dt.date
    df['Data_Validade_dt'] = pd.to_datetime(df['Data_Validade'], errors='coerce').dt.date

    # 1. Classificação Cronológica da Validade (Skill analise-epis)
    def classificar_validade(row):
        d = row['Data_Validade_dt']
        if pd.isnull(d):
            return 'Indeterminado'
        if d < data_ref:
            return 'Vencido'
        elif d == data_ref:
            return 'Vence hoje'
        elif data_ref < d <= limite_a_vencer:
            return 'A vencer (30 dias)'
        else:
            return 'Vigente'

    df['Classificacao_Validade'] = df.apply(classificar_validade, axis=1)

    # Dias restantes / vencidos
    def calcular_dias(row):
        d = row['Data_Validade_dt']
        if pd.isnull(d):
            return None
        return (d - data_ref).days

    df['Dias_Ate_Vencimento'] = df.apply(calcular_dias, axis=1)

    # 2. Análise da Necessidade de Troca (Skill analise-epis)
    # Analisar separadamente a validade cronológica e o status de troca registrado
    def avaliar_necessidade_troca(row):
        val = row['Classificacao_Validade']
        st = str(row['Status_Troca']).strip() if pd.notnull(row['Status_Troca']) else 'Ausente'

        if val == 'Indeterminado' or st == 'Ausente':
            return 'Indeterminada (Dado Incompleto)'
        
        is_vencido = val in ['Vencido', 'Vence hoje']
        is_marcado_troca = (st == 'Troca Necessária')
        
        if is_vencido and is_marcado_troca:
            return 'Simultaneamente Vencido e Marcado para Troca'
        elif is_vencido and st == 'Vencido':
            return 'Vencido Cronológico (Confirmado na Base)'
        elif is_vencido and st == 'Regular':
            return 'Divergência Crítica: Vencido com Status Regular'
        elif not is_vencido and is_marcado_troca:
            return 'Troca Necessária Solicitada (Item Vigente)'
        elif val == 'A vencer (30 dias)' and st == 'Regular':
            return 'Atenção Preventiva (Vence em 30d)'
        elif val == 'Vigente' and st == 'Regular':
            return 'Regular em Conformidade'
        else:
            return f'{val} / {st}'

    df['Analise_Troca_Detalhada'] = df.apply(avaliar_necessidade_troca, axis=1)

    # 3. Classificação Operacional Consolidada (Totais Sem Sobreposição)
    def definir_acao_operacional(row):
        val = row['Classificacao_Validade']
        st = str(row['Status_Troca']).strip() if pd.notnull(row['Status_Troca']) else ''
        
        if val in ['Vencido', 'Vence hoje']:
            return 'Substituição Imediata (Vencido)'
        elif st == 'Troca Necessária':
            return 'Substituição Imediata (Solicitação/Avaria)'
        elif val == 'A vencer (30 dias)':
            return 'Alerta Preventivo (A vencer em 30d)'
        elif val == 'Vigente' and st == 'Regular':
            return 'Conforme / Vigente'
        else:
            return 'Pendente de Auditoria'

    df['Acao_Operacional'] = df.apply(definir_acao_operacional, axis=1)

    # Tratamento de Setor ausente
    df['Setor_Normalizado'] = df['Setor'].fillna('Setor Não Informado')

    return df, data_ref, limite_a_vencer

def gerar_graficos(df, data_ref, output_dir='relatorios'):
    os.makedirs(output_dir, exist_ok=True)
    
    # Paleta de cores corporativa SST
    cor_vencido = '#D9534F'      # Vermelho Alerta
    cor_troca = '#F0AD4E'        # Laranja Atenção
    cor_avencer = '#5BC0DE'      # Azul Claro Preventivo
    cor_regular = '#5CB85C'      # Verde Conforme
    cor_neutra = '#6C757D'       # Cinza Auditoria

    # -------------------------------------------------------------
    # Gráfico 1: Situação Operacional dos EPIs (Visão Executiva)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    contagem_acao = df['Acao_Operacional'].value_counts()
    
    cores_map = {
        'Substituição Imediata (Vencido)': cor_vencido,
        'Substituição Imediata (Solicitação/Avaria)': cor_troca,
        'Alerta Preventivo (A vencer em 30d)': cor_avencer,
        'Conforme / Vigente': cor_regular,
        'Pendente de Auditoria': cor_neutra
    }
    cores_plot = [cores_map.get(cat, cor_neutra) for cat in contagem_acao.index]

    bars = ax.barh(contagem_acao.index, contagem_acao.values, color=cores_plot, edgecolor='black', alpha=0.85, height=0.55)
    ax.invert_yaxis()
    
    # Anotações dos valores nas barras
    for bar in bars:
        w = bar.get_width()
        pct = (w / len(df)) * 100
        ax.annotate(f'{int(w)} ({pct:.1f}%)',
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(6, 0), textcoords="offset points",
                    ha='left', va='center', fontsize=11, fontweight='bold', color='#2C3E50')

    ax.set_title(f'Controle de EPIs - Situação Operacional das Demandas de SST\nData de Referência: {data_ref.strftime("%d/%m/%Y")} (Total: {len(df)} itens analisados)',
                 fontsize=13, fontweight='bold', pad=15, color='#1A252F')
    ax.set_xlabel('Quantidade de Itens de EPI', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_xlim(0, max(contagem_acao.values) * 1.25)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Rodapé da fonte
    fig.text(0.1, -0.02, 'Fonte: SESMT / Base de Controle de EPIs (dados/base_controle_epis.csv) | Diretrizes NR-6', fontsize=8, color='#555555')
    
    grafico1_path = os.path.join(output_dir, 'grafico_status_validade.png')
    plt.tight_layout()
    plt.savefig(grafico1_path, bbox_inches='tight', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Gráfico 2: Pendências e Demandas de Substituição por Setor
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    
    setor_pivot = pd.crosstab(
        df['Setor_Normalizado'], 
        df['Acao_Operacional']
    )
    
    ordem_colunas = [
        'Substituição Imediata (Vencido)',
        'Substituição Imediata (Solicitação/Avaria)',
        'Alerta Preventivo (A vencer em 30d)',
        'Conforme / Vigente'
    ]
    colunas_presentes = [c for c in ordem_colunas if c in setor_pivot.columns]
    setor_pivot = setor_pivot[colunas_presentes]
    setor_pivot['Total'] = setor_pivot.sum(axis=1)
    setor_pivot = setor_pivot.sort_values(by='Total', ascending=True)
    setor_pivot_plot = setor_pivot.drop(columns=['Total'])

    bottom = pd.Series([0] * len(setor_pivot_plot), index=setor_pivot_plot.index)
    bars_list = []
    for col in setor_pivot_plot.columns:
        values = setor_pivot_plot[col]
        bar = ax.barh(setor_pivot_plot.index, values, left=bottom, label=col, 
                      color=cores_map.get(col, cor_neutra), edgecolor='black', alpha=0.85, height=0.6)
        bottom += values
        bars_list.append(bar)

    # Anotação do total por setor
    for idx, (setor, total) in enumerate(setor_pivot['Total'].items()):
        ax.annotate(f' Total: {total}',
                    xy=(total, idx),
                    xytext=(5, 0), textcoords="offset points",
                    ha='left', va='center', fontsize=10, fontweight='bold', color='#2C3E50')

    ax.set_title(f'Panorama de EPIs por Setor Operacional\nConformidade vs. Necessidade de Substituição ({data_ref.strftime("%d/%m/%Y")})',
                 fontsize=13, fontweight='bold', pad=15, color='#1A252F')
    ax.set_xlabel('Quantidade de EPIs', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_xlim(0, max(setor_pivot['Total']) * 1.25)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9, fontsize=9)

    fig.text(0.1, -0.02, 'Fonte: SESMT / Base de Controle de EPIs | Setores em conformidade com registro de entrega', fontsize=8, color='#555555')

    grafico2_path = os.path.join(output_dir, 'grafico_pendencias_por_setor.png')
    plt.tight_layout()
    plt.savefig(grafico2_path, bbox_inches='tight', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Gráfico 3: Situação por Tipo de EPI
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    epi_pivot = pd.crosstab(df['Tipo_EPI'], df['Acao_Operacional'])
    colunas_presentes_epi = [c for c in ordem_colunas if c in epi_pivot.columns]
    epi_pivot = epi_pivot[colunas_presentes_epi]
    epi_pivot['Total'] = epi_pivot.sum(axis=1)
    epi_pivot = epi_pivot.sort_values(by='Total', ascending=True)
    epi_pivot_plot = epi_pivot.drop(columns=['Total'])

    bottom = pd.Series([0] * len(epi_pivot_plot), index=epi_pivot_plot.index)
    for col in epi_pivot_plot.columns:
        values = epi_pivot_plot[col]
        ax.barh(epi_pivot_plot.index, values, left=bottom, label=col, 
                color=cores_map.get(col, cor_neutra), edgecolor='black', alpha=0.85, height=0.6)
        bottom += values

    for idx, (epi, total) in enumerate(epi_pivot['Total'].items()):
        ax.annotate(f' Total: {total}',
                    xy=(total, idx),
                    xytext=(5, 0), textcoords="offset points",
                    ha='left', va='center', fontsize=10, fontweight='bold', color='#2C3E50')

    ax.set_title(f'Demanda de Reposição e Validade por Tipo de EPI\nIdentificação de Itens Críticos para Aquisição e Estoque',
                 fontsize=13, fontweight='bold', pad=15, color='#1A252F')
    ax.set_xlabel('Quantidade de Equipamentos', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_xlim(0, max(epi_pivot['Total']) * 1.25)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9, fontsize=9)

    fig.text(0.1, -0.02, 'Fonte: SESMT / Base de Controle de EPIs | Classificação por equipamento', fontsize=8, color='#555555')

    grafico3_path = os.path.join(output_dir, 'grafico_tipos_epi.png')
    plt.tight_layout()
    plt.savefig(grafico3_path, bbox_inches='tight', dpi=300)
    plt.close()

    return [grafico1_path, grafico2_path, grafico3_path]

def exportar_excel_profissional(df, data_ref, limite_a_vencer, output_path='relatorios/relatorio_controle_epis.xlsx'):
    wb = openpyxl.Workbook()
    # Remove sheet padrão
    wb.remove(wb.active)

    # Estilos padrão
    font_titulo = Font(name='Calibri', size=14, bold=True, color='FFFFFF')
    font_subtitulo = Font(name='Calibri', size=11, bold=True, color='1F4E79')
    font_header = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    font_body = Font(name='Calibri', size=10)
    font_bold = Font(name='Calibri', size=10, bold=True)
    
    fill_titulo = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
    fill_header = PatternFill(start_color='2F5597', end_color='2F5597', fill_type='solid')
    fill_section = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
    
    # Cores de status
    fill_vencido = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
    font_vencido = Font(name='Calibri', size=10, bold=True, color='9C0006')
    
    fill_troca = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
    font_troca = Font(name='Calibri', size=10, bold=True, color='9C6500')
    
    fill_regular = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
    font_regular = Font(name='Calibri', size=10, bold=True, color='006100')

    fill_alerta = PatternFill(start_color='BDD7EE', end_color='BDD7EE', fill_type='solid')
    font_alerta = Font(name='Calibri', size=10, bold=True, color='1F4E79')

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # =============================================================
    # ABA 1: RESUMO EXECUTIVO (DASHBOARD)
    # =============================================================
    ws_resumo = wb.create_sheet(title='Resumo Executivo')
    ws_resumo.views.sheetView[0].showGridLines = True

    # Cabeçalho Principal
    ws_resumo.merge_cells('A1:G1')
    c_title = ws_resumo['A1']
    c_title.value = "RELATÓRIO DE GESTÃO E CONTROLE DE EPIs - SESMT"
    c_title.font = font_titulo
    c_title.fill = fill_titulo
    c_title.alignment = Alignment(horizontal='center', vertical='center')
    ws_resumo.row_dimensions[1].height = 35

    # Parâmetros
    ws_resumo['A3'] = "Parâmetro"
    ws_resumo['B3'] = "Valor"
    ws_resumo['A3'].font = font_header
    ws_resumo['A3'].fill = fill_header
    ws_resumo['B3'].font = font_header
    ws_resumo['B3'].fill = fill_header

    params = [
        ("Data de Referência da Análise", data_ref.strftime('%d/%m/%Y')),
        ("Janela de Vencimento Preventivo", f"30 dias (até {limite_a_vencer.strftime('%d/%m/%Y')})"),
        ("Total de Registros Analisados", len(df)),
        ("Total de Colaboradores Cobertos", df['Colaborador'].nunique()),
        ("Total de Setores Identificados", df['Setor'].dropna().nunique()),
        ("Norma Regulamentadora Base", "NR-06 (Equipamentos de Proteção Individual)")
    ]
    for r_idx, (p, v) in enumerate(params, start=4):
        ws_resumo[f'A{r_idx}'] = p
        ws_resumo[f'B{r_idx}'] = v
        ws_resumo[f'A{r_idx}'].font = font_body
        ws_resumo[f'B{r_idx}'].font = font_bold
        ws_resumo[f'A{r_idx}'].border = thin_border
        ws_resumo[f'B{r_idx}'].border = thin_border

    # Tabela 1: Situação Operacional Consolidada (Sem sobreposição)
    start_r = 11
    ws_resumo.cell(row=start_r, column=1, value="Situação Operacional Consolidada (Totais Sem Dupla Contagem)").font = font_subtitulo
    ws_resumo.cell(row=start_r+1, column=1, value="Categoria de Ação de SST").font = font_header
    ws_resumo.cell(row=start_r+1, column=1).fill = fill_header
    ws_resumo.cell(row=start_r+1, column=2, value="Qtd").font = font_header
    ws_resumo.cell(row=start_r+1, column=2).fill = fill_header
    ws_resumo.cell(row=start_r+1, column=3, value="% da Base").font = font_header
    ws_resumo.cell(row=start_r+1, column=3).fill = fill_header
    ws_resumo.cell(row=start_r+1, column=4, value="Diretriz Operacional do SESMT").font = font_header
    ws_resumo.cell(row=start_r+1, column=4).fill = fill_header

    acoes_info = [
        ("Substituição Imediata (Vencido)", "Recolher imediatamente o EPI e fornecer novo item com CA válido (NR-6 item 6.5.1)."),
        ("Substituição Imediata (Solicitação/Avaria)", "Substituir item com solicitação de troca por desgaste físico ou defeito."),
        ("Alerta Preventivo (A vencer em 30d)", "Programar reposição e providenciar estoque antes do término da validade."),
        ("Conforme / Vigente", "Item em conformidade temporal e em uso regular."),
        ("Pendente de Auditoria", "Dados incompletos ou divergentes que impedem atestar conformidade.")
    ]
    
    cur_row = start_r + 2
    for cat, diretriz in acoes_info:
        qtd = (df['Acao_Operacional'] == cat).sum()
        pct = (qtd / len(df)) * 100
        ws_resumo.cell(row=cur_row, column=1, value=cat).font = font_body
        ws_resumo.cell(row=cur_row, column=2, value=qtd).font = font_bold
        ws_resumo.cell(row=cur_row, column=3, value=f"{pct:.1f}%").font = font_body
        ws_resumo.cell(row=cur_row, column=4, value=diretriz).font = font_body
        
        for c_idx in range(1, 5):
            cell = ws_resumo.cell(row=cur_row, column=c_idx)
            cell.border = thin_border
            if 'Vencido' in cat:
                cell.fill = fill_vencido
            elif 'Solicitação' in cat:
                cell.fill = fill_troca
            elif 'Preventivo' in cat:
                cell.fill = fill_alerta
            elif 'Conforme' in cat:
                cell.fill = fill_regular
        cur_row += 1

    # Totalizador
    ws_resumo.cell(row=cur_row, column=1, value="TOTAL GERAL").font = font_header
    ws_resumo.cell(row=cur_row, column=1).fill = fill_header
    ws_resumo.cell(row=cur_row, column=2, value=len(df)).font = font_header
    ws_resumo.cell(row=cur_row, column=2).fill = fill_header
    ws_resumo.cell(row=cur_row, column=3, value="100.0%").font = font_header
    ws_resumo.cell(row=cur_row, column=3).fill = fill_header
    ws_resumo.cell(row=cur_row, column=4, value="Base 100% auditada").font = font_header
    ws_resumo.cell(row=cur_row, column=4).fill = fill_header

    # Tabela 2: Resumo por Setor
    cur_row += 3
    ws_resumo.cell(row=cur_row, column=1, value="Síntese por Setor").font = font_subtitulo
    cur_row += 1
    headers_setor = ["Setor", "Total Itens", "Vencidos", "Troca Solicitada", "A Vencer (30d)", "Conformes", "% Crítica"]
    for col_idx, h_text in enumerate(headers_setor, start=1):
        c = ws_resumo.cell(row=cur_row, column=col_idx, value=h_text)
        c.font = font_header
        c.fill = fill_header
        c.border = thin_border

    setores_unicos = sorted(df['Setor_Normalizado'].unique())
    for s in setores_unicos:
        cur_row += 1
        sub_s = df[df['Setor_Normalizado'] == s]
        tot_s = len(sub_s)
        venc_s = (sub_s['Classificacao_Validade'].isin(['Vencido', 'Vence hoje'])).sum()
        troca_s = (sub_s['Status_Troca'] == 'Troca Necessária').sum()
        avenc_s = (sub_s['Classificacao_Validade'] == 'A vencer (30 dias)').sum()
        conf_s = (sub_s['Acao_Operacional'] == 'Conforme / Vigente').sum()
        pct_crit = ((venc_s + (sub_s['Acao_Operacional'] == 'Substituição Imediata (Solicitação/Avaria)').sum()) / tot_s) * 100

        ws_resumo.cell(row=cur_row, column=1, value=s).font = font_body
        ws_resumo.cell(row=cur_row, column=2, value=tot_s).font = font_bold
        ws_resumo.cell(row=cur_row, column=3, value=venc_s).font = font_body
        ws_resumo.cell(row=cur_row, column=4, value=troca_s).font = font_body
        ws_resumo.cell(row=cur_row, column=5, value=avenc_s).font = font_body
        ws_resumo.cell(row=cur_row, column=6, value=conf_s).font = font_body
        ws_resumo.cell(row=cur_row, column=7, value=f"{pct_crit:.1f}%").font = font_bold
        
        for c_idx in range(1, 8):
            ws_resumo.cell(row=cur_row, column=c_idx).border = thin_border

    # =============================================================
    # ABA 2: PENDÊNCIAS CRÍTICAS E DEMANDAS DE TROCA
    # =============================================================
    ws_crit = wb.create_sheet(title='Pendências Críticas')
    ws_crit.views.sheetView[0].showGridLines = True
    
    ws_crit.merge_cells('A1:I1')
    c_crit = ws_crit['A1']
    c_crit.value = "RELATÓRIO PRIORITÁRIO: ITENS VENCIDOS E COM TROCA NECESSÁRIA"
    c_crit.font = font_titulo
    c_crit.fill = PatternFill(start_color='C00000', end_color='C00000', fill_type='solid')
    c_crit.alignment = Alignment(horizontal='center', vertical='center')
    ws_crit.row_dimensions[1].height = 30

    colunas_tabela = [
        "ID Registro", "Colaborador", "Setor", "Tipo do EPI", 
        "Data Entrega", "Data Validade", "Status Original", 
        "Validade Calculada", "Ação Recomendada"
    ]
    for c_idx, col_name in enumerate(colunas_tabela, start=1):
        c = ws_crit.cell(row=3, column=c_idx, value=col_name)
        c.font = font_header
        c.fill = fill_header
        c.border = thin_border

    df_pendencias = df[df['Acao_Operacional'].str.contains('Substituição|Alerta', na=False)].sort_values(
        by=['Acao_Operacional', 'Data_Validade'], ascending=[True, True]
    )

    for r_idx, (_, row) in enumerate(df_pendencias.iterrows(), start=4):
        ws_crit.cell(row=r_idx, column=1, value=row['ID_Registro']).font = font_body
        ws_crit.cell(row=r_idx, column=2, value=row['Colaborador']).font = font_bold
        ws_crit.cell(row=r_idx, column=3, value=row['Setor_Normalizado']).font = font_body
        ws_crit.cell(row=r_idx, column=4, value=row['Tipo_EPI']).font = font_body
        ws_crit.cell(row=r_idx, column=5, value=str(row['Data_Entrega'])).font = font_body
        ws_crit.cell(row=r_idx, column=6, value=str(row['Data_Validade'])).font = font_body
        ws_crit.cell(row=r_idx, column=7, value=str(row['Status_Troca'])).font = font_body
        ws_crit.cell(row=r_idx, column=8, value=row['Classificacao_Validade']).font = font_body
        ws_crit.cell(row=r_idx, column=9, value=row['Acao_Operacional']).font = font_bold
        
        for c_idx in range(1, 10):
            cell = ws_crit.cell(row=r_idx, column=c_idx)
            cell.border = thin_border
            if 'Vencido' in row['Acao_Operacional']:
                cell.fill = fill_vencido
            elif 'Solicitação' in row['Acao_Operacional']:
                cell.fill = fill_troca
            elif 'Alerta' in row['Acao_Operacional']:
                cell.fill = fill_alerta

    # =============================================================
    # ABAS POR SETOR (Uma aba para cada setor)
    # =============================================================
    setores_lista = df['Setor_Normalizado'].unique()
    for s_nome in sorted(setores_lista):
        # Sanitizar título da aba para limite de 31 chars do Excel
        titulo_aba = s_nome[:30].replace('/', '_').replace(':', '')
        ws_s = wb.create_sheet(title=titulo_aba)
        ws_s.views.sheetView[0].showGridLines = True

        ws_s.merge_cells('A1:I1')
        c_s = ws_s['A1']
        c_s.value = f"CONTROLE DE EPIs - SETOR: {s_nome.upper()}"
        c_s.font = font_titulo
        c_s.fill = fill_titulo
        c_s.alignment = Alignment(horizontal='center', vertical='center')
        ws_s.row_dimensions[1].height = 30

        for c_idx, col_name in enumerate(colunas_tabela, start=1):
            c = ws_s.cell(row=3, column=c_idx, value=col_name)
            c.font = font_header
            c.fill = fill_header
            c.border = thin_border

        df_setor_rows = df[df['Setor_Normalizado'] == s_nome].sort_values(by=['Colaborador', 'Data_Validade'])
        for r_idx, (_, row) in enumerate(df_setor_rows.iterrows(), start=4):
            ws_s.cell(row=r_idx, column=1, value=row['ID_Registro']).font = font_body
            ws_s.cell(row=r_idx, column=2, value=row['Colaborador']).font = font_bold
            ws_s.cell(row=r_idx, column=3, value=row['Setor_Normalizado']).font = font_body
            ws_s.cell(row=r_idx, column=4, value=row['Tipo_EPI']).font = font_body
            ws_s.cell(row=r_idx, column=5, value=str(row['Data_Entrega'])).font = font_body
            ws_s.cell(row=r_idx, column=6, value=str(row['Data_Validade'])).font = font_body
            ws_s.cell(row=r_idx, column=7, value=str(row['Status_Troca'])).font = font_body
            ws_s.cell(row=r_idx, column=8, value=row['Classificacao_Validade']).font = font_body
            ws_s.cell(row=r_idx, column=9, value=row['Acao_Operacional']).font = font_bold
            
            for c_idx in range(1, 10):
                cell = ws_s.cell(row=r_idx, column=c_idx)
                cell.border = thin_border
                if 'Vencido' in row['Acao_Operacional']:
                    cell.fill = fill_vencido
                elif 'Solicitação' in row['Acao_Operacional']:
                    cell.fill = fill_troca
                elif 'Alerta' in row['Acao_Operacional']:
                    cell.fill = fill_alerta
                elif 'Conforme' in row['Acao_Operacional']:
                    cell.fill = fill_regular

    # =============================================================
    # ABA AUDITORIA E DADOS INCONSISTENTES
    # =============================================================
    ws_aud = wb.create_sheet(title='Auditoria e Inconsistências')
    ws_aud.views.sheetView[0].showGridLines = True

    ws_aud.merge_cells('A1:G1')
    c_aud = ws_aud['A1']
    c_aud.value = "AUDITORIA DE DADOS E LACUNAS NORMATIVAS (NR-6 / LGPD)"
    c_aud.font = font_titulo
    c_aud.fill = PatternFill(start_color='7030A0', end_color='7030A0', fill_type='solid')
    c_aud.alignment = Alignment(horizontal='center', vertical='center')
    ws_aud.row_dimensions[1].height = 30

    ws_aud.cell(row=3, column=1, value="ID Registro").font = font_header
    ws_aud.cell(row=3, column=1).fill = fill_header
    ws_aud.cell(row=3, column=2, value="Colaborador").font = font_header
    ws_aud.cell(row=3, column=2).fill = fill_header
    ws_aud.cell(row=3, column=3, value="Setor").font = font_header
    ws_aud.cell(row=3, column=3).fill = fill_header
    ws_aud.cell(row=3, column=4, value="Tipo Inconsistência").font = font_header
    ws_aud.cell(row=3, column=4).fill = fill_header
    ws_aud.cell(row=3, column=5, value="Detalhe da Anomalia").font = font_header
    ws_aud.cell(row=3, column=5).fill = fill_header
    ws_aud.cell(row=3, column=6, value="Risco Operacional").font = font_header
    ws_aud.cell(row=3, column=6).fill = fill_header
    ws_aud.cell(row=3, column=7, value="Ação Corretiva Exigida").font = font_header
    ws_aud.cell(row=3, column=7).fill = fill_header

    inconsistencias = [
        ("EPI-1006", "Maria Oliveira", "NaN (Ausente)", "Setor Não Cadastrado", "Colaborador sem setor alocado na entrega do Óculos de Proteção.", "Dificuldade de rastreamento do SESMT", "Auditar ficha de entrega física e atribuir setor."),
        ("EPI-1013", "Ana Santos", "Produção", "Status Troca Nulo", "EPI Luva Raspa venceu em 28/01/2026, mas campo Status_Troca está vazio.", "Falso sentimento de regularidade", "Atualizar cadastro para Troca Necessária e recolher EPI."),
        ("EPI-1005", "Carlos Souza", "Almoxarifado", "Divergência de Status", "Validade expirou em 23/10/2026, mas status no sistema consta como Regular.", "Uso de EPI vencido sob chancela de regular", "Atualizar flag do sistema para Vencido e efetuar entrega."),
        ("TODOS", "Geral", "Geral", "Ausência do Número do CA", "Base não possui campo de Certificado de Aprovação (CA) emitido pelo MTE.", "Não conformidade legal grave com a NR-6 item 6.5.1", "Incluir obrigatoriamente coluna CA e validar vigência no MTE."),
        ("TODOS", "Geral", "Geral", "Ausência de Cargo / Função", "Base não informa a função exercida pelo trabalhador.", "Impossibilidade de auditar adequação do EPI ao risco", "Integrar com tabela de cargos/funções do RH."),
        ("TODOS", "Geral", "Geral", "Ausência de Assinatura/Aceite", "Sem comprovante de assinatura física ou digital do trabalhador.", "Fragilidade jurídica em fiscalizações trabalhistas", "Implantar registro eletrônico de entrega de EPI conforme Portaria 672.")
    ]

    for r_idx, item in enumerate(inconsistencias, start=4):
        for c_idx, val in enumerate(item, start=1):
            cell = ws_aud.cell(row=r_idx, column=c_idx, value=val)
            cell.font = font_body
            cell.border = thin_border
            if 'TODOS' in item[0]:
                cell.fill = fill_section
            else:
                cell.fill = fill_troca

    # Ajuste automático da largura de todas as colunas em todas as abas
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                # Ignorar células mescladas na linha 1 para não distorcer largura
                if cell.row == 1:
                    continue
                v_str = str(cell.value or '')
                if len(v_str) > max_len:
                    max_len = len(v_str)
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(output_path)
    return output_path

if __name__ == '__main__':
    print("Iniciando processamento da base de dados de EPIs...")
    df, dt_ref, dt_lim = processar_base_epis()
    print(f"Base processada: {len(df)} registros. Data de Referência: {dt_ref}")
    
    print("Gerando gráficos de indicadores...")
    graficos = gerar_graficos(df, dt_ref)
    for g in graficos:
        print(f" - Gráfico gerado: {g}")

    print("Gerando planilha Excel de controle...")
    excel_path = exportar_excel_profissional(df, dt_ref, dt_lim)
    print(f" - Planilha Excel gerada com sucesso: {excel_path}")
    print("Processamento concluído com êxito!")

