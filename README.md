# Ingrid - assistente virtual de vendas

Projeto de hackathon para atender clientes de uma artesã de terços e laços pelo WhatsApp, usando n8n e a API que será disponibilizada pela HGTX.

## Etapa atual

Planejamento do Sprint 3, organização das tarefas e desenho da solução. A automação ainda não foi implementada, integrada ou testada em execução.

- Entrega preparatória do Sprint 3: **06/10/2026**.
- Entrega do sistema pronto: **03/11/2026**.
- Novas funcionalidades até 27/10; correções e testes até 30/10; margem de 31/10 a 02/11.
- Revisão interna de S03, S04, S05 e S06 até 08/10; S08 e S11 começam em 09/10. A revisão interna não altera o prazo oficial do Sprint 3.

## Materiais

| Material | Conteúdo |
| --- | --- |
| [Plano do Sprint 3](PLANO_SPRINT_3_INGRID.md) | Escopo, cronograma, responsabilidades, arquitetura e critérios de entrega. A atualização de 06/10 prevalece sobre o registro anterior. |
| [Fluxogramas editáveis](FLUXOGRAMAS_INGRID.md) | Atendimento, processamento no n8n, aprovação e recuperação de falhas, em Mermaid. |
| [PDF dos fluxogramas](output/pdf/fluxogramas.pdf) | Quatro páginas para revisão e compartilhamento com a equipe. |

## Equipe

- Bruno Proença Silva: liderança, escopo, regras comerciais, contato com HGTX e entrega.
- Rafael: integração técnica, n8n e banco de dados.
- Matheus: instruções da IA, limites, testes e documentação.
- Maria Clara Lima: experiência do cliente, telas, testes de uso e demonstração.

## Regras principais

Produtos, fotos, preços e capacidade de produção precisam de aprovação da vendedora. A IA interpreta as mensagens; preço, prazo e reservas são controlados por regras e pelo banco. A confirmação da encomenda depende do aceite do cliente e da aprovação da vendedora. Mensagens repetidas não podem duplicar pedidos, e o atendimento humano pausa o bot.

Não publicar credenciais, dados reais de clientes ou exportações do n8n com segredos. As metas de melhoria descritas no planejamento são hipóteses, não resultados medidos.

O acompanhamento da equipe acontece em um quadro privado. Links, identificadores, perfis, capturas e registros desse quadro não fazem parte desta versão pública. O PDF interno do Sprint 3 também permanece fora do repositório por conter links e QR code de acesso ao quadro; seu planejamento está disponível no Markdown acima.

## Gerar novamente o PDF dos fluxogramas

O gerador é uma ferramenta de documentação, não um workflow executável do n8n. Ele usa Python, ReportLab, pypdf e as fontes Arial instaladas no Windows (`C:/Windows/Fonts`).

```powershell
python -m pip install -r output/sprint3/requirements.txt
python output/sprint3/gerar_fluxogramas.py
```

O comando atualiza o PDF e o Markdown dos fluxogramas a partir das etapas definidas no script. Para mudar as etapas de ambos, edite `output/sprint3/gerar_fluxogramas.py`; mudanças manuais apenas no Markdown não alteram o PDF.
