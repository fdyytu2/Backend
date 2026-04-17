from pydantic import BaseModel
from typing import List

class NotificationItem(BaseModel):
    id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: str

class NotificationListOut(BaseModel):
    data: List[NotificationItem]
    unread_count: int
