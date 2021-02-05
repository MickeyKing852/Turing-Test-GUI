from enum import Enum


class FileKind(Enum):
    FILE = 'drive#file'

    @classmethod
    def _missing_(cls, value):
        return FileKind.FILE


class MimeType(Enum):
    JPEG = 'image/jpeg'
    GIF = 'image/gif'
    ZIP = 'application/x-zip-compressed'
    FOLDER = 'application/vnd.google-apps.folder'
    CSV = 'text/csv'
    UNKNOWN = ''

    @classmethod
    def _missing_(cls, value):
        return MimeType.UNKNOWN


class File:
    name: str
    id: str
    kind: FileKind
    mimeType: MimeType

    def __init__(self, name='', id='', kind='', mimeType='') -> None:
        super().__init__()
        self.name = name
        self.id = id
        self.kind = FileKind(kind)
        self.mimeType = MimeType(mimeType)

    def get_file_type(self) -> str:
        return 'Folder' if self.mimeType is MimeType.FOLDER else f'{self.mimeType.name} File'

    def to_dict(self):
        return {'name': self.name, 'id': self.id, 'kind': self.kind.value, 'mimeType': self.mimeType.value}

    def __str__(self) -> str:
        return f'Google Drive {self.get_file_type()}[name="{self.name}", id="{self.id}"]'
