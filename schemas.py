from pydantic import BaseModel
from typing import Optional


# Validatsiyalr berish uchun
class SignUpModel(BaseModel):
    id: Optional[int]  # majmuriy kiritish shart emas
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        # orm rejimini yoqib beradi
        # malumotlar to'g'ri kiritilgan bo'lsa pydentic uni sqlalchemyga ogirib beradi malumotlar bazasiga saqlanadi
        schema_extra = {
            'example': {
                'username': "Ismingiz",
                'email': "Emailingiz",
                'password': "password",
                'is_staff': False,
                "is_active": True
            }  # foydalanuvshiga placeholder korinishida shu malumotlarni ko'rsatib turadi
        }


class UserUpdate(BaseModel):
    id: Optional[int]  # majmuriy kiritish shart emas
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        # orm rejimini yoqib beradi
        # malumotlar to'g'ri kiritilgan bo'lsa pydentic uni sqlalchemyga ogirib beradi malumotlar bazasiga saqlanadi
        schema_extra = {
            'example': {
                'username': "Ismingiz",
                'email': "Emailingiz",
                'password': "password",
                'is_staff': False,
                "is_active": True
            }  # foydalanuvshiga placeholder korinishida shu malumotlarni ko'rsatib turadi
        }


class Settings(BaseModel):
    authjwt_secret_key: str = 'a952f06b061769101daf6ef549d6284510cd958d9e77f26ebe9b3edf790efc73'
    # shu secret key orqali userning tokenini enkod va decod qilib haqiqiligini tekshiramiz


class LoginModel(BaseModel):
    username_or_email: str
    password: str


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_statuses: Optional[str] = "PENDING"
    user_id: Optional[int]
    product_id: int

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "quantity": 'Soni',
            }
        }


class OrderStatusModel(BaseModel):
    order_statuses: Optional[str] = "PENDING"

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "order_statuses": "PENDING"
            }
        }


class ProductModel(BaseModel):
    id: Optional[int]
    name: str
    price: int

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "name": "Maxsulot nomi",
                "price": "Mahsulot narxi"
            }
        }


class ProductUpdateModel(BaseModel):
    id: Optional[int]
    name: Optional[str]
    price: Optional[int]

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "name": "Maxsulot nomi",
                "price": "Mahsulot narxi"
            }
        }
