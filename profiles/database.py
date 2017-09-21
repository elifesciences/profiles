from datetime import datetime, timezone
from typing import Type, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types

db = SQLAlchemy()


class UTCDateTime(types.TypeDecorator):
    impl = types.DateTime

    def python_type(self) -> Type:
        return datetime

    def process_bind_param(self, value, dialect) -> Optional[datetime]:
        if value is not None:
            return value.astimezone(timezone.utc)

    def process_literal_param(self, value, dialect):
        raise NotImplementedError()

    def process_result_value(self, value, dialect) -> Optional[datetime]:
        if value is not None:
            return datetime(value.year, value.month, value.day,
                            value.hour, value.minute, value.second,
                            value.microsecond, tzinfo=timezone.utc)
