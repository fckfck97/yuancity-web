"""
Comando de Django para reorganizar archivos de medios existentes.
Uso: python manage.py reorganize_media
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.product.models import ProductImage, ProductVideo
from apps.user.models import UserProfile


class Command(BaseCommand):
    help = 'Reorganiza archivos de medios a la nueva estructura de carpetas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la reorganización sin mover archivos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY-RUN: No se moverán archivos\n'))
        
        # Reorganizar avatares de usuarios
        self.stdout.write(self.style.SUCCESS('\n=== Reorganizando avatares de usuarios ==='))
        self._reorganize_user_avatars(dry_run)
        
        # Reorganizar imágenes de productos
        self.stdout.write(self.style.SUCCESS('\n=== Reorganizando imágenes de productos ==='))
        self._reorganize_product_images(dry_run)
        
        # Reorganizar videos de productos
        self.stdout.write(self.style.SUCCESS('\n=== Reorganizando videos de productos ==='))
        self._reorganize_product_videos(dry_run)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Reorganización completada'))

    def _reorganize_user_avatars(self, dry_run):
        """Reorganiza avatares y covers de usuarios"""
        profiles = UserProfile.objects.exclude(avatar='').exclude(avatar__isnull=True)
        total = profiles.count()
        
        for idx, profile in enumerate(profiles, 1):
            try:
                old_path = profile.avatar.path
                if not os.path.exists(old_path):
                    continue
                
                # Nueva ruta
                ext = os.path.splitext(old_path)[1]
                new_relative = f"users/{profile.user.id}/avatar/avatar{ext}"
                new_path = os.path.join(settings.MEDIA_ROOT, new_relative)
                
                if old_path == new_path:
                    continue
                
                self.stdout.write(f'[{idx}/{total}] Moviendo avatar de {profile.user.email}')
                
                if not dry_run:
                    # Crear directorio si no existe
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    
                    # Mover archivo
                    shutil.move(old_path, new_path)
                    
                    # Actualizar DB
                    profile.avatar.name = new_relative
                    profile.save(update_fields=['avatar'])
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error con {profile.user.email}: {e}'))
        
        # Igual para cover_image
        profiles = UserProfile.objects.exclude(cover_image='').exclude(cover_image__isnull=True)
        for profile in profiles:
            try:
                old_path = profile.cover_image.path
                if not os.path.exists(old_path):
                    continue
                
                ext = os.path.splitext(old_path)[1]
                new_relative = f"users/{profile.user.id}/cover/cover{ext}"
                new_path = os.path.join(settings.MEDIA_ROOT, new_relative)
                
                if old_path == new_path:
                    continue
                
                if not dry_run:
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    shutil.move(old_path, new_path)
                    profile.cover_image.name = new_relative
                    profile.save(update_fields=['cover_image'])
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error con cover de {profile.user.email}: {e}'))

    def _reorganize_product_images(self, dry_run):
        """Reorganiza imágenes de productos"""
        images = ProductImage.objects.all()
        total = images.count()
        
        for idx, img in enumerate(images, 1):
            try:
                old_path = img.image.path
                if not os.path.exists(old_path):
                    continue
                
                vendor_id = img.product.vendor.id
                product_id = img.product.id
                ext = os.path.splitext(old_path)[1]
                filename = f"img_{img.id.hex[:8]}{ext}"
                
                new_relative = f"users/{vendor_id}/products/{product_id}/images/{filename}"
                new_path = os.path.join(settings.MEDIA_ROOT, new_relative)
                
                if old_path == new_path:
                    continue
                
                self.stdout.write(f'[{idx}/{total}] Moviendo imagen de producto {img.product.name}')
                
                if not dry_run:
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    shutil.move(old_path, new_path)
                    img.image.name = new_relative
                    img.save(update_fields=['image'])
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error con imagen {img.id}: {e}'))

    def _reorganize_product_videos(self, dry_run):
        """Reorganiza videos de productos"""
        videos = ProductVideo.objects.all()
        total = videos.count()
        
        for idx, vid in enumerate(videos, 1):
            try:
                old_path = vid.video.path
                if not os.path.exists(old_path):
                    continue
                
                vendor_id = vid.product.vendor.id
                product_id = vid.product.id
                ext = os.path.splitext(old_path)[1]
                filename = f"vid_{vid.id.hex[:8]}{ext}"
                
                new_relative = f"users/{vendor_id}/products/{product_id}/videos/{filename}"
                new_path = os.path.join(settings.MEDIA_ROOT, new_relative)
                
                if old_path == new_path:
                    continue
                
                self.stdout.write(f'[{idx}/{total}] Moviendo video de producto {vid.product.name}')
                
                if not dry_run:
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    shutil.move(old_path, new_path)
                    vid.video.name = new_relative
                    vid.save(update_fields=['video'])
                    
                # Reorganizar thumbnail si existe
                if vid.thumbnail:
                    old_thumb = vid.thumbnail.path
                    if os.path.exists(old_thumb):
                        ext_thumb = os.path.splitext(old_thumb)[1]
                        thumb_filename = f"thumb_{vid.id.hex[:8]}{ext_thumb}"
                        new_thumb_relative = f"users/{vendor_id}/products/{product_id}/thumbnails/{thumb_filename}"
                        new_thumb_path = os.path.join(settings.MEDIA_ROOT, new_thumb_relative)
                        
                        if not dry_run:
                            os.makedirs(os.path.dirname(new_thumb_path), exist_ok=True)
                            shutil.move(old_thumb, new_thumb_path)
                            vid.thumbnail.name = new_thumb_relative
                            vid.save(update_fields=['thumbnail'])
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error con video {vid.id}: {e}'))
