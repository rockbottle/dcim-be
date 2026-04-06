from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql.schema import ForeignKey, CheckConstraint
from sqlalchemy.sql.sqltypes import Integer, String, Boolean
from db.database import Base
from sqlalchemy import Column
import re

class DcCompany(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, index=True)  # Auto-generated unique ID
    name = Column(String, unique=True, nullable=False)  # Unique company name
    users = relationship("DcUser", back_populates="company")  # One-to-many with users
    purchase = relationship("DcPurchase", back_populates="company", uselist=False)  # One-to-one with purchase


class DcUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)  # Auto-generated unique ID
    username = Column(String, unique=True, nullable=False)  # Unique username
    email = Column(String, unique=True, nullable=False)  # Unique email
    password = Column(String, nullable=False)  # Hashed password
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)  # Links to company
    company = relationship("DcCompany", back_populates="users")  # Many-to-one with company
    items = relationship('DcInventory', back_populates='user')  # One-to-many with inventory
    # Validator for non-empty fields
    @validates('username', 'password', 'company')
    def validate_non_empty_string(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key} cannot be empty or contain only whitespace.")
        return value

    # Validator for email
    @validates('email')
    def validate_email(self, key, value):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, value):
            raise ValueError(f"Invalid email format: {value}")
        return value

class DcInventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, index=True)  # Auto-generated unique ID
    device_type = Column(String, nullable=False)  # Type of device
    device_hostname = Column(String, nullable=False)  # Hostname
    device_model = Column(String, nullable=False)  # Model name
    device_serial = Column(String, unique=True, nullable=False)  # Serial number
    rack_name = Column(String, nullable=False)  # Rack name
    rack_unit = Column(Integer, nullable=False)  # Rack unit
    rack_uspace = Column(Integer, nullable=False)  # Rack unit space
    device_power = Column(Integer, nullable=False)  # Power consumption
    device_nports = Column(Integer, nullable=False)  # Network Ports
    device_sports = Column(Integer, nullable=False)  # SAN Ports 
    power_status = Column(Boolean, default=False)  # Power on/off
    device_status = Column(Boolean, default=True)  # Device status
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Links to user
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False) # Links to company
    user = relationship("DcUser", back_populates='items')  # Many-to-one with user
    __table_args__ = (
        CheckConstraint('rack_uspace > 0', name='check_rack_uspace_positive'),
        CheckConstraint('device_power > 0', name='check_device_power_positive'),
        CheckConstraint('device_nports > 0', name='check_device_nports_positive'),
    ) 
    @validates('device_type', 'device_hostname', 'device_model', 'device_serial', 'rack_name')
    def validate_non_empty_string(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key} cannot be empty or contain only whitespace.")
        return value   


class DcPurchase(Base):
    __tablename__ = 'dcusage'
    id = Column(Integer, primary_key=True, index=True)  # Auto-generated unique ID
    dcpower = Column(Integer, nullable=False)  # Purchased power
    uspace = Column(Integer, nullable=False)  # Purchased rack space
    nport = Column(Integer, nullable=False)  # Purchased network ports
    sport = Column(Integer, nullable=False)  # Purchased SAN ports
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)  # Links to company (one-to-one)
    created_by = Column(Integer, nullable=False)
    company = relationship("DcCompany", back_populates="purchase")  # One-to-one with company
    __table_args__ = (
        CheckConstraint('dcpower > 0', name='check_dcpower_positive'),
        CheckConstraint('uspace > 0', name='check_uspace_positive'),
        CheckConstraint('nport > 0', name='check_nport_positive'),
        CheckConstraint('sport > 0', name='check_sport_positive'),
    )