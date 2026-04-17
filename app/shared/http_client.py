import requests
from app.core.logging import logger

def safe_api_request(method: str, url: str, timeout: int = 10, **kwargs):
    """
    Kurir pengantar data ke API luar.
    Update: Sekarang kurir nggak buang paket JSON meskipun vendor ngasih error HTTP 400/500.
    """
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        
        # 1. Coba buka paketnya, apakah isinya format JSON?
        try:
            data = response.json()
            # 🛡️ Kalau wujudnya JSON, bilang "Kurir Sukses". 
            # Masalah isinya error 400/Bad Request, biarin Parser yang baca.
            return {"success": True, "data": data, "status_code": response.status_code}
        except ValueError:
            # 2. Kalau isinya bukan JSON (misal HTML Cloudflare block), baru ngambek
            response.raise_for_status()
            
    except requests.exceptions.Timeout:
        logger.error(f"[HTTP] Timeout saat nembak {url}")
        return {"success": False, "error": "Koneksi vendor RTO (Timeout)", "status_code": 408}
    except requests.exceptions.RequestException as e:
        logger.error(f"[HTTP] Gagal koneksi ke {url}: {e}")
        return {"success": False, "error": str(e), "status_code": 500}
