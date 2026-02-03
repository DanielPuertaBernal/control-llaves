"""
Servicios técnicos de infraestructura
Adaptadores para componentes técnicos: MongoDB, NFC
"""
from .mongo_client import MongoClientProvider
from .nfc_service import NFCService

__all__ = ['MongoClientProvider', 'NFCService']
