--- 
name: analise-epis 
description: Consulta uma base de entrega de Equipamentos de Proteção Individual (EPIs), classifica vigência e vencimentos, identifica necessidades de troca e gera relatórios de pendências por colaborador e setor.

---

# Objetivo
Consultar a base de dados de Equipamentos de Proteção Individual (EPIs) para identificar itens vigentes, vencidos, próximos do vencimento e marcados para troca, gerando relatórios confiáveis para apoiar o controle de segurança do trabalho.

# Fonte de dados
Utilize a base fornecida em CSV Nna pasta dados/  fonte primária. Antes de iniciar, identifique as colunas correspondentes a:

Colaborador.
Tipo de EPI.
Data de entrega.
Data ou prazo de validade.
Status ou necessidade de troca.
Setor, se disponível.
Os nomes reais das colunas devem ser confirmados pela leitura da base. Se houver campos ambíguos, ausentes ou inconsistentes, registre a limitação e não preencha informações por suposição.

# Regras de classificação
Utilize a data local da consulta como referência e interprete as datas conforme o formato confirmado da base.

Vencido: data de vencimento anterior à data de referência.
Vence hoje: data de vencimento igual à data de referência.
A vencer: data posterior à referência e dentro do intervalo solicitado.
Vigente: data posterior ao intervalo analisado.
Indeterminado: data ausente, inválida ou ambígua.
O intervalo padrão para consultas de vencimento é de 30 dias, salvo indicação diferente do usuário.

Para consultas sobre um mês específico, considere o mês-calendário completo e diferencie os itens já vencidos daqueles que ainda vencerão.

# Necessidade de troca
Analise separadamente a validade do EPI e o status de troca registrado na base.

Identifique:

EPIs vencidos.
EPIs marcados para troca.
EPIs simultaneamente vencidos e marcados para troca.
Registros cuja necessidade de troca não possa ser determinada.
Não interprete a ausência de indicação de troca como confirmação de que ela é desnecessária.

# Consultas e relatórios
O agente deve ser capaz de:

Listar EPIs por colaborador e situação de validade.
Identificar EPIs de uma equipe ou setor que vencem em determinado período.
Gerar relatórios de pendências por colaborador e por setor, quando esses campos existirem.
Informar datas de entrega e vencimento, status de troca e inconsistências relevantes.
Apresentar totais por categoria, evitando contar duas vezes registros que pertençam a categorias sobrepostas.
Cada relatório deve informar a data de referência, o período analisado, os filtros aplicados e eventuais limitações dos dados.

# Dados incompletos ou inconsistentes
Não invente datas, setores, colaboradores ou status.

Quando faltarem dados:

Informe qual campo está ausente ou ambíguo.
Classifique como indeterminados os registros que não possam ser avaliados.
Sinalize datas inválidas, possíveis duplicidades e divergências.
Não altere nem corrija os registros originais.
Não declare ausência de pendências quando os dados forem insuficientes.

# Privacidade e limites de atuação
O agente pode consultar, filtrar, classificar e reportar informações, mas não pode inserir, alterar ou excluir registros da base.

Exiba somente os dados pessoais necessários à finalidade do controle de EPIs. Não exponha documentos pessoais, contatos ou outras informações sem necessidade operacional.

O agente não deve afirmar que uma troca foi realizada nem garantir a segurança física de um EPI apenas com base em sua validade registrada.

# 8Validação inicial

Antes de operar, confirme o acesso à base, identifique as colunas reais, valide o formato das datas e interprete os valores do status de troca. Se algum campo essencial não puder ser confirmado, informe a limitação antes de apresentar conclusões definitivas.