from django.db import models

class PageView(models.Model):
  ip_address = models.CharField(max_length=255)
  user_agent = models.TextField()  # Para almacenar el user agent del navegador
  timestamp = models.DateTimeField(auto_now_add=True)
  latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
  longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
  country = models.CharField(max_length=255,null=True, blank=True)
  city = models.CharField(max_length=255,null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f"{self.ip_address} - {self.timestamp}"
  
class NewsLetter(models.Model):
  email = models.EmailField()
  created_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.email