from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import pvlib
import pandas as pd

app = Flask(__name__)

def calculate_total_load(appliances):
    """Calculates the total daily energy consumption in Watt-hours."""
    total_load = 0
    for i in range(len(appliances['appliance_name'])):
        quantity = int(appliances['quantity'][i])
        wattage = float(appliances['wattage'][i])
        hours = float(appliances['hours'][i])
        total_load += quantity * wattage * hours
    return total_load

def get_solar_irradiance(address):
    """Gets the average daily solar irradiance (peak sun hours) for a given address."""
    try:
        geolocator = Nominatim(user_agent="solar_calculator")
        location = geolocator.geocode(address)
        if location is None:
            # Default to Lagos, Nigeria if address not found
            latitude, longitude = 6.5244, 3.3792
        else:
            latitude, longitude = location.latitude, location.longitude

        # Get TMY data from PVGIS
        tmy, _, _, _ = pvlib.iotools.get_pvgis_tmy(latitude, longitude)

        # Calculate daily GHI (Global Horizontal Irradiance)
        daily_ghi = tmy['ghi'].resample('D').sum() / 1000 # Convert from Wh/m^2 to kWh/m^2

        # Return the annual average daily GHI (Peak Sun Hours)
        return daily_ghi.mean()
    except Exception as e:
        print(f"Could not get solar irradiance: {e}")
        # Return a default value for Nigeria if the API fails
        return 5.0


def size_solar_panels(total_load, peak_sun_hours):
    """Sizes the solar panels in Watts."""
    # Add a 30% safety factor for system losses
    required_wattage = (total_load / peak_sun_hours) * 1.3
    return required_wattage

def suggest_panels(required_wattage):
    """Suggests solar panel models and quantity."""
    # Common panel sizes in Watts
    panel_models = [250, 300, 330, 350, 400, 450, 500]
    suggestions = []
    for wattage in panel_models:
        num_panels = -(-required_wattage // wattage) # Ceiling division
        suggestions.append(f"{int(num_panels)} x {wattage}W panels")
    return suggestions

def size_batteries(total_load, system_voltage):
    """Sizes the batteries in Amp-hours."""
    # Assuming 2 days of autonomy and 50% depth of discharge for lead-acid
    days_of_autonomy = 2
    depth_of_discharge = 0.5
    battery_capacity_wh = total_load * days_of_autonomy / depth_of_discharge
    battery_capacity_ah = battery_capacity_wh / system_voltage
    return battery_capacity_ah

def size_inverter(appliances):
    """Sizes the inverter in Watts."""
    total_wattage = 0
    for i in range(len(appliances['appliance_name'])):
        quantity = int(appliances['quantity'][i])
        wattage = float(appliances['wattage'][i])
        total_wattage += quantity * wattage
    # Add a 25% safety factor for surge loads
    inverter_size = total_wattage * 1.25
    return inverter_size

def size_mppt(panel_wattage, system_voltage):
    """Sizes the MPPT charge controller in Amps."""
    # Add a 25% safety factor
    charge_controller_current = (panel_wattage / system_voltage) * 1.25
    return charge_controller_current

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    appliances = {
        'appliance_name': request.form.getlist('appliance_name[]'),
        'quantity': request.form.getlist('quantity[]'),
        'wattage': request.form.getlist('wattage[]'),
        'hours': request.form.getlist('hours[]')
    }
    address = request.form['address']
    system_voltage = int(request.form['system_voltage'])

    total_load_wh = calculate_total_load(appliances)
    peak_sun_hours = get_solar_irradiance(address)

    panel_wattage = size_solar_panels(total_load_wh, peak_sun_hours)
    panel_suggestions = suggest_panels(panel_wattage)

    battery_ah = size_batteries(total_load_wh, system_voltage)
    inverter_watts = size_inverter(appliances)
    mppt_amps = size_mppt(panel_wattage, system_voltage)

    report = {
        'total_load': f"{total_load_wh:,.2f} Wh/day",
        'peak_sun_hours': f"{peak_sun_hours:.2f} hours",
        'required_panel_wattage': f"{panel_wattage:,.2f} W",
        'panel_suggestions': panel_suggestions,
        'battery_capacity': f"{battery_ah:,.2f} Ah",
        'inverter_size': f"{inverter_watts:,.2f} W",
        'mppt_size': f"{mppt_amps:,.2f} A",
        'system_voltage': f"{system_voltage}V"
    }

    return render_template('results.html', report=report)

if __name__ == '__main__':
    app.run(debug=True)
