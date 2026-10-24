# -*- coding: utf-8 -*-
import pandas as pd
from datetime import date

df = pd.read_csv('dados/base_controle_epis.csv', encoding='utf-8')
ref_date = date(2026, 10, 24)
df['Data_Validade_dt'] = pd.to_datetime(df['Data_Validade']).dt.date

def sit(row):
    d = row['Data_Validade_dt']
    st = str(row['Status_Troca'])
    if d < ref_date:
        return 'VENCIDO'
    elif st == 'Troca Necessária':
        return 'TROCA SOLICITADA'
    elif (d - ref_date).days <= 30:
        return 'A VENCER (30d)'
    return 'REGULAR'

df['Situacao'] = df.apply(sit, axis=1)

print('=' * 85)
print('          PAINEL DE AUDITORIA E CONTROLE DE EPIs (SESMT)')
print(f'          Data de Referência: {ref_date.strftime("%d/%m/%Y")} | Total de Registros: {len(df)}')
print('=' * 85)

print('\n[1] DISTRIBUIÇÃO OPERACIONAL:')
for k, v in df['Situacao'].value_counts().items():
    pct = (v / len(df)) * 100
    print(f'  * {k:<20}: {v:>2} itens ({pct:>5.1f}%)')

print('\n[2] QUADRO RESUMO POR SETOR:')
df['Setor_Disp'] = df['Setor'].fillna('[SETOR NÃO INFORMADO]')
setor_tab = pd.crosstab(df['Setor_Disp'], df['Situacao'], margins=True, margins_name='TOTAL')
print(setor_tab.to_string())

print('\n[3] LISTAGEM DE PENDÊNCIAS PRIORITÁRIAS (SUBSTITUIÇÃO / REPOSIÇÃO):')
criticos = df[df['Situacao'].isin(['VENCIDO', 'TROCA SOLICITADA', 'A VENCER (30d)'])].sort_values(by=['Situacao', 'Data_Validade'])
print(criticos[['ID_Registro', 'Colaborador', 'Setor_Disp', 'Tipo_EPI', 'Data_Validade', 'Situacao']].to_string(index=False))
print('=' * 85)
