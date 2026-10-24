"""Local file tooling only: media derivatives, provenance and delivery QA. No DB access."""
import argparse
import csv
import hashlib
import html
import json
import mimetypes
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, quote
from PIL import Image, ImageOps
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE if (_HERE / 'core').is_dir() else _HERE.parents[2]))
from core.content_delivery.delivery_values import CC, identity
from core.content_delivery.validation_media import cc_license_matches, official_cc_url

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def local_file(root,relative):
    p=PurePosixPath(relative)
    if p.is_absolute() or '..' in p.parts or not p.parts:raise ValueError('Unsafe package path')
    target=(root/relative).resolve()
    if not target.is_relative_to(root.resolve()):raise ValueError('Path leaves package root')
    return target

def create_web_copy(root,row):
    original=local_file(root,row['original_file'])
    actual=digest(original)
    if actual!=row['original_sha256']:raise ValueError('Original checksum mismatch: '+row['photo_id'])
    with Image.open(original) as image:
        image.verify()
    with Image.open(original) as image:
        width,height=image.size
        if image.format=='WEBP' and max(width,height)<=1600:
            return {**row,'web_file':row['original_file'],'web_sha256':actual,'web_width':width,'web_height':height,'derivation':'Mevcut WebP dosyası aynen korunur; yeniden kodlanmadı.'}
        target=root/'Teslimler/WebKopyalari'/(actual+'.webp')
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            converted=ImageOps.exif_transpose(image).convert('RGB')
            converted.thumbnail((1600,1600),Image.Resampling.LANCZOS)
            temporary=target.with_suffix('.part')
            converted.save(temporary,format='WEBP',quality=84,method=6)
            temporary.replace(target)
    with Image.open(target) as result:
        result.verify()
    with Image.open(target) as result:
        width,height=result.size
    return {**row,'web_file':str(target.relative_to(root)),'web_sha256':digest(target),'web_width':width,'web_height':height,'derivation':'Özgün teslim dosyası korundu. EXIF yönü uygulandı; kırpma yapılmadan en çok 1600 px, WebP kalite 84. Önceki kaynak değişiklik notları ayrıca korunur.'}

def valid_url(value):
    try:
        p=urlsplit(value)
        return p.scheme in ('http','https') and bool(p.hostname) and not p.username and not p.password
    except (ValueError, TypeError):
        return False

def license_error(photo):
    label=photo.get('license','');url=photo.get('license_url','')
    if CC.fullmatch(label):
        return None if cc_license_matches(label,url) else 'lisans etiketi ve resmî sürüm URL uyuşmuyor'
    if label in ('CC0','CC0 1.0'):
        return None if official_cc_url(url,r'/publicdomain/zero/1\.0(?:/deed\.[a-z]{2})?/?') else 'CC0 resmî sürüm bağlantısı gerekli'
    if label in ('Public domain','Kamu malı'):
        return None if valid_url(url) else 'kamu malı dayanak bağlantısı eksik'
    if label in ('FAL','Özgür Sanat Lisansı') and valid_url(url) and urlsplit(url).hostname in ('artlibre.org','www.artlibre.org'):
        return None
    return 'desteklenmeyen lisans; NC/ND veya belirsiz izin kabul edilmez'

def audit(root,photos,provenance,require_new_chain=False):
    errors=[];notes=[];seen=set();hashes=set();sources=set()
    index={r['photo_id']:r for r in provenance}
    if len(index)!=len(provenance):errors.append('Yinelenen kaynak photo_id')
    for photo in photos:
        pid=photo['photo_id']
        if pid in seen:errors.append(pid+': yinelenen fotoğraf kimliği')
        seen.add(pid)
        row=index.get(pid)
        if not row:
            errors.append(pid+': kaynak zinciri kaydı eksik');continue
        for field in ('author','source_url','license','license_url'):
            if not photo.get(field):errors.append(pid+': eksik '+field)
        for field in ('source_url','license_url'):
            if photo.get(field) and not valid_url(photo[field]):errors.append(pid+': geçersiz '+field)
        problem=license_error(photo)
        if problem:errors.append(pid+': '+problem)
        if valid_url(photo.get('source_url')):sources.add(identity(photo['source_url']))
        for field in ('author_url','attribution_url','original_file_url','downloaded_file_url'):
            if row.get(field) and not valid_url(row[field]):errors.append(pid+': geçersiz '+field)
        if not row.get('author_url'):notes.append(pid+': bağımsız fotoğrafçı profil URL kaydı yok')
        if photo.get('author','').strip().lower()=='own work':
            notes.append(pid+': kaynakta yalnız Own work var; gerçek atıf kimliği ayrıca doğrulanmalı')
            if require_new_chain:errors.append(pid+': Own work kişi adı değildir; yeni üretimde gerçek atıf kimliği gerekli')
        if not row.get('original_file_url'):notes.append(pid+': özgün kaynak dosyası URL kaydı yok')
        if not row.get('downloaded_file_url'):notes.append(pid+': tarihsel indirme URL kaydı yok; tahmin edilmedi')
        if require_new_chain:
            for field in ('original_file_url','downloaded_file_url','downloaded_on','attribution_url'):
                if not row.get(field):errors.append(pid+': yeni üretimde zorunlu '+field)
        for key,sha in [('original_file','original_sha256'),('web_file','web_sha256')]:
            if not row.get(key):
                errors.append(pid+': dosya alanı eksik '+key);continue
            try:
                file=local_file(root,row[key])
                if digest(file)!=row[sha]:errors.append(pid+': dosya SHA uyuşmazlığı '+key)
                with Image.open(file) as image:image.verify()
            except (OSError,ValueError,KeyError) as exc:errors.append(pid+': dosya okunamadı '+key+' ('+type(exc).__name__+')')
        if row.get('original_sha256'):hashes.add(row['original_sha256'])
        if photo.get('file')!=row.get('original_file') or photo.get('sha256')!=row.get('original_sha256'):
            errors.append(pid+': ana fotoğraf kaydı ile kaynak dosyası uyuşmuyor')
    for pid in set(index)-seen:errors.append(pid+': karşılıksız kaynak kaydı')
    return {'schema':'corteqs-media-provenance/7.0','photos':len(photos),'different_files':len(hashes),'different_source_pages':len(sources),'errors':errors,'open_provenance_points':notes,'structural_passed':not errors,'checks':{'file_bytes_and_sha':True,'image_decoding':True,'license_label_url':True,'url_format':True,'live_http_availability':False,'human_pixel_and_underlying_rights_review':False},'human_rights_approval_granted_by_tool':False,'existing_package_approval':'Bu dosya denetimi mevcut insan onayını değiştirmez.','database_written':False,'published':False}

def export_attributions(root,photos,provenance):
    index={r['photo_id']:r for r in provenance}
    fields=['photo_id','entry_id','role','file','caption','capture_date','author','author_url','attribution_url','license','license_url','source_url','original_file_url','downloaded_file_url','downloaded_on','source_checked_on','sha256','modifications','evidence_id','web_file','web_sha256','web_width','web_height','derivation','provenance_status','provenance_note']
    target=root/'Teslimler/fotograf-atiflari-v7.csv';target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        for photo in photos:writer.writerow({**photo,**index.get(photo['photo_id'],{})})
    cards=[]
    def link(url,label):
        if not valid_url(url):return html.escape(label)+' (geçerli bağlantı eksik)'
        return '<a href="'+html.escape(url,quote=True)+'">'+html.escape(label)+'</a>'
    for photo in photos:
        row=index.get(photo['photo_id'],{})
        credit=link(row.get('author_url') or photo['source_url'],photo['author'])
        credit+=' · '+link(photo['source_url'],'Kaynak')+' · '+link(photo['license_url'],photo['license'])
        path=row.get('web_file') or photo.get('file','');preview=''
        try:
            local_file(root,path)
            preview='<img loading="lazy" src="../'+quote(path,safe='/')+'" alt="'+html.escape(photo['caption'],quote=True)+'">'
        except ValueError:
            pass
        changes = '<p>Kaynak dosyanın değişiklik notu: ' + html.escape(photo.get('modifications','')) + '</p>'
        if row.get('derivation'):
            changes += '<p>Gösterilen web kopyası: ' + html.escape(row['derivation']) + '</p>'
        cards.append('<article>'+preview+'<div><h2>'+html.escape(photo['caption'])+'</h2><p>'+credit+'</p>'+changes+'<small>'+html.escape(photo['photo_id'])+'</small></div></article>')
    document='<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Fotoğraf atıfları · Corteqs</title><style>body{font:17px Arial;background:#f5f6f2;color:#17382f;max-width:1000px;margin:40px auto;padding:16px}article{background:white;margin:20px 0;border-radius:12px;overflow:hidden;display:grid;grid-template-columns:40% 1fr}article div{padding:24px}img{width:100%;height:100%;max-height:320px;object-fit:contain;background:#e8eee2}h2{font-size:20px}a{color:#175b46}small{color:#60746a}@media(max-width:600px){article{display:block}}</style><h1>Fotoğraf atıfları</h1><p>Yerel sunum örneği; site veya DB yayını yapılmadı. Görsellerin açılması için arşivi bütün klasörleriyle çıkarın.</p>'+''.join(cards)+'</html>'
    (root/'Teslimler/fotograf-atif-onizleme.html').write_text(document)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('root',type=Path);parser.add_argument('--photos',type=Path,required=True);parser.add_argument('--provenance',type=Path,required=True);parser.add_argument('--web-copies',action='store_true');parser.add_argument('--new-content',action='store_true');args=parser.parse_args()
    photos=json.loads(args.photos.read_text());rows=json.loads(args.provenance.read_text())
    if args.web_copies:rows=[create_web_copy(args.root,row) for row in rows]
    out=args.root/'Teslimler';out.mkdir(parents=True,exist_ok=True)
    (out/'photo-provenance-v7.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    report=audit(args.root,photos,rows,require_new_chain=args.new_content)
    (out/'photo-quality-v7.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    export_attributions(args.root,photos,rows)
    print(json.dumps({'photos':report['photos'],'errors':len(report['errors']),'open_points':len(report['open_provenance_points'])}))
    if report['errors']:raise SystemExit(1)

if __name__=='__main__':main()
