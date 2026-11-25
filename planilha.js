// NPS Clique e Retire - planilha compartilhada dos acionamentos (opcional).
// Segurança: a URL do Apps Script e a chave NÃO ficam no repositório. Os marcadores abaixo são trocados na
// publicação (GitHub Actions) pelos segredos NPS_PLANILHA_URL e NPS_PLANILHA_CHAVE.
// Sem os segredos (ex.: painel aberto no computador), os contatos ficam salvos só no navegador.
window.NPS_PLANILHA = (function () {
  var url = '__NPS_PLANILHA_URL__', chave = '__NPS_PLANILHA_CHAVE__';
  return url.indexOf('__') === 0 ? null : { url: url, chave: chave };
})();
