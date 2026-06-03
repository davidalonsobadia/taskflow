from sqlalchemy.orm import Session
from app.domains.api_clients.models import APIClient

def load_active_hashed_keys(db: Session) -> set[str]:
    return {
        client.api_key for client in db.query(APIClient).filter(APIClient.active == True).all()
    }
