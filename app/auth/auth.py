from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend, BearerTransport
from fastapi_users.authentication import JWTStrategy

from auth.manager import get_user_manager
from auth.models import User
from setings import Settings


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=Settings().SECRET_KEY, lifetime_seconds=3600)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

cookie_transport = CookieTransport(cookie_name="bonds", cookie_max_age=3600)
cookie_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

auth_backend = cookie_backend
fastapi_users = FastAPIUsers[User, int](get_user_manager, [cookie_backend])
current_active_user = fastapi_users.current_user(active=True)
