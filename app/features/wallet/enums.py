import enum

class AccountType(str, enum.Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"             # Dompet modal lu
    VENDOR = "VENDOR"             # Dompet API Provider
    SYSTEM_PROFIT = "SYSTEM_PROFIT" # 🚩 Penampung cuan selisih harga
    SYSTEM_FEE = "SYSTEM_FEE"       # 🚩 Penampung biaya admin/layanan

class JournalType(str, enum.Enum):
    TOPUP = "TOPUP"
    PAYMENT = "PAYMENT"
    REFUND = "REFUND"
    PROFIT_SWEEP = "PROFIT_SWEEP"   # 🚩 Mutasi tarik cuan harian

class JournalStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class LedgerDirection(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
