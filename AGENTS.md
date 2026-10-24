# AGENTS.md - Agente de Inteligência em SST: Controle de EPIs e Indicadores de Acidentes

## 1. Visão Geral do Projeto
Este projeto implementa um agente de software especializado em Segurança e Saúde no Trabalho (SST). Sua finalidade primordial é consumir bases de dados operacionais para auditar a vigência de Equipamentos de Proteção Individual (EPIs), rastrear prazos de validade e reposição, apontar anomalias cadastrais e projetar indicadores de acidentes de trabalho.

### Usuários-Alvo:
* **Técnicos e Engenheiros de Segurança do Trabalho (SESMT):** Acompanhamento diário das pendências de campo, trocas preventivas e controle de conformidade com as Normas Regulamentadoras (NRs).
* **Recursos Humanos (RH) e Departamento Pessoal:** Cruzamento de cargos, admissões e conformidade de entregas legais.
* **Gestores e Supervisores Operacionais:** Tomada de decisão setorial sobre reposições de materiais e integridade da equipe.

### Resultado Esperado de Cada Entrega:
* Planilhas consolidadas em formato Microsoft Excel (`.xlsx`) com abas individualizadas por setor e painel de resumo executivo.
* Gráficos analíticos de distribuição de validade, pendências por setor e criticidade de itens em alta resolução (`.png` / `.svg`).
* Relatório executivo descritivo em Markdown detalhando premissas, divergências encontradas, métricas não sobrepostas e lacunas cadastrais.

---

## 2. Fontes de Dados

### 2.1 Localização e Conexão
* **Caminho da Base Primária:** `dados/base_controle_epis.csv` (codificação UTF-8).
* **Regras de Conexão:** Caso a fonte evolua para bancos relacionais (PostgreSQL/SQL Server) ou data lakes, os parâmetros devem ser injetados exclusivamente via variáveis de ambiente (`DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`), sendo terminantemente proibido o hardcoding de credenciais no código-fonte.
* **Política de Acesso:** Modo estritamente **somente-leitura** (*read-only*). O agente não possui permissão para modificar, deletar ou inserir registros no arquivo fonte.

### 2.2 Esquema da Base Fornecida (`base_controle_epis.csv`)
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `ID_Registro` | String | Identificador alfanumérico único da ficha de entrega (ex: `EPI-1001`). |
| `Colaborador` | String | Nome completo do funcionário recebedor. |
| `Setor` | String | Lotação do funcionário (Almoxarifado, Logística, Manutenção, Obras, Produção, Qualidade). |
| `Tipo_EPI` | String | Denominação padronizada do equipamento de proteção. |
| `Data_Entrega` | Date (YYYY-MM-DD) | Data em que o equipamento foi fornecido ao colaborador. |
| `Data_Validade` | Date (YYYY-MM-DD) | Data limite para uso seguro / expiração da validade de troca. |
| `Status_Troca` | String | Situação registrada no sistema (`Vencido`, `Troca Necessária`, `Regular`). |

### 2.3 Lacunas Documentadas na Base de Dados Atual
Em estrita observância à proibição de inventar campos ou dados fictícios:
1. **Campos de EPI Ausentes:** A base atual **não** contém:
   * `Matrícula` do colaborador.
   * `Função / Cargo` do colaborador.
   * `CA (Certificado de Aprovação)` emitido pelo Ministério do Trabalho e Emprego (MTE).
   * `Quantidade` fornecida.
   * `Assinatura / Aceite` formal (físico ou eletrônico).
2. **Base de Acidentes de Trabalho Ausente:** Não há, no repositório atual, tabela de acidentes de trabalho (`Data do Acidente`, `Setor`, `Tipo de Acidente`, `Gravidade`, `Dias de Afastamento`, `CAT emitida` ou `Horas-Homem Trabalhadas - HHT`). Os indicadores de acidentes estão documentados estruturalmente na Seção 4, aguardando o fornecimento da fonte respectiva.

---

## 3. Planilhas de EPIs

### 3.1 Colunas Normativas e Estrutura da Planilha
A saída gerada (`relatorios/relatorio_controle_epis.xlsx`) é estruturada com:
1. **Aba "Resumo Executivo":** Parâmetros temporais, totais sem sobreposição, matriz de validade vs. status registrado e visão resumida por setor.
2. **Aba "Pendências Críticas":** Listagem prioritária com todos os itens vencidos ou com troca solicitada.
3. **Abas Setoriais:** Uma aba dedicada para cada setor (`Almoxarifado`, `Logística`, `Manutenção`, `Obras`, `Produção`, `Qualidade`, e `Setor Não Informado`).
4. **Aba "Auditoria e Inconsistências":** Registro das anomalias cadastrais e lacunas legais.

### 3.2 Regras de Cálculo de Vencimento e Reposição
* **Data de Referência ($D_{ref}$):** Data local de execução da auditoria (padrão: `24/10/2026`).
* **Vencido:** $\text{Data\_Validade} < D_{ref}$.
* **Vence Hoje:** $\text{Data\_Validade} = D_{ref}$.
* **A Vencer:** $D_{ref} < \text{Data\_Validade} \le D_{ref} + 30\text{ dias}$.
* **Vigente:** $\text{Data\_Validade} > D_{ref} + 30\text{ dias}$.
* **Indeterminado:** Data ausente, inválida ou campo nulo.

### 3.3 Análise Cruzada e Totais Sem Dupla Contagem
Para evitar distorções de estoque e dupla contagem nas categorias:
* **Substituição Imediata (Vencidos):** Todos os itens com prazo expirado cronologicamente (inclusive se marcados como "Troca Necessária" ou "Regular" por desatualização).
* **Substituição Imediata (Solicitação/Avaria):** Itens com prazo cronológico vigente, porém com marcação de "Troca Necessária" (desgaste físico ou dano prévio).
* **Alerta Preventivo (A vencer em 30d):** Itens em conformidade que expirarão dentro da janela de 30 dias.
* **Conforme / Vigente:** Itens dentro do prazo de validade e com status operacional regular.

---

## 4. Gráficos de Indicadores de Acidentes

### 4.1 Fórmulas Regulamentares (NR-4, CIPA e NBR 14280)
Quando a base de sinistros for disponibilizada pelo usuário, o agente aplicará as fórmulas oficiais:

1. **Taxa de Frequência de Acidentes ($TF$):**
   $$TF = \frac{N \times 1.000.000}{HHT}$$
   * Onde $N$ = número total de acidentes com lesão no período; $HHT$ = Horas-Homem Trabalhadas no mesmo período.

2. **Taxa de Gravidade dos Acidentes ($TG$):**
   $$TG = \frac{T \times 1.000.000}{HHT}$$
   * Onde $T$ = total de dias perdidos (afastamentos) + dias debitados (incapacidades permanentes/morte).

3. **Quantidade de Acidentes:**
   * Distribuição por Setor, Tipo (Típico, Trajeto, Doença Ocupacional) e Mês do ano.

### 4.2 Padrão de Formatação dos Gráficos
* **Formatos de Saída:** Arquivos vetoriais SVG ou imagens rasterizadas de alta definição PNG (mínimo 300 DPI).
* **Elementos Obrigatórios:** Título claro e objetivo, rótulos explícitos nos eixos X e Y, valores numéricos anotados diretamente sobre as barras/fatias, legenda de cores padronizada e rodapé contendo a indicação da fonte primária dos dados.

---

## 5. Regras de Negócio e Conformidade Legal

* **NR-06 (Equipamentos de Proteção Individual):**
  * O empregador é obrigado a fornecer apenas EPI aprovado pelo órgão nacional competente e com CA válido (item 6.5.1).
  * O registro de entrega físico ou eletrônico é mandatório e deve conter descrição, CA, datas e confirmação de recebimento.
* **NR-04 e NR-05 (SESMT e CIPA):**
  * Acompanhamento mensal dos mapas de risco e estatísticas de segurança.
* **Proibição de Dados Fictícios:** É estritamente vedada a geração de dados artificiais ou inventados em relatórios técnicos de SST. Registros incompletos devem ser classificados como "Indeterminados" ou "Dados Ausentes".

---

## 6. Privacidade e LGPD (Lei 13.709/2018)

* **Minimização de Dados:** Exposição estritamente limitada ao nome do colaborador e setor para finalidade de gestão de segurança.
* **Dados Sensíveis de Saúde:** Laudos médicos, atestados de saúde ocupacional (ASO) e detalhes clínicos de Comunicação de Acidente de Trabalho (CAT) jamais devem ser mesclados ou expostos em planilhas operacionais de entrega de EPIs.
* **Não Versionamento de Dados Pessoais:** Arquivos com nomes e documentos de colaboradores não devem ser publicados em repositórios abertos.

---

## 7. Como Executar

### 7.1 Pré-requisitos
Ambiente Python 3.10+ com as bibliotecas:
```bash
pip install pandas openpyxl matplotlib
```

### 7.2 Execução do Processamento e Geração dos Relatórios
Para ler a base de dados, classificar vigências e gerar as planilhas e gráficos:
```bash
python gerar_relatorios.py
```
Os arquivos resultantes serão salvos no diretório `relatorios/`:
* `relatorios/relatorio_controle_epis.xlsx` (Planilha formatada multi-abas)
* `relatorios/grafico_status_validade.png` (Situação operacional dos EPIs)
* `relatorios/grafico_pendencias_por_setor.png` (Pendências por setor)
* `relatorios/grafico_tipos_epi.png` (Demandas por tipo de EPI)

### 7.3 Execução dos Testes Automatizados
```bash
python -m unittest tests/test_relatorios.py
```

---

## 8. Testes e Validação
O conjunto de testes unitários valida:
1. Contagem total exata de registros sem omissões (40 registros).
2. Classificação precisa dos itens vencidos (28 registros com data $< D_{ref}$).
3. Janela preventiva de 30 dias (identificação precisa do EPI-1036 com validade para 30/10/2026).
4. Identificação de divergência crítica de segurança (EPI-1005 vencido em 23/10/2026 com flag "Regular" na base).
5. Tratamento de registros com campos nulos (EPI-1006 com Setor ausente e EPI-1013 com Status nulo).
6. Soma não-sobreposta das categorias totalizando 100% da base.

---

## 9. Limites do Agente
1. **Natureza Consultiva:** O agente organiza, processa e apresenta dados de controle; ele **não** substitui o julgamento técnico, a inspeção visual e as decisões do Engenheiro ou Técnico de Segurança do Trabalho.
2. **Validade de Uso vs. Integridade Física:** A vigência temporal de um EPI não atesta automaticamente sua integridade mecânica. EPIs danificados devem ser substituídos de imediato, independentemente da data de expiração.
3. **Premissas Declaradas:** Sempre que houver lacunas cadastrais ou datas ausentes, o agente declara explicitamente as limitações nos relatórios emitidos.

---

## 2. Fontes de Dados

### 2.1 Localização e Conexão
* **Caminho da Base Primária:** `dados/base_controle_epis.csv` (codificação UTF-8).
* **Regras de Conexão:** Caso a fonte evolua para bancos relacionais (PostgreSQL/SQL Server) ou data lakes, os parâmetros devem ser injetados exclusivamente via variáveis de ambiente (`DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`), sendo terminantemente proibido o hardcoding de credenciais no código-fonte.
* **Política de Acesso:** Modo estritamente **somente-leitura** (*read-only*). O agente não possui permissão para modificar, deletar ou inserir registros no arquivo fonte.

### 2.2 Esquema da Base Fornecida (`base_controle_epis.csv`)
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `ID_Registro` | String | Identificador alfanumérico único da ficha de entrega (ex: `EPI-1001`). |
| `Colaborador` | String | Nome completo do funcionário recebedor. |
| `Setor` | String | Lotação do funcionário (Almoxarifado, Logística, Manutenção, Obras, Produção, Qualidade). |
| `Tipo_EPI` | String | Denominação padronizada do equipamento de proteção. |
| `Data_Entrega` | Date (YYYY-MM-DD) | Data em que o equipamento foi fornecido ao colaborador. |
| `Data_Validade` | Date (YYYY-MM-DD) | Data limite para uso seguro / expiração da validade de troca. |
| `Status_Troca` | String | Situação registrada no sistema (`Vencido`, `Troca Necessária`, `Regular`). |

### 2.3 Lacunas Documentadas na Base de Dados Atual
Em estrita observância à proibição de inventar campos ou dados fictícios:
1. **Campos de EPI Ausentes:** A base atual **não** contém:
   * `Matrícula` do colaborador.
   * `Função / Cargo` do colaborador.
   * `CA (Certificado de Aprovação)` emitido pelo Ministério do Trabalho e Emprego (MTE).
   * `Quantidade` fornecida.
   * `Assinatura / Aceite` formal (físico ou eletrônico).
2. **Base de Acidentes de Trabalho Ausente:** Não há, no repositório atual, tabela de acidentes de trabalho (`Data do Acidente`, `Setor`, `Tipo de Acidente`, `Gravidade`, `Dias de Afastamento`, `CAT emitida` ou `Horas-Homem Trabalhadas - HHT`). Os indicadores de acidentes estão documentados estruturalmente na Seção 4, aguardando o fornecimento da fonte respectiva.

---

## 3. Planilhas de EPIs

### 3.1 Colunas Normativas e Estrutura da Planilha
A saída gerada (`relatorios/relatorio_controle_epis.xlsx`) é estruturada com:
1. **Aba "Resumo Executivo":** Parâmetros temporais, totais sem sobreposição, matriz de validade vs. status registrado e visão resumida por setor.
2. **Aba "Pendências Críticas":** Listagem prioritária com todos os itens vencidos ou com troca solicitada.
3. **Abas Setoriais:** Uma aba dedicada para cada setor (`Almoxarifado`, `Logística`, `Manutenção`, `Obras`, `Produção`, `Qualidade`, e `Setor Não Informado`).
4. **Aba "Auditoria e Inconsistências":** Registro das anomalias cadastrais e lacunas legais.

### 3.2 Regras de Cálculo de Vencimento e Reposição
* **Data de Referência ($D_{ref}$):** Data local de execução da auditoria (padrão: `24/10/2026`).
* **Vencido:** $\text{Data\_Validade} < D_{ref}$.
* **Vence Hoje:** $\text{Data\_Validade} = D_{ref}$.
* **A Vencer:** $D_{ref} < \text{Data\_Validade} \le D_{ref} + 30\text{ dias}$.
* **Vigente:** $\text{Data\_Validade} > D_{ref} + 30\text{ dias}$.
* **Indeterminado:** Data ausente, inválida ou campo nulo.

### 3.3 Análise Cruzada e Totais Sem Dupla Contagem
Para evitar distorções de estoque e dupla contagem nas categorias:
* **Substituição Imediata (Vencidos):** Todos os itens com prazo expirado cronologicamente (inclusive se marcados como "Troca Necessária" ou "Regular" por desatualização).
* **Substituição Imediata (Solicitação/Avaria):** Itens com prazo cronológico vigente, porém com marcação de "Troca Necessária" (desgaste físico ou dano prévio).
* **Alerta Preventivo (A vencer em 30d):** Itens em conformidade que expirarão dentro da janela de 30 dias.
* **Conforme / Vigente:** Itens dentro do prazo de validade e com status operacional regular.

---

## 4. Gráficos de Indicadores de Acidentes

### 4.1 Fórmulas Regulamentares (NR-4, CIPA e NBR 14280)
Quando a base de sinistros for disponibilizada pelo usuário, o agente aplicará as fórmulas oficiais:

1. **Taxa de Frequência de Acidentes ($TF$):**
   $$TF = \frac{N \times 1.000.000}{HHT}$$
   * Onde $N$ = número total de acidentes com lesão no período; $HHT$ = Horas-Homem Trabalhadas no mesmo período.

2. **Taxa de Gravidade dos Acidentes ($TG$):**
   $$TG = \frac{T \times 1.000.000}{HHT}$$
   * Onde $T$ = total de dias perdidos (afastamentos) + dias debitados (incapacidades permanentes/morte).

3. **Quantidade de Acidentes:**
   * Distribuição por Setor, Tipo (Típico, Trajeto, Doença Ocupacional) e Mês do ano.

### 4.2 Padrão de Formatação dos Gráficos
* **Formatos de Saída:** Arquivos vetoriais SVG ou imagens rasterizadas de alta definição PNG (mínimo 300 DPI).
* **Elementos Obrigatórios:** Título claro e objetivo, rótulos explícitos nos eixos X e Y, valores numéricos anotados diretamente sobre as barras/fatias, legenda de cores padronizada e rodapé contendo a indicação da fonte primária dos dados.

---

## 5. Regras de Negócio e Conformidade Legal

* **NR-06 (Equipamentos de Proteção Individual):**
  * O empregador é obrigado a fornecer apenas EPI aprovado pelo órgão nacional competente e com CA válido (item 6.5.1).
  * O registro de entrega físico ou eletrônico é mandatório e deve conter descrição, CA, datas e confirmação de recebimento.
* **NR-04 e NR-05 (SESMT e CIPA):**
  * Acompanhamento mensal dos mapas de risco e estatísticas de segurança.
* **Proibição de Dados Fictícios:** É estritamente vedada a geração de dados artificiais ou inventados em relatórios técnicos de SST. Registros incompletos devem ser classificados como "Indeterminados" ou "Dados Ausentes".

---

## 6. Privacidade e LGPD (Lei 13.709/2018)

* **Minimização de Dados:** Exposição estritamente limitada ao nome do colaborador e setor para finalidade de gestão de segurança.
* **Dados Sensíveis de Saúde:** Laudos médicos, atestados de saúde ocupacional (ASO) e detalhes clínicos de Comunicação de Acidente de Trabalho (CAT) jamais devem ser mesclados ou expostos em planilhas operacionais de entrega de EPIs.
* **Não Versionamento de Dados Pessoais:** Arquivos com nomes e documentos de colaboradores não devem ser publicados em repositórios abertos.

---

## 7. Como Executar

### 7.1 Pré-requisitos
Ambiente Python 3.10+ com as bibliotecas:
```bash
pip install pandas openpyxl matplotlib
```

### 7.2 Execução do Processamento e Geração dos Relatórios
Para ler a base de dados, classificar vigências e gerar as planilhas e gráficos:
```bash
python gerar_relatorios.py
```
Os arquivos resultantes serão salvos no diretório `relatorios/`:
* `relatorios/relatorio_controle_epis.xlsx` (Planilha formatada multi-abas)
* `relatorios/grafico_status_validade.png` (Situação operacional dos EPIs)
* `relatorios/grafico_pendencias_por_setor.png` (Pendências por setor)
* `relatorios/grafico_tipos_epi.png` (Demandas por tipo de EPI)

### 7.3 Execução dos Testes Automatizados
```bash
python -m unittest tests/test_relatorios.py
```

---

## 8. Testes e Validação
O conjunto de testes unitários valida:
1. Contagem total exata de registros sem omissões (40 registros).
2. Classificação precisa dos itens vencidos (28 registros com data $< D_{ref}$).
3. Janela preventiva de 30 dias (identificação precisa do EPI-1036 com validade para 30/10/2026).
4. Identificação de divergência crítica de segurança (EPI-1005 vencido em 23/10/2026 com flag "Regular" na base).
5. Tratamento de registros com campos nulos (EPI-1006 com Setor ausente e EPI-1013 com Status nulo).
6. Soma não-sobreposta das categorias totalizando 100% da base.

---

## 9. Limites do Agente
1. **Natureza Consultiva:** O agente organiza, processa e apresenta dados de controle; ele **não** substitui o julgamento técnico, a inspeção visual e as decisões do Engenheiro ou Técnico de Segurança do Trabalho.
2. **Validade de Uso vs. Integridade Física:** A vigência temporal de um EPI não atesta automaticamente sua integridade mecânica. EPIs danificados devem ser substituídos de imediato, independentemente da data de expiração.
3. **Premissas Declaradas:** Sempre que houver lacunas cadastrais ou datas ausentes, o agente declara explicitamente as limitações nos relatórios emitidos.

