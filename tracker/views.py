from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, F, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Journey, Settings, FuelType, Car
from .forms import JourneyForm, SettingsForm, FuelTypeForm, CarForm
import datetime

@login_required
def dashboard(request):
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    journeys = Journey.objects.filter(
        user=request.user,
        date__year=current_year, 
        date__month=current_month
    ).order_by('-date', '-created_at')

    total_cost = journeys.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    total_distance = journeys.aggregate(Sum('distance'))['distance__sum'] or 0
    
    recent_journeys = Journey.objects.filter(user=request.user).order_by('-date', '-created_at')[:5]

    context = {
        'journeys': recent_journeys,
        'total_cost': total_cost,
        'total_distance': total_distance,
        'current_date': today,
    }
    return render(request, 'tracker/dashboard.html', context)

@login_required
def add_journey(request):
    settings, created = Settings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = JourneyForm(request.user, request.POST)
        if form.is_valid():
            journey = form.save(commit=False)
            journey.user = request.user
            journey.save()
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
        form = JourneyForm(request.user, initial=initial_data)

    return render(request, 'tracker/add_journey.html', {'form': form})

from django.utils import translation

@login_required
def settings_view(request):
    settings, created = Settings.objects.get_or_create(user=request.user)
    
    # Initialize forms with GET data/defaults
    form = SettingsForm(request.user, instance=settings)
    fuel_form = FuelTypeForm()
    car_form = CarForm(request.user)
    
    if request.method == 'POST':
        if 'save_settings' in request.POST:
            form = SettingsForm(request.user, request.POST, instance=settings)
            if form.is_valid():
                form.save()
                return redirect('settings')
                
        elif 'add_fuel' in request.POST:
             fuel_form = FuelTypeForm(request.POST)
             if fuel_form.is_valid():
                 fuel = fuel_form.save(commit=False)
                 fuel.user = request.user
                 fuel.save()
                 return redirect('settings')

        elif 'add_car' in request.POST:
             car_form = CarForm(request.user, request.POST)
             if car_form.is_valid():
                 car = car_form.save(commit=False)
                 car.user = request.user
                 car.save()
                 return redirect('settings')

    return render(request, 'tracker/settings.html', {
        'form': form, 
        'fuel_form': fuel_form,
        'car_form': car_form,
        'fuel_types': FuelType.objects.filter(user=request.user),
        'cars': Car.objects.filter(user=request.user)
    })

@login_required
def edit_journey(request, journey_id):
    journey = get_object_or_404(Journey, pk=journey_id, user=request.user)
    
    if request.method == 'POST':
        form = JourneyForm(request.user, request.POST, instance=journey)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        initial = {}
        if journey.fuel_type_ref:
            initial['fuel_type_select'] = journey.fuel_type_ref
        
        form = JourneyForm(request.user, instance=journey, initial=initial)

    return render(request, 'tracker/add_journey.html', {'form': form, 'journey': journey, 'is_edit': True})

@login_required
def history_view(request):
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')

    journeys = Journey.objects.filter(user=request.user).order_by('-date', '-created_at')
    
    # Get available years/months for filter
    dates = journeys.dates('date', 'month', order='DESC')
    
    current_date = timezone.now()
    
    # Default to current month/year if no params, BUT allow 'all' to clear filter
    # If params are missing entirely (first visit), default to current
    if 'month' not in request.GET and 'year' not in request.GET:
        selected_month = current_date.month
        selected_year = current_date.year
    
    if selected_year and str(selected_year) != 'all':
        journeys = journeys.filter(date__year=selected_year)
    
    if selected_month and str(selected_month) != 'all':
        journeys = journeys.filter(date__month=selected_month)

    context = {
        'journeys': journeys,
        'dates': dates,
        'selected_month': int(selected_month) if selected_month and str(selected_month) != 'all' else None,
        'selected_year': int(selected_year) if selected_year and str(selected_year) != 'all' else None,
    }
    return render(request, 'tracker/history.html', context)

@login_required
def reports_view(request):
    # Costs by Fuel Type
    # Aggregate by fuel_type (name string)
    # or fuel_type_ref? Refs might be deleted. Use CharField name for historical accuracy?
    # Actually, grouping by the stored name is safer if ref is deleted
    
    settings = Settings.objects.get(user=request.user)
    
    data = (
        Journey.objects.filter(user=request.user)
        .values('fuel_type')
        .annotate(
            total_cost=Sum('total_cost'),
            total_distance=Sum('distance'),
            count=Count('id')
        )
        .order_by('-total_cost')
    )
    
    context = {
        'report_data': data,
        'currency': settings.currency
    }
    return render(request, 'tracker/reports.html', context)
@login_required
def delete_journey(request, journey_id):
    journey = get_object_or_404(Journey, pk=journey_id, user=request.user)
    if request.method == 'POST':
        journey.delete()
        return redirect('dashboard')
    # If GET, maybe show confirmation? For now just redirect if accessed directly or use a simple confirm template
    # Assuming simple POST button from UI
    return render(request, 'tracker/confirm_delete.html', {'object': journey, 'type': 'Journey'})

@login_required
def edit_fuel(request, fuel_id):
    fuel = get_object_or_404(FuelType, pk=fuel_id, user=request.user)
    if request.method == 'POST':
        form = FuelTypeForm(request.POST, instance=fuel)
        if form.is_valid():
            form.save()
            return redirect('settings')
    else:
        form = FuelTypeForm(instance=fuel)
    return render(request, 'tracker/edit_fuel.html', {'form': form, 'fuel': fuel})

@login_required
def delete_fuel(request, fuel_id):
    fuel = get_object_or_404(FuelType, pk=fuel_id, user=request.user)
    if request.method == 'POST':
        fuel.delete()
        return redirect('settings')
    return render(request, 'tracker/confirm_delete.html', {'object': fuel, 'type': 'Fuel Type'})

