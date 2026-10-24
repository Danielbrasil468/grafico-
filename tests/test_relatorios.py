# -*- coding: utf-8 -*-
"""
Testes Unitários para Validação das Regras de Negócio e Indicadores de EPIs (SST)
Garante a conformidade dos cálculos temporais, integridade e ausência de contagem dupla.
"""

import unittest
from datetime import date, timedelta
import pandas as pd
from gerar_relatorios import processar_base_epis

class TesteControleEPIs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Executa o processamento com data de referência fixada para testes reproduzíveis
        cls.data_ref = date(2026, 10, 24)
        cls.df, cls.dt_ref, cls.dt_lim = processar_base_epis(
            caminho_csv='dados/base_controle_epis.csv',
            data_ref=cls.data_ref,
            dias_janela=30
        )

    def test_total_registros(self):
        """Valida se todos os 40 registros foram carregados sem perda."""
        self.assertEqual(len(self.df), 40)

    def test_classificacao_vencidos(self):
        """Valida que registros anteriores a 24/10/2026 são marcados como Vencido."""
        vencidos = self.df[self.df['Classificacao_Validade'] == 'Vencido']
        self.assertEqual(len(vencidos), 28)
        for _, row in vencidos.iterrows():
            self.assertLess(row['Data_Validade_dt'], self.data_ref)

    def test_classificacao_a_vencer_30_dias(self):
        """Valida que registros entre 25/10/2026 e 23/11/2026 são marcados como A Vencer (30 dias)."""
        a_vencer = self.df[self.df['Classificacao_Validade'] == 'A vencer (30 dias)']
        self.assertEqual(len(a_vencer), 1)
        row = a_vencer.iloc[0]
        self.assertEqual(row['ID_Registro'], 'EPI-1036')
        self.assertEqual(row['Colaborador'], 'Thiago Rocha')
        self.assertEqual(row['Data_Validade_dt'], date(2026, 10, 30))

    def test_classificacao_vigentes(self):
        """Valida que registros posteriores a 23/11/2026 são marcados como Vigente."""
        vigentes = self.df[self.df['Classificacao_Validade'] == 'Vigente']
        self.assertEqual(len(vigentes), 11)
        for _, row in vigentes.iterrows():
            self.assertGreater(row['Data_Validade_dt'], self.data_ref + timedelta(days=30))

    def test_totais_sem_sobreposicao(self):
        """Garante que a soma das categorias operacionais exclusivas totalize exatamente 100% da base."""
        contagem = self.df['Acao_Operacional'].value_counts()
        total_acumulado = contagem.sum()
        self.assertEqual(total_acumulado, 40)
        
        # Subtotais conhecidos
        self.assertEqual(contagem['Substituição Imediata (Vencido)'], 28)
        self.assertEqual(contagem['Substituição Imediata (Solicitação/Avaria)'], 4)
        self.assertEqual(contagem['Alerta Preventivo (A vencer em 30d)'], 1)
        self.assertEqual(contagem['Conforme / Vigente'], 7)

    def test_deteccao_divergencias(self):
        """Valida se o registro EPI-1005 (Carlos Souza) foi detectado com divergência (Vencido mas marcado Regular)."""
        row_carlos = self.df[self.df['ID_Registro'] == 'EPI-1005'].iloc[0]
        self.assertEqual(row_carlos['Classificacao_Validade'], 'Vencido')
        self.assertEqual(row_carlos['Status_Troca'], 'Regular')
        self.assertEqual(row_carlos['Analise_Troca_Detalhada'], 'Divergência Crítica: Vencido com Status Regular')

    def test_tratamento_setor_nulo(self):
        """Garante que o registro sem setor (EPI-1006) seja sinalizado sem ser descartado."""
        row_maria = self.df[self.df['ID_Registro'] == 'EPI-1006'].iloc[0]
        self.assertTrue(pd.isna(row_maria['Setor']))
        self.assertEqual(row_maria['Setor_Normalizado'], 'Setor Não Informado')

    def test_tratamento_status_nulo(self):
        """Garante que o registro sem Status_Troca (EPI-1013) seja sinalizado adequadamente."""
        row_ana = self.df[self.df['ID_Registro'] == 'EPI-1013'].iloc[0]
        self.assertTrue(pd.isna(row_ana['Status_Troca']))
        self.assertEqual(row_ana['Analise_Troca_Detalhada'], 'Indeterminada (Dado Incompleto)')

if __name__ == '__main__':
    unittest.main()

