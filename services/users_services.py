from ldap.client import LDAPClient
from ldap.models import EquipoLDAP
from config.settings import settings
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(__name__)

class UserService:
    def __init__(self):
        self.ldap_client = LDAPClient()
        