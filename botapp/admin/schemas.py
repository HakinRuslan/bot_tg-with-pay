from pydantic import BaseModel, ConfigDict, Field

class ProductCategoryIDModel(BaseModel):
    id: int

class UserBaseInDB(BaseModel):
    telegram_id: int

    
    model_config = ConfigDict(from_attributes=True)


class Usersch(UserBaseInDB):
    username: str


class User_upd_active(BaseModel):
    active: bool


# class ProductCategoryIDModel(BaseModel):
#     category_id: int

class CategoryModel(BaseModel):
    type_tarif_name: str = Field(..., min_length=5)
    how_much_days: int

class ProductModel(BaseModel):
    name: str = Field(..., min_length=5)
    description: str = Field(..., min_length=5)
    price: int = Field(..., gt=0)
    type_of_tarrifs_id: int = Field(..., gt=0)
    file_id: str | None = None

class Payment_user_id(BaseModel):
        user_id: int = Field(..., description="ID пользователя Telegram")


class PaymentData(BaseModel):
    user_id: int = Field(..., description="ID пользователя Telegram")
    payment_id: str = Field(..., max_length=255, description="Уникальный ID платежа")
    active: bool
    price: int = Field(..., description="Сумма платежа в рублях")
    tariff_id: int = Field(..., description="ID товара")