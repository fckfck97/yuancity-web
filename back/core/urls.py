from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
urlpatterns = [
    path('authentication/', include('djoser.urls')),
    path('authentication/', include('djoser.urls.jwt')),
    path('authentication/', include('djoser.social.urls')),
    path('api/AI/', include('apps.AI.urls')),
    path('api/category/', include('apps.category.urls')),
    path('api/products/', include('apps.product.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payment/', include('apps.payment.urls')),
    path('api/coupons/', include('apps.coupons.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/promotions/', include('apps.promotions.urls')),
    path('api/wishlist/', include('apps.wishlist.urls')),
    path('api/', include('apps.count.urls')),
    path('api/', include('apps.user.urls')),
    path('admin/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls'),
         name="ck_editor_5_upload_file"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
