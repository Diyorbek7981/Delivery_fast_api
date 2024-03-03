from fastapi import APIRouter
from fastapi_jwt_auth import AuthJWT
from models import Order, User, Product
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
        quantity=order.quantity
        # product = order.product.id
    )
    new_order.user = user
    session.add(new_order)  # add() da saqlanib turadi
    session.commit()  # commit() bo'lsa malumotlar bazasiga saqlanidi

    data = {
        'id': new_order.id,
        'quantity': new_order.quantity,
        'order_statuses': new_order.order_status
    }
    response = {
        'success': True,
        'code': 201,
        'message': 'Order is created successfully',
        'data': data
    }
    return jsonable_encoder(response)


# Barcha buyurtmalar ro'yhatini qaytaradi ---------------------------------------------------------------------------->
@order_router.get('/list', status_code=status.HTTP_200_OK)
async def list_all_orders(Authorize: AuthJWT = Depends()):
    #  Bu barcha buyurtmalar ro'yhatini qaytaradi
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if user.is_staff:
        order = session.query(Order).all()  # Order modeldan barchasini olish u-n
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
            for order in order
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
                    "id": order.product.id,
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
