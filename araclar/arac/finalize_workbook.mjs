import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const file=process.argv[2];
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(file));
const overview=wb.worksheets.getItem('Özet');
overview.getRange('A14').values=[['v7 · Kaynak zinciri: FotoğrafKaynakları. Miktar, onay değildir.']];
overview.getRange('A28').values=[['Fotoğraf miktarı dosya SHA-256 özeti ve rolüyle ölçülür; aynı kareye ait türevler ayrıca ayıklanır. Sayımda kullanılabilir eski alanı korunur, insan onayı yerine geçmez. Paket kararı yönetim ekranındadır.']];
await(await SpreadsheetFile.exportXlsx(wb)).save(file);
console.log(JSON.stringify({file,ok:true}));
