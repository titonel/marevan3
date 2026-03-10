from django.contrib import admin
from django.urls import path, include # <--- Importar o include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Incluir os URLs da nossa app 'core' na raiz do site
    path('', include('core.urls')), 
]