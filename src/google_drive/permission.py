from enum import Enum
from typing import List

from src.google_drive.corpora import Corpora


class UserId(Enum):
    CHARLES = '02949549340170868175'
    HOWOON = '03372216605504017635'
    MICKEY = '08403683784038458566'
    UNKNOWN = ''

    @classmethod
    def _missing_(cls, value):
        return UserId.UNKNOWN


class PermissionRole(Enum):
    OWNER = 'owner'
    ORGANIZER = 'organizer'
    FILE_ORGANIZER = 'fileOrganizer'
    WRITER = 'writer'
    COMMENTER = 'commenter'
    READER = 'reader'
    UNKNOWN = ''

    @classmethod
    def _missing_(cls, value):
        return PermissionRole.UNKNOWN


class PermissionKind(Enum):
    LIST = 'drive#permissionList'
    PERMISSION = 'drive#permission'

    @classmethod
    def _missing_(cls, value):
        return PermissionKind.PERMISSION


class Permission:
    kind: PermissionKind
    id: str
    type: Corpora
    role: PermissionRole

    def __init__(self, kind='', id='', type='', role='') -> None:
        self.kind = PermissionKind(kind)
        self.id = id
        self.type = Corpora(type)
        self.role = PermissionRole(role)

    def __str__(self) -> str:
        user_id = UserId(self.id)
        user_str = self.id if user_id is UserId.UNKNOWN else user_id.name
        return f'{user_str} = {self.role.name}'


class PermissionList:
    kind: PermissionKind
    permissions: List[Permission]

    def __init__(self, kind='', permissions=None) -> None:
        super().__init__()
        if permissions is None:
            permissions = []
        self.kind = PermissionKind(kind)
        self.permissions = [Permission(**x) for x in permissions]

    def __str__(self) -> str:
        return f'[{", ".join([str(x) for x in self.permissions])}]'
