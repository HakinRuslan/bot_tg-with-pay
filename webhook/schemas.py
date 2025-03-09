from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date


class PaymentData(BaseModel):
    user_id: int = Field(..., description="ID пользователя Telegram")
    payment_id: str = Field(..., max_length=255, description="Уникальный ID платежа")
    price: int = Field(..., description="Сумма платежа в рублях")
    active: bool
    expires: date
    tariff_id: int = Field(..., description="ID товара")
 