#!/usr/bin/env python3
"""Gera as páginas estáticas dos 3 lofts a partir de modelos/loft-modelo.html e dos dados de site/assets/disp.js.
Também escreve site/sitemap.xml e site/robots.txt.

Também gera as páginas internas a partir de modelos/paginas/*.html (Os lofts, Matoterapia, Como chegar, Perguntas
frequentes) e mantém o MENU do cabeçalho e os links do RODAPÉ iguais em todas as páginas (marcadores
<!--MENU--> e <!--RODAPE--> em index.html, reservar.html, modelo do loft e páginas geradas).

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


# ---------------------------------------------------------------- menu, rodapé e páginas internas
MENU_LINKS = [("index.html", "Início"), ("lofts.html", "Nossos Lofts-Spa"), ("matoterapia.html", "Matoterapia"),
              ("como-chegar.html", "Gonçalves - MG"), ("perguntas-frequentes.html", "Perguntas frequentes")]


def menu_html():
    links = "".join('<a href="%s">%s</a>' % (h, n) for h, n in MENU_LINKS)
    return ('<details class="menu"><summary aria-label="Menu"><span class="bars" aria-hidden="true"></span><span class="lbl">Menu</span></summary>'
            '<div class="menu-panel" role="navigation" aria-label="Menu principal">%s<a class="cta" href="index.html#calendario">Reservar</a></div></details>' % links)


def links_html():
    # links do cabeçalho no desktop (sem "Início": o logo já leva à home)
    return '<div class="hlinks" role="navigation" aria-label="Páginas">%s</div>' % "".join('<a href="%s">%s</a>' % (h, n) for h, n in MENU_LINKS[1:])


def rodape_nav():
    return '<nav class="rodape-nav" aria-label="Rodapé">%s</nav>' % "".join('<a href="%s">%s</a>' % (h, n) for h, n in MENU_LINKS + [("index.html#calendario", "Reservar")])


def rodape_html():
    return ('<footer><span class="lg">Kaá Ipira Vila Spa · Gonçalves, Minas Gerais</span>%s'
            '<small class="rodape-leg"><span>Estrada do Sertão do Cantagalo, KM 7 · Gonçalves – MG</span>'
            '<span>E-mail: <a href="mailto:reservas@kaaipira.com.br">reservas@kaaipira.com.br</a></span></small></footer>' % rodape_nav())


def trocar_marcador(texto, nome, conteudo):
    pad = re.compile(r"<!--%s-->.*?<!--/%s-->" % (nome, nome), re.S)
    if not pad.search(texto):
        return texto
    return pad.sub(lambda m: "<!--%s-->%s<!--/%s-->" % (nome, conteudo, nome), texto)


def aplicar_marcadores(texto):
    texto = trocar_marcador(texto, "MENU", menu_html())
    texto = trocar_marcador(texto, "LINKS", links_html())
    texto = trocar_marcador(texto, "RODAPE", rodape_html())
    texto = trocar_marcador(texto, "RODAPENAV", rodape_nav())
    return texto


FOTO_CARD = {"1": ("quarto-taipa.jpg", "Cama de casal diante da parede de taipa de pilão, com luminárias de franjas e abajures acesos"),
             "2": ("det-cadeiras.jpg", "Poltronas de madeira com almofadas e um vaso de flores secas"),
             "3": ("fachada-capuchinha.jpg", "Fachada de ripas de madeira e painel de taipa sobre um canteiro de capuchinhas")}

BASE_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
{SEO}
<link rel="icon" href="assets/logo-verde.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Courgette&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400;1,600&family=Sacramento&display=swap">
<link rel="stylesheet" href="assets/paginas.css?v=12">
<link rel="stylesheet" href="assets/menu.css?v=2">
</head>
<body>
<header class="nav"><div class="wrap">
  <div class="nav-left"><!--MENU--><!--/MENU--><a class="logo" href="index.html" aria-label="Kaá Ipira Vila Spa, início"><img src="assets/logo-verde.png" alt="Kaá Ipira"><span class="vila-h">Vila Spa</span></a></div>
  <!--LINKS--><!--/LINKS-->
  <a class="btn" href="index.html#calendario">Reservar</a>
</div></header>
<main>
{CONTEUDO}
</main>
<!--RODAPE--><!--/RODAPE-->
<script src="assets/menu.js?v=2" defer></script>
</body>
</html>
"""


def sem_tags(x):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()


def gerar_paginas_internas(lofts, amen):
    pasta = os.path.join(RAIZ, "modelos", "paginas")
    gerados = []
    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith(".html"):
            continue
        src = open(os.path.join(pasta, nome), encoding="utf-8").read()
        mm = re.match(r"\s*<!--META\s*(\{.*?\})\s*-->", src, re.S)
        if not mm:
            sys.exit("Falta o bloco META em modelos/paginas/" + nome)
        meta = json.loads(mm.group(1))
        corpo = src[mm.end():]
        # blocos dinâmicos
        cards = ""
        for k, L in lofts.items():
            f, alt = FOTO_CARD[k]
            curto = L["texto"].split(". ")[0].rstrip(".") + "."
            cards += ('<article class="card"><span class="tag">%s</span><figure class="ph%s"><img src="assets/%s" alt="%s" loading="lazy"></figure>'
                      '<div class="in"><h3>%s</h3><p>%s</p><a class="btn" href="%s.html">Conheça este loft</a></div></article>\n'
                      % (a(L["nome"]), " b" if k == "2" else "", f, a(alt), a(L["nome"].replace("Loft-Spa ", "")), a(curto), L["slug"]))
        corpo = corpo.replace("{{CARDS_LOFTS}}", cards)
        metade = (len(amen) + 1) // 2
        corpo = corpo.replace("{{AMENIDADES}}", "".join('<ul class="tick">%s</ul>' % "".join("<li>%s</li>" % a(x) for x in col) for col in (amen[:metade], amen[metade:])))
        faq = meta.get("faq", [])
        corpo = corpo.replace("{{FAQ}}", "\n".join('<details><summary>%s</summary><div class="ans">%s</div></details>' % (a(q), r) for q, r in faq))
        # SEO
        url = BASE + meta["path"]
        ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": meta["title"], "description": meta["description"], "url": url,
               "isPartOf": {"@type": "WebSite", "name": "Kaá Ipira Vila Spa", "url": BASE}}]
        if faq:
            ld.append({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": sem_tags(r)}} for q, r in faq]})
        seo = "\n".join([
            '<meta name="description" content="%s">' % a(meta["description"]),
            '<link rel="canonical" href="%s">' % a(url),
            '<meta property="og:type" content="website">', '<meta property="og:locale" content="pt_BR">',
            '<meta property="og:site_name" content="Kaá Ipira Vila Spa">',
            '<meta property="og:title" content="%s">' % a(meta["title"]),
            '<meta property="og:description" content="%s">' % a(meta["description"]),
            '<meta property="og:url" content="%s">' % a(url),
            '<meta property="og:image" content="%sassets/%s">' % (BASE, meta.get("og", "og-home.jpg")),
            '<meta name="twitter:card" content="summary_large_image">',
        ] + ['<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in ld])
        pagina = BASE_HTML.replace("{TITLE}", a(meta["title"])).replace("{SEO}", seo).replace("{CONTEUDO}", corpo)
        pagina = aplicar_marcadores(pagina)
        open(os.path.join(SITE, meta["path"]), "w", encoding="utf-8").write(pagina)
        gerados.append(meta["path"])
    return gerados


def gerar():
    lofts = ler_lofts()
    modelo = open(MODELO, encoding="utf-8").read()
    amen = amenidades(modelo)
    modelo = aplicar_marcadores(modelo)
    for nome in ("index.html", "reservar.html"):
        caminho = os.path.join(SITE, nome)
        conteudo = open(caminho, encoding="utf-8").read()
        novo_c = aplicar_marcadores(conteudo)
        if novo_c != conteudo:
            open(caminho, "w", encoding="utf-8").write(novo_c)
    internas = gerar_paginas_internas(lofts, amen)
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
    urls = [(BASE, "1.0")] + [(BASE + p, "0.9") for p in ("lofts.html", "matoterapia.html")] + [(BASE + L["slug"] + ".html", "0.8") for L in lofts.values()] + [(BASE + p, "0.6") for p in ("como-chegar.html", "perguntas-frequentes.html")]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, p in urls:
        sm.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (u, HOJE, p))
    sm.append("</urlset>")
    open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")
    open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\nDisallow: /reservar.html\n\nSitemap: %ssitemap.xml\n" % BASE)
    print("Geradas:", ", ".join([L["slug"] + ".html" for L in lofts.values()] + internas), "+ sitemap.xml, robots.txt")


if __name__ == "__main__":
    gerar()
