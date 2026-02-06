from django import forms
from .models import Journey, Settings, FuelType

class JourneyForm(forms.ModelForm):
    # Override fuel_type to be a ModelChoiceField selection, but we will save it manually to the ref & char fields
    fuel_type_select = forms.ModelChoiceField(
        queryset=FuelType.objects.all(), 
        required=True, 
        label="Fuel Type",
        widget=forms.Select(attrs={'class': 'form-select w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'})
    )

    fuel_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}))
    total_cost = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}))
    cost_per_liter = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}))

    class Meta:
        model = Journey
        fields = ['date', 'distance', 'reason', 'cost_per_liter', 'fuel_quantity', 'total_cost']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
            'distance': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
            'reason': forms.TextInput(attrs={'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
            'cost_per_liter': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        distance = cleaned_data.get('distance')
        fuel_type = cleaned_data.get('fuel_type_select')
        qty = cleaned_data.get('fuel_quantity')
        cost_per = cleaned_data.get('cost_per_liter')
        total = cleaned_data.get('total_cost')

        # Auto-calculate Quantity if missing
        if distance and fuel_type and not qty:
            try:
                efficiency = fuel_type.efficiency
                if efficiency > 0:
                    qty = distance / efficiency
                    # Round to 2 decimals
                    qty = round(qty, 2)
                    cleaned_data['fuel_quantity'] = qty
            except:
                pass # Use default validation error if needed or let it fail
        
        # Auto-calculate Total Cost if missing
        # Note: we use the (possibly calculated) qty
        if qty and not total:
            if not cost_per and fuel_type:
                 cost_per = fuel_type.cost_per_unit
                 cleaned_data['cost_per_liter'] = cost_per
            
            if cost_per:
                total = qty * cost_per
                total = round(total, 2)
                cleaned_data['total_cost'] = total

        # If still missing, we will likely have model validation errors if the model requires them.
        # But we did our best calculation.
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        ft = self.cleaned_data['fuel_type_select']
        instance.fuel_type_ref = ft
        instance.fuel_type = ft.name # Snapshot
        
        # Ensure calculated values are on the instance (ModelForm usually handles this from cleaned_data, but let's be safe)
        if self.cleaned_data.get('fuel_quantity'):
            instance.fuel_quantity = self.cleaned_data['fuel_quantity']
        if self.cleaned_data.get('total_cost'):
            instance.total_cost = self.cleaned_data['total_cost']
            
        if commit:
            instance.save()
        return instance

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['default_fuel_type', 'currency']
        widgets = {
            'default_fuel_type': forms.Select(attrs={'class': 'form-select w-full rounded-lg border-slate-200 dark:border-white/10 bg-background-light dark:bg-background-dark text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
            'currency': forms.TextInput(attrs={'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
        }

class FuelTypeForm(forms.ModelForm):
    class Meta:
        model = FuelType
        fields = ['name', 'cost_per_unit', 'unit_name', 'efficiency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
            'cost_per_unit': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
            'unit_name': forms.TextInput(attrs={'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
            'efficiency': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
        }
