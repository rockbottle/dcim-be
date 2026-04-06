import os
from fastapi import APIRouter, Depends
# Import your actual OAuth2 scheme or dependency here
from auth.oauth2 import get_current_user

router = APIRouter(
    prefix='/identity',
    tags=['identity']
)

@router.get("/identityz")
def identity_check(current_user: dict = Depends(get_current_user)):
    """
    Identity check: Protected by Password/JWT.
    Only authorized users can see the POD & Node metadata.
    """
    pod_name = os.getenv("MY_POD_NAME", "unknown-pod")
    node_name = os.getenv("MY_NODE_NAME", "unknown-node")
    
    return {
        "status": "ok", 
        "user_id": current_user.get("user_id"), # Optional: Show who is asking
        "pod_name": pod_name,
        "node_hostname": node_name
    }