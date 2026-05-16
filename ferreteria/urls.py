from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView
from django.urls import include, path
from django.urls import reverse_lazy

from inventario.forms import NuevaContrasenaForm, RecuperarContrasenaForm

urlpatterns = [
    path(
        'admin/password-reset/',
        PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/admin_password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            form_class=RecuperarContrasenaForm,
            success_url=reverse_lazy('admin_password_reset_done')
        ),
        name='admin_password_reset'
    ),
    path(
        'admin/password-reset/enviado/',
        PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='admin_password_reset_done'
    ),
    path(
        'admin/password-reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            form_class=NuevaContrasenaForm,
            success_url=reverse_lazy('admin_password_reset_complete')
        ),
        name='admin_password_reset_confirm'
    ),
    path(
        'admin/password-reset/completo/',
        PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='admin_password_reset_complete'
    ),
    path('admin/', admin.site.urls),
    path('', include('inventario.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
