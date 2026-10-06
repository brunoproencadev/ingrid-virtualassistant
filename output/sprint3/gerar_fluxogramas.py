from pathlib import Path
from math import atan2, cos, sin
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/fluxogramas.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold')
INK='#243044';PINK='#AD236D';MUTED='#526176'
style=ParagraphStyle('box',fontName='Arial',fontSize=9,leading=12,textColor=colors.HexColor(INK))
small=ParagraphStyle('note',fontName='Arial',fontSize=9,leading=12,textColor=colors.HexColor(MUTED))
# Cada nó: id, coluna, linha, título, explicação, é decisão.
# Cada ligação: origem, destino, rótulo, desvio opcional (coordenadas do topo).
pages=[
('01','Atendimento no WhatsApp','Maria Clara revisa a jornada; Matheus confere mensagens e limites.',[
 ('A',0,0,'Cliente envia uma mensagem','A Ingrid recebe pelo WhatsApp via HGTX.',False),
 ('B',0,1,'Identificar o que a pessoa precisa','Comprar, consultar, cancelar ou pedir ajuda.',False),
 ('C',0,2,'Mostrar catálogo e coletar escolhas','Produto real, opções e quantidade válida.',False),
 ('D',0,3,'Calcular e apresentar o resumo','Preço do catálogo e previsão de produção.',False),
 ('E',0,4,'Cliente confirma o resumo?','Uma mudança exige um novo resumo.',True),
 ('F',1,0,'Consultar ou cancelar pedido','Consultar somente o próprio contato. Cancelamento usa as regras do pedido.',False),
 ('G',1,1,'Precisa da vendedora?','Pedido de ajuda, assunto não atendido ou personalização não prevista.',True),
 ('H',2,1,'Transferir o atendimento','Avisar a vendedora e pausar respostas do bot.',False),
 ('I',1,4,'Criar solicitação única','Seguir o fluxo de aprovação (página 3).',False),
 ('J',2,4,'Informar o andamento','Prazo final somente após aprovação. Consultas futuras mostram o status salvo.',False),
 ], [('A','B',''),('B','C','Comprar'),('B','F','Consultar',[(280,222),(280,144)]),('B','G','Ajuda'),('G','H','Sim'),('G','C','Não',[(411,268),(290,268),(290,300)]),('C','D',''),('D','E',''),('E','I','Sim'),('I','J','Aprovado'),('E','C','Corrigir',[(28,456),(28,300)])],
 'Sem descontos ou condições não aprovadas. Opt-out (pedido para parar mensagens) interrompe os envios automáticos; mensagens de erro oferecem uma alternativa clara.'),
('02','Recepção e processamento no n8n','Rafael revisa os nós e o banco; Matheus testa repetição, reinício e dois clientes.',[
 ('A',0,0,'Webhook: receber evento HGTX','Conferir assinatura/autenticação, formato e tamanho.',False),
 ('B',0,1,'Evento válido?','Sem autenticação válida, não aceitar dados.',True),
 ('C',0,2,'Já recebemos este ID?','Banco com ID único por evento.',True),
 ('D',0,3,'Salvar evento antes de confirmar','Evento e tarefa pendente gravados juntos.',False),
 ('E',0,4,'Confirmar recebimento à HGTX','ACK após a gravação; status de envio segue rota própria.',False),
 ('F',1,0,'Recusar e registrar falha','Usar resposta prevista no contrato HGTX.',False),
 ('G',1,2,'Confirmar sem repetir trabalho','Não criar nova resposta ou novo pedido.',False),
 ('N',1,1,'Recuperar ou chamar a vendedora','Campos inválidos: não alterar pedido; seguir página 4.',False),
 ('H',1,4,'Schedule Trigger: buscar pendências','Assumir uma tarefa por vez com controle no banco.',False),
 ('I',2,4,'Recuperar estado da conversa','Processar em ordem por contato; humano ou opt-out bloqueia respostas do bot.',False),
 ('J',2,3,'IA: interpretar e extrair campos','Basic LLM Chain + modelo + parser de saída.',False),
 ('K',2,2,'Campos válidos?','Validar produto, quantidade, ação e identidade fora da IA.',True),
 ('L',2,1,'Aplicar regras e salvar resultado','Preço, prazo e pedido no banco; gravar também a resposta pendente.',False),
 ('M',2,0,'Enviar pelo fluxo de saída','Página 4. Se a execução cair, recuperar apenas o trabalho pendente.',False),
 ], [('A','B',''),('B','F','Não',[(280,222),(280,144)]),('B','C','Sim'),('C','G','Sim'),('C','D','Não'),('D','E',''),('E','H','Evento'),('H','I',''),('I','J',''),('J','K',''),('K','L','Sim'),('K','N','Não',[(542,300),(542,222)]),('L','M','')],
 'Evento de status atualiza a entrega, sem chamar a IA. Banco indisponível: não dar ACK de sucesso; permitir reentrega conforme contrato. Saída inválida da IA: não alterar pedido; recuperação limitada ou atendimento humano (página 4).'),
('03','Encomenda, capacidade e aprovação','Rafael monta o cálculo; Bruno valida as regras com a vendedora.',[
 ('A',0,0,'Consultar catálogo aprovado','Preço, foto, opções e tempo por item.',False),
 ('B',0,1,'Calcular orçamento e previsão','Fila, capacidade, materiais, dias úteis e margem. Entrega é separada da produção.',False),
 ('C',0,2,'Salvar versão do resumo','Registrar os termos mostrados ao cliente.',False),
 ('D',0,3,'Cliente aceita a versão atual?','Aceite explícito; termos antigos não valem.',True),
 ('E',0,4,'Conferir capacidade e reservar','Tudo em uma transação no banco, com chave única da solicitação.',False),
 ('F',1,3,'Corrigir escolhas ou encerrar','Novo resumo se houver mudança.',False),
 ('G',1,4,'Ainda existe capacidade?','Outro cliente pode ter reservado antes.',True),
 ('H',2,4,'Recalcular ou avaliar com humano','Não prometer o prazo que ficou indisponível.',False),
 ('I',1,2,'Aguardar revisão da vendedora','Reserva temporária com validade definida; pedido ainda não está confirmado.',False),
 ('J',1,1,'Vendedora aprova os mesmos termos?','Acesso autenticado; conferir prazo, reserva e validade.',True),
 ('K',1,0,'Confirmar encomenda uma única vez','Gravar aprovação e resposta a enviar na mesma transação.',False),
 ('L',2,1,'Termos mudaram ou foi recusado?','Alteração: novo resumo e novo aceite. Recusa: encerrar e liberar a reserva.',False),
 ('M',2,0,'Cancelar ou vencer a reserva','Liberar capacidade uma única vez; pedido confirmado segue a política da vendedora.',False),
 ], [('A','B',''),('B','C',''),('C','D',''),('D','E','Sim'),('D','F','Não'),('E','G',''),('G','H','Não'),('G','I','Sim',[(542,456),(542,300)]),('I','J',''),('J','K','Sim'),('J','L','Não'),('L','M','Recusa'),('F','C','Revisar',[(280,378),(280,300)])],
 'A reserva e a aprovação revalidam dados no banco; chamadas separadas não podem vender a mesma capacidade. Alteração de preço, prazo ou opções invalida o aceite anterior. Expiração e rejeição liberam apenas reservas ativas.'),
('04','Envio, falhas e atendimento humano','Rafael implementa a recuperação; Matheus registra o esperado e o observado.',[
 ('A',0,0,'Buscar resposta pendente no banco','Em ordem por contato; conferir se bot pode enviar.',False),
 ('B',0,1,'Envio permitido?','Humano, opt-out ou resposta antiga impedem envio automático.',True),
 ('C',0,2,'HTTP Request: enviar via HGTX','Usar chave de idempotência se o contrato oferecer.',False),
 ('D',0,3,'Qual foi o resultado?','Sucesso, falha conhecida ou resultado incerto.',True),
 ('E',0,4,'Salvar ID e acompanhar status','Aceito pela API não significa entregue ao cliente.',False),
 ('F',1,1,'Pausar ou descartar saída antiga','Vendedora assume; retomada do bot é explícita.',False),
 ('G',1,3,'Falha temporária conhecida','Repetir com intervalo crescente e limite de tentativas; respeitar limites HGTX.',False),
 ('H',2,3,'É possível verificar o envio incerto?','Consultar status ou usar a mesma chave, se o contrato permitir.',True),
 ('N',2,2,'Consultar e decidir o próximo passo','Já entregue: ir a E. Não enviado: voltar a C, somente com repetição segura.',False),
 ('I',1,4,'Falha permanente ou limite atingido','Registrar erro, avisar a operação e oferecer recuperação humana.',False),
 ('J',2,4,'Sem consulta ou chave segura','Não reenviar às cegas; registrar envio incerto e pedir verificação humana.',False),
 ('K',1,0,'Falha IA ou dados inválidos','Nenhuma mudança comercial. Uma tentativa de recuperação controlada ou humano.',False),
 ('L',2,0,'Detectar trabalho parado','Schedule Trigger verifica tarefas presas; Error Trigger registra falhas da execução.',False),
 ], [('A','B',''),('B','F','Não'),('B','C','Sim'),('C','D',''),('D','E','Sucesso'),('D','G','Falha'),('D','H','Incerto',[(280,378),(280,417),(800,417),(800,378)]),('G','I','Limite'),('H','N','Sim'),('H','J','Não'),('J','I','')],
 'Envio confirmado: salvar resultado. Nova tentativa segura volta ao envio (C). Falhas de execução são registradas sem apagar encomendas; logs e capturas omitem dados pessoais e segredos. O contrato HGTX ainda precisa confirmar IDs, status e idempotência.'),
]

c=canvas.Canvas(str(OUT),pagesize=(842,595))
c.setTitle('Ingrid - Fluxogramas do atendimento e automação')
c.setAuthor('Bruno Proença Silva')
markdown=['# Ingrid: fluxogramas do atendimento e automação','',
'Bruno Proença Silva | Revisão de 06/10/2026. Desenhos para revisão da equipe; a automação ainda será implementada. Sistema pronto: 03/11/2026.',
'','Como ler: retângulos são etapas; caixas rosas com pergunta são decisões; setas indicam o próximo passo. O PDF usa a mesma sequência deste arquivo.',
'','Prazos internos: S03, S04, S05 e S06 até 08/10; S08 e S11 iniciam em 09/10. O envio oficial do Sprint 3 continua em 06/10.',
'','Vocabulário: webhook = entrada de eventos; ACK = confirmação de recebimento; parser = leitor do formato de saída; transação = gravação que acontece por inteiro ou não acontece; idempotência = repetir sem duplicar o efeito; opt-out = pedido para parar mensagens.','']

def para(text,x,top,width,sty=style):
 p=Paragraph(text,sty);_,h=p.wrap(width,600);p.drawOn(c,x,595-top-h);return h
def arrow(points,label=''):
 c.setStrokeColor(colors.HexColor(MUTED));c.setLineWidth(1)
 pts=[(x,595-y) for x,y in points]
 p=c.beginPath();p.moveTo(*pts[0])
 for xy in pts[1:]:p.lineTo(*xy)
 c.drawPath(p)
 a=atan2(pts[-1][1]-pts[-2][1],pts[-1][0]-pts[-2][0]);x,y=pts[-1]
 for da in [-.5,.5]:c.line(x,y,x-6*cos(a+da),y-6*sin(a+da))
 if label:
  # Rótulos curtos nos espaços entre caixas, sem invadir texto das etapas.
  segments=list(zip(points,points[1:]))
  a,b=max(segments,key=lambda pair:abs(pair[0][1]-pair[1][1])) if len(points)>2 else segments[0]
  mx=(a[0]+b[0])/2;my=(a[1]+b[1])/2
  size=6.5
  tw=pdfmetrics.stringWidth(label,'Arial',size)
  if a[1]==b[1]:
   while tw>abs(a[0]-b[0])-4 and size>5:
    size-=.25;tw=pdfmetrics.stringWidth(label,'Arial',size)
  c.setFillColor(colors.white);c.rect(mx-tw/2-1,595-my-3,tw+2,8,fill=1,stroke=0)
  c.setFillColor(colors.HexColor(MUTED));c.setFont('Arial',size);c.drawCentredString(mx,595-my-1,label)

for number,title,subtitle,nodes,edges,note in pages:
 c.setFillColor(colors.HexColor(PINK));c.rect(0,586,842,9,fill=1,stroke=0)
 c.setFillColor(colors.HexColor(MUTED));c.setFont('Arial',9);c.drawString(42,562,f'INGRID / FLUXOGRAMA {number} / 06.10.2026')
 c.setFillColor(colors.HexColor(INK));c.setFont('Arial-Bold',22);c.drawString(42,533,title)
 para(subtitle,42,70,758,small)
 c.setFont('Arial',8);c.setFillColor(colors.HexColor(MUTED));c.drawString(42,492,'Planejamento para implementação posterior. Caixas rosas: decisões. Letras identificam etapas.')
 boxes={n[0]:(42+n[1]*260,112+n[2]*78,218,64) for n in nodes}
 for src,dst,label,*route in edges:
  x,y,w,h=boxes[src];xx,yy,ww,hh=boxes[dst]
  if route:
   fx,fy=route[0][0];lx,ly=route[0][-1]
   if fx<x:start=(x,y+h/2)
   elif fx>x+w:start=(x+w,y+h/2)
   else:start=(x+w/2,y+h if fy>y else y)
   if lx<xx:end=(xx,yy+hh/2)
   elif lx>xx+ww:end=(xx+ww,yy+hh/2)
   else:end=(xx+ww/2,yy+hh if ly>yy else yy)
   points=[start]+route[0]+[end]
  elif x==xx:
   points=[(x+w/2,y+h if yy>y else y),(xx+ww/2,yy if yy>y else yy+hh)]
  else:points=[(x+w if xx>x else x,y+h/2),(xx if xx>x else xx+ww,yy+hh/2)]
  arrow(points,label)
 for id,col,row,title_,body,decision in nodes:
  x,y,w,h=boxes[id]
  c.setFillColor(colors.HexColor('#F8EBF2' if decision else '#F4F6F9'))
  c.setStrokeColor(colors.HexColor(PINK if decision else '#DCE1E8'));c.roundRect(x,595-y-h,w,h,6,fill=1,stroke=1)
  height=para(f'<b>{id}. {escape(title_)}</b><br/>{escape(body)}',x+9,y+7,w-18)
  assert height<=h-12,(number,id,height)
 para(note,42,516,758,small)
 c.setStrokeColor(colors.HexColor('#DCE1E8'));c.line(42,32,800,32)
 c.setFont('Arial',8);c.setFillColor(colors.HexColor(MUTED));c.drawString(42,20,'Bruno Proença Silva | Revisão da equipe antes da construção | HGTX: contrato a confirmar');c.drawRightString(800,20,number)
 c.showPage()
 markdown+=['## '+number+' - '+title,'',subtitle,'','```mermaid','flowchart TD']
 for id,col,row,title_,body,decision in nodes:
  label=(title_+'<br/>'+body).replace('"',"'")
  markdown.append(f'  {id}{{"{label}"}}' if decision else f'  {id}["{label}"]')
 for src,dst,label,*_ in edges:markdown.append(f'  {src} -->|{label}| {dst}' if label else f'  {src} --> {dst}')
 markdown+=['```','',note,'']
c.save()
(ROOT/'FLUXOGRAMAS_INGRID.md').write_text('\n'.join(markdown),encoding='utf-8')
from pypdf import PdfReader
r=PdfReader(OUT)
assert len(r.pages)==4
print(f'PDF: {OUT}; 4 páginas; fonte editável: FLUXOGRAMAS_INGRID.md')
