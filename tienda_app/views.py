from django.shortcuts import render
from django.views import View

from .models import Libro
from .infra.factories import PaymentFactory
from .services import CompraService, PagoRechazadoError


class CompraView(View):
    """CBV: actúa como "portero": recibe la petición y delega al servicio."""

    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        return render(request, self.template_name, servicio.obtener_detalle_producto(libro_id))

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            orden = servicio.ejecutar_compra(
                libro_id,
                cantidad=1,
                direccion=request.POST.get("direccion", ""),
                usuario=request.user,
            )
            return render(request, self.template_name, {
                'mensaje_exito': f"¡Gracias por su compra! Orden #{orden.id} - Total: ${orden.total}",
                'total': orden.total,
            })
        except (ValueError, PagoRechazadoError) as e:
            contexto = servicio.obtener_detalle_producto(libro_id)
            contexto['error'] = str(e)
            return render(request, self.template_name, contexto, status=400)



class CompraRapidaView(View):
    

    template_name = 'tienda_app/compra_rapida.html'

    def _servicio(self):
        return CompraRapidaService(procesador_pago=PaymentFactory.get_processor())

    def get(self, request, libro_id):
        return render(request, self.template_name, self._servicio().obtener_detalle(libro_id))

    def post(self, request, libro_id):
        servicio = self._servicio()
        try:
            total = servicio.procesar(libro_id, usuario=request.user)
            return render(request, self.template_name, {
                'mensaje_exito': f"Compra exitosa. Total: ${total}",
                'total': total,
            })
        except (ValueError, PagoRechazadoError) as e:
            contexto = servicio.obtener_detalle(libro_id)
            contexto['error'] = str(e)
            return render(request, self.template_name, contexto, status=400)

class InventarioView(View):
    template_name = 'tienda_app/inventario.html'

    def get(self, request):
        libros = Libro.objects.select_related('inventario').order_by('id')
        return render(request, self.template_name, {'libros': libros})
