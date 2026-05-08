from typing import List, Optional
#from pydantic import BaseModel, Field
from pydantic import BaseModel, ConfigDict # <--- Add ConfigDict

class CompanyBase(BaseModel):
    name: str

class UserBase(BaseModel):
  username: str
  email: str
  password: str
  company_name: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserDisplay(BaseModel):
  username: str
  email: str
  company_name: Optional[str] = None
  model_config = ConfigDict(from_attributes=True)

# Article inside UserDisplay
class DcBase(BaseModel):
  dcpower: int
  uspace: int
  nport: int
  sport: int
  model_config = ConfigDict(from_attributes=True)

class DcUpdate(BaseModel):
  dcpower: Optional[int] = None
  uspace: Optional[int] = None
  nport: Optional[int] = None
  sport: Optional[int] = None
  model_config = ConfigDict(from_attributes=True)

class DcInvBase(BaseModel):
  device_type: str
  device_hostname: str
  device_model: str
  device_serial: str
  rack_name: str
  rack_unit: int = 1
  rack_uspace: int = 1
  device_power: int = 0
  device_nports: int = 0
  device_sports: int = 0
  power_status: bool
  device_status: bool
  model_config = ConfigDict(from_attributes=True)

class DcInvUpdate(BaseModel):
  device_type: Optional[str] = None
  device_hostname: Optional[str] = None
  device_model: Optional[str] = None
  device_serial: Optional[str] = None
  rack_name: Optional[str] = None
  rack_unit: Optional[int] = None
  rack_uspace: Optional[int] = None
  device_power: Optional[int] = None
  device_nports: Optional[int] = None
  device_sports: Optional[int] = None
  power_status: Optional[bool] = None
  device_status: Optional[bool] = None
  model_config = ConfigDict(from_attributes=True)



