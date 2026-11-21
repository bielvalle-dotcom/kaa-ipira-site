#!/usr/bin/env python3
"""Gera as páginas estáticas dos 3 lofts a partir de modelos/loft-modelo.html e dos dados de site/assets/disp.js.
Também escreve site/sitemap.xml e site/robots.txt.

Uso (o publicar.sh já roda isto): python3 gerar_paginas.py
IMPORTANTE: para mudar o visual/estrutura das páginas dos lofts, edite modelos/loft-modelo.html (NÃO os arquivos
loft-spa-*.html de site/, que são sobrescritos). Textos e fotos dos lofts ficam em site/assets/disp.js.
Quando o domínio próprio estiver no ar, troque BASE abaixo (e o mesmo endereço em site/index.html).
"""
import json, os, re, sys, datetime, html

BASE = "https://bielvalle-dotcom.github.io/kaa-ipira-site/"   # <- trocar pelo domínio próprio quando existir
RAIZ = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(RAIZ, "site")
MODELO = os.path.join(RAIZ, "modelos", "loft-modelo.html")
HOJE = datetime.date.today().isoformat()

# Textos de SEO de cada loft (título ~60 caracteres, descrição ~155)
SEO = {
    "1": ("Loft-Spa Kaápim · taipa de pilão em Gonçalves, MG | Kaá Ipira",
          "Loft-spa de paredes de pedra e de terra (taipa de pilão) para 2 hóspedes, com banheira Air Massage e ofurô privativo, na Serra da Mantiqueira, em Gonçalves (MG)."),
    "2": ("Loft-Spa Kaámomila · verde sálvia em Gonçalves, MG | Kaá Ipira",
          "Loft-spa para 2 hóspedes com painel verde na cabeceira e forro de madeira, banheira Air Massage e ofurô privativo, na Serra da Mantiqueira, em Gonçalves (MG)."),
    "3": ("Loft-Spa Kaápuchinha · para até 4 hóspedes em Gonçalves, MG | Kaá Ipira",
          "Loft-spa para até 4 hóspedes, com cama, bancada e poltronas num só ambiente, banheira Air Massage e ofurô privativo, na Serra da Mantiqueira, em Gonçalves (MG)."),
}
OG = {"1": "og-kaapim.jpg", "2": "og-kaamomila.jpg", "3": "og-kaapuchinha.jpg"}


def ler_lofts():
    js = open(os.path.join(SITE, "assets", "disp.js"), encoding="utf-8").read()
    bloco = js[js.index("LOFTS: {"): js.index("BOOKED:")]
    lofts = {}
    for m in re.finditer(r'"(\d)": \{ nome: "([^"]+)", slug: "([^"]+)", titulo: "([^"]*)", max: (\d+),\s*texto: "([^"]+)",\s*fotos: \[(.*?)\] \}', bloco, re.S):
        k, nome, slug, titulo, mx, texto, fotos = m.groups()
        fs = re.findall(r'\["([^"]+)","([^"]+)"\]', fotos)
        lofts[k] = dict(nome=nome, slug=slug, titulo=titulo, max=int(mx), texto=texto, fotos=fs)
    if len(lofts) != 3:
        sys.exit("Não consegui ler os 3 lofts de disp.js (achei %d)." % len(lofts))
    return lofts


def amenidades(modelo):
    ul = modelo[modelo.index('<div class="facts">'): modelo.index("</section>", modelo.index('<div class="facts">'))]
    return [html.unescape(x.strip()) for x in re.findall(r"</svg>([^<]+)</li>", ul)]


def a(s):
    return html.escape(s, quote=True)


def head_seo(k, L, amen):
    titulo, desc = SEO[k]
    url = BASE + L["slug"] + ".html"
    img = BASE + "assets/" + OG[k]
    ld = {
        "@context": "https://schema.org",
        "@type": "HotelRoom",
        "name": L["nome"],
        "description": desc,
        "url": url,
        "image": [BASE + "assets/" + f[0] for f in L["fotos"]],
        "occupancy": {"@type": "QuantitativeValue", "maxValue": L["max"]},
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in amen],
        "containedInPlace": {"@type": "LodgingBusiness", "name": "Kaá Ipira Vila Spa", "url": BASE},
    }
    return "\n".join([
        '<meta name="description" content="%s">' % a(desc),
        '<link rel="canonical" href="%s">' % a(url),
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="pt_BR">',
        '<meta property="og:site_name" content="Kaá Ipira Vila Spa">',
        '<meta property="og:title" content="%s">' % a(titulo),
        '<meta property="og:description" content="%s">' % a(desc),
        '<meta property="og:url" content="%s">' % a(url),
        '<meta property="og:image" content="%s">' % a(img),
        '<meta name="twitter:card" content="summary_large_image">',
        '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False),
    ])


def gerar():
    lofts = ler_lofts()
    modelo = open(MODELO, encoding="utf-8").read()
    amen = amenidades(modelo)
    for k, L in lofts.items():
        t = modelo
        titulo = SEO[k][0]
        t = t.replace("<title>Loft-spa · Kaá Ipira Vila Spa</title>", "<title>%s</title>\n%s" % (a(titulo), head_seo(k, L, amen)))
        t = t.replace("<body{{BODYATTR}}>", '<body data-loft="%s">' % k)
        t = t.replace('<span class="eyebrow" id="l-nome"></span>', '<span class="eyebrow" id="l-nome">%s</span>' % a(L["nome"]))
        t = t.replace('<h1 id="l-titulo"></h1>', '<h1 id="l-titulo">%s</h1>' % a(L["nome"].replace("Loft-Spa ", "")))
        t = t.replace('<p class="lede" id="l-texto"></p>', '<p class="lede" id="l-texto">%s</p>' % a(L["texto"]))
        gal = "".join('<figure><img src="assets/%s" alt="%s" loading="lazy"></figure>' % (f, a(alt)) for f, alt in L["fotos"])
        t = t.replace('<div class="gal" id="l-gal"></div>', '<div class="gal" id="l-gal">%s</div>' % gal)
        t = t.replace('<br class="mbr"> no Loft-Spa</h2>', '<br class="mbr"> no %s</h2>' % a(L["nome"]))
        outros = "".join('<a href="%s.html"%s>%s</a>' % (o["slug"], ' aria-current="page"' if ok == k else "", a(o["nome"])) for ok, o in lofts.items())
        t = t.replace('<nav class="others" id="others" aria-label="Outros lofts"></nav>', '<nav class="others" id="others" aria-label="Outros lofts">%s</nav>' % outros)
        for marca in ('{{BODYATTR}}', 'id="l-titulo"></h1>'):
            if marca in t:
                sys.exit("Marcador não substituído no modelo: " + marca)
        open(os.path.join(SITE, L["slug"] + ".html"), "w", encoding="utf-8").write(t)

    # sitemap e robots
    urls = [(BASE, "1.0")] + [(BASE + L["slug"] + ".html", "0.8") for L in lofts.values()]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, p in urls:
        sm.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (u, HOJE, p))
    sm.append("</urlset>")
    open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")
    open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\nDisallow: /reservar.html\n\nSitemap: %ssitemap.xml\n" % BASE)
    print("Geradas:", ", ".join(L["slug"] + ".html" for L in lofts.values()), "+ sitemap.xml, robots.txt")


if __name__ == "__main__":
    gerar()
