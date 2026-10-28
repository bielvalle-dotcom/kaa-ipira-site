#!/bin/sh
# Copia o site para docs/ (pasta que o GitHub Pages publica), salva e envia.
cd "$(dirname "$0")" || exit 1
rm -rf docs && cp -R site docs && touch docs/.nojekyll
git add site docs
git commit -m "${1:-Atualiza o site publicado}"
git push
