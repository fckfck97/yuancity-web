# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserAccount, UserProfile, UserFollow, ExpoPushToken, Notification
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

@admin.register(UserAccount)
class UserAccountAdmin(BaseUserAdmin, ModelAdmin):
  form = UserChangeForm
  add_form = UserCreationForm
  change_password_form = AdminPasswordChangeForm

  # Fields to be used in displaying the User model.
  fieldsets = (
    (None, {'fields': ('email', 'password')}),
    (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'phone_verified')}),
    (_('Permissions'), {
      'fields': (
        'is_active',
        'is_staff',
        'is_superuser',
        'groups',
        'user_permissions',
        'rol',
      ),
    }),

    (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
  )

  # Fields to be used when creating a user.
  add_fieldsets = (
    (None, {
      'classes': ('wide',),
      'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
    }),
  )

  list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'rol')
  list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups', 'rol')
  search_fields = ('email', 'first_name', 'last_name', 'rol')
  readonly_fields = ('created_at', 'updated_at')
  ordering = ('-created_at',)
  filter_horizontal = ('groups', 'user_permissions')


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
  list_display = ("username", "user", "location", "created_at")
  search_fields = ("username", "user__email", "user__first_name", "user__last_name")
  readonly_fields = ("created_at", "updated_at")


@admin.register(UserFollow)
class UserFollowAdmin(ModelAdmin):
  list_display = ("follower", "following", "created_at")
  search_fields = ("follower__email", "following__email")
  list_filter = ("created_at",)

@admin.register(ExpoPushToken)
class ExpoPushTokenAdmin(ModelAdmin):
  list_display = ('user', 'token', 'device_os', 'active', 'last_used')
  search_fields = ('user__email', 'token', 'device_os')
  list_filter = ('device_os', 'active')
  readonly_fields = ('last_used',)
  
  
@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
  list_display = ('title', 'body', 'created_at')
  search_fields = ('title', 'body')
  list_filter = ('created_at',)
  readonly_fields = ('created_at',)
  ordering = ('-created_at',)
  
  fieldsets = (
    (_('Notification Content'), {
      'fields': ('title', 'body'),
      'description': 'You can use emojis in both title and body fields. Example: 🎬 New Movie Available! 🍿'
    }),
    (_('Metadata'), {
      'fields': ('created_at',),
      'classes': ('collapse',)
    }),
  )
  
  def get_form(self, request, obj=None, **kwargs):
    form = super().get_form(request, obj, **kwargs)
    if 'title' in form.base_fields:
      form.base_fields['title'].widget.attrs.update({
        'placeholder': '🎬 Enter notification title with emojis...',
        'style': 'width: 100%;'
      })
    if 'body' in form.base_fields:
      form.base_fields['body'].widget.attrs.update({
        'placeholder': '📱 Enter notification message with emojis...\nExample: 🍿 New movies added to your favorites! Check them out now! ⭐',
        'rows': 4,
        'style': 'width: 100%;'
      })
    return form
