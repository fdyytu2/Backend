import logging
from sqlalchemy import inspect
from app.core.db_engine import engine
from app.core.db_base import Base

def init_db():
    # Ini buat import otomatis pas mau create table
    from app.features.users.models import User
    from app.features.auth.otp_models import UserOTP
    from app.features.wallet.models import Wallet, LedgerJournal, LedgerEntry
    from app.features.transfers.models import Transfer
    from app.features.ppob.models import PPOBProduct, PPOBOrder
    from app.features.topup.models import Topup
    from app.features.admin.models import Banner, Ticket
    from app.features.paylater.models import PaylaterAccount
    from app.features.deposit.models import Deposit

    inspector = inspect(engine)
    if not inspector.get_table_names():
        Base.metadata.create_all(bind=engine)
