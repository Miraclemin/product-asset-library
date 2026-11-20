"""Local persistent asset and usage index. See references/index.md for the JSON contract."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
from index_view import export
from inventory import IGNORED, IGNORED_FILES, MARKER

SCHEMA = """
CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY,sha TEXT,stamp TEXT,present INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS by_sha ON files(sha);
CREATE TABLE IF NOT EXISTS notes(path TEXT PRIMARY KEY REFERENCES files,sha TEXT NOT NULL,category TEXT,description TEXT);
CREATE TABLE IF NOT EXISTS uses(
 source TEXT NOT NULL, pointer TEXT NOT NULL, asset TEXT NOT NULL REFERENCES files,
 site TEXT NOT NULL,page TEXT NOT NULL,model TEXT NOT NULL,slot TEXT NOT NULL,
 evidence TEXT NOT NULL, asset_sha TEXT NOT NULL,source_sha TEXT NOT NULL,
 PRIMARY KEY(source,pointer,asset,site,page,model,slot));
CREATE INDEX IF NOT EXISTS by_page ON uses(page,site,slot);
CREATE INDEX IF NOT EXISTS by_model ON uses(model,site,slot);
CREATE INDEX IF NOT EXISTS by_asset ON uses(asset);
CREATE VIEW IF NOT EXISTS usage AS
 SELECT u.source,u.pointer,u.asset,u.site,u.page,u.model,u.slot,u.evidence,
 CASE WHEN f.present=0 THEN '原件缺失' WHEN u.asset_sha!=f.sha THEN '原件换版待复核'
 WHEN substr(u.source,1,6)!='@user/' AND (s.present IS NOT 1 OR s.sha!=u.source_sha)
 THEN '依据变化待复核' ELSE '已登记' END AS status
 FROM uses u JOIN files f ON f.path=u.asset LEFT JOIN files s ON s.path=u.source;
"""

def excluded(path):
    return path.name in IGNORED_FILES or path.name.startswith('._') or any(p in IGNORED for p in path.parts)

def safe_path(root, name):
    rel = Path(name)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise ValueError('需要库内相对文件路径：'+name)
    f = root / rel
    if excluded(rel) or f.resolve()!=f or any((p / MARKER).is_file() for p in [f.parent,*f.parents] if p.is_relative_to(root)):
        raise ValueError('路径不属于原始资料：'+name)
    return f

def output_dir(root):
    base = root / '素材库整理结果'
    for i in range(1,10000):
        d = base if i==1 else root/(base.name+'-'+str(i))
        if d.is_symlink():
            continue
        if d.is_dir() and (d/MARKER).is_file():
            return d
        if not d.exists():
            try:
                d.mkdir()
            except FileExistsError:
                continue
            (d/MARKER).touch()
            return d
    raise ValueError('找不到可用的结果目录')

def scan(db, root, paths):
    counts = dict(目录遍历=0,检查路径=0,读取内容=0,变化=[],需复核用途=[],错误=[])
    seen = set()
    def error(exc):
        counts['错误'].append(str(exc))
    def missing(name):
        if db.execute('UPDATE files SET present=0 WHERE path=? AND present=1',(name,)).rowcount:
            counts['变化'].append(name)
    def inspect(name):
        if name in seen:
            return
        seen.add(name)
        f = safe_path(root,name)
        counts['检查路径']+=1
        try:
            s = f.stat()
            if not stat.S_ISREG(s.st_mode):
                if paths:
                    raise ValueError('指定具体文件路径：'+name)
                missing(name)
                return
            def stamp(s):return f'{s.st_dev}/{s.st_ino}/{s.st_size}/{s.st_mtime_ns}/{s.st_ctime_ns}'
            row=db.execute('SELECT sha,stamp,present FROM files WHERE path=?',(name,)).fetchone()
            if row and row['present'] and row['stamp']==stamp(s):
                return
            h=hashlib.sha256()
            with f.open('rb') as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):
                    h.update(block)
            counts['读取内容']+=1
            if stamp(s)!=stamp(f.stat()):
                raise OSError(f'读取时文件发生变化：{name}')
            digest=h.hexdigest()
            if not row or not row['present'] or row['sha']!=digest:
                counts['变化'].append(name)
            db.execute('INSERT OR REPLACE INTO files VALUES(?,?,?,1)',(name,digest,stamp(s)))
        except FileNotFoundError:
            missing(name)
        except OSError as exc:
            error(exc)
    if paths:
        for p in paths:
            inspect(Path(p).as_posix())
    else:
        for directory,dirs,names in os.walk(root,onerror=error):
            base=Path(directory)
            if (base/MARKER).is_file():
                dirs.clear()
                continue
            counts['目录遍历']+=1
            dirs[:]=sorted(d for d in dirs if d not in IGNORED and not (base/d).is_symlink())
            for n in sorted(names):
                f=base/n
                if not excluded(f.relative_to(root)) and not f.is_symlink():
                    inspect(f.relative_to(root).as_posix())
        if not counts['错误']:
            for (name,) in db.execute('SELECT path FROM files WHERE present=1').fetchall():
                if name not in seen:
                    missing(name)
    for name in counts['变化']:
        stale=db.execute("SELECT * FROM usage WHERE (source=? OR asset=?) AND status!='已登记'",(name,name))
        counts['需复核用途'].extend(dict(r) for r in stale)
    return counts

def current(db,name,sha):
    row=db.execute('SELECT sha FROM files WHERE path=? AND present=1',(name,)).fetchone()
    if not row or not sha or sha!=row['sha']:
        raise ValueError('请按当前已盘点的版本登记：'+name)

def ingest(db, payload):
    for n in payload.get('notes',[]):
        current(db,n['path'],n['sha'])
        db.execute('INSERT OR REPLACE INTO notes VALUES(?,?,?,?)',(n['path'],n['sha'],n['category'],n['description']))
    for batch in payload.get('sources',[]):
        src=batch['source'];sha=batch.get('sha','')
        if not src.startswith('@user/'):
            current(db,src,sha)
        # A batch is a full set of assertions from ONE document or named user instruction.
        db.execute('CREATE TEMP TABLE IF NOT EXISTS seen_uses(id INTEGER PRIMARY KEY)')
        db.execute('DELETE FROM seen_uses')
        for u in batch['uses']:
            current(db,u['asset'],u['sha'])
            if not u['site'] or not u['slot'] or not (u.get('page') or u.get('model')) or not u['evidence']:
                raise ValueError('缺目标站、页面或型号、位置或依据')
            key=(src,u['pointer'],u['asset'],u['site'],u.get('page',''),u.get('model',''),u['slot'])
            db.execute("""INSERT INTO uses VALUES(?,?,?,?,?,?,?,?,?,?)
                          ON CONFLICT DO UPDATE SET evidence=excluded.evidence, asset_sha=excluded.asset_sha,
                          source_sha=excluded.source_sha WHERE evidence!=excluded.evidence
                          OR asset_sha!=excluded.asset_sha OR source_sha!=excluded.source_sha""",
                       (*key,u['evidence'],u['sha'],sha))
            db.execute("""INSERT OR IGNORE INTO seen_uses SELECT rowid FROM uses WHERE
                          (source,pointer,asset,site,page,model,slot)=(?,?,?,?,?,?,?)""",key)
        db.execute('DELETE FROM uses WHERE source=? AND rowid NOT IN (SELECT id FROM seen_uses)',(src,))
    return {'素材描述':len(payload.get('notes',[])),'依据组':len(payload.get('sources',[]))}

def main():
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path)
    cmds=p.add_subparsers(dest='cmd',required=True)
    s=cmds.add_parser('scan');s.add_argument('paths',nargs='*')
    put=cmds.add_parser('ingest');put.add_argument('payload',type=Path)
    q=cmds.add_parser('find')
    for key in ('site','page','model','asset','slot','source'):
        q.add_argument('--'+key)
    cmds.add_parser('files');cmds.add_parser('export')
    a=p.parse_args();root=a.folder.expanduser().resolve(strict=True)
    if not root.is_dir():p.error('请给素材文件夹地址')
    folder=output_dir(root)
    db=sqlite3.connect(folder/'素材索引.sqlite3',timeout=30);db.row_factory=sqlite3.Row
    try:
        db.execute('PRAGMA foreign_keys=ON')
        db.executescript(SCHEMA)
        with db:
            if a.cmd in ('scan','ingest'):db.execute('BEGIN IMMEDIATE')
            if a.cmd=='scan':result=scan(db,root,a.paths)
            elif a.cmd=='ingest':result=ingest(db,json.loads(a.payload.read_text()))
            elif a.cmd=='export':result=export(db,folder,root)
            elif a.cmd=='files':
                result=[dict(r) for r in db.execute('SELECT f.*,n.category,n.description,n.sha=f.sha AND f.present=1 AS note_current FROM files f LEFT JOIN notes n USING(path) ORDER BY f.path')]
            else:
                filters={k:getattr(a,k) for k in ('site','page','model','asset','slot','source') if getattr(a,k) is not None}
                sql='SELECT * FROM usage'+(' WHERE '+' AND '.join(k+'=?' for k in filters) if filters else '')+' ORDER BY site,page,model,slot,asset'
                result=[dict(r) for r in db.execute(sql,list(filters.values()))]
        print(json.dumps(result,ensure_ascii=False,indent=2))
    finally:
        db.close()
if __name__=='__main__':main()
