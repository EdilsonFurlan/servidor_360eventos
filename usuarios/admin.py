from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    # Campos que aparecerão na lista de usuários
    list_display = ('email', 'nome', 'is_active', 'data_vencimento', 'is_staff')

    # Buscar por email ou nome
    search_fields = ('email', 'nome')

    # Filtros laterais
    list_filter = ('is_active', 'is_staff', 'data_vencimento')

    # Organização dos campos na edição do usuário
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'data_vencimento')}),
        ('Permissões', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Datas importantes', {'fields': ('last_login',)}),
    )

    # Ao criar usuário via admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)


admin.site.register(Usuario, UsuarioAdmin)
