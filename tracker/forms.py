from django import forms
from .models import Journey, Settings, FuelType, Car

class JourneyForm(forms.ModelForm):
    # Override fuel_type to be a ModelChoiceField selection, but we will save it manually to the ref & char fields
    fuel_type_select = forms.ModelChoiceField(
        queryset=FuelType.objects.none(), 
        required=True, 
        label="Fuel Type",
        widget=forms.Select(attrs={'class': 'form-select w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'})
    )
    
    car = forms.ModelChoiceField(
        queryset=Car.objects.none(),
        required=False,
        label="Car",
        widget=forms.Select(attrs={'class': 'form-select w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'})
    )

    fuel_quantity = forms.DecimalField(required=False, label="Fuel Quantity", widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}))
    total_cost = forms.DecimalField(required=False, label="Total Cost", widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}))
    cost_per_liter = forms.DecimalField(required=False, label="Cost per Unit", widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fuel_type_select'].queryset = FuelType.objects.filter(user=user)
        self.fields['car'].queryset = Car.objects.filter(user=user)

    class Meta:
        model = Journey
        fields = ['date', 'car', 'distance', 'reason', 'cost_per_liter', 'fuel_quantity', 'total_cost']
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
                    qty = round(qty, 2)
                    cleaned_data['fuel_quantity'] = qty
            except:
                pass 
        
        # Auto-calculate Total Cost if missing
        if qty and not total:
            if not cost_per and fuel_type:
                 cost_per = fuel_type.cost_per_unit
                 cleaned_data['cost_per_liter'] = cost_per
            
            if cost_per:
                total = qty * cost_per
                total = round(total, 2)
                cleaned_data['total_cost'] = total

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        ft = self.cleaned_data['fuel_type_select']
        instance.fuel_type_ref = ft
        instance.fuel_type = ft.name # Snapshot
        
        if self.cleaned_data.get('fuel_quantity'):
            instance.fuel_quantity = self.cleaned_data['fuel_quantity']
        if self.cleaned_data.get('total_cost'):
            instance.total_cost = self.cleaned_data['total_cost']
            
        if commit:
            instance.save()
        return instance

class SettingsForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['default_fuel_type'].queryset = FuelType.objects.filter(user=user)

    class Meta:
        model = Settings
        fields = ['currency', 'default_fuel_type']
        widgets = {
            'currency': forms.TextInput(attrs={'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-background-light dark:bg-background-dark text-slate-900 dark:text-white focus:border-primary focus:ring-primary py-2.5'}),
            'default_fuel_type': forms.Select(attrs={'class': 'form-select w-full rounded-lg border-slate-200 dark:border-white/10 bg-background-light dark:bg-background-dark text-slate-900 dark:text-white focus:border-primary focus:ring-primary py-2.5'}),
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

class CarForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fuel_type'].queryset = FuelType.objects.filter(user=user)

    class Meta:
        model = Car
        fields = ['name', 'make', 'model', 'fuel_type']
        widgets = {
             'name': forms.TextInput(attrs={'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
             'make': forms.TextInput(attrs={'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
             'model': forms.TextInput(attrs={'class': 'form-input w-full rounded-lg border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
             'fuel_type': forms.Select(attrs={'class': 'form-select w-full rounded-lg border-slate-200 dark:border-white/10 bg-background-light dark:bg-background-dark text-slate-900 dark:text-white focus:border-primary focus:ring-primary'}),
        }
