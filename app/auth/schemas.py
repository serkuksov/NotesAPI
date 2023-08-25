from fastapi_users import schemas
from pydantic import EmailStr, BaseModel


class UserRead(schemas.BaseUser[int]):
    user_name: str


class UserName(BaseModel):
    user_name: str

    class Config:
        orm_mode = True


class UserCreate(schemas.CreateUpdateDictModel):
    email: EmailStr
    password: str
    user_name: str


class UserUpdate(schemas.BaseUserUpdate):
    pass
