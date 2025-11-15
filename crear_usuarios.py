import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from authentication.models import User

usuarios = [
    {'username': 'usuario1', 'email': 'usuario1@example.com', 'password': 'password123'},
    {'username': 'usuario2', 'email': 'usuario2@example.com', 'password': 'password123'},
    {'username': 'usuario3', 'email': 'usuario3@example.com', 'password': 'password123'},
]

for u in usuarios:
    if not User.objects.filter(email=u['email']).exists():
        user = User.objects.create_user(
            username=u['username'],
            email=u['email'],
            password=u['password']
        )
        print(f"Usuario creado: {u['username']} ({u['email']})")
    else:
        print(f"El usuario {u['email']} ya existe.")
