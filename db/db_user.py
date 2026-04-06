from sqlalchemy.orm.session import Session
from db.hash import Hash
from db.models import DcUser, DcCompany, DcPurchase
from schemas import UserBase, UserUpdate
from fastapi import HTTPException, status

def create_dcuser(db: Session, request: UserBase):
    company = db.query(DcCompany).filter(DcCompany.name == request.company_name).first()

    if not company:
        company = DcCompany(name=request.company_name)
        db.add(company)
        db.commit()
        db.refresh(company)

    new_user = DcUser(
        username=request.username,
        email=request.email,
        password=Hash.bcrypt(request.password),
        company_id=company.id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "company_name": company.name
    }

def get_my_details(db: Session, current_user: dict):
    company_id = current_user.get("company_id")
    user_id = current_user.get("user_id")

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user context"
        )

    users = (
        db.query(DcUser.id, DcUser.username, DcUser.email, DcCompany.name.label("company_name"))
        .join(DcCompany, DcUser.company_id == DcCompany.id)
        .filter(DcUser.company_id == company_id, DcUser.id == user_id)
        .all()
    )

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Users found for your company"
        )

    return [
        {
            "username": user.username,
            "email": user.email,
            "company_name": user.company_name
        } for user in users
    ]

def get_dcuser_by_username_auth(db: Session, username: str):
    user = (
        db.query(DcUser.id, DcUser.username, DcUser.email, DcUser.company_id, DcCompany.name.label("company_name"))
        .join(DcCompany, DcUser.company_id == DcCompany.id)
        .filter(DcUser.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with username {username} not found'
        )

    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "company_id": user.company_id,
        "company_name": user.company_name
    }

def update_dcuser(db: Session, request: UserUpdate, current_user: dict):
    company_id = current_user.get("company_id")
    user_id = current_user.get("user_id")

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user context"
        )

    user = (
        db.query(DcUser)
        .join(DcCompany, DcUser.company_id == DcCompany.id)
        .filter(DcUser.company_id == company_id, DcUser.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found'
        )

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, Hash.bcrypt(value) if key == "password" else value)

    db.commit()
    return {"message": "User details updated successfully"}

def delete_dcuser(db: Session, current_user: dict):
    company_id = current_user.get("company_id")
    user_id = current_user.get("user_id")

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user context"
        )

    usage_record = (
        db.query(DcPurchase)
        .filter(DcPurchase.company_id == company_id, DcPurchase.created_by == user_id)
        .first()
    )

    if usage_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete user as usage record exists for the company."
        )

    user = (
        db.query(DcUser)
        .join(DcCompany, DcUser.company_id == DcCompany.id)
        .filter(DcUser.company_id == company_id, DcUser.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found'
        )

    db.delete(user)
    db.commit()
    return 'User got deleted'

def get_dcuser_by_company_name(db: Session, current_user: dict):
    company_id = current_user.get("company_id")

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user context"
        )

    users = (
        db.query(DcUser.username, DcUser.email, DcCompany.name.label("company_name"))
        .join(DcCompany, DcUser.company_id == DcCompany.id)
        .filter(DcCompany.id == company_id)
        .all()
    )

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No users found for company name {DcUser.company_name}'
        )

    return [
        {
            "username": user.username,
            "email": user.email,
            "company_name": user.company_name
        } for user in users
    ]