from typing import List
from schemas import DcInvBase, DcInvUpdate, UserBase
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_inventory
from auth.oauth2 import get_current_user


router = APIRouter(prefix="/inventory", tags=["INVENTORY CRUD Operations"])


# Create Device Inventory
@router.post("/create")
def create_dc_inventory(request: DcInvBase, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    return db_inventory.create_dc_inventory(db, request, current_user)


# Read all Device Inventory
@router.get("/my_details")
def get_all_dc_inventory(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    return db_inventory.get_dc_inventory(db, current_user)


# Read one Device Inventory
# @router.get('/{id}')
# def get_specif_dc_inventor(id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
#  return db_inventory.get_specif_dc_inventory(db, id)


# Update one Device Inventory
@router.put("/update/")
def update_dc_inventory(
    id: int, request: DcInvUpdate, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)
):
    return db_inventory.update_dc_inventory(db, id, request, current_user)


# Delete one Device Inventory
@router.delete("/delete")
def delete_dc_inventory(id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    return db_inventory.delete_dc_inventory(db, id, current_user)
