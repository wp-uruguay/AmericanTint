# Este archivo hace que todos los modelos sean visibles entre sí
# y para el sistema de migraciones
from app.models.user import User
from app.models.product import Producto
from app.models.stock import Rollo
from app.models.warranty import Subcodigo
# Asegúrate de que transaction.py tenga la clase AuditLog dentro
from app.models.transaction import AuditLog
# Este archivo hace que todos los modelos sean visibles entre sí
from app.models.user import User
from app.models.product import Producto
from app.models.stock import Rollo
from app.models.warranty import Subcodigo
from app.models.transaction import AuditLog
# --- NUEVO: SOPORTE ---
from app.models.support import Ticket, TicketMessage