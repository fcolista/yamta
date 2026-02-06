from django.shortcuts import render, redirect
from django.db.models import Sum, Q, F
from django.utils import timezone
from .models import Journey, Settings, FuelType
from .forms import JourneyForm, SettingsForm, FuelTypeForm
import datetime

def dashboard(request):
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    journeys = Journey.objects.filter(
        date__year=current_year, 
        date__month=current_month
    ).order_by('-date', '-created_at')

    total_cost = journeys.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    total_distance = journeys.aggregate(Sum('distance'))['distance__sum'] or 0
    
    # Recent journeys should be global, not just current month
    recent_journeys = Journey.objects.all().order_by('-date', '-created_at')[:5]

    context = {
        'journeys': recent_journeys,
        'total_cost': total_cost,
        'total_distance': total_distance,
        'current_date': today,
    }
    return render(request, 'tracker/dashboard.html', context)

def add_journey(request):
    settings = Settings.get_solo()
    
    if request.method == 'POST':
        form = JourneyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        # Get defaults
        default_fuel = settings.default_fuel_type
        cost_per = default_fuel.cost_per_unit if default_fuel else 0
        
        initial_data = {
            'fuel_type_select': default_fuel,
            'cost_per_liter': cost_per,
            'date': timezone.now().date()
        }
        form = JourneyForm(initial=initial_data)

    return render(request, 'tracker/add_journey.html', {'form': form})

def settings_view(request):
    settings = Settings.get_solo()
    
    # Handle Fuel Type Addition/Edition could be separate, but let's just show list or simple add form for now
    # For MVP, maybe just a link to Django Admin or a simple inline formset? 
    # Let's add a separate section or logic for adding a FuelType if requested, 
    # but initially just SettingsForm.
    
    if request.method == 'POST':
        if 'save_settings' in request.POST:
            form = SettingsForm(request.POST, instance=settings)
            if form.is_valid():
                form.save()
                return redirect('settings')
        elif 'add_fuel' in request.POST:
             fuel_form = FuelTypeForm(request.POST)
             if fuel_form.is_valid():
                 fuel_form.save()
                 return redirect('settings')
             else:
                 # Re-render with settings form and errors
                 form = SettingsForm(instance=settings)
                 # We need to pass fuel_form to render errors
                 return render(request, 'tracker/settings.html', {'form': form, 'fuel_form': fuel_form, 'fuel_types': FuelType.objects.all()})

    else:
        form = SettingsForm(instance=settings)
        fuel_form = FuelTypeForm()

    return render(request, 'tracker/settings.html', {
        'form': form, 
        'fuel_form': fuel_form,
        'fuel_types': FuelType.objects.all()
    })

def edit_journey(request, journey_id):
    journey = Journey.objects.get(pk=journey_id)
    settings = Settings.get_solo()
    
    if request.method == 'POST':
        form = JourneyForm(request.POST, instance=journey)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        # We need to set initial for fuel_type_select based on the ref if it exists
        initial = {}
        if journey.fuel_type_ref:
            initial['fuel_type_select'] = journey.fuel_type_ref
            
        form = JourneyForm(instance=journey, initial=initial)

    return render(request, 'tracker/add_journey.html', {'form': form, 'is_edit': True, 'journey': journey})

def delete_journey(request, journey_id):
    journey = Journey.objects.get(pk=journey_id)
    if request.method == 'POST':
        journey.delete()
        return redirect('dashboard')
    # Optional: Confirm delete page, but for MVP we might just do POST from a modal or simple page
    # Let's assume the button sends a POST or we render a confirmation page.
    # For speed, let's render a simple confirmation page.
    return render(request, 'tracker/confirm_delete.html', {'object': journey, 'type': 'Journey'})

def edit_fuel(request, fuel_id):
    fuel = FuelType.objects.get(pk=fuel_id)
    
    if request.method == 'POST':
        form = FuelTypeForm(request.POST, instance=fuel)
        if form.is_valid():
            form.save()
            return redirect('settings')
    else:
        form = FuelTypeForm(instance=fuel)
        
    return render(request, 'tracker/edit_fuel.html', {'form': form, 'fuel': fuel})

def delete_fuel(request, fuel_id):
    fuel = FuelType.objects.get(pk=fuel_id)
    if request.method == 'POST':
        fuel.delete()
        return redirect('settings')
    return render(request, 'tracker/confirm_delete.html', {'object': fuel, 'type': 'Fuel Type'})

def history_view(request):
    journeys = Journey.objects.all().order_by('-date', '-created_at')
    
    # Get all distinct months/years from db for the filter dropdown
    # This is a simple set of dates
    dates = Journey.objects.dates('date', 'month', order='DESC')
    
    # Default to current month/year if not specified
    today = timezone.now()
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    # If parameters are not provided at all, default to current month and year
    if selected_month is None and selected_year is None:
        selected_month = str(today.month)
        selected_year = str(today.year)
    
    if selected_year and selected_year != 'all':
        journeys = journeys.filter(date__year=selected_year)
    
    if selected_month and selected_month != 'all':
        journeys = journeys.filter(date__month=selected_month)

    context = {
        'journeys': journeys,
        'dates': dates,
        'selected_month': int(selected_month) if selected_month and selected_month != 'all' else None,
        'selected_year': int(selected_year) if selected_year and selected_year != 'all' else None,
    }
    return render(request, 'tracker/history.html', context)

def reports_view(request):
    # Simple report: Costs by Fuel Type
    # Group by fuel_type (snapshot name) or fuel_type_ref if available
    
    # Let's group by the snapshot name to include deleted fuel types history correctly
    from django.db.models import Count
    
    report_data = Journey.objects.values('fuel_type').annotate(
        total_cost=Sum('total_cost'),
        total_distance=Sum('distance'),
        count=Count('id')
    ).order_by('-total_cost')
    
    return render(request, 'tracker/reports.html', {'report_data': report_data})
