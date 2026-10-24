import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const root=path.dirname(new URL(import.meta.url).pathname);
const fields=JSON.parse(await fs.readFile(path.join(root,'provenance-fields.json'),'utf8'));
const [input,output,recordsPath,dataPath]=process.argv.slice(2);
const rows=recordsPath?JSON.parse(await fs.readFile(recordsPath,'utf8')):[];
const col=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(input));
if(dataPath){
 const data=JSON.parse(await fs.readFile(dataPath,'utf8'));
 const schema=JSON.parse(await fs.readFile(path.join(root,'base-schema.json'),'utf8'));
 const typed=(v,f)=>{
  if(v===null||v===undefined||v==='')return null;
  if(typeof v==='object'&&v.corteqs_long_value)return JSON.stringify(v);
  if(f.type==='date')return new Date(v+'T00:00:00Z');
  if(f.type==='id_list'&&Array.isArray(v))return v.join(';');
  if(f.type==='text_list'&&Array.isArray(v))return v.join('\n');
  if(f.type==='object'&&typeof v==='object')return JSON.stringify(v);
  if(f.type==='boolean')return v===true||v==='Evet'?'Evet':'Hayır';
  if(f.choice_map)return Object.keys(f.choice_map).find(k=>f.choice_map[k]===v)||v;
  return v;
 };
 for(const [key,config] of Object.entries(schema.tables)){
  const records=data[key]||[],sheet=wb.worksheets.getItem(config.sheet);
  if(!records.length)continue;
  const values=records.map(r=>config.fields.map(f=>f.readonly?null:typed(r[f.key],f)));
  if(values.some(r=>r.some(v=>typeof v==='string'&&v.length>32767)))throw Error('Excel hücre sınırı: kayıp önlendi');
  sheet.getRange(`A8:${col(config.fields.length-1)}${7+records.length}`).values=values;
  if(key==='topics'){
   sheet.getRange('H8').formulas=[['=IF(A8="",0,IF(COUNTIFS(\'Yanıtlar\'!$N$8:$N$607,A8)>0,1,0))']];
   sheet.getRange(`H8:H${7+config.capacity}`).fillDown();
  }
 }
 if(data._long_values?.length){
  const archive=wb.worksheets.add('UzunAlanlar');
  archive.getRange('A1:E1').values=[['archive_id','table','row_id','field','value_sha256']];
  archive.getRange('F1:G1').values=[['chunk_order','chunk']];
  const chunks=data._long_values.flatMap(r=>r.chunks.map((chunk,i)=>[r.id,r.table,r.row_id,r.field,r.sha256,i,chunk]));
  archive.getRange(`A2:G${chunks.length+1}`).values=chunks;
  archive.getRange('A:G').format.columnWidth=30;archive.getRange('G:G').format.columnWidth=100;
  archive.freezePanes.freezeRows(1);
 }
}
const source=wb.worksheets.add('FotoğrafKaynakları');
const last=col(fields.length-1),end=Math.max(607,rows.length+7);
source.showGridLines=false;
source.getRange(`A1:${last}${end}`).format={font:{name:'Arial',size:11,color:'#17382F'},rowHeight:54,verticalAlignment:'top',wrapText:true};
source.getRange('A2').values=[['Corteqs · Fotoğrafın kaynak zinciri · v7']];
source.getRange('A2').format.font={name:'Arial',size:17,bold:true,color:'#173B31'};
source.mergeCells('A3:F3');source.getRange('A3').values=[['Her fotoğraf kimliği için bir kayıt. İsim, lisans ve kaynak sayfası Fotoğraflar sayfasında kalır. Bilinmeyen bağlantı veya tarih uydurulmaz.']];
source.getRange('A3:F3').format.rowHeight=44;
source.getRange(`A5:${last}5`).values=[fields.map(([key])=>key==='photo_id'?'Zorunlu bağlantı':'Kanıt varsa doldurun')];
source.getRange(`A6:${last}6`).values=[fields.map(f=>f[1])];
source.getRange(`A6:${last}6`).format={fill:'#E7EDDF',font:{name:'Arial',size:11,bold:true,color:'#17382F'},rowHeight:50};
source.getRange(`A7:${last}7`).values=[fields.map(f=>f[0])];
source.getRange(`A7:${last}7`).format={fill:'#173B31',font:{name:'Arial',size:10,color:'#FFFFFF'},rowHeight:32};
source.getRange(`A8:${last}${end}`).format.fill='#FFF4D7';
fields.forEach((f,i)=>source.getRange(`${col(i)}1:${col(i)}${end}`).format.columnWidth=f[2]);
if(rows.length)source.getRange(`A8:${last}${rows.length+7}`).values=rows.map(r=>fields.map(([key])=>r[key]??null));
source.tables.add(`A7:${last}${end}`,true,'CT_photo_provenance').showFilterButton=true;
source.freezePanes.freezeRows(7);source.freezePanes.freezeColumns(1);source.tabColor='#F66C4E';
const overview=wb.worksheets.getItem('Özet');
overview.getRange('A10:A11').values=[['Farklı mekân fotoğrafı'],['Farklı kapak fotoğrafı']];
overview.getRange('A14').values=[['v7 · Kaynak zinciri: FotoğrafKaynakları. Miktar, onay değildir.']];
overview.getRange('A14:F14').format={rowHeight:68,wrapText:true,fill:'#E7EDDF'};
overview.getRange('A22').values=[['5. Paketin tamamı insan editör tarafından incelenir; tek paket kararı yönetim ekranında verilir. Excel’de satır satır onay işaretlemek gerekmez.']];
overview.getRange('A22:F22').format={rowHeight:54,wrapText:true};
overview.getRange('A28').values=[['Fotoğraf miktarı dosya SHA-256 özeti ve rolüyle ölçülür; aynı kareye ait türevler ayrıca ayıklanır. Sayımda kullanılabilir eski alanı korunur, insan onayı yerine geçmez. Paket kararı yönetim ekranındadır.']];
const photos=wb.worksheets.getItem('Fotoğraflar');
const maxPhotoRow=Math.max(607,photos.getUsedRange().values.length);
photos.getRange('S8:T8').formulas=[[
 '=IF(OR(A8="",F8="",C8<>"Mekân"),0,IF(COUNTIFS($F$8:F8,F8,$C$8:C8,"Mekân")=1,1,0))',
 '=IF(OR(A8="",F8="",C8<>"Kapak"),0,IF(COUNTIFS($F$8:F8,F8,$C$8:C8,"Kapak")=1,1,0))']];
photos.getRange(`S8:T${maxPhotoRow}`).fillDown();
overview.getRange('B10:B11').formulas=[[`=SUM('Fotoğraflar'!$S$8:$S$${maxPhotoRow})`],[`=SUM('Fotoğraflar'!$T$8:$T$${maxPhotoRow})`]];
wb.recalculate();
await fs.mkdir(path.dirname(output),{recursive:true});
const stagedOutput=output+'.new.xlsx';
await (await SpreadsheetFile.exportXlsx(wb)).save(stagedOutput);
await fs.rename(stagedOutput,output);
if(process.env.CORTEQS_V7_PREVIEW==='1'){
 for(const [sheet,range,name] of [['Özet','A1:F16','after-overview'],['FotoğrafKaynakları','A5:E10','after-provenance']]){
  const pic=await wb.render({sheetName:sheet,range,scale:1,format:'png'});
  await fs.writeFile(path.join(root,`previews/${name}.png`),new Uint8Array(await pic.arrayBuffer()));
 }
}
console.log(JSON.stringify({output,provenance_rows:rows.length,counts:overview.getRange('B6:B13').values}));
