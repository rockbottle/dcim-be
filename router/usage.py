from schemas import DcBase, DcUpdate, UserBase
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_usage, db_calculator
from auth.oauth2 import get_current_user

router = APIRouter(
  prefix='/usage',
  tags=['USAGE CURD Operations']
)

@router.post('/create')
def create_dc_usage(request: DcBase, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    """
    Create a DC usage record for a specific company.
    """
    return db_usage.create_dc_usage(db, request, current_user)

# Read all DC Usage
@router.get('/my_details')
def get_my_dc_usage(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    """
    Retrieve all DC usage records.
    """
    return db_usage.get_my_usage(db, current_user)

@router.get('/my_current_usage')
def get_my_current_dc_usage(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    """
    Retrieve all DC usage records.
    """
    return db_calculator.calculate_company_totals(db, current_user)

@router.get('/my_availble_usage')
def get_my_available_dc_usage(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    """
    Retrieve all DC usage records.
    """
    return db_calculator.calculate_available_resources(db, current_user)


# Get DC usage of a specific company name
#@router.get('/by_name/')
#def get_all_dc_usage(company_name: str, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
#    """
#    Retrieve all DC usage records.
#    """
#    return db_usage.get_specif_dc_usage(db, company_name)

# Update one DC Usage
@router.put('/update')
def update_dc_usage(request: DcUpdate, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    """
    Update a DC usage record by its ID.
    """
    return db_usage.update_dc_usage(db, request, current_user)

# Delete one DC Usage
@router.delete('/delete')
def delete_dc_usage(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    """
    Delete a specific DC usage record by its ID.
    """
    return db_usage.delete_dc_usage(db, current_user)