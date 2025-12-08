from django.db import models

class AppVersion(models.Model):
    version_code = models.IntegerField(unique=True, help_text="Código da versão (inteiro) para comparação")
    version_name = models.CharField(max_length=50, help_text="Nome da versão (ex: 1.0.0)")
    apk_file = models.FileField(upload_to='apks/', help_text="Arquivo APK para download")
    is_mandatory = models.BooleanField(default=False, help_text="Se a atualização é obrigatória")
    release_notes = models.TextField(blank=True, help_text="Notas da versão")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_code']
        verbose_name = "Versão do App"
        verbose_name_plural = "Versões do App"

    def __str__(self):
        return f"{self.version_name} ({self.version_code})"
