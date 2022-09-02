from datetime import datetime
from typing import Optional, Type

from flask_sqlalchemy import SQLAlchemy
from iso3166 import Country, countries
import pendulum
from sqlalchemy import types
from sqlalchemy.engine import Dialect

db = SQLAlchemy()


class ISO3166Country(types.TypeDecorator):
    impl = types.String(2)

    def python_type(self) -> Type:
        return Country

    def process_bind_param(
        self, value: Optional[Country], dialect: Dialect
    ) -> Optional[str]:
        if value is not None:
            return value.alpha2

    def process_result_value(
        self, value: Optional[str], dialect: Dialect
    ) -> Optional[Country]:
        if value is not None:
            return countries.get(value)


class UTCDateTime(types.TypeDecorator):
    impl = types.DateTime

    def python_type(self) -> Type:
        return datetime

    def process_result_value(self, value, dialect) -> Optional[datetime]:
        if value is not None:
            return pendulum.timezone("utc").convert(value)
