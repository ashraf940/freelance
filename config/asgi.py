import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# ✅ Pehle sirf yeh call karo — yeh Django apps load karta hai
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# ✅ Baad mein yeh sab import karo
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})