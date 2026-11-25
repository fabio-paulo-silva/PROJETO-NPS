# Publicar o NPS Clique e Retire no GitHub Pages

A cada `push` na `main`, o GitHub Actions (`.github/workflows/pages.yml`) publica `index.html`, `dados.js`, `ativacao_cripto.js` e `planilha.js`.

> O site é **público**: qualquer pessoa com o link vê as contagens por loja. Nomes e telefones só abrem com a senha da praça (ou a geral), que ficam em `senhas_ativacao.json`, no computador, fora do Git. Troque as senhas apagando o arquivo e rodando o script de novo (gera novas e recriptografa).

## Configuração única
1. Crie o repositório no GitHub e envie esta pasta (`git init`, `git add .`, `git commit`, `git remote add origin ...`, `git push -u origin main`). O `.gitignore` já deixa de fora as planilhas e as senhas.
2. No GitHub, abra o repositório > **Settings > Pages** > em **Source**, escolha **GitHub Actions**.
3. Envie as senhas de cada praça para quem vai operar (por canal seguro, não pelo repositório).

## Dia a dia: atualizar os dados
1. Salve a nova exportação do NPS em `base_nps/` e a base de pedidos em `Base_Pedidos_Clique&Retire/`.
2. Rode:
   ```
   python atualizar_dados.py
   ```
3. Envie:
   ```
   git add dados.js ativacao_cripto.js
   git commit -m "Dados até DD/MM"
   git push
   ```
4. Em 1 a 2 minutos o site atualiza.

Se as marcações de "acionado" precisam ser vistas por toda a equipe e você quer acompanhar os acessos, configure a planilha compartilhada abaixo; sem ela, cada pessoa vê só as marcações do próprio navegador e nada de acessos.

## Planilha compartilhada: acionamentos e acessos (Apps Script)
Usa a mesma planilha e o mesmo Apps Script do PULSAR/SUPER DESAFIO CSAT, com abas próprias do NPS:

| Aba | O que guarda |
|---|---|
| `acionamentos_nps` | cada marcação e desmarcação de contato: quando, praça, loja, número do pedido e quem fez (sem nome nem telefone do cliente) |
| `acessos_nps` | cada acesso ao painel: quem, quando, tela, praça e loja (no máximo 1 vez a cada 30 min por tela) |

1. Abra o Apps Script da planilha e cole o conteúdo de `apps_script_nps.gs` (fica só no computador). **Mantenha a chave que o script já usa**: troque o texto `COLE-AQUI-A-CHAVE-QUE-O-SCRIPT-JA-USA` pela mesma chave de hoje. Tudo que o PULSAR e o CSAT usam continua igual.
2. **Implantar > Gerenciar implantações > editar > Nova versão** (Executar como: Eu; Acesso: Qualquer pessoa). A URL continua a mesma.
3. No GitHub (repositório PROJETO-NPS) > **Settings > Secrets and variables > Actions**, crie `NPS_PLANILHA_URL` (a mesma URL do Apps Script, que termina em `/exec`) e `NPS_PLANILHA_CHAVE` (a mesma chave do script).
4. Rode de novo a publicação (Actions > Publicar no GitHub Pages > Run workflow, ou um novo `git push`).

Com a planilha ligada, o painel pede o nome de quem acessa (lista dos gestores do cadastro de lojas ou "Outro nome"), mostra o chip "Planilha conectada" na Ativação e a aba **Uso** passa a listar quem acessou e quem marcou ou desmarcou contatos. Acessos feitos no computador local (localhost) não são gravados.
