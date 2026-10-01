from django.core.management.base import BaseCommand

from tienda_app.models import Inventario, Libro

LIBROS = [
    ("Cien años de Soledad", "155.00", 10),
    ("Harry Potter y La Orden del Fénix", "132.00", 5),
    ("El Amor en los Tiempos del Cólera", "98.50", 3),
]


class Command(BaseCommand):
    help = "Carga libros e inventario de prueba (idempotente)."

    def handle(self, *args, **options):
        for titulo, precio, stock in LIBROS:
            libro, creado = Libro.objects.get_or_create(titulo=titulo, defaults={"precio": precio})
            Inventario.objects.update_or_create(libro=libro, defaults={"cantidad": stock})
            self.stdout.write(f"  {'creado' if creado else 'actualizado'}: [{libro.id}] {titulo} (stock {stock})")
        self.stdout.write(self.style.SUCCESS("Datos de prueba listos."))