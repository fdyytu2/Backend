import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os
from contextvars import ContextVar

# Variabel "Ghaib" untuk nyimpen Nomor Resi (Correlation ID) di memori
request_id_var: ContextVar[str] = ContextVar("request_id", default="SYSTEM")

# Filter biar setiap laporan otomatis nempelin Nomor Resi
class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

def setup_logger():
    # Bikin folder 'logs' kalau belum ada
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("ppob_app")
    logger.setLevel(logging.INFO)
    
    # Bersihin handler lama biar nggak dobel
    if logger.hasHandlers():
        logger.handlers.clear()

    # Format Laporan: [Tanggal] [Level] [Nomor Resi] [Nama File] Pesannya
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(request_id)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Output ke Terminal (Console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(CorrelationFilter())
    logger.addHandler(console_handler)

    # 2. Output ke File (Pisah tiap jam 12 malam, hapus setelah 30 hari)
    file_handler = TimedRotatingFileHandler(
        filename="logs/ppob.log",
        when="midnight",
        interval=1,
        backupCount=30, 
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(CorrelationFilter())
    logger.addHandler(file_handler)

    return logger

# Bikin instance logger biar bisa di-import kepingan lain
logger = setup_logger()
