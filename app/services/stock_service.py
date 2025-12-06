from app.extensions import db
from app.models import Rollo, Subcodigo, Producto, AuditLog
import random
import string

class StockService:
    
    @staticmethod
    def importar_stock(producto_id, cantidad, usuario_responsable, pais_destino):
        """
        Genera nuevos rollos y sus subcódigos.
        """
        producto = Producto.query.get(producto_id)
        if not producto:
            return False, "Producto no encontrado"

        nuevos_rollos = []

        # 1. LOGICA DE CÓDIGO PADRE
        # Determinamos las siglas (AT, ATN, ATC)
        siglas = "AT"
        if "Premium" in producto.linea: siglas = "ATP"
        elif "Nanocarbon" in producto.linea: siglas = "ATN"
        elif "Nanoceramic" in producto.linea: siglas = "ATC"

        # Prefijo base para buscar correlativos (Ej: PY-ATC05)
        prefijo_busqueda = f"{pais_destino}-{siglas}{producto.variedad}"

        # Buscamos cuántos existen con ese prefijo EXACTO para saber el siguiente número
        # Usamos 'like' para contar solo los de ese país y esa variedad
        conteo_actual = Rollo.query.filter(Rollo.codigo_padre.like(f"{prefijo_busqueda}%")).count()
        
        for i in range(1, cantidad + 1):
            siguiente_numero = conteo_actual + i
            codigo_padre = f"{prefijo_busqueda}-{siguiente_numero:04d}"
            
            # Verificación de seguridad: Si por alguna razón ese código ya existe, saltamos al siguiente
            while Rollo.query.filter_by(codigo_padre=codigo_padre).first():
                siguiente_numero += 1
                codigo_padre = f"{prefijo_busqueda}-{siguiente_numero:04d}"

            # Crear el Rollo
            nuevo_rollo = Rollo(
                codigo_padre=codigo_padre,
                estado='EN_DEPOSITO',
                user_id=usuario_responsable.id,
                producto_id=producto.id
            )
            db.session.add(nuevo_rollo)
            db.session.flush() # ID necesario para los hijos

            # 2. LOGICA DE SUBCÓDIGOS (HIJOS)
            for _ in range(15):
                intentos = 0
                while True:
                    # Generar PIN de 3 dígitos
                    pin = ''.join(random.choices(string.digits, k=3))
                    codigo_hijo = f"{codigo_padre}-{pin}"
                    
                    # Verificar que NO exista en la base de datos globalmente
                    # (Aunque es raro que se repita, es posible)
                    if not Subcodigo.query.filter_by(codigo_hijo=codigo_hijo).first():
                        break # Es único, salimos del while
                    
                    intentos += 1
                    if intentos > 100:
                        # Si tras 100 intentos no encuentra uno libre (imposible matemáticamente con 3 dígitos si solo hay 15),
                        # lanzamos error para evitar bucle infinito.
                        return False, "Error de colisión de códigos. Intente de nuevo."

                sub = Subcodigo(
                    codigo_hijo=codigo_hijo,
                    pin_seguridad=pin,
                    estado='INACTIVO',
                    rollo_id=nuevo_rollo.id
                )
                db.session.add(sub)
            
            nuevos_rollos.append(codigo_padre)

        # Auditoría
        log = AuditLog(
            user_id=usuario_responsable.id,
            accion='IMPORTAR_STOCK',
            detalle=f"Importados {cantidad} rollos de {producto.nombre} para {pais_destino}"
        )
        db.session.add(log)
        
        try:
            db.session.commit()
            return True, f"Se generaron {cantidad} rollos exitosamente. ({nuevos_rollos[0]} ... {nuevos_rollos[-1]})"
        except Exception as e:
            db.session.rollback()
            return False, str(e)