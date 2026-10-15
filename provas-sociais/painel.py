from pathlib import Path
import shutil,uuid,webbrowser
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from build import ROOT,read_data,write_data,build

def image_file(value):
 p=Path(value)
 if not p.is_file() or p.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):raise ValueError('Escolha uma imagem PNG, JPG ou WEBP existente.')
 with p.open('rb') as f:b=f.read(16)
 if not (b.startswith(b'\x89PNG\r\n\x1a\n') or b.startswith(b'\xff\xd8\xff') or (b[:4]==b'RIFF' and b[8:12]==b'WEBP')):raise ValueError('Imagem inválida: '+p.name)
 return p

def save_album(nome,idade,capa,fotos,current=None):
 if not nome.strip() or not idade.strip():raise ValueError('Preencha o nome e a idade.')
 if len(fotos)!=5:raise ValueError('Selecione exatamente cinco fotos.')
 sources=[image_file(v) for v in [capa,*fotos]];data=read_data()
 if current and not any(a['id']==current for a in data):raise ValueError('Álbum não encontrado. Abra-o novamente.')
 ident=current or uuid.uuid4().hex;folder=ROOT/'img'/uuid.uuid4().hex;folder.mkdir(parents=True)
 try:
  paths=[]
  for i,src in enumerate(sources):
   # Reutiliza os arquivos internos ao editar somente nome/idade.
   if ROOT in src.resolve().parents:dest=src.resolve()
   else:
    dest=folder/(('capa' if i==0 else str(i))+src.suffix.lower());shutil.copy2(src,dest)
   paths.append(dest.relative_to(ROOT).as_posix())
  item={'id':ident,'nome':nome.strip(),'idade':idade.strip(),'capa':paths[0],'fotos':paths[1:]}
  updated=[item if a['id']==ident else a for a in data]
  if not current:updated.append(item)
  write_data(updated)
  try:build()
  except Exception:write_data(data);build();raise
  return ident
 except Exception:
  shutil.rmtree(folder,ignore_errors=True);raise
 finally:
  if folder.exists() and not any(folder.iterdir()):folder.rmdir()

def delete_album(ident):
 old=read_data();write_data([a for a in old if a['id']!=ident])
 try:build()
 except Exception:write_data(old);build();raise

def main():
 root=tk.Tk();root.title('Maria Luiza Studio — Painel dos álbuns');root.geometry('1000x780');root.minsize(820,650)
 style=ttk.Style();style.theme_use('clam');style.configure('TButton',padding=7)
 main=ttk.Frame(root,padding=18);main.pack(fill='both',expand=True)
 ttk.Label(main,text='Álbuns dos bebês',font=('Segoe UI',21,'bold')).pack(anchor='w')
 ttk.Label(main,text='Cadastre no computador. Para publicar, faça Commit e Push no GitHub Desktop.').pack(anchor='w',pady=(5,15))
 body=ttk.Frame(main);body.pack(fill='both',expand=True)
 left=ttk.Frame(body);left.pack(side='left',fill='y',padx=(0,20))
 listing=tk.Listbox(left,width=25,exportselection=False,font=('Segoe UI',10));listing.pack(fill='both',expand=True)
 right=ttk.Frame(body);right.pack(side='left',fill='both',expand=True)
 canvas=tk.Canvas(right,highlightthickness=0);scroll=ttk.Scrollbar(right,orient='vertical',command=canvas.yview);scroll.pack(side='right',fill='y');canvas.pack(fill='both',expand=True);canvas.configure(yscrollcommand=scroll.set)
 form=ttk.Frame(canvas,padding=(0,0,12,0));window=canvas.create_window((0,0),window=form,anchor='nw');canvas.bind('<Configure>',lambda e:canvas.itemconfigure(window,width=e.width));form.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
 values=[tk.StringVar() for _ in range(8)];name,age,cover,*photos=values;selected={'id':None}
 for label,var in [('Nome do bebê',name),('Idade (exemplo: 2 meses ou 15 días)',age)]:
  ttk.Label(form,text=label).pack(anchor='w',pady=(8,4));ttk.Entry(form,textvariable=var,font=('Segoe UI',11)).pack(fill='x')
 def choose(var):
  path=filedialog.askopenfilename(title='Escolha a imagem',filetypes=[('Fotos','*.png *.jpg *.jpeg *.webp')])
  if path:var.set(path)
 for label,var in [('Capa do card',cover),*[(f'Foto {i+1} do álbum',v) for i,v in enumerate(photos)]]:
  ttk.Label(form,text=label).pack(anchor='w',pady=(12,4));row=ttk.Frame(form);row.pack(fill='x');ttk.Entry(row,textvariable=var).pack(side='left',fill='x',expand=True);ttk.Button(row,text='Escolher…',command=lambda v=var:choose(v)).pack(side='left',padx=(5,0))
 def select_five():
  paths=filedialog.askopenfilenames(title='Selecione as 5 fotos',filetypes=[('Fotos','*.png *.jpg *.jpeg *.webp')])
  if not paths:return
  if len(paths)!=5:messagebox.showerror('Quantidade incorreta','Selecione exatamente cinco fotos.');return
  for v,p in zip(photos,sorted(paths)):v.set(p)
  messagebox.showinfo('Fotos selecionadas','Ordenadas pelo nome do arquivo. Confira os campos Foto 1 a Foto 5 antes de salvar.')
 ttk.Button(form,text='Selecionar as 5 fotos de uma vez',command=select_five).pack(anchor='w',pady=14)
 def refresh():
  listing.delete(0,'end')
  for a in read_data():listing.insert('end',a['nome']+' · '+a['idade'])
 def new():
  selected['id']=None;listing.selection_clear(0,'end')
  for v in values:v.set('')
 def load(_=None):
  if not listing.curselection():return
  a=read_data()[listing.curselection()[0]];selected['id']=a['id'];name.set(a['nome']);age.set(a['idade']);cover.set(str(ROOT/a['capa']))
  for v,p in zip(photos,a['fotos']):v.set(str(ROOT/p))
 def save():
  try:
   selected['id']=save_album(name.get(),age.get(),cover.get(),[v.get() for v in photos],selected['id']);refresh();messagebox.showinfo('Salvo','Álbum salvo e páginas atualizadas.\nClique em Abrir site para conferir.\nPara publicar: Commit e Push no GitHub Desktop.')
  except Exception as e:messagebox.showerror('Não foi possível salvar',str(e))
 def delete():
  if not selected['id']:return
  if not messagebox.askyesno('Remover álbum','Remover este álbum do site? As imagens continuarão guardadas.'):return
  try:delete_album(selected['id']);refresh();new()
  except Exception as e:messagebox.showerror('Erro',str(e))
 def move(step):
  if not selected['id']:return
  old=read_data();data=list(old);i=next(i for i,a in enumerate(data) if a['id']==selected['id']);j=i+step
  if not 0<=j<len(data):return
  data[i],data[j]=data[j],data[i]
  try:write_data(data);build();refresh();listing.selection_set(j)
  except Exception as e:write_data(old);build();messagebox.showerror('Erro',str(e))
 listing.bind('<<ListboxSelect>>',load)
 for label,cmd in [('Novo álbum',new),('Remover selecionado',delete),('Subir na página inicial',lambda:move(-1)),('Descer na página inicial',lambda:move(1))]:ttk.Button(left,text=label,command=cmd).pack(fill='x',pady=(8,0))
 footer=ttk.Frame(main);footer.pack(fill='x',pady=(15,0));ttk.Button(footer,text='Salvar álbum e atualizar site',command=save).pack(side='right');ttk.Button(footer,text='Abrir site',command=lambda:webbrowser.open((ROOT/'index.html').as_uri())).pack(side='left')
 refresh();root.mainloop()
if __name__=='__main__':main()
