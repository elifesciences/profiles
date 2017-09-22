from datetime import datetime
from typing import Optional, Type

from flask_sqlalchemy import SQLAlchemy
import pendulum
from sqlalchemy import types

db = SQLAlchemy()


class UTCDateTime(types.TypeDecorator):
    impl = types.DateTime

    def python_type(self) -> Type:
        return datetime

    def process_result_value(self, value, dialect) -> Optional[datetime]:
        if value is not None:
            return pendulum.timezone('utc').convert(value)
