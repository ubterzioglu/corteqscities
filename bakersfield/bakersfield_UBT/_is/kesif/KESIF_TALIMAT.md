# Kaynak keşfi talimatı (Bakersfield, Kaliforniya, ABD · CITY-901)

Görevin: verilen 3 konunun her biri için Bakersfield'a yeni taşınan Türkçe konuşan birine pratik bilgi verecek **resmî** web sayfalarını bulmak ve her sayfa için sayfada birebir geçen kanıt ifadeleri (`must_contain`) yazmak. Metin yazmıyorsun; yalnız adres ve kanıt ifadesi topluyorsun.

## Hangi sayfalar kabul edilir
- Yalnız resmî yayıncının **derin sayfası**: ABD federal kurumu (irs.gov, ssa.gov, dol.gov, usa.gov, consumerfinance.gov, fdic.gov, ftc.gov, fcc.gov, hud.gov …), California eyalet kurumu (*.ca.gov, coveredca.com, courts.ca.gov …), Kern County (kerncounty.com, kernpublichealth.com, kernpublicworks.com, kcdhs.org, kernbhrs.org, kerncountyfire.org …), okul bölgeleri (bcsd.com, kernhigh.org, kern.org), kamu kurumları ve hizmeti fiilen veren kuruluşun kendi sayfası (ör. PG&E, Cal Water, Amtrak San Joaquins, Meadows Field havalimanı, hastanenin kendi sitesi, Bakersfield College, CSUB). Türkiye Cumhuriyeti resmî siteleri (mfa.gov.tr, konsolosluk.gov.tr …) de olur.
- **Yasak:** Wikipedia; tek başına anasayfa (bilgi taşıyan alt sayfa olmalı); blog, forum, haber sitesi; ticari rehber/expat portalı, emlak ilanı sitesi, karşılaştırma sitesi, avukat/danışman bürosu; kâr amaçlı aracı. Kamu adına çalışan resmî program sitesi (ör. California LifeLine, Covered California) olur.
- Bakersfield'a ya da Kern County'ye özgü sayfa varsa onu tercih et; yoksa California, o da yoksa federal sayfa.
- İngilizce sayfa tercih edilir (`lang: "en"`); Türkiye resmî sayfası `tr`.

## Bilinen erişim durumu (bu ortamın indiricisiyle denendi, 23.10.2026)
- **403 / bot engeli, KULLANMA:** uscis.gov ve alt alanları (egov.uscis.gov dahil), travel.state.gov, state.gov, tr.usembassy.gov, dhs.gov, studyinthestates.dhs.gov, cbp.gov, bakersfieldcity.us (Bakersfield belediyesi), dhcs.ca.gov (Medi-Cal), hcd.ca.gov, kernha.org, kerncountylibrary.org, kernmedical.com, adventisthealth.org.
- **TLS/DNS/zaman aşımı, KULLANMA:** cdph.ca.gov, covered.ca.gov, kerncountysheriff.org, bakersfieldpd.us, bakersfieldfire.us, cde.ca.gov (yönlendirme döngüsü), valleyair.org, cdss.ca.gov (zaman aşımı), losangeles.bk.mfa.gov.tr, americasjobcenter.ca.gov, 211kern.org, kernrecycles.com.
- **Çalışıyor:** irs.gov, ssa.gov, dol.gov, usa.gov (bazı yollar 404; doğru yolu bul), my.uscis.gov, dmv.ca.gov, edd.ca.gov, ftb.ca.gov, dir.ca.gov, labor.ca.gov, cpuc.ca.gov, caloes.ca.gov, ca.gov, courts.ca.gov, dca.ca.gov, cslb.ca.gov, coveredca.com, pge.com, calwater.com, usps.com, consumerfinance.gov, kerncounty.com, kernpublichealth.com, kernpublicworks.com, kerncountyfire.org, kernbhrs.org, kcdhs.org, bcsd.com, kernhigh.org, kern.org, meadowsfield.com, amtraksanjoaquins.com, bakersfieldcollege.edu, csub.edu, dignityhealth.org, mfa.gov.tr.
- getbus.org (GET otobüsleri) anasayfası JS ile yükleniyor (ince metin); alt sayfalarını dene.
- Engelli bir kurumun bilgisi başka resmî yayıncıda varsa (ör. göçmenlik için usa.gov, dol.gov, my.uscis.gov, federalregister.gov, ecfr.gov, justice.gov/eoir, ice.gov) onu kullan. Bulamazsan `gaps`'e yaz.

## Kanıt ifadesi (`must_contain`) ve ZORUNLU yerel deneme
- Her adres için 1–3 ifade: sayfada **birebir** geçen, bilginin orada olduğunu kanıtlayan kısa parça (4–12 kelime; sayı/kural/ücret içeren cümle parçası ideal). Genel kelime ("Bakersfield", "apply") olmaz. Büyük/küçük harf ve boşluk farkı önemsizdir; noktalama ve kelimeler birebir olmalı.
- WebFetch özet döndürür, birebir metni garanti etmez. Bu yüzden listeye yazmadan önce adresleri **bizim indiricimizle** dene:
  1. Kendi geçici klasöründe (`<senin_klasörün>`) `urls.txt` (satır başına bir adres) ve `mc.jsonl` (`{"url": "...", "must_contain": ["..."]}` satırları, UTF-8) yaz.
  2. PowerShell:
     ```powershell
     & 'C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe' 'C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts\fetch_snapshot.py' --urls '<klasör>\urls.txt' --out-dir '<klasör>\snap_<n>' --cache-dir '<klasör>\cache' --must-contain '<klasör>\mc.jsonl'
     ```
  3. `<klasör>\snap_<n>\index.jsonl`'de her satır: `status`, `flags`, `evidence.missing`, `text_file`. Yalnız `status` 200, `flags` içinde `fetch_failed`/`thin_text`/`soft_404` yok ve `evidence.missing` boş olan adresler listeye girer. İfade tutmadıysa `snap_<n>\<text_file>` metnini aç ve oradan birebir ifade seç, sonra yeniden dene (her denemede yeni `snap_<n>` klasörü; `cache` aynı kalır).
- İndirilen metin sayfanın bizim gördüğümüz hâlidir; ifadeyi o metinden almak en güvenli yoldur.

## Çıktı
- Konu başına `C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\kesif\<konu>\selected.jsonl`, UTF-8, satır başına bir JSON:
  `{"url": "...", "must_contain": ["...", "..."], "title": "<sayfa başlığı>", "publisher": "<kurum adı>", "lang": "en", "why": "<Türkçe, bu sayfa hangi soruyu/alt konuyu karşılıyor>"}`
- Konu başına 12–18 kabul edilebilir adres. Verilen 5 "ilk soru"nun her birine en az bir adres. Birden çok konuya yarayan sayfa her ilgili konunun dosyasına ayrı satır olarak yazılır (bu dosyalar senin 3 konununsa).
- Aynı dosyada aynı adres iki kez olmaz. Adres, indiricinin `final_url`'ü değil, denediğin adres olsun (yönlendirme varsa `final_url`'ü yaz ve onu dene).
- Yalnız kendi geçici klasörüne ve kendi 3 konunun `selected.jsonl` dosyasına yaz. Başka dosyaya dokunma.

## Bütçe ve dönüş
- En çok 30 dakika ve 120 araç çağrısı. Bütçe dolunca bulduklarınla dön.
- Son mesajın yalnız tek satır JSON: `{"agent":"<harf>","topics":{"<konu>":<satır sayısı>,...},"tested_ok":<n>,"rejected_tested":<n>,"gaps":["<konu>: <kaynağı bulunamayan soru/alt konu ve nedeni>"]}`
