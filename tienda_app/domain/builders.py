from decimal import Decimal, ROUND_HALF_UP

from ..models import Orden
from .logic import CalculadorImpuestos


class OrdenBuilder:
    CENTAVOS = Decimal("0.01")

    def __init__(self):
        self.reset()

    def reset(self):
        self._usuario = None
        self._libro = None
        self._cantidad = 1
        self._direccion = ""

    def con_usuario(self, usuario):
        
        if usuario is None or not getattr(usuario, "is_authenticated", False):
            self._usuario = None
        else:
            self._usuario = usuario
        return self  

    def con_libro(self, libro):
        self._libro = libro
        return self

    def con_cantidad(self, cantidad):
        self._cantidad = int(cantidad)
        return self

    def para_envio(self, direccion):
        self._direccion = (direccion or "").strip()
        return self

    def build(self) -> Orden:
        try:
            #Validaciones centralizadas: la vista ya no puede crear una orden inválida
            if self._libro is None:
                raise ValueError("Datos insuficientes para crear la orden: falta el libro.")
            if self._cantidad < 1:
                raise ValueError("La cantidad debe ser al menos 1.")

            #Encapsulamos la lógica de cálculo (todo en Decimal)
            precio_unitario = CalculadorImpuestos.obtener_total_con_iva(self._libro.precio)
            total = (precio_unitario * self._cantidad).quantize(
                self.CENTAVOS, rounding=ROUND_HALF_UP
            )

            return Orden.objects.create(
                usuario=self._usuario,
                libro=self._libro,
                cantidad=self._cantidad,
                total=total,
                direccion_envio=self._direccion,
            )
        finally:
            self.reset()  