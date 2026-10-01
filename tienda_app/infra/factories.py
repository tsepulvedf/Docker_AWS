import os

from ..domain.interfaces import ProcesadorPago
from .gateways import BancoNacionalProcesador


class MockPaymentProcessor(ProcesadorPago):
    

    def pagar(self, monto) -> bool:
        print(f"[DEBUG] Mock Payment: Procesando pago de ${monto} sin cargo real.", flush=True)
        return True


class PaymentFactory:
    @staticmethod
    def get_processor() -> ProcesadorPago:
        
        provider = os.getenv("PAYMENT_PROVIDER", "BANCO").strip().upper()

        if provider == "MOCK":
            return MockPaymentProcessor()

        
        return BancoNacionalProcesador()
