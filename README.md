# NPS CLIQUE E RETIRE

Painel para aumentar o NPS das lojas nos pedidos do Clique e Retire: cruza os pedidos com a exportação do survey de NPS, mostra quem já respondeu e quem ainda não, e permite chamar no WhatsApp, com mensagem personalizada, os clientes que ainda não responderam.

Feito no mesmo padrão do SUPER DESAFIO CSAT (site estático no GitHub Pages, dados gerados por script, dados nominais criptografados por senha).

## Abas
- **Visão geral:** pedidos, taxa de resposta, pendentes e NPS por loja e por semana da compra. Só contagens, sem nomes nem telefones.
- **Ativação:** lista de clientes que ainda não responderam, com botão de WhatsApp e mensagem editável. Nomes e telefones ficam **protegidos por senha** (uma por praça e uma geral).

## Como o cruzamento funciona
O número do pedido é a chave: `PEDIDO` da base de pedidos (sem o sufixo `BOT`) = `Código do pedido` do NPS. CPF não serve (no e-commerce o código do consumidor no NPS é outro ID). Quem tem resposta no NPS para o pedido já respondeu; o restante é pendente.

## Arquivos
| Arquivo | O que é |
|---|---|
| `index.html` | O painel (abre direto no navegador) |
| `dados.js` | Dados públicos gerados pelo script: contagens por loja e por dia |
| `ativacao_cripto.js` | Dados nominais **criptografados** (AES-GCM + PBKDF2) por praça |
| `atualizar_dados.py` | Lê as bases em `Base_Pedidos_Clique&Retire/` e `base_nps/` e gera os dois arquivos acima; configuração no topo |
| `cripto_ativacao.py` | Criptografia dos dados nominais |
| `planilha.js` | Planilha compartilhada de acionamentos (opcional; ver PUBLICAR.md) |

Ficam só no computador, fora do GitHub: `Base_Pedidos_Clique&Retire/`, `base_nps/`, `dCentros/` e `senhas_ativacao.json`.

## Limites conhecidos
- A mensagem cita a **quantidade** de itens; a base de pedidos não traz o nome dos produtos. Com uma base item a item dá para citar os produtos.
- A mensagem diz que a pesquisa foi enviada por e-mail (suposição pelo campo de entrega do convite do NPS); ajuste o texto se não for o caso.
- O clique no botão abre o WhatsApp Web com a mensagem pronta; quem opera ainda aperta enviar. O envio automático exige a API oficial do WhatsApp Business.

Para atualizar os dados e publicar, veja [PUBLICAR.md](PUBLICAR.md).
