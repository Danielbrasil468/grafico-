# RELATÓRIO TÉCNICO DE AUDITORIA E GESTÃO DE EPIs - SESMT

**Data de Referência da Avaliação:** 24 de Outubro de 2026  
**Janela Preventiva de Vencimento:** 30 dias (até 23 de Novembro de 2026)  
**Fonte de Dados Primária:** `dados/base_controle_epis.csv` (Total: 40 registros analisados)  
**Normas de Referência:** NR-06 (EPIs), NR-04 (SESMT), NR-05 (CIPA) e Portaria MTP nº 672/2021  

---

## 1. Sumário Executivo e Indicadores Consolidados

A presente auditoria técnica avaliou a totalidade da base de entrega e validade de Equipamentos de Proteção Individual (EPIs).

### 1.1 Indicadores Globais
* **Total de Registros de Entrega:** 40
* **Total de Colaboradores Cobertos:** 14
* **Total de Setores Identificados:** 6 setores mapeados (+ 1 registro com setor não informado)
* **Taxa de Itens em Conformidade Plena:** 17,5% (7 de 40 itens)
* **Taxa de Itens em Risco Imediato (Substituição Crítica):** 80,0% (32 de 40 itens)
* **Taxa de Itens em Alerta Preventivo (Vencimento em 30 dias):** 2,5% (1 de 40 itens)

### 1.2 Totais Operacionais Sem Sobreposição (Categorias Exclusivas)

| Situação Operacional de SST | Quantidade | Percentual | Ação Recomendada pelo SESMT |
| :--- | :---: | :---: | :--- |
| **Substituição Imediata (Vencidos Cronológicos)** | 28 | 70,0% | Recolhimento obrigatório e fornecimento de novo EPI com CA válido. |
| **Substituição Imediata (Troca Solicitada / Avaria)** | 4 | 10,0% | Substituição física de itens vigentes com relato de avaria ou desgaste. |
| **Alerta Preventivo (A vencer em até 30 dias)** | 1 | 2,5% | Verificação de saldo de almoxarifado para reposição antes do vencimento. |
| **Conforme / Vigente** | 7 | 17,5% | Manter monitoramento de integridade e uso correto. |
| **TOTAL GERAL** | **40** | **100,0%** | **Base auditada sem dupla contagem.** |

---

## 2. Análise Cruzada: Validade Cronológica vs. Status Registrado

A auditoria confrontou a data de validade cronológica do equipamento contra a marcação de status no sistema, revelando divergências operacionais críticas:

```
+-----------------------------+--------------+---------+------------------+---------+-------+
| Validade Calculada          | Ausente/Nulo | Regular | Troca Necessária | Vencido | Total |
+-----------------------------+--------------+---------+------------------+---------+-------+
| Vencido (< 24/10/2026)      |      1       |    1    |        8         |   18    |  28   |
| A vencer (próximos 30 dias) |      0       |    1    |        0         |    0    |   1   |
| Vigente (> 23/11/2026)      |      0       |    7    |        4         |    0    |  11   |
+-----------------------------+--------------+---------+------------------+---------+-------+
| TOTAL                       |      1       |    9    |        12        |   18    |  40   |
+-----------------------------+--------------+---------+------------------+---------+-------+
```

### Anomalias e Divergências Detectadas:
1. **Divergência Crítica de Falsa Regularidade (EPI-1005):**
   * Colaborador: Carlos Souza | Setor: Almoxarifado | Item: Luva Nitrílica.
   * Data de Validade: `23/10/2026` (Venceu ontem!).
   * Status na Base: `Regular`.
   * **Risco:** O colaborador está trabalhando com EPI vencido sob a falsa premissa de que o item encontra-se regular.
2. **Troca Necessária em Itens Cronologicamente Vigentes (4 registros):**
   * `EPI-1010` (Maria Oliveira, Almoxarifado, Luva de Raspa, Val: `23/08/2027`)
   * `EPI-1025` (Gabriel Rodrigues, Produção, Protetor Auricular, Val: `22/05/2027`)
   * `EPI-1037` (Rafael Ribeiro, Qualidade, Máscara PFF2, Val: `23/05/2027`)
   * `EPI-1038` (Maria Oliveira, Obras, Botina de Segurança, Val: `08/05/2027`)
   * **Conclusão:** O status "Troca Necessária" nesses itens decorre de avaria, perda de capacidade protetiva mecânica ou solicitação do empregado, devendo ter prioridade imediata de troca.
3. **Status de Troca Nulo/Ausente (EPI-1013):**
   * Colaboradora: Ana Santos | Setor: Produção | Item: Luva de Proteção em Raspa.
   * Data de Validade: `28/01/2026` (Vencido há quase 9 meses).
   * Status na Base: `[Vazio / Nulo]`.

---

## 3. Panorama e Pendências por Setor Operacional

| Setor | Total Itens | Vencidos | Troca Solicitada (Vigente) | A Vencer (30d) | Conformes | % em Demanda Crítica |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logística** | 10 | 8 | 0 | 0 | 2 | **80,0%** |
| **Qualidade** | 7 | 3 | 1 | 0 | 3 | **57,1%** |
| **Almoxarifado** | 6 | 4 | 1 | 1 | 1 | **83,3%** |
| **Obras** | 6 | 2 | 1 | 0 | 3 | **50,0%** |
| **Manutenção** | 5 | 4 | 0 | 0 | 1 | **80,0%** |
| **Produção** | 5 | 3 | 1 | 0 | 1 | **80,0%** |
| **Setor Não Informado** | 1 | 1 | 0 | 0 | 0 | **100,0%** |
| **TOTAL** | **40** | **25** | **4** | **1** | **11** | **80,0%** |

*(Nota: Na tabela setorial, itens simultaneamente vencidos e com troca necessária constam na coluna de Vencidos).*

---

## 4. Pendências Individuais por Colaborador

| Colaborador | Total Itens | Substituição Crítica (Vencidos + Trocas) | Alerta Preventivo (30d) | Itens Conformes | Situação do Colaborador |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Maria Oliveira** | 6 | 4 | 0 | 2 | Crítica (Possui 1 item sem setor informado) |
| **Rafael Ribeiro** | 5 | 2 | 0 | 3 | Atenção (Máscara PFF2 com troca necessária) |
| **João da Silva** | 4 | 4 | 0 | 0 | **100% Irregular (Todos os 4 EPIs vencidos)** |
| **Rodrigo Barbosa** | 4 | 2 | 0 | 2 | Atenção (Capacete e Botina vencidos) |
| **Beatriz Lima** | 3 | 3 | 0 | 0 | **100% Irregular (Todos os 3 EPIs vencidos)** |
| **Gabriel Rodrigues** | 3 | 2 | 0 | 1 | Crítica (Protetor auricular com avaria) |
| **Lucas Pereira** | 3 | 2 | 0 | 1 | Crítica (Luva de raspa vencida) |
| **Mariana Carvalho** | 3 | 2 | 0 | 1 | Crítica (Botina vencida) |
| **Ana Santos** | 2 | 2 | 0 | 0 | **100% Irregular (1 vencido e 1 com status nulo)** |
| **Camila Martins** | 2 | 2 | 0 | 0 | **100% Irregular (Ambos vencidos)** |
| **Juliana Alves** | 2 | 1 | 0 | 1 | Atenção (Luva de raspa vencida) |
| **Carlos Souza** | 1 | 1 | 0 | 0 | **100% Irregular (Luva nitrílica vencida ontem)** |
| **Pedro Lima** | 1 | 1 | 0 | 0 | **100% Irregular (Luva nitrílica vencida)** |
| **Thiago Rocha** | 1 | 0 | 1 | 0 | **Alerta Preventivo (Vence em 30/10/2026)** |

---

## 5. Itens Próximos do Vencimento (Janela de 30 Dias)

Apenas **1 registro** encontra-se na janela de vencimento preventivo imediato:
* **ID:** `EPI-1036`
* **Colaborador:** Thiago Rocha
* **Setor:** Almoxarifado
* **EPI:** Luva de Proteção em Raspa
* **Data de Entrega:** 30/10/2025
* **Data de Validade:** 30/10/2026 (vence em **6 dias** a partir da data de referência)
* **Recomendação:** Emitir ordem de reposição junto ao almoxarifado para substituição programada até 29/10/2026.

---

## 6. Auditoria de Qualidade dos Dados e Conformidade Normativa (NR-06 / LGPD)

### 6.1 Inconsistências Pontuais
1. **Registro EPI-1006 (Maria Oliveira):** O campo `Setor` está vazio (`NaN`). A colaboradora possui outros registros vinculados ao Almoxarifado, Logística e Obras. Recomenda-se checar a ficha física para alocação correta.
2. **Registro EPI-1013 (Ana Santos):** O campo `Status_Troca` está ausente. Pela data (`28/01/2026`), o item já está expirado há mais de 260 dias.

### 6.2 Lacunas Estruturais da Base de Dados
A análise em relação aos requisitos mínimos da **NR-06 (Portaria MTP nº 672/2021)** e diretrizes da CIPA/SESMT revelou a ausência dos seguintes campos mandatórios:
* **Certificado de Aprovação (CA):** A ausência do número de CA na base impede a verificação da regularidade do fabricante perante o Ministério do Trabalho e Emprego (MTE).
* **Função / Cargo do Trabalhador:** Impede o cruzamento automático com o Programa de Gerenciamento de Riscos (PGR) e Perfil Profissiográfico Previdenciário (PPP).
* **Quantidade Fornecida:** Impede o cálculo de taxa de consumo e vida útil real.
* **Comprovante de Entrega / Assinatura:** Não há evidência digital ou protocolo de assinatura do colaborador, expondo a organização a passivos fiscais e trabalhistas.
* **Base de Acidentes e Sinistros:** A inexistência da tabela de registros de acidentes e HHT inviabiliza temporariamente o cômputo da Taxa de Frequência ($TF$) e Taxa de Gravidade ($TG$).

---

## 7. Arquivos Gerados pelo Agente

1. **Planilha Completa em Microsoft Excel:**
   * Arquivo: `relatorios/relatorio_controle_epis.xlsx`
   * Abas geradas:
     - `Resumo Executivo`: Dashboard com parâmetros, tabela operacional e síntese setorial.
     - `Pendências Críticas`: Lista com os 33 itens prioritários de reposição.
     - Abas por setor: `Almoxarifado`, `Logística`, `Manutenção`, `Obras`, `Produção`, `Qualidade` e `Setor Não Informado`.
     - `Auditoria e Inconsistências`: Registro das anomalias e lacunas legais.
2. **Gráficos em Alta Definição (300 DPI):**
   * `relatorios/grafico_status_validade.png`: Gráfico da situação operacional dos EPIs.
   * `relatorios/grafico_pendencias_por_setor.png`: Gráfico comparativo de pendências por setor.
   * `relatorios/grafico_tipos_epi.png`: Distribuição das demandas por tipo de EPI.
3. **Automação e Testes:**
   * `gerar_relatorios.py`: Script autônomo de processamento e geração.
   * `tests/test_relatorios.py`: Bateria de testes unitários automatizados (100% de aprovação).

