from sqlalchemy.orm import (
    relationship,
    validates,
    Mapped,
    mapped_column,
)  # UPDATED: Added Mapped and mapped_column for 2.0 style
from sqlalchemy.sql.schema import ForeignKey, CheckConstraint
from sqlalchemy.sql.sqltypes import Integer, String, Boolean
from db.database import Base

# from sqlalchemy import Column # REMOVED: No longer needed with mapped_column
import re


class DcCompany(Base):
    __tablename__ = "companies"
    # UPDATED: Using Mapped[int] and mapped_column instead of Column(Integer, ...)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # UPDATED: Added type hinting to relationships for better IDE support
    users: Mapped[list["DcUser"]] = relationship("DcUser", back_populates="company")
    purchase: Mapped["DcPurchase"] = relationship("DcPurchase", back_populates="company", uselist=False)


class DcUser(Base):
    __tablename__ = "users"
    # UPDATED: Standardized to 2.0 mapped_column syntax
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)

    # UPDATED: Explicit Mapped types for relationships
    company: Mapped["DcCompany"] = relationship("DcCompany", back_populates="users")
    items: Mapped[list["DcInventory"]] = relationship("DcInventory", back_populates="user")

    @validates("username", "password", "company")
    def validate_non_empty_string(self, key, value):
        # UPDATED: Added isinstance check to prevent errors when value is a relationship object
        if not value or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"{key} cannot be empty or contain only whitespace.")
        return value

    @validates("email")
    def validate_email(self, key, value):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            raise ValueError(f"Invalid email format: {value}")
        return value


class DcInventory(Base):
    __tablename__ = "inventory"
    # UPDATED: Transitioned all Column calls to Mapped[type] = mapped_column
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_type: Mapped[str] = mapped_column(String, nullable=False)
    device_hostname: Mapped[str] = mapped_column(String, nullable=False)
    device_model: Mapped[str] = mapped_column(String, nullable=False)
    device_serial: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    rack_name: Mapped[str] = mapped_column(String, nullable=False)
    rack_unit: Mapped[int] = mapped_column(Integer, nullable=False)
    rack_uspace: Mapped[int] = mapped_column(Integer, nullable=False)
    device_power: Mapped[int] = mapped_column(Integer, nullable=False)
    device_nports: Mapped[int] = mapped_column(Integer, nullable=False)
    device_sports: Mapped[int] = mapped_column(Integer, nullable=False)
    power_status: Mapped[bool] = mapped_column(Boolean, default=False)
    device_status: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)

    user: Mapped["DcUser"] = relationship("DcUser", back_populates="items")

    __table_args__ = (
        CheckConstraint("rack_uspace > 0", name="check_rack_uspace_positive"),
        CheckConstraint("device_power > 0", name="check_device_power_positive"),
        CheckConstraint("device_nports > 0", name="check_device_nports_positive"),
    )

    @validates("device_type", "device_hostname", "device_model", "device_serial", "rack_name")
    def validate_non_empty_string(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key} cannot be empty or contain only whitespace.")
        return value


class DcPurchase(Base):
    __tablename__ = "dcusage"
    # UPDATED: Final set of 2.0 syntax updates for consistency
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dcpower: Mapped[int] = mapped_column(Integer, nullable=False)
    uspace: Mapped[int] = mapped_column(Integer, nullable=False)
    nport: Mapped[int] = mapped_column(Integer, nullable=False)
    sport: Mapped[int] = mapped_column(Integer, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)

    company: Mapped["DcCompany"] = relationship("DcCompany", back_populates="purchase")

    __table_args__ = (
        CheckConstraint("dcpower > 0", name="check_dcpower_positive"),
        CheckConstraint("uspace > 0", name="check_uspace_positive"),
        CheckConstraint("nport > 0", name="check_nport_positive"),
        CheckConstraint("sport > 0", name="check_sport_positive"),
    )
