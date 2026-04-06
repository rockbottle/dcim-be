from sqlalchemy.orm import Session
#from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import func
from fastapi import HTTPException, status
from db.models import DcInventory, DcPurchase

def calculate_company_totals(db: Session, current_user: dict) -> dict:
    """
    Calculate the total power, rack space, network ports, and SAN ports for all inventory items of a company.

    Args:
        db (Session): SQLAlchemy session for database interaction.
        current_user (dict): Dictionary containing current user's details, including company_id.

    Returns:
        dict: A dictionary containing total power, rack space, network ports, and SAN ports.

    Raises:
        HTTPException: If no inventory is found for the company.
    """
    # Extract company_id as a scalar value
    company_id = current_user.get("company_id")

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company ID is missing from the current user details."
        )

    # Query to calculate totals
    totals = db.query(
        func.sum(DcInventory.device_power).label("total_power"),
        func.sum(DcInventory.rack_uspace).label("total_uspace"),
        func.sum(DcInventory.device_nports).label("total_nports"),
        func.sum(DcInventory.device_sports).label("total_sports")
    ).filter(DcInventory.company_id == company_id).first()

    return {
        "total_power": totals.total_power if totals.total_power and totals.total_power > 0 else 0,
        "total_uspace": totals.total_uspace if totals.total_uspace and totals.total_uspace > 0 else 0,
        "total_nports": totals.total_nports if totals.total_nports and totals.total_nports > 0 else 0,
        "total_sports": totals.total_sports if totals.total_sports and totals.total_sports > 0 else 0,
    }

def calculate_available_resources(db: Session, current_user: dict) -> dict:
    company_id = current_user.get("company_id")
    
    try:
        # Fetch the purchased resources for the company
        purchase = db.query(
            DcPurchase.dcpower,
            DcPurchase.uspace,
            DcPurchase.nport,
            DcPurchase.sport
        ).filter(DcPurchase.company_id == company_id).first()
        
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No purchase data found for company with ID {company_id}."
            )

        # Fetch the current usage for the company
        usage = db.query(
            func.sum(DcInventory.device_power).label("total_power"),
            func.sum(DcInventory.rack_uspace).label("total_uspace"),
            func.sum(DcInventory.device_nports).label("total_nports"),
            func.sum(DcInventory.device_sports).label("total_sports")
        ).filter(DcInventory.company_id == company_id).one()

        # Calculate the available resources
        available_resources = {
            "available_power": max((purchase.dcpower or 0) - (usage.total_power or 0), 0),
            "available_uspace": max((purchase.uspace or 0) - (usage.total_uspace or 0), 0),
            "available_nports": max((purchase.nport or 0) - (usage.total_nports or 0), 0),
            "available_sports": max((purchase.sport or 0) - (usage.total_sports or 0), 0),
        }

        return available_resources

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calculating resources: {str(e)}"
        )