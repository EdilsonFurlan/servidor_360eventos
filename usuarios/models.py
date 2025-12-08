from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class GerenciadorDeUsuario(BaseUserManager):
    def create_user(self, email, nome, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail deve ser fornecido')
        
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, nome, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=150)

    # Campo de controle do Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Campo opcional que você criou
    data_vencimento = models.DateField(null=True, blank=True)

    objects = GerenciadorDeUsuario()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email
