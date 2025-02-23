# Dirsearch Tool

*Dirsearch Tool*, veb serverlərin təhlükəsizlik auditində istifadə edilən bir Python əsaslı direktoriyaların və faylların brute-force vasitəsidir.
 Bu skript, wordlist-də olan potensial direktoriyalar və fayl yolları üzərində HTTP sorğuları göndərərək, mövcud olan resursları aşkar edir.
 Bu vasitə penetrasiya testçiləri və kibertəhlükəsizlik araşdırmaçılar üçün gizli resursları tapmaqda çox faydalıdır.

## Xüsusiyyətlər

- *Çox İplikli Tarama:* Paralel işləmə ilə sürətli tarama təmin edir.
- *Wildcard Baseline:* Təsadüfi mövcud olmayan path sorğusu vasitəsilə alınan cavabı istifadə edərək yanlış pozitivləri aradan qaldırır.
- *Ətraflı Nəticə Analizi:* Hər bir sorğunun status kodu, cavab ölçüsü (bytes) və keçən vaxtı (saniyə) qeyd olunur.
- *False Positive Yoxlaması:* Cavablar, baseline ilə müqayisə edilərək potensial yanlış pozitivlər işarələnir.
- *Progress Bar:* TQDM modulundan istifadə edərək tarama prosesini izləmək imkanı verir.
- *JSON Çıxış:* Nəticələri JSON formatında çıxarmaq imkanı ilə əlavə analiz üçün əlverişlidir.

## Quraşdırma

### Əsas Tələblər

- Python 3.x
- Aşağıdakı Python paketləri:
  - requests
  - tqdm

# Paketləri quraşdırmaq üçün:

sh
pip install requests tqdm

git clone https://github.com/yourusername/dirsearch.git
cd dirsearch

# İstifadə Qaydası

python3 dirsearch_tool.py -u https://target.com -w wordlist.txt -t 20 -o results.txt --timeout 10 --user-agent "Mozilla/5.0 (X11; Linux x86_64)" --json
