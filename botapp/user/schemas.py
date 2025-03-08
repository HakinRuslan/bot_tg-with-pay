from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class UserBaseInDB(BaseModel):
    telegram_id: int

    
    model_config = ConfigDict(from_attributes=True)

class UserPurch(BaseModel):
    telegram_id: int

    
    model_config = ConfigDict(from_attributes=True)


class User(UserBaseInDB):
    username: str


class TariffIDModel(BaseModel):
    id: int


class TypeoftariffIDModel(BaseModel):
    type_of_tarrifs_id: int


class PaymentData(BaseModel):
    user_id: int = Field(..., description="ID пользователя Telegram")
    payment_id: str = Field(..., max_length=255, description="Уникальный ID платежа")
    price: int = Field(..., description="Сумма платежа в рублях")
    product_id: int = Field(..., description="ID товара")
 