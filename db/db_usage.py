from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status
from db.models import DcCompany, DcPurchase, DcUser, DcInventory
from schemas import DcBase, DcUpdate

# Validator function
def check_dc_purchase(data: dict):
    """
    Validate DC purchase fields to ensure they are non-zero and positive.
    """
    for field in ['dcpower', 'uspace', 'nport', 'sport']:
        if data.get(field) is None or data[field] <= 0:
            raise ValueError(f"{field} must be greater than 0.")

# Create DC usage record
def create_dc_usage(db: Session, request: DcBase, current_user: dict):
    company_id = current_user.get("company_id")
    user_id = current_user.get("user_id")

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user context"
        )

    company = db.query(DcCompany).filter(DcCompany.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found"
        )

    user = db.query(DcUser).filter(DcUser.id == user_id, DcUser.company_id == company_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Users found for your company"
        )

    existing_purchase = db.query(DcPurchase).filter(DcPurchase.company_id == company.id).first()
    if existing_purchase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Usage record already exists for the company '{company_id}'."
        )

    try:
        check_dc_purchase(request.dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    new_usage = DcPurchase(
        dcpower=request.dcpower,
        uspace=request.uspace,
        nport=request.nport,
        sport=request.sport,
        company_id=company_id,
        created_by=user_id
    )
    db.add(new_usage)
    db.commit()
    db.refresh(new_usage)

    return {
        "id": new_usage.id,
        "dcpower": new_usage.dcpower,
        "uspace": new_usage.uspace,
        "nport": new_usage.nport,
        "sport": new_usage.sport
    }

# Update DC usage record
def update_dc_usage(db: Session, request: DcUpdate, current_user: dict):
    company_id = current_user.get("company_id")
    user_id = current_user.get("user_id")

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user context"
        )

    company = db.query(DcCompany).filter(DcCompany.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found"
        )

    user = db.query(DcUser).filter(DcUser.id == user_id, DcUser.company_id == company_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Users found for your company"
        )

    usage = db.query(DcPurchase).filter(DcPurchase.company_id == company_id).first()
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No usage record found for your company."
        )

    update_data = request.dict(exclude_unset=True)

    try:
        check_dc_purchase(update_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    for key, value in update_data.items():
        setattr(usage, key, value)

    db.commit()
    db.refresh(usage)
    return {
        "id": usage.id,
        "dcpower": usage.dcpower,
        "uspace": usage.uspace,
        "nport": usage.nport,
        "sport": usage.sport
    }

# Delete DC usage record
def delete_dc_usage(db: Session, current_user: dict):
    company_id = current_user.get("company_id")
    user_id = current_user.get("user_id")

    if not company_id or not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user context"
        )

    other_users = db.query(DcUser).filter(DcUser.company_id == company_id, DcUser.id != user_id).count()
    if other_users > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete usage record as other users exist in the same company."
        )

    inventory = db.query(DcInventory).filter(DcInventory.company_id == company_id).count()
    if inventory > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete usage record as inventory exists for the same company."
        )

    usage = db.query(DcPurchase).filter(DcPurchase.company_id == company_id).first()
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No usage record found for your company."
        )

    db.delete(usage)
    db.commit()
    return {"message": f"Usage record with ID {usage.id} has been deleted successfully."}

# Get DC usage record for the current user
def get_my_usage(db: Session, current_user: dict):
    company_id = current_user.get("company_id")
    user_id = current_user.get("user_id")

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user context"
        )

    user = db.query(DcUser).filter(DcUser.id == user_id, DcUser.company_id == company_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Users found for your company"
        )

    usage = db.query(DcPurchase).filter(DcPurchase.company_id == company_id).first()
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No usage record found for your company."
        )

    return {
        "id": usage.id,
        "dcpower": usage.dcpower,
        "uspace": usage.uspace,
        "nport": usage.nport,
        "sport": usage.sport
    }