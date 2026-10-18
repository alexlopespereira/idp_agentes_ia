---
layout: default
title: Codebook de falhas por resposta, v1
---

# Onda 5r — codebook prospectivo de falhas por resposta, v1

Fixado em 26/09/2026 após o piloto dirigido da 5q e **antes da próxima
amostra**. Esta versão define decisões observáveis, não a verdade factual ou
o efeito do atendimento. Mudanças futuras exigem nova versão datada antes de
analisar os rótulos da amostra independente. O relatório do piloto e sua
proveniência permanecem no repositório de pesquisa, sem conteúdo aqui.

## Unidade, contexto e ordem de decisão

A unidade é um registro literal `Output` selecionado, com as mensagens
anteriores da mesma sessão validada até o alvo. Mensagens posteriores não
sustentam o vínculo do alvo com o pedido. `Input`/`Output`, papel literal e
horário são pistas; isoladamente não provam autoria ou causa. Guarde a
referência `Mn` do `Input` que expressa a demanda humana.

1. **Avaliabilidade.** Marque `resposta_avaliavel` apenas se houver demanda
   humana identificável em `Input` anterior, vínculo defensável com o alvo e
   contexto suficiente para julgar essa resposta. Caso contrário marque
   `nao_avaliavel` e um motivo: `sem_pedido_identificavel`, `vinculo_incerto`,
   `conteudo_insuficiente` ou `autoria_incerta`. Sem `Input` anterior na fonte,
   use `sem_pedido_identificavel`; isto não afirma que não existiu pedido fora
   da fonte. Um relato dirigido aparentemente a outra organização, sem
   demanda identificável ao assistente, também pode receber esse motivo.
2. **Falha observável.** Somente em resposta avaliável, marque `sim` se houver
   indício suficiente de falha no atendimento ao pedido referenciado;
   `nao` se não houver falha observável; `indeterminado` se a evidência
   permitir vincular a resposta ao pedido, mas não decidir se houve falha.
   Uma recusa clara a pedido fora do escopo, com orientação útil quando
   possível, não é falha automática.
3. **Subtipo e justificativa.** Se a falha for `sim`, escolha um subtipo e
   registre justificativa curta baseada no texto até o alvo, sem
   identificadores pessoais. Não atribua erro factual ou de elegibilidade sem
   conferir fonte oficial datada; na falta dela, use `indeterminado` quando
   essa verificação for decisiva.

## Subtipos de `sim`

| Subtipo | Regra operacional |
| --- | --- |
| `nao_responde_ao_pedido` | A resposta ignora a demanda referenciada ou trata apenas de outro assunto. Inclui texto genérico que não oferece encaminhamento pertinente. |
| `repeticao_ou_loop` | A resposta repete conteúdo ou passo já tentado, sem avançar a demanda, com repetição observável no contexto anterior. Não use com uma única mensagem apenas parecida com um modelo. |
| `pedido_de_humano_nao_atendido` | Há pedido explícito para falar com pessoa, e a resposta ignora esse pedido ou deixa de oferecer encaminhamento ou orientação útil observável. Dê preferência a este subtipo quando esse for o problema central, mesmo que a resposta também seja genérica. |
| `clarificacao_evitavel` | O tema é identificável e era possível dar uma resposta inicial útil e segura, mas o assistente apenas pede mais detalhes. Pedido realmente ambíguo pode justificar esclarecimento. |
| `outro` | Falha observável que não cabe nos quatro subtipos acima; descreva concretamente o comportamento e a razão de não caber nas categorias. |

Se mais de um subtipo se aplicar, escolha o que melhor descreve a falha
central da resposta e registre a sobreposição na justificativa. Uma pergunta
que não permite saber qual serviço ou ação a pessoa quer não torna toda
clarificação evitável. Resposta fora de escopo e pedido impossível não são
falhas por si.

## Aplicação na amostra independente

- Selecione as unidades sem usar rótulos ou propostas do Gemma como critério
  de inclusão, salvo estrato explicitamente pré-registrado com peso conhecido.
- Registre por item decisão, referência, subtipo, justificativa, versão deste
  codebook, anotador, data e modo de obtenção (`individual` ou `lote`).
- Revise desacordos e categorias `outro` sem mudar retrospectivamente os
  critérios desta versão. Qualquer emenda deve preservar os rótulos brutos e
  explicitar quais itens foram reaplicados sob a nova versão.
- Calcule denominadores e incerteza respeitando a seleção de sessões e a
  dependência entre respostas da mesma sessão.
