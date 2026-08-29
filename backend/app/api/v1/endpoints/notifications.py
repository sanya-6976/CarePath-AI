from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connections import get_db
from app.services import notification_service
from app.core.security import get_current_user, verify_resource_ownership
from database.models import Notification
from database.crud.utils import safe_uuid

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
def get_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return notification_service.get_notifications(db, current_user.user_id)

@router.put("/{notification_id}/read")
def mark_read(notification_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    notification = db.query(Notification).filter(Notification.notification_id == safe_uuid(notification_id)).first()
    if not notification:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    verify_resource_ownership(current_user, notification.user_id)
    notif = notification_service.mark_notification_read(db, notification_id)
    db.commit()
    return notif
