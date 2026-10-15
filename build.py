from pathlib import Path
import json, html, re
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'albuns.json'
def esc(value):return html.escape(str(value),quote=True)
def read_data():return json.loads(DATA.read_text(encoding='utf-8'))
def write_data(data):
 tmp=DATA.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(DATA)
def check_image(rel):
 p=(ROOT/rel).resolve()
 if ROOT not in p.parents or not p.is_file():raise ValueError('Imagem ausente ou inválida: '+rel)
def page(title,body,up=''):
 return f'''<!doctype html><html lang="es-MX"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · Maria Luiza Studio</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,500;1,400&amp;family=Jost:wght@300;400;500&amp;display=swap"><link rel="stylesheet" href="{up}css/style.css"><link rel="stylesheet" href="{up}css/albuns.css"><script src="{up}js/galeria.js" defer></script></head><body><header class="site-header wrap"><a class="brand" href="{up}index.html">Maria Luiza Studio</a></header><main class="wrap">{body}</main><footer>Maria Luiza Studio · Recuerdos hechos con cariño</footer><dialog aria-label="Foto ampliada"><button class="close" aria-label="Cerrar">×</button><button class="prev" aria-label="Foto anterior">‹</button><div class="stage"><p class="status" role="status">Cargando foto…</p><img class="original" alt=""><p class="count" aria-live="polite"></p></div><button class="next" aria-label="Foto siguiente">›</button></dialog></body></html>'''
def build():
 data=read_data();outputs={};cards='';ids=set()
 for a in data:
  ident=a['id']
  if not re.fullmatch(r'[a-f0-9]{32}',ident) or ident in ids:raise ValueError('Identificador inválido ou duplicado.')
  ids.add(ident)
  if len(a['fotos'])!=5:raise ValueError('Cada álbum deve ter exatamente cinco fotos.')
  for path in [a['capa'],*a['fotos']]:check_image(path)
  cards+=f'''<a class="theme-card has-img album-card" href="albuns/{ident}.html"><div class="album-cover"><img src="{esc(a['capa'])}" alt="{esc(a['nome'])}" loading="lazy" decoding="async"></div><div class="theme-body"><h2>{esc(a['nome'])}</h2><p>{esc(a['idade'])}</p><span class="view">Ver sesión · 5 fotos ↗</span></div></a>'''
  images=''
  for i,path in enumerate(a['fotos'],1):
   images+=f'''<a class="photo ph-{i}" href="../{esc(path)}" aria-label="Ampliar foto {i} de {esc(a['nome'])}"><img src="../{esc(path)}" alt="{esc(a['nome'])}, foto {i}" loading="{'eager' if i<=2 else 'lazy'}" decoding="async"></a>'''
  outputs[f'albuns/{ident}.html']=page(a['nome'],f'''<a class="back-link" href="../index.html">← Volver a las sesiones</a><section class="page-title"><h1>{esc(a['nome'])}</h1><p>{esc(a['idade'])}</p></section><p class="gallery-hint">Toca una foto para verla en grande</p><div class="photo-grid">{images}</div><a class="back-link" href="../index.html">Ver más sesiones</a>''','../')
 empty='<div class="empty"><h2>Pronto, nuevas historias</h2><p>Estamos preparando nuestras sesiones para compartirlas contigo.</p></div>' if not data else cards
 outputs['index.html']=page('Nuestras sesiones',f'''<section class="hero"><div class="eyebrow">NUESTROS PEQUEÑOS PROTAGONISTAS</div><h1>Recuerdos que se quedan contigo</h1><p>Descubre cada sesión y sus cinco fotografías.</p></section><div class="grid-3">{empty}</div>''')
 for rel,content in outputs.items():
  f=ROOT/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(content,encoding='utf-8')
 folder=ROOT/'albuns';folder.mkdir(exist_ok=True)
 for f in folder.glob('*.html'):
  if re.fullmatch(r'[a-f0-9]{32}',f.stem) and f.stem not in ids:f.unlink()
 return len(data)
if __name__=='__main__':print('Site atualizado. Álbuns:',build())
