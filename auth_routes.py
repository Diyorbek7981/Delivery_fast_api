import datetime
from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_
from schemas import SignUpModel, LoginModel
from database import session, engine
from models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
# parolni heshlash va uni check orali tekshirish
from fastapi_jwt_auth import AuthJWT

auth_router = APIRouter(
    prefix="/auth"
)

session = session(bind=engine)  # session ishlashi uchun engine dagi malumotlarni oladi


# urlda auth so'zi kelsa shu packagedagi urllar ishlaydi

@auth_router.get('/')
async def welcom(Authorize: AuthJWT = Depends()):
    # Authorize: AuthJWT = Depends() bu ushbu apiga token kiritish majburiy ekanligini anglatadi

    try:
        Authorize.jwt_required()  # valid access tokenni talab qiladi
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token yaroqsiz")

    return {"message": "Authentication uchun"}


# sigup -------------------------------------------------------------------------------------------------------------->
@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):  # user kiritgan malumotlarni tekshirib bazaga saqlash
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Bu email malumotlar bazasida allaqachon bor")

    db_user = session.query(User).filter(User.username == user.username).first()
    if db_user is not None:
        return HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Bu username malumotlar bazasida allaqachon bor")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),  # parloni heshlash uchun
        is_active=user.is_active,
        is_staff=user.is_staff
    )
    session.add(new_user)
    session.commit()  # malumotlar bazasiga qo'shish uchun

    data = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_staff": new_user.is_staff,
        "is_active": new_user.is_active,
    }
    response_model = {
        'success': True,
        'code': 201,
        'message': 'User muvofaqiyatli yaratildi',
        'data': data  # user malumotlari
    }

    return response_model


# Login -------------------------------------------------------------------------------------------------------------->
@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
    # query  email yoki username orqali qidiradi
    db_user = session.query(User).filter(
        or_(
            User.username == user.username_or_email,
            User.email == user.username_or_email
        )
    ).first()
    # first() orqali 1 obyekt qilib olamiz

    if db_user and check_password_hash(db_user.password, user.password):
        access_lifetime = datetime.timedelta(days=1)  # acses va refresh tokenga vaqt qo'yiladi
        refresh_lifetime = datetime.timedelta(days=3)
        access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username, expires_time=refresh_lifetime)
        # expires_time orqali unin yaroqilik muddati belgilanadi

        token = {
            "access": access_token,
            "refresh": refresh_token
        }
        response = {
            "success": True,
            "code": 200,
            "message": "User muvofaqiyatli login qilindi",
            "data": token
        }

        return jsonable_encoder(response)
        # dictionaty malumotini json formatga ogirib beradi

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")


# Login refresh ------------------------------------------------------------------------------------------------------->
@auth_router.get('/login_refresh', status_code=status.HTTP_200_OK)
async def login_refresh(Authorize: AuthJWT = Depends()):
    try:
        access_lifetime = datetime.timedelta(days=1)
        Authorize.jwt_refresh_token_required()  # valid refresh tokenni talab qiladi
        current_user = Authorize.get_jwt_subject()  # access tokendan usernameni ajratib olamiz

        db_user = session.query(User).filter(User.username == current_user).first()
        # databasedan userni filter orqali topamiz

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User topilmadi")

        new_access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        # yangi access token yaratamiz

        response_model = {
            'success': True,
            'code': 201,
            'message': 'Yangi access token yaratildi',
            'data': {
                'access_token': new_access_token
            }
        }
        return response_model

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Notog`ri refresh token')
