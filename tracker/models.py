from django.db import models
from django.utils import timezone

class FuelType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    cost_per_unit = models.DecimalField(max_digits=5, decimal_places=2, help_text="Current cost per unit (e.g. per liter)")
    unit_name = models.CharField(max_length=20, default='Liters', help_text="Unit of measurement (e.g. Liters, Gallons, kWh)")
    efficiency = models.DecimalField(max_digits=6, decimal_places=2, default=15.0, help_text="Average Distance per Unit (e.g. km/L)")

    def __str__(self):
        return self.name

class Settings(models.Model):
    """
    Singleton model to store application defaults.
    """
    default_fuel_type = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.CharField(max_length=5, default='$', help_text="Currency symbol (e.g. $, €, £)")
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super(Settings, self).save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Application Settings"

class Journey(models.Model):
    date = models.DateField(default=timezone.now)
    distance = models.DecimalField(max_digits=10, decimal_places=2, help_text="Distance in kilometers")
    reason = models.CharField(max_length=255)
    
    fuel_type_ref = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fuel Type")
    # Snapshot of the name for display if FuelType is deleted
    fuel_type = models.CharField(max_length=50, verbose_name="Fuel Type Name") 
    
    cost_per_liter = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cost per Unit")
    fuel_quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total units (e.g. liters)")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.reason} ({self.distance} km)"
