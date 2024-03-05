from fastapi_jwt_auth import AuthJWT
from sqlalchemy.sql.functions import current_user

from models import User, Product
from schemas import ProductModel, ProductUpdateModel
from database import session, engine
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

product_router = APIRouter(
    prefix='/product',
)
session = session(bind=engine)


# Product yaratish --------------------------------------------------------------------------------------------------->
@product_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        new_product = Product(
            name=product.name,
            price=product.price
        )

        session.add(new_product)
        session.commit()
        data = {
            "success": True,
            "code": 201,
            "message": "Product is created successfully",
            "data": {
                "id": new_product.id,
                "name": new_product.name,
                "price": new_product.price
            }
        }
        return jsonable_encoder(data)

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Faqat admin mahsulot qo'shaoladi")


# Barcha productlar ro'yhati --------------------------------------------------------------------------------------->
@product_router.get('/list', status_code=status.HTTP_200_OK)
async def prodcut_list(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    products = session.query(Product).all()
    custom_data = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        for product in products
    ]
    return jsonable_encoder(custom_data)


# ID bo'yicha product ------------------------------------------------------------------------------------------------>
@product_router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_product_by_id(id: int, Authorize: AuthJWT = Depends()):
    #  Get an order by its ID

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Enter valid access token")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    product = session.query(Product).filter(Product.id == id).first()
    if product:
        custom_order = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
        }
        return jsonable_encoder(custom_order)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with {id} ID is not found")


# ID bo'yicha o'chirish ----------------------------------------------------------------------------------------------->
@product_router.delete('/delete/{id}', status_code=status.HTTP_200_OK)
async def delete_product_by_id(id: int, Authorize: AuthJWT = Depends()):
    #  Bu endpoint mahsulotni o'chirish uchun ishlatiladi
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            session.delete(product)
            session.commit()
            data1 = {
                "success": True,
                "code": 200,
                "message": f"Product with ID {id} has been deleted",
            }
            return jsonable_encoder(data1)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with ID {id} is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only SuperAdmin is allowed to delete product")


# UPdate uchun ------------------------------------------------------------------------------------------------------->
@product_router.put('/update/{id}', status_code=status.HTTP_200_OK)
async def update_product_by_id(id: int, update_data: ProductUpdateModel, Authorize: AuthJWT = Depends()):
    #  Bu endpoint mahsulotni yangilash uchun ishlatiladi
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Enter valid access token")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()
    if current_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            # update product
            for key, value in update_data.dict(exclude_unset=True).items():
                # qisman update qilish uchun exclude_unset true qoyiladi (yani faqat nomini yangilamoqchi bolsak)
                setattr(product, key, value)
                # Ushbu setattr ob'ektning atributlarini dinamik ravishda yangilaydi
            session.commit()

            data = {
                "success": True,
                "code": 200,
                "message": f"Product with ID {id} has been updated",
                "data": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price
                }
            }
            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with ID {id} is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only SuperAdmin is allowed to update product")
