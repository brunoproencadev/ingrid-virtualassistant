# Ingrid: fluxogramas do atendimento e automação

Bruno Proença Silva | Revisão de 06/10/2026. Desenhos para revisão da equipe; a automação ainda será implementada. Sistema pronto: 03/11/2026.

Como ler: retângulos são etapas; caixas rosas com pergunta são decisões; setas indicam o próximo passo. O PDF usa a mesma sequência deste arquivo.

Prazos internos: S03, S04, S05 e S06 até 08/10; S08 e S11 iniciam em 09/10. O envio oficial do Sprint 3 continua em 06/10.

Vocabulário: webhook = entrada de eventos; ACK = confirmação de recebimento; parser = leitor do formato de saída; transação = gravação que acontece por inteiro ou não acontece; idempotência = repetir sem duplicar o efeito; opt-out = pedido para parar mensagens.

## 01 - Atendimento no WhatsApp

Maria Clara revisa a jornada; Matheus confere mensagens e limites.

```mermaid
flowchart TD
  A["Cliente envia uma mensagem<br/>A Ingrid recebe pelo WhatsApp via HGTX."]
  B["Identificar o que a pessoa precisa<br/>Comprar, consultar, cancelar ou pedir ajuda."]
  C["Mostrar catálogo e coletar escolhas<br/>Produto real, opções e quantidade válida."]
  D["Calcular e apresentar o resumo<br/>Preço do catálogo e previsão de produção."]
  E{"Cliente confirma o resumo?<br/>Uma mudança exige um novo resumo."}
  F["Consultar ou cancelar pedido<br/>Consultar somente o próprio contato. Cancelamento usa as regras do pedido."]
  G{"Precisa da vendedora?<br/>Pedido de ajuda, assunto não atendido ou personalização não prevista."}
  H["Transferir o atendimento<br/>Avisar a vendedora e pausar respostas do bot."]
  I["Criar solicitação única<br/>Seguir o fluxo de aprovação (página 3)."]
  J["Informar o andamento<br/>Prazo final somente após aprovação. Consultas futuras mostram o status salvo."]
  A --> B
  B -->|Comprar| C
  B -->|Consultar| F
  B -->|Ajuda| G
  G -->|Sim| H
  G -->|Não| C
  C --> D
  D --> E
  E -->|Sim| I
  I -->|Aprovado| J
  E -->|Corrigir| C
```

Sem descontos ou condições não aprovadas. Opt-out (pedido para parar mensagens) interrompe os envios automáticos; mensagens de erro oferecem uma alternativa clara.

## 02 - Recepção e processamento no n8n

Rafael revisa os nós e o banco; Matheus testa repetição, reinício e dois clientes.

```mermaid
flowchart TD
  A["Webhook: receber evento HGTX<br/>Conferir assinatura/autenticação, formato e tamanho."]
  B{"Evento válido?<br/>Sem autenticação válida, não aceitar dados."}
  C{"Já recebemos este ID?<br/>Banco com ID único por evento."}
  D["Salvar evento antes de confirmar<br/>Evento e tarefa pendente gravados juntos."]
  E["Confirmar recebimento à HGTX<br/>ACK após a gravação; status de envio segue rota própria."]
  F["Recusar e registrar falha<br/>Usar resposta prevista no contrato HGTX."]
  G["Confirmar sem repetir trabalho<br/>Não criar nova resposta ou novo pedido."]
  N["Recuperar ou chamar a vendedora<br/>Campos inválidos: não alterar pedido; seguir página 4."]
  H["Schedule Trigger: buscar pendências<br/>Assumir uma tarefa por vez com controle no banco."]
  I["Recuperar estado da conversa<br/>Processar em ordem por contato; humano ou opt-out bloqueia respostas do bot."]
  J["IA: interpretar e extrair campos<br/>Basic LLM Chain + modelo + parser de saída."]
  K{"Campos válidos?<br/>Validar produto, quantidade, ação e identidade fora da IA."}
  L["Aplicar regras e salvar resultado<br/>Preço, prazo e pedido no banco; gravar também a resposta pendente."]
  M["Enviar pelo fluxo de saída<br/>Página 4. Se a execução cair, recuperar apenas o trabalho pendente."]
  A --> B
  B -->|Não| F
  B -->|Sim| C
  C -->|Sim| G
  C -->|Não| D
  D --> E
  E -->|Evento| H
  H --> I
  I --> J
  J --> K
  K -->|Sim| L
  K -->|Não| N
  L --> M
```

Evento de status atualiza a entrega, sem chamar a IA. Banco indisponível: não dar ACK de sucesso; permitir reentrega conforme contrato. Saída inválida da IA: não alterar pedido; recuperação limitada ou atendimento humano (página 4).

## 03 - Encomenda, capacidade e aprovação

Rafael monta o cálculo; Bruno valida as regras com a vendedora.

```mermaid
flowchart TD
  A["Consultar catálogo aprovado<br/>Preço, foto, opções e tempo por item."]
  B["Calcular orçamento e previsão<br/>Fila, capacidade, materiais, dias úteis e margem. Entrega é separada da produção."]
  C["Salvar versão do resumo<br/>Registrar os termos mostrados ao cliente."]
  D{"Cliente aceita a versão atual?<br/>Aceite explícito; termos antigos não valem."}
  E["Conferir capacidade e reservar<br/>Tudo em uma transação no banco, com chave única da solicitação."]
  F["Corrigir escolhas ou encerrar<br/>Novo resumo se houver mudança."]
  G{"Ainda existe capacidade?<br/>Outro cliente pode ter reservado antes."}
  H["Recalcular ou avaliar com humano<br/>Não prometer o prazo que ficou indisponível."]
  I["Aguardar revisão da vendedora<br/>Reserva temporária com validade definida; pedido ainda não está confirmado."]
  J{"Vendedora aprova os mesmos termos?<br/>Acesso autenticado; conferir prazo, reserva e validade."}
  K["Confirmar encomenda uma única vez<br/>Gravar aprovação e resposta a enviar na mesma transação."]
  L["Termos mudaram ou foi recusado?<br/>Alteração: novo resumo e novo aceite. Recusa: encerrar e liberar a reserva."]
  M["Cancelar ou vencer a reserva<br/>Liberar capacidade uma única vez; pedido confirmado segue a política da vendedora."]
  A --> B
  B --> C
  C --> D
  D -->|Sim| E
  D -->|Não| F
  E --> G
  G -->|Não| H
  G -->|Sim| I
  I --> J
  J -->|Sim| K
  J -->|Não| L
  L -->|Recusa| M
  F -->|Revisar| C
```

A reserva e a aprovação revalidam dados no banco; chamadas separadas não podem vender a mesma capacidade. Alteração de preço, prazo ou opções invalida o aceite anterior. Expiração e rejeição liberam apenas reservas ativas.

## 04 - Envio, falhas e atendimento humano

Rafael implementa a recuperação; Matheus registra o esperado e o observado.

```mermaid
flowchart TD
  A["Buscar resposta pendente no banco<br/>Em ordem por contato; conferir se bot pode enviar."]
  B{"Envio permitido?<br/>Humano, opt-out ou resposta antiga impedem envio automático."}
  C["HTTP Request: enviar via HGTX<br/>Usar chave de idempotência se o contrato oferecer."]
  D{"Qual foi o resultado?<br/>Sucesso, falha conhecida ou resultado incerto."}
  E["Salvar ID e acompanhar status<br/>Aceito pela API não significa entregue ao cliente."]
  F["Pausar ou descartar saída antiga<br/>Vendedora assume; retomada do bot é explícita."]
  G["Falha temporária conhecida<br/>Repetir com intervalo crescente e limite de tentativas; respeitar limites HGTX."]
  H{"É possível verificar o envio incerto?<br/>Consultar status ou usar a mesma chave, se o contrato permitir."}
  N["Consultar e decidir o próximo passo<br/>Já entregue: ir a E. Não enviado: voltar a C, somente com repetição segura."]
  I["Falha permanente ou limite atingido<br/>Registrar erro, avisar a operação e oferecer recuperação humana."]
  J["Sem consulta ou chave segura<br/>Não reenviar às cegas; registrar envio incerto e pedir verificação humana."]
  K["Falha IA ou dados inválidos<br/>Nenhuma mudança comercial. Uma tentativa de recuperação controlada ou humano."]
  L["Detectar trabalho parado<br/>Schedule Trigger verifica tarefas presas; Error Trigger registra falhas da execução."]
  A --> B
  B -->|Não| F
  B -->|Sim| C
  C --> D
  D -->|Sucesso| E
  D -->|Falha| G
  D -->|Incerto| H
  G -->|Limite| I
  H -->|Sim| N
  H -->|Não| J
  J --> I
```

Envio confirmado: salvar resultado. Nova tentativa segura volta ao envio (C). Falhas de execução são registradas sem apagar encomendas; logs e capturas omitem dados pessoais e segredos. O contrato HGTX ainda precisa confirmar IDs, status e idempotência.
