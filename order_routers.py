from fastapi_jwt_auth import AuthJWT
from models import Order, User
from schemas import OrderModel, OrderStatusModel
from database import session, engine
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, status
from starlette.exceptions import HTTPException

order_router = APIRouter(
    prefix="/order"
)

session = session(bind=engine)  # session ishlashi uchun engine dagi malumotlarni oladi


@order_router.get('/')
async def welcome_page(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()  # valid access tokenni talab qiladi
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token yaroqsiz")

    return {"message": "Order uchun"}


# Order yaratish -------------------------------------------------------------------------------------------------->
@order_router.post('/make_order', status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()  # valid access tokenni talab qiladi
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Siz ro'yhatdan o'tmagansz")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    # request berayotgan userni bazadan topib user o'zgaruvchiga o'zlashtirdik

    new_order = Order(
        quantity=order.quantity,
        product_id=order.product_id
    )
    new_order.user = user
    session.add(new_order)  # add() da saqlanib turadi
    session.commit()  # commit() bo'lsa malumotlar bazasiga saqlanidi

    data = {
        "success": True,
        "code": 201,
        "message": "Order is created successfully",
        "data": {
            "id": new_order.id,
            "product": {
                "id": new_order.product.id,
                "name": new_order.product.name,
                "price": new_order.product.price
            },
            "quantity": new_order.quantity,
            "order_status": new_order.order_status.value,
            "total_price": new_order.quantity * new_order.product.price
        }
    }

    response = data
    return jsonable_encoder(response)


# Barcha buyurtmalar ro'yhatini qaytaradi ---------------------------------------------------------------------------->
@order_router.get('/adm/list', status_code=status.HTTP_200_OK)
async def list_all_orders(Authorize: AuthJWT = Depends()):
    #  Bu barcha buyurtmalar ro'yhatini qaytaradi
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if user.is_staff:
        orders = session.query(Order).all()  # Order modeldan barchasini olish u-n
        custom_data = [
            {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product": {
                    "id": order.product_id,
                    "name": order.product.name,
                    "price": order.product.price
                },
                "quantity": order.quantity,
                "order_statuses": order.order_status.value,
                "total_price": order.quantity * order.product.price
            }
            for order in orders
        ]
        return jsonable_encoder(custom_data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin can see all orders")


# ID bo'yicha malumotlarni olish ------------------------------------------------------------------------------------->
@order_router.get('/adm/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    #  Get an order by its ID

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            custom_order = {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product": {
                    "id": order.product_id,
                    "name": order.product.name,
                    "price": order.product.price
                },
                "quantity": order.quantity,
                "order_statuses": order.order_status.value,
                "total_price": order.quantity * order.product.price

            }
            return jsonable_encoder(custom_order)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Order with {id} ID is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only SuperAdmin is allowed to this request")


# Foydalanuvchiga tegishli bo'lgan buyurtmalar ro'yhati--------------------------------------------------------------->
@order_router.get('/user/orders', status_code=status.HTTP_200_OK)
async def get_user_orders(Authorize: AuthJWT = Depends()):
    # Get a requested user's orders
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    custom_data = [
        {
            "id": order.id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "quantity": order.quantity,
            "order_statuses": order.order_status.value,
            "total_price": order.quantity * order.product.price
        }
        for order in user.orders  # relationshipdagi bog'lanish orqali userga tegishli barcha orderlarni olamiz
    ]
    return jsonable_encoder(custom_data)


# ID bo'yicha foydalanuvchiga tegishli bo'lgan buyurtma---------------------------------------------------------------->
@order_router.get('/user/order/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    # Get a requested user's order by ID
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    order = session.query(Order).filter(Order.id == id, Order.user == user).first()
    # IDsi va yuseri shu bo'lgan orderni olib keladi
    if order:
        custom_data = {
            "id": order.id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "quantity": order.quantity,
            "order_statuses": order.order_status.value,
            "total_price": order.quantity * order.product.price
        }
        return jsonable_encoder(custom_data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with this ID {id}")


# ID bo'yicha buyurtmani yangilsh-------------------------------------------------------------------------------------->
@order_router.put('/update/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, order: OrderModel, Authorize: AuthJWT = Depends()):
    """Updating user order by fields: quantity and product_id"""
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    order_update = session.query(Order).filter(Order.id == id).first()

    if order_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with this ID {id}")

    if order_update.user != user:  # Order useri request berayotgan userga tengmi yoki yoq tekshiriladi
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Kechirasiz, siz boshqa foydalanuvchilarning buyurtmalarini tahrirlay olmaysiz!")

    order_update.quantity = order.quantity
    order_update.product_id = order.product_id
    session.commit()

    custom_response = {
        "success": True,
        "code": 200,
        "message": "Sizning buyurtmangiz muvaffaqiyatli o'zgartirildi",
        "data": {
            "id": id,
            "quantity": order.quantity,
            "product": order.product_id,
            "order_status": order.order_statuses
        }
    }
    return jsonable_encoder(custom_response)


# ID bo'yicha buyurtmani o'chirish------------------------------------------------------------------------------------->
@order_router.delete('/delete/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    # Delete a requested user's order by ID
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    order = session.query(Order).filter(Order.id == id).first()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with this ID {id}")

    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Kechirasiz, siz boshqa foydalanuvchilarning buyurtmalarini o'chira olmaysiz!")

    if order.order_status != "PENDING":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Kechirasiz, siz yolga chiqqan va yetkazib berilgan buyurtmalarni o'chira olmaysiz!")

    session.delete(order)
    session.commit()
    custom_response = {
        "success": True,
        "code": 200,
        "message": "User order is succesfully deleted",
        "data": None
    }
    return jsonable_encoder(custom_response)


# ID boyicha order statusini yangilash--------------------------------------------------------------------------------->
@order_router.put('/update/status/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, order: OrderStatusModel, Authorize: AuthJWT = Depends()):
    """Updating user order status"""
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        order_id = session.query(Order).filter(Order.id == id).first()

        if order_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with this ID {id}")

        order_id.order_status = order.order_statuses
        # bazadan olingan order_id ning order_statusini  kritilgan inputdagi order_statusesga o'zgartirish
        session.commit()

        custom_response = {
            "success": True,
            "code": 200,
            "message": "User order is succesfully updated",
            "data": {
                "id": order_id.id,
                "order_status": order_id.order_status
            }
        }
        return jsonable_encoder(custom_response)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only SuperAdmin is allowed to update orders statuses")
