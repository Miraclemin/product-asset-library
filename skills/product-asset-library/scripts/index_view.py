"""Render portable, read-only views of the registered WordPress usages."""
from collections import defaultdict
from html import escape
from pathlib import Path
from urllib.parse import quote
import os
import tempfile


def write_atomic(path, text):
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as f:
        f.write(text)
    os.replace(f.name, path)


def export(db, folder, root):
    groups = defaultdict(list)
    for row in db.execute('SELECT * FROM usage ORDER BY site,page,model,slot,asset'):
        groups[row['site'], row['page'], row['model']].append(row)
    md = ['# 网站用途索引', '', '来源、位置和原件按目标排列。', '']
    content = ['''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>网站用途索引</title><style>*{box-sizing:border-box}body{max-width:1030px;margin:auto;background:#f6f4eb;color:#203f34;padding:30px 4%;font:17px/1.55 system-ui}h1,h2{font-family:Georgia,"Songti SC",serif}input{width:100%;padding:10px;font:inherit}article{padding:12px 0;border-top:1px solid #c0caba;display:flex;gap:16px}article img{width:100px;height:70px;object-fit:contain}a{color:#176448}small{display:block}section{margin-top:32px}</style><h1>网站用途索引</h1><label>按页面、型号、图片名或使用位置查找<input id="search" type="search" placeholder="例如 poster.jpg"></label><p id="count" aria-live="polite"></p>''']
    for key, rows in groups.items():
        heading = ' · '.join(filter(None,key))
        content.append('<section><h2>'+escape(heading)+'</h2>')
        md.extend(['## '+heading,''])
        for row in rows:
            name=row['asset']
            url=quote(os.path.relpath(root/name,folder))
            proof=row['source']+' · '+row['pointer']+' · '+row['evidence']
            label=f"{row['slot']} · {name} · {row['status']}"
            thumb=''
            if Path(name).suffix.lower() in ('.jpg','.jpeg','.png','.gif','.webp') and row['status']!='原件缺失':
                thumb=f'<img src="{url}" alt="" loading="lazy">'
            content.append(f'<article>{thumb}<div><a href="{url}">{escape(label)}</a><small>{escape(proof)}</small></div></article>')
            md.append(f"- {row['slot']} · [{name}]({url}) · {row['status']}。{proof}")
        content.append('</section>');md.append('')
    content.append('''<script>function filter(){let q=document.querySelector('#search').value.toLowerCase().trim(),n=0;for(let s of document.querySelectorAll('section')){let m=0;for(let a of s.querySelectorAll('article')){let show=(s.querySelector('h2').textContent+' '+a.textContent).toLowerCase().includes(q);a.style.display=show?'':'none';if(show)m++}s.hidden=m===0;n+=m}document.querySelector('#count').textContent=n+' 条用途记录'}document.querySelector('#search').oninput=filter;filter()</script></html>''')
    write_atomic(folder/'用途索引.html',''.join(content))
    write_atomic(folder/'用途索引.md','\n'.join(md))
    return {'用途数':sum(map(len,groups.values())),'查询入口':str(folder/'用途索引.html')}
