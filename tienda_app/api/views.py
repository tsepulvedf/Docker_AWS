from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tienda_app.infra.factories import PaymentFactory
from tienda_app.models import Libro
from tienda_app.services import CompraService, PagoRechazadoError

from .serializers import LibroSerializer, OrdenInputSerializer


class CatalogoAPIView(APIView):
    """GET /api/v1/libros/ -> catálogo con el stock actual."""

    def get(self, request):
        libros = Libro.objects.select_related('inventario').all()
        return Response(LibroSerializer(libros, many=True).data)


class CompraAPIView(APIView):
    """
    Endpoint para procesar compras vía JSON.
    POST /api/v1/comprar/
    Payload: {"libro_id": 1, "direccion_envio": "Calle 123", "cantidad": 1}
    """

    def get(self, request):
        # Sin este GET, abrir la URL en el navegador muestra "405 Method Not Allowed"
        return Response({
            "endpoint": "POST /api/v1/comprar/",
            "payload": {"libro_id": 1, "direccion_envio": "Calle 123", "cantidad": 1},
            "catalogo": LibroSerializer(
                Libro.objects.select_related('inventario').all(), many=True
            ).data,
        })

    def post(self, request):
        # 1. Validación de datos de entrada (Adapter)
        serializer = OrdenInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data

        try:
            # 2. Inyección de dependencias (Factory)
            gateway = PaymentFactory.get_processor()

            # 3. Ejecución de la lógica de negocio (Service Layer)
            #    El servicio NO cambia: solo cambia quién lo llama.
            servicio = CompraService(procesador_pago=gateway)
            orden = servicio.ejecutar_compra(
                libro_id=datos['libro_id'],
                cantidad=datos['cantidad'],
                direccion=datos['direccion_envio'],
                usuario=request.user,
            )

            return Response({
                "estado": "exito",
                "orden_id": orden.id,
                "total": str(orden.total),
                "mensaje": f"Orden {orden.id} creada. Total: ${orden.total}",
            }, status=status.HTTP_201_CREATED)

        except Http404:
            # get_object_or_404 lanza Http404; sin este bloque terminaba en 500
            return Response({"error": "El libro solicitado no existe."},
                            status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            # Errores de negocio (ej: sin stock)
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except PagoRechazadoError as e:
            # La pasarela rechazó el cobro: 402 es el código semántico correcto
            return Response({"error": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)

