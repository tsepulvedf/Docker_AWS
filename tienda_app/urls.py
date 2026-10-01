from django.urls import path

from .api.views import CatalogoAPIView, CompraAPIView
from .views import CompraView, InventarioView

urlpatterns = [
    path('', InventarioView.as_view(), name='inventario'),
    path('compra/<int:libro_id>/', CompraView.as_view(), name='finalizar_compra'),
    path('api/v1/libros/', CatalogoAPIView.as_view(), name='api_libros'),
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
]