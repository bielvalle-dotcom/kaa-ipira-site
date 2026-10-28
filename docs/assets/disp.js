/* Disponibilidade dos lofts.
   ATENÇÃO: as reservas abaixo são EXEMPLOS para demonstrar o funcionamento. Troque pelas reservas reais
   (ou ligue a um calendário/Google Agenda/sistema de reservas) antes de publicar.
   Cada período vai da data de chegada até a data de partida; no dia da partida o loft já fica livre. */
window.KAA = {
  WHATSAPP: "", // só dígitos com DDI e DDD, ex.: "5535999999999"
  LOFTS: {
    "1": { nome: "Loft-Spa Kaápim", titulo: "Parede de terra", max: 2,
      texto: "A cama fica diante da taipa de pilão, com luz baixa, franjas artesanais e toalhas dobradas em rolo. Um loft moderno de paredes de pedra e de terra, a mesma terra onde o mato nasce, cresce e mora.",
      fotos: [["quarto-taipa.jpg","Cama de casal diante da parede de taipa de pilão"],["det-taipa.jpg","Detalhe da taipa de pilão"],["banheira-mata.jpg","Banheira no deck, diante da mata"],["det-mesa-pedra.jpg","Mesa de madeira diante da parede de pedra"]] },
    "2": { nome: "Loft-Spa Kaámomila", titulo: "Verde sálvia", max: 2,
      texto: "Um painel verde na cabeceira, almofadas em tons de mata e lâmpadas de filamento sob o forro de madeira. Um loft para desacelerar, com tudo o que o self-spa oferece por perto.",
      fotos: [["det-cama-verde.jpg","Cama com almofadas verde-sálvia"],["loft-noite.jpg","Banheira iluminada à noite"],["det-cadeiras.jpg","Poltronas de madeira com flores secas"],["ofuro-madeira.jpg","Ofurô de madeira com vista para a mata"]] },
    "3": { nome: "Loft-Spa Kaápuchinha", titulo: "Tudo à mão", max: 4,
      texto: "Cama, bancada e poltronas num só ambiente, com tapete de crochê e janelas para o verde. Pensado para ficar à vontade, a dois ou em grupo pequeno.",
      fotos: [["det-loft-sala.jpg","Loft com cama, bancada e poltronas"],["cadeira-pedra.jpg","Poltrona e ofurô de escalda-pés diante da pedra"],["sauna-vidro.jpg","Sauna de vidro entre pedra e deck"],["det-balanco.jpg","Balanço verde na varanda envidraçada"]] }
  },
  BOOKED: {
    "1": [["2026-10-30","2026-11-02"],["2026-11-13","2026-11-16"],["2026-12-04","2026-12-08"]],
    "2": [["2026-10-23","2026-10-26"],["2026-11-06","2026-11-09"],["2026-11-27","2026-11-30"]],
    "3": [["2026-10-28","2026-10-31"],["2026-11-20","2026-11-23"],["2026-12-18","2026-12-27"]]
  }
};
(function (K) {
  var DAY = 86400000;
  function t(d) { return Date.parse(d + "T00:00:00Z"); }
  function iso(ms) { return new Date(ms).toISOString().slice(0, 10); }
  K.fmt = function (d) { var p = d.split("-"); return p[2] + "/" + p[1]; };
  // { ok, noites, conflito:[ini,fim] | null, proxima:[ini,fim] | null, erro }
  K.check = function (loft, ini, fim) {
    if (!ini || !fim || t(fim) <= t(ini)) return { erro: "Escolha uma partida posterior à chegada." };
    var a = t(ini), b = t(fim), noites = Math.round((b - a) / DAY), list = K.BOOKED[loft] || [], hit = null;
    for (var i = 0; i < list.length; i++) { if (a < t(list[i][1]) && b > t(list[i][0])) { hit = list[i]; break; } }
    var out = { ok: !hit, noites: noites, conflito: hit, proxima: null };
    if (hit) { // próxima janela livre com o mesmo número de noites
      var s = a;
      for (var g = 0; g < 400; g++) {
        var e = s + noites * DAY, bad = false;
        for (var j = 0; j < list.length; j++) { if (s < t(list[j][1]) && e > t(list[j][0])) { s = t(list[j][1]); bad = true; break; } }
        if (!bad) { out.proxima = [iso(s), iso(e)]; break; }
      }
    }
    return out;
  };
})(window.KAA);
