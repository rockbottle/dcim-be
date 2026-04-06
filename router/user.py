from typing import List
from schemas import UserBase, UserUpdate
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_user
from auth.oauth2 import get_current_user


router = APIRouter(
  prefix='/user',
  tags=['USER CURD Operations']
)

# Create user
@router.post('/create')
def create_user(request: UserBase, db: Session = Depends(get_db)):
  return db_user.create_dcuser(db, request)

# Read all users
#@router.get('/')#, response_model=List[UserDisplay])
#def get_all_users(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
#  return db_user.get_all_dcusers(db)

##@router.get('/')
##def get_all_users(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
##  return db_user.get_all_dcusers(db, current_user)

@router.get('/my_details')
def get_all_users(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
  return db_user.get_my_details(db, current_user)

## Read one user
##@router.get('/{id}')
##def get_specific_user(id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
##  return db_user.get_dcuser_by_id(db, id, current_user)

# Read one user with username
#@router.get('/by_username/{username}')
#def get_specific_user(username: str, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
#  return db_user.get_dcuser_by_username(db, username, current_user)

# Update user
@router.put('/update')
def update_user(request: UserUpdate, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
  return db_user.update_dcuser(db, request, current_user)

# Delete user
@router.delete('/delete')
def delete_user(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
  return db_user.delete_dcuser(db, current_user)

# Get all users of a company
@router.get('/my_team')
def get_users_by_company(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
  return db_user.get_dcuser_by_company_name(db, current_user)