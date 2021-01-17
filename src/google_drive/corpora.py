from enum import Enum


class Corpora(Enum):
    USER = 'user'  # Files created/opened/shared with user
    DRIVE = 'drive'  # Shared Drive (Enterprise usage)
    DOMAIN = 'domain'  # Files shared with user's domain
    ALL = 'allDrives'  # Everywhere, will be slow

    @classmethod
    def _missing_(cls, value):
        return Corpora.USER
