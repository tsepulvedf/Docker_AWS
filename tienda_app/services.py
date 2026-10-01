from django.db import transaction
from django.shortcuts import get_object_or_404

from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos
from .models import Inventario, Libro


class PagoRechazadoError(Exception):
    """Error de negocio: la pasarela rechazó la transacción."""


class CompraService:
    """SERVICE LAYER: orquesta dominio, infraestructura y base de datos."""

    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago  # inyectado por la Factory (DIP)

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def ejecutar_compra(self, libro_id, cantidad=1, direccion="", usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = get_object_or_404(Inventario, libro=libro)

        if inv.cantidad < cantidad:
            raise ValueError("No hay suficiente stock para completar la compra.")

        with transaction.atomic():
            orden = (
                OrdenBuilder()
                .con_usuario(usuario)
                .con_libro(libro)
                .con_cantidad(cantidad)
                .para_envio(direccion)
                .build()
            )

            if not self.procesador_pago.pagar(orden.total):
                raise PagoRechazadoError("La transacción fue rechazada por el banco.")

            inv.cantidad -= cantidad
            inv.save(update_fields=["cantidad"])

        return orden


class CompraRapidaService:
    """
    SERVICE LAYER (Tutorial 01 - Compra Rápida).
    Actualizado en Tutorial 02: ahora construye la orden con OrdenBuilder
    y recibe el procesador desde PaymentFactory.
    """

    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago

    def obtener_detalle(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def procesar(self, libro_id, usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = get_object_or_404(Inventario, libro=libro)

        if inv.cantidad <= 0:
            raise ValueError("No hay existencias.")

        with transaction.atomic():
            orden = (
                OrdenBuilder()
                .con_usuario(usuario)
                .con_libro(libro)
                .con_cantidad(1)
                .build()
            )

            if not self.procesador_pago.pagar(orden.total):
                raise PagoRechazadoError("La transacción fue rechazada por el banco.")

            inv.cantidad -= 1
            inv.save(update_fields=["cantidad"])

        return orden.total