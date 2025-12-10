from app.extensions import db
from app.models import Rollo, Subcodigo, Producto, AuditLog
import random
import string
from datetime import datetime

class StockService:
    
    @staticmethod
    def importar_stock(producto_id, cantidad, usuario_responsable, pais_destino):
        producto = Producto.query.get(producto_id)
        if not producto:
            return False, "Producto no encontrado"

        nuevos_rollos = []
        
        # Generar ID de Lote (Ej: IMP-20231025-1430)
        # Esto permite filtrar "La importación que hicimos el martes a las 14:30"
        batch_id = f"IMP-{datetime.now().strftime('%Y%m%d-%H%M')}"

        # Lógica de Siglas
        siglas = "AT"
        if "Premium" in producto.linea: siglas = "ATP"
        elif "Nanocarbon" in producto.linea: siglas = "ATN"
        elif "Nanoceramic" in producto.linea: siglas = "ATC"
        else: siglas = producto.linea[:3].upper() # Fallback para líneas nuevas

        prefijo_busqueda = f"{pais_destino}-{siglas}{producto.variedad}"
        conteo_actual = Rollo.query.filter(Rollo.codigo_padre.like(f"{prefijo_busqueda}%")).count()
        
        for i in range(1, cantidad + 1):
            siguiente_numero = conteo_actual + i
            codigo_padre = f"{prefijo_busqueda}-{siguiente_numero:04d}"
            
            while Rollo.query.filter_by(codigo_padre=codigo_padre).first():
                siguiente_numero += 1
                codigo_padre = f"{prefijo_busqueda}-{siguiente_numero:04d}"

            nuevo_rollo = Rollo(
                codigo_padre=codigo_padre,
                estado='EN_DEPOSITO',
                user_id=usuario_responsable.id,
                producto_id=producto.id,
                lote=batch_id # <--- Guardamos el lote
            )
            db.session.add(nuevo_rollo)
            db.session.flush()

            for _ in range(15):
                while True:
                    pin = ''.join(random.choices(string.digits, k=3))
                    codigo_hijo = f"{codigo_padre}-{pin}"
                    if not Subcodigo.query.filter_by(codigo_hijo=codigo_hijo).first():
                        break 
                
                sub = Subcodigo(
                    codigo_hijo=codigo_hijo,
                    pin_seguridad=pin,
                    estado='INACTIVO',
                    rollo_id=nuevo_rollo.id
                )
                db.session.add(sub)
            
            nuevos_rollos.append(codigo_padre)

        log = AuditLog(
            user_id=usuario_responsable.id,
            accion='IMPORTAR_STOCK',
            detalle=f"Lote {batch_id}: {cantidad} rollos de {producto.nombre} ({pais_destino})"
        )
        db.session.add(log)
        
        try:
            db.session.commit()
            return True, f"✅ Lote {batch_id} generado: {len(nuevos_rollos)} rollos."
        except Exception as e:
            db.session.rollback()
            return False, str(e)