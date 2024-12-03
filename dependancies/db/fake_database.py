import datetime

from dependancies.schemas.qr import Qr
from dependancies.schemas.users import UserCreateRequest
from types import SimpleNamespace

fake_user_id_sequence = 1
fake_user: dict[str, SimpleNamespace] = {}

fake_qr: dict[str, Qr] = {}


def add_user(create_user: UserCreateRequest):
    global fake_user_id_sequence
    global fake_user

    if find_user_by_name_and_tel(create_user.username, create_user.tel):
        raise Exception("이미 존재함")

    fake_user_id_sequence += 1
    fake_user[f"{fake_user_id_sequence}"] = SimpleNamespace(
        **create_user.model_dump(),
        user_id=fake_user_id_sequence,
        bot_id=None,
        deleted_at=None,
    )
    return fake_user[f"{fake_user_id_sequence}"]


def update_user(user_id: int, create_user: UserCreateRequest):
    global fake_user_id_sequence
    global fake_user

    if f"{user_id}" not in fake_user:
        raise Exception('없음')

    fake_user[f"{user_id}"] = SimpleNamespace(
        **create_user.model_dump(),
        bot_id=fake_user[f"{user_id}"].bot_id,
        deleted_at=None,
    )
    return fake_user[f"{user_id}"]


def delete_user(user_id: int):
    global fake_user_id_sequence
    global fake_user

    if f"{user_id}" not in fake_user:
        raise Exception('없음')

    # 중복 키를 제거한 후 업데이트
    existing_data = vars(fake_user[f"{user_id}"]).copy()  # 기존 속성 복사
    existing_data.pop('deleted_at', None)  # 'deleted_at' 키가 있다면 제거

    fake_user[f"{user_id}"] = SimpleNamespace(
        **existing_data,
        deleted_at=datetime.datetime.now(datetime.UTC)
    )
    return fake_user[f"{user_id}"]


def find_user_by_name_and_tel(username: str, tel: str):
    global fake_user
    for user in fake_user.values():
        if user.username == username and user.tel == tel:
            return user
    return None


def read_all_users(include_deleted_user: bool = False):
    return list(filter(lambda u: True if include_deleted_user else u.deleted_at is None, fake_user.values()))


def add_qr(new_qr: Qr):
    global fake_qr
    fake_qr[new_qr.qr_code] = new_qr

    return new_qr


def get_qr(qr_code: str):
    global fake_qr

    if qr_code not in fake_qr:
        raise Exception("없는 qr")

    elif fake_qr[qr_code].expires_at < datetime.datetime.now(datetime.UTC):
        raise Exception("유효기간이 지난 QR")

    return fake_qr[qr_code]


def list_qr(include_expired_qr: bool = False):
    return list(filter(lambda q: True if include_expired_qr else q.expires_at > datetime.datetime.now(datetime.UTC), fake_qr.values()))
