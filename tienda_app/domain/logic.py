from decimal import Decimal, ROUND_HALF_UP


class CalculadorImpuestos:
    """S: Responsabilidad única - Solo calcula impuestos.
    O: Abierto a extensión - Podríamos heredar para diferentes países."""

    IVA = Decimal("0.19")
    CENTAVOS = Decimal("0.01")

    @classmethod
    def obtener_total_con_iva(cls, precio_base) -> Decimal:
        base = Decimal(str(precio_base))            
        total = base * (Decimal("1") + cls.IVA)
        return total.quantize(cls.CENTAVOS, rounding=ROUND_HALF_UP)