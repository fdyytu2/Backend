import json
from app.core.logging import logger

class DigiflazzParser:
    RC_MAP = {
        "00": "Transaksi Sukses",
        "01": "Timeout (Cek Mutasi)",
        "02": "Transaksi Gagal",
        "03": "Transaksi Pending",
        "40": "Payload Error: Tipe data tidak sesuai",
        "41": "Signature tidak valid! Cek API Key & Username di Dashboard",
        "42": "Username belum sesuai",
        "43": "SKU tidak ditemukan/Non-Aktif",
        "44": "Saldo Vendor Gak Cukup!",
        "45": "IP lo belum di-whitelist di Digiflazz!",
        "49": "Ref ID tidak unik",
        "83": "Limit pengecekan tercapai (5 Menit 1x)",
        "99": "DF Router Issue (Pending)"
    }

    @staticmethod
    def parse_balance_response(response: dict):
        logger.info(f"[DIGIFLAZZ RAW] 📦 Isi paket mentah: {json.dumps(response)}")

        if not response.get("success"):
            return {"status": "error", "message": response.get("error", "Koneksi Timeout/Down")}

        # BUKA KOTAK MATRYOSHKA
        http_data = response.get("data", {})
        digiflazz_data = http_data.get("data", {})
        
        # 💡 FIX: Kalau ada 'deposit', berarti SUKSES (karena pas sukses saldo, Digiflazz gak ngirim rc)
        if "deposit" in digiflazz_data:
            logger.info(f"[DIGIFLAZZ] ✅ Cek Saldo Sukses: Rp{digiflazz_data['deposit']}")
            return {
                "status": "success",
                "balance": digiflazz_data["deposit"],
                "message": "Koneksi Normal"
            }

        # Kalau gak ada deposit, baru kita cari tau error-nya lewat RC
        raw_rc = digiflazz_data.get("rc")
        rc = str(raw_rc) if raw_rc is not None else None

        error_msg = DigiflazzParser.RC_MAP.get(rc, digiflazz_data.get("message", "Format vendor tidak dikenali"))
        logger.warning(f"[DIGIFLAZZ] 🚨 TERTOLAK! RC: {rc} | Alasan: {error_msg}")

        return {"status": "error", "message": error_msg, "rc": rc}

    @staticmethod
    def parse_transaction_response(response: dict):
        logger.info(f"[DIGIFLAZZ RAW TRX] 📦 {json.dumps(response)}")
        if not response.get("success"):
            return {"status": "error", "message": response.get("error")}

        http_data = response.get("data", {})
        data = http_data.get("data", {})

        if not data:
            return {"status": "error", "message": "Tidak ada data dari vendor"}

        rc = str(data.get("rc", ""))
        vendor_status = str(data.get("status", "")).upper()
        sn = data.get("sn", "")
        message = data.get("message", DigiflazzParser.RC_MAP.get(rc, "Pesan vendor tidak diketahui"))

        # Mapping status Digiflazz ke status Database kita
        mapped_status = "PENDING"
        if vendor_status == "SUKSES" or rc == "00":
            mapped_status = "SUCCESS"
        elif vendor_status == "GAGAL" or rc in ["02", "40", "41", "42", "43", "44", "45", "49"]:
            mapped_status = "FAILED"

        return {
            "status": "success",
            "mapped_status": mapped_status,
            "vendor_status": vendor_status,
            "sn": sn,
            "message": message,
            "rc": rc,
            "raw": response
        }
