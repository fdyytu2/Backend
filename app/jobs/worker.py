from app.core.logging import logger

def run_background_task(task_name: str, *args, **kwargs):
    """
    Penerima tugas instan di balik layar (FastAPI BackgroundTasks).
    """
    logger.info(f"[WORKER] 🛠️ Memulai Task: {task_name}")
    
    try:
        if task_name == "sync_pricelist":
            from app.jobs.tasks.sync_digiflazz_pricelist import task_sync_pricelist
            task_sync_pricelist()
        
        elif task_name == "poll_pending":
            from app.jobs.tasks.poll_ppob_pending import task_poll_pending
            task_poll_pending()
            
        # Nanti bisa tambah: send_whatsapp, send_email, dll
        
    except Exception as e:
        logger.error(f"[WORKER] ❌ Task {task_name} GAGAL TOTAL: {e}")
