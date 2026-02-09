from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class FuelType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fuel_types', null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name=_("Fuel Name"))
    cost_per_unit = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("Current cost per unit (e.g. per liter)"), verbose_name=_("Cost per Unit"))
    unit_name = models.CharField(max_length=20, default='Liters', help_text=_("Unit of measurement (e.g. Liters, Gallons, kWh)"), verbose_name=_("Unit Name"))
    efficiency = models.DecimalField(max_digits=6, decimal_places=2, default=15.0, help_text=_("Average Distance per Unit (e.g. km/L)"), verbose_name=_("Efficiency"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_fuel_type_per_user')
        ]
        verbose_name = _("Fuel Type")
        verbose_name_plural = _("Fuel Types")

    def __str__(self):
        return self.name

class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    name = models.CharField(max_length=50, verbose_name=_("Car Name"))
    make = models.CharField(max_length=50, blank=True, verbose_name=_("Make"))
    model = models.CharField(max_length=50, blank=True, verbose_name=_("Model"))
    fuel_type = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Default Fuel Type"))

    class Meta:
        verbose_name = _("Car")
        verbose_name_plural = _("Cars")

    def __str__(self):
        return f"{self.name} ({self.make} {self.model})"

class Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    default_fuel_type = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Default Fuel Type"))
    currency = models.CharField(max_length=5, default='$', help_text=_("Currency symbol (e.g. $, €, £)"), verbose_name=_("Currency"))
    


    class Meta:
        verbose_name = _("Settings")
        verbose_name_plural = _("Settings")

    def __str__(self):
        return f"Settings for {self.user.username}"

class Journey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journeys', null=True, blank=True)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Car"))
    date = models.DateField(default=timezone.now, verbose_name=_("Date"))
    distance = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Distance in kilometers"), verbose_name=_("Distance"))
    reason = models.CharField(max_length=255, verbose_name=_("Reason"))
    
    fuel_type_ref = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Fuel Type"))
    # Snapshot of the name for display if FuelType is deleted
    fuel_type = models.CharField(max_length=50, verbose_name=_("Fuel Type Name")) 
    
    cost_per_liter = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Cost per Unit"))
    fuel_quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Total units (e.g. liters)"), verbose_name=_("Fuel Quantity"))
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Total Cost"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Journey")
        verbose_name_plural = _("Journeys")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.reason} ({self.distance} km)"
