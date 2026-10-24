import sys, openpyxl
wb=openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=False)
ws=wb['FotoğrafKaynakları']
hdr=[c.value for c in next(ws.iter_rows(min_row=7,max_row=7))]
i=hdr.index('downloaded_on')
types={}
for row in ws.iter_rows(min_row=8, max_row=ws.max_row):
    v=row[i].value
    if v is None: continue
    types[type(v).__name__]=types.get(type(v).__name__,0)+1
print('FotoğrafKaynakları.downloaded_on types:',types)
ws=wb['Fotoğraflar']; hdr=[c.value for c in next(ws.iter_rows(min_row=7,max_row=7))]
for col in ('capture_date','source_checked_on'):
    i=hdr.index(col); t={}
    for row in ws.iter_rows(min_row=8,max_row=ws.max_row):
        v=row[i].value
        if v is None: continue
        t[type(v).__name__]=t.get(type(v).__name__,0)+1
    print('Fotoğraflar.'+col, t)
ws=wb['Teslimat']; hdr=[c.value for c in next(ws.iter_rows(min_row=7,max_row=7))]
r8=[c.value for c in next(ws.iter_rows(min_row=8,max_row=8))]
print(dict(zip(hdr,r8)))
wb.close()
