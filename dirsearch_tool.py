#!/usr/bin/env python3
import requests
import argparse
import concurrent.futures
import time
import sys
import random
import string
import json
from tqdm import tqdm

def generate_random_string(length=12):
    """Təsadüfi string yaradır."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_wildcard_baseline(base_url, timeout, user_agent):
    """
    Wildcard baseline əldə etmək üçün təsadüfi bir path sorğusu göndərir.
    Bu cavabı gələcək sorğularla müqayisə edərək yanlış pozitivləri aradan qaldırır.
    """
    random_path = generate_random_string()
    url = f"{base_url.rstrip('/')}/{random_path}"
    headers = {"User-Agent": user_agent}
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        baseline = {
            "status": response.status_code,
            "length": len(response.content),
            "content": response.text[:200]  # ilk 200 simvolu yadda saxlayırıq
        }
        return baseline
    except Exception as e:
        print(f"Wildcard baseline əldə edilərkən xəta: {e}")
        return None

def scan_path(base_url, path, timeout, user_agent, baseline):
    """
    Hər bir path üçün sorğu göndərir və cavabı təhlil edir.
    Wildcard baseline ilə müqayisə edərək yanlış pozitivləri işarələyir.
    """
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    headers = {"User-Agent": user_agent}
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        elapsed_time = time.time() - start_time
        
        result = {
            "url": url,
            "status": response.status_code,
            "length": len(response.content),
            "time": elapsed_time,
            "false_positive": False
        }
        
        # Wildcard baseline ilə müqayisə: əgər status və uzunluq oxşardırsa,
        # nəticə böyük ehtimalla yanlış pozitivdir.
        if baseline is not None:
            if (result["status"] == baseline["status"] and abs(result["length"] - baseline["length"]) < 10):
                result["false_positive"] = True
                
        return result
    except requests.RequestException:
        return None

def main():
    parser = argparse.ArgumentParser(description="Dirsearch Tool - Ətraflı Dizin Axtarışı")
    parser.add_argument("-u", "--url", required=True, help="Hədəf URL (məsələn, https://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Direktoriyalar/fayllar üçün wordlist faylı")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Eyni anda işləyəcək iplik sayı (default: 20)")
    parser.add_argument("-o", "--output", default="dirsearch_results.txt", help="Nəticələrin yazılacağı fayl")
    parser.add_argument("--timeout", type=int, default=10, help="HTTP sorğular üçün timeout (default: 10 saniyə)")
    parser.add_argument("--user-agent", default="Mozilla/5.0 (X11; Linux x86_64)", help="Xüsusi User-Agent header")
    parser.add_argument("--json", action="store_true", help="Nəticələri JSON formatında yaz")
    args = parser.parse_args()

    # Wordlist faylını oxuyuruq
    try:
        with open(args.wordlist, "r", encoding="utf-8", errors="ignore") as f:
            paths = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        print(f"Wordlist faylını oxuyarkən xəta: {e}")
        sys.exit(1)

    total_paths = len(paths)
    print(f"[+] {args.url} üçün {total_paths} path ilə scan başlayır (İplik sayı: {args.threads})...")

    # Wildcard baseline əldə edilir
    print("[*] Wildcard baseline tapılır...")
    baseline = get_wildcard_baseline(args.url, args.timeout, args.user_agent)
    if baseline:
        print(f"    Baseline: Status {baseline['status']}, Length {baseline['length']}")
    else:
        print("    Wildcard baseline tapılmadı, davam edilir...")

    results = []
    start_time = time.time()
    
    # ThreadPoolExecutor ilə paralel işləmə və progress bar (tqdm)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(scan_path, args.url, path, args.timeout, args.user_agent, baseline): path for path in paths}
        for future in tqdm(concurrent.futures.as_completed(futures), total=total_paths, desc="Scanning"):
            res = future.result()
            if res:
                results.append(res)

    elapsed_total = time.time() - start_time
    print(f"\n[+] Scan bitdi. Ümumi vaxt: {elapsed_total:.2f} saniyə")
    
    # Nəticələri ekranda göstəririk
    for res in results:
        if res:
            status_line = f"[{res['status']}] {res['url']} - {res['length']} bytes in {res['time']:.2f}s"
            if res["false_positive"]:
                status_line += " (False Positive)"
            print(status_line)
    
    # Nəticələri fayla yazırıq
    try:
        with open(args.output, "w") as f:
            if args.json:
                json.dump(results, f, indent=2)
            else:
                for r in results:
                    if r:
                        line = f"{r['status']} {r['url']} {r['length']} bytes {r['time']:.2f}s"
                        if r["false_positive"]:
                            line += " (False Positive)"
                        f.write(line + "\n")
        print(f"[+] Nəticələr {args.output} faylına yazıldı.")
    except Exception as e:
        print(f"Nəticələri fayla yazarkən xəta: {e}")

if __name__ == "__main__":
    main()
