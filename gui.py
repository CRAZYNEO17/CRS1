#!/usr/bin/env python
# GUI Module for Agri Wiz
# Provides a graphical user interface for the crop recommendation system

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
import logging
import datetime
import json
import requests
from agri_wiz import AgriWiz
from weather_api import WeatherAPI, get_humidity_level, get_rainfall_level
from gps_service import GPSService

class CropDialog:
    def __init__(self, parent, title):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x500")
        self.result = None
        
        # Create and pack widgets
        self.create_widgets()
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        parent.wait_window(self.dialog)
        
    def create_widgets(self):
        # Create input fields
        fields = [
            ("Crop Name:", "crop_name", None),
            ("Soil Types (comma-separated):", "soil_types", None),
            ("Climates (comma-separated):", "climates", None),
            ("Seasons (comma-separated):", "seasons", None),
            ("Water Needs:", "water_needs", ["low", "medium", "high"]),
            ("Humidity Preference:", "humidity_preference", ["low", "medium", "high"]),
            ("Soil Fertility Needs:", "soil_fertility", ["low", "medium", "high"])
        ]
        
        # Create a frame with padding
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Create entries dictionary
        self.entries = {}
        
        # Create input fields
        for i, (label, key, values) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            if values:
                var = tk.StringVar()
                ttk.Combobox(main_frame, textvariable=var, values=values).grid(row=i, column=1, sticky='ew', padx=5, pady=2)
                self.entries[key] = var
            else:
                var = tk.StringVar()
                ttk.Entry(main_frame, textvariable=var).grid(row=i, column=1, sticky='ew', padx=5, pady=2)
                self.entries[key] = var
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='left', padx=5)
        
    def save(self):
        # Validate required fields
        if not self.entries["crop_name"].get():
            messagebox.showerror("Error", "Crop name is required")
            return
            
        # Create crop data dictionary
        self.result = {
            "crop_name": self.entries["crop_name"].get(),
            "soil_types": self.entries["soil_types"].get(),
            "climates": self.entries["climates"].get(),
            "seasons": self.entries["seasons"].get(),
            "water_needs": self.entries["water_needs"].get(),
            "humidity_preference": self.entries["humidity_preference"].get(),
            "soil_fertility": self.entries["soil_fertility"].get()
        }
        
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()

class AgriWizGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Agri Wiz - Crop Recommendation System")
        self.root.geometry("1200x800")
        
        # Initialize asyncio event loop for background tasks
        self.loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.async_thread.start()
        
        # Initialize backend systems with the event loop
        self.agri_wiz = AgriWiz()
        self.weather_api = WeatherAPI()
        self.gps_service = GPSService(loop=self.loop)  # Pass event loop to GPS service
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Initialize variables
        self.location_var = tk.StringVar()
        self.soil_type_var = tk.StringVar()
        self.climate_var = tk.StringVar()
        self.season_var = tk.StringVar()
        self.humidity_var = tk.StringVar()
        self.rainfall_var = tk.StringVar()
        self.soil_fertility_var = tk.StringVar()
        
        # Create tabs
        self.create_recommendation_tab()
        self.create_yield_estimation_tab()
        self.create_schemes_tab()
        self.create_crops_tab()
        self.create_weather_tab()  # New weather monitoring tab

        # Initialize crop lists
        self._initialize_crop_lists()

        # Add status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var)
        self.status_bar.pack(fill='x', padx=5, pady=2)
        
        # Style configuration
        self.setup_styles()
        
    def _run_event_loop(self):
        """Run the asyncio event loop in a separate thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_async(self, coro):
        """Run an async coroutine from the GUI thread"""
        if not self.loop or not self.loop.is_running():
            return None
            
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            return future.result(timeout=10)  # 10 second timeout
        except asyncio.TimeoutError:
            self.status_var.set("Operation timed out")
            return None
        except Exception as e:
            self.status_var.set(f"Operation failed: {str(e)}")
            return None

    def on_closing(self):
        """Clean up when the window is closed"""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.root.destroy()

    def setup_styles(self):
        """Configure styles for the GUI"""
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        
        # Configure custom Treeview style
        style.configure('Custom.Treeview', rowheight=25)
        style.configure('Custom.Treeview.Heading', font=('Helvetica', 10, 'bold'))

    async def detect_location(self):
        """Asynchronously detect current location"""
        try:
            self.status_var.set("Checking Windows Location Services...")
            self.root.update_idletasks()
            
            location = await self.gps_service.get_location()
            if not location:
                # Try IP-based location as fallback
                self.status_var.set("Windows Location unavailable, trying IP-based location...")
                self.root.update_idletasks()
                
                location = await self.weather_api.gps_config._get_ip_location()
                if not location:
                    # Read the error log for details
                    try:
                        with open('gps_debug.log', 'r') as f:
                            error_details = f.readlines()[-5:]  # Get last 5 lines
                            error_details = ''.join(error_details)
                    except Exception:
                        error_details = "Could not read error log"
                        
                    raise Exception(
                        "Could not detect location.\n\n"
                        "Please ensure:\n"
                        "1. Location services are enabled in Windows Settings\n"
                        "2. This app has permission to access location\n"
                        "3. Your device has a GPS sensor or Wi-Fi positioning\n"
                        "4. You are connected to the internet\n\n"
                        f"Technical details:\n{error_details}"
                    )

            # Try to get location name through reverse geocoding
            try:
                response = requests.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params={
                        "lat": location['latitude'],
                        "lon": location['longitude'],
                        "format": "json"
                    },
                    headers={'User-Agent': 'AgriWiz/1.0'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    address = data.get('address', {})
                    loc_name = address.get('city', 
                               address.get('town',
                               address.get('village',
                               address.get('suburb',
                               address.get('county', '')))))
                    if loc_name:
                        state = address.get('state', '')
                        country = address.get('country', '')
                        loc_name = f"{loc_name}, {state or country}"
                    else:
                        # Fallback to coordinates if no location name found
                        loc_name = f"{location['latitude']:.4f}, {location['longitude']:.4f}"
                        if location.get('source') == 'ip':
                            loc_name += " (IP-based)"
                else:
                    # Use coordinate format if reverse geocoding fails
                    loc_name = f"{location['latitude']:.4f}, {location['longitude']:.4f}"
                    if location.get('source') == 'ip':
                        loc_name += " (IP-based)"

                # Set location and update status
                self.location_var.set(loc_name)
                self.status_var.set(f"Location detected: {loc_name}")
                
                # Try to update weather data
                await self.update_weather()
                    
            except Exception as e:
                # If reverse geocoding fails, still use the coordinates
                loc_name = f"{location['latitude']:.4f}, {location['longitude']:.4f}"
                if location.get('source') == 'ip':
                    loc_name += " (IP-based)"
                self.location_var.set(loc_name)
                self.status_var.set(f"Location detected (coordinates only)")
                
        except Exception as e:
            error_msg = str(e)
            self.status_var.set(f"Error detecting location: {error_msg}")
            messagebox.showerror("Location Detection Error", error_msg)

    def update_weather_display(self, weather_data):
        """Update weather information display"""
        if hasattr(self, 'weather_text'):
            self.weather_text.delete(1.0, tk.END)
            self.weather_text.insert(tk.END, f"""
Current Weather Conditions:
-------------------------
Location: {weather_data.get('location', 'Unknown')}
Temperature: {weather_data.get('temperature', 'N/A')}°C
Humidity: {weather_data.get('humidity', 'N/A')}% ({get_humidity_level(weather_data.get('humidity', 0))})
Rainfall: {weather_data.get('rainfall', 'N/A')}mm ({get_rainfall_level(weather_data.get('rainfall', 0))})
Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

    async def update_weather(self):
        """Update weather information for the current location"""
        try:
            if not self.location_var.get():
                raise ValueError("Please enter a location or use location detection")
                
            self.status_var.set("Fetching weather data...")
            weather_data = await self.weather_api.get_weather_data(self.location_var.get())
            
            if weather_data:
                self.update_weather_display(weather_data)
                
                # Add to history
                now = datetime.datetime.now().strftime('%H:%M:%S')
                self.weather_history.insert('', 0, values=(
                    now,
                    f"{weather_data.get('temperature', 'N/A')}",
                    f"{weather_data.get('humidity', 'N/A')}",
                    f"{weather_data.get('rainfall', 'N/A')}"
                ))
                
                self.status_var.set("Weather data updated successfully")
            else:
                raise Exception("Could not fetch weather data")
                
        except Exception as e:
            self.status_var.set(f"Error updating weather: {str(e)}")
            messagebox.showerror("Error", f"Could not update weather: {str(e)}")

    def create_weather_tab(self):
        """Create the weather monitoring tab"""
        weather_frame = ttk.Frame(self.notebook)
        self.notebook.add(weather_frame, text="Weather Monitor")

        # Current conditions frame
        conditions_frame = ttk.LabelFrame(weather_frame, text="Current Weather Conditions", padding=10)
        conditions_frame.pack(fill='x', padx=5, pady=5)

        # Location frame
        loc_frame = ttk.Frame(conditions_frame)
        loc_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(loc_frame, text="Location:").pack(side='left', padx=5)
        ttk.Entry(loc_frame, textvariable=self.location_var).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(loc_frame, text="Get Weather", 
                  command=lambda: self.run_async(self.update_weather())
        ).pack(side='left', padx=5)
        ttk.Button(loc_frame, text="Detect Location", 
                  command=lambda: self.run_async(self.detect_location())
        ).pack(side='left', padx=5)

        # Weather display
        self.weather_text = scrolledtext.ScrolledText(conditions_frame, height=10)
        self.weather_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Weather history frame
        history_frame = ttk.LabelFrame(weather_frame, text="Weather History", padding=10)
        history_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.weather_history = ttk.Treeview(history_frame, columns=('Time', 'Temp', 'Humidity', 'Rainfall'), show='headings')
        self.weather_history.heading('Time', text='Time')
        self.weather_history.heading('Temp', text='Temperature (°C)')
        self.weather_history.heading('Humidity', text='Humidity (%)')
        self.weather_history.heading('Rainfall', text='Rainfall (mm)')
        self.weather_history.pack(fill='both', expand=True)

    def create_schemes_tab(self):
        """Create the government schemes tab"""
        schemes_frame = ttk.Frame(self.notebook)
        self.notebook.add(schemes_frame, text="Govt. Schemes")

        # Search frame
        search_frame = ttk.LabelFrame(schemes_frame, text="Search Schemes", padding=10)
        search_frame.pack(fill='x', padx=5, pady=5)

        # Search type
        ttk.Label(search_frame, text="Search by:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.scheme_search_var = tk.StringVar(value="category")
        ttk.Radiobutton(search_frame, text="Category", variable=self.scheme_search_var, value="category", command=self.update_scheme_search).grid(row=0, column=1)
        ttk.Radiobutton(search_frame, text="Crop & Location", variable=self.scheme_search_var, value="crop", command=self.update_scheme_search).grid(row=0, column=2)

        self.scheme_params_frame = ttk.Frame(search_frame)
        self.scheme_params_frame.grid(row=1, column=0, columnspan=3, pady=5)

        # Results frame
        results_frame = ttk.LabelFrame(schemes_frame, text="Available Schemes", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.schemes_text = scrolledtext.ScrolledText(results_frame)
        self.schemes_text.pack(fill='both', expand=True)

        self.update_scheme_search()

    def create_crops_tab(self):
        """Create the crops management tab"""
        crops_frame = ttk.Frame(self.notebook)
        self.notebook.add(crops_frame, text="Manage Crops")

        # Crops list
        list_frame = ttk.LabelFrame(crops_frame, text="Available Crops", padding=10)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        columns = ('Crop', 'Soil Types', 'Climate', 'Seasons', 'Water Needs')
        self.crops_tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        for col in columns:
            self.crops_tree.heading(col, text=col)
            self.crops_tree.column(col, width=100)

        self.crops_tree.pack(fill='both', expand=True)

        # Add crop frame
        add_frame = ttk.LabelFrame(crops_frame, text="Add New Crop", padding=10)
        add_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(add_frame, text="Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.new_crop_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_crop_var).grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        ttk.Button(add_frame, text="Add Crop", command=self.add_crop).grid(row=1, column=0, columnspan=2, pady=10)

    def create_recommendation_tab(self):
        """Create the crop recommendation tab"""
        rec_frame = ttk.Frame(self.notebook)
        self.notebook.add(rec_frame, text="Recommendations")

        # Location frame
        loc_frame = ttk.LabelFrame(rec_frame, text="Location", padding=10)
        loc_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(loc_frame, text="Location:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(loc_frame, textvariable=self.location_var).grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        ttk.Button(loc_frame, text="Detect Location", 
                  command=lambda: self.run_async(self.detect_location())
        ).grid(row=0, column=2, padx=5, pady=2)

        # Parameters frame
        params_frame = ttk.LabelFrame(rec_frame, text="Growing Parameters", padding=10)
        params_frame.pack(fill='x', padx=5, pady=5)

        # Soil type
        ttk.Label(params_frame, text="Soil Type:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        soil_types = ['clay', 'loamy', 'sandy', 'black soil']
        ttk.Combobox(params_frame, textvariable=self.soil_type_var, values=soil_types).grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        # Climate
        ttk.Label(params_frame, text="Climate:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        climates = ['tropical', 'subtropical', 'temperate']
        ttk.Combobox(params_frame, textvariable=self.climate_var, values=climates).grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        # Season
        ttk.Label(params_frame, text="Season:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        seasons = ['summer', 'winter', 'rainy', 'spring', 'fall']
        ttk.Combobox(params_frame, textvariable=self.season_var, values=seasons).grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        # Optional parameters
        opt_frame = ttk.LabelFrame(params_frame, text="Optional Parameters", padding=10)
        opt_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Humidity
        ttk.Label(opt_frame, text="Humidity:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        humidity_levels = ['low', 'medium', 'high']
        ttk.Combobox(opt_frame, textvariable=self.humidity_var, values=humidity_levels).grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        # Rainfall
        ttk.Label(opt_frame, text="Rainfall:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        rainfall_levels = ['low', 'medium', 'high']
        ttk.Combobox(opt_frame, textvariable=self.rainfall_var, values=rainfall_levels).grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        # Soil Fertility
        ttk.Label(opt_frame, text="Soil Fertility:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        fertility_levels = ['low', 'medium', 'high']
        ttk.Combobox(opt_frame, textvariable=self.soil_fertility_var, values=fertility_levels).grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        # Get recommendations button
        ttk.Button(params_frame, text="Get Recommendations", 
                  command=self.get_recommendations
        ).grid(row=4, column=0, columnspan=2, pady=10)

        # Results frame
        results_frame = ttk.LabelFrame(rec_frame, text="Recommendations", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.recommendations_text = scrolledtext.ScrolledText(results_frame)
        self.recommendations_text.pack(fill='both', expand=True)

    def create_yield_estimation_tab(self):
        """Create the yield estimation tab"""
        yield_frame = ttk.Frame(self.notebook)
        self.notebook.add(yield_frame, text="Yield Estimation")

        # Input parameters frame
        input_frame = ttk.LabelFrame(yield_frame, text="Input Parameters", padding=10)
        input_frame.pack(fill='x', padx=5, pady=5)

        # Create input fields
        params = [
            ("Crop:", "yieldCrop", self.agri_wiz.crop_data),
            ("Temperature (°C):", "yieldTemp", None),
            ("Rainfall (mm):", "yieldRainfall", None),
            ("Humidity (%):", "yieldHumidity", None),
            ("Soil pH:", "yieldSoilPh", None),
            ("Soil Fertility:", "yieldSoilFertility", ['low', 'medium', 'high']),
            ("Water Availability:", "yieldWater", ['low', 'medium', 'high']),
            ("Season:", "yieldSeason", ['summer', 'winter', 'rainy', 'spring'])
        ]

        for i, (label, var_name, values) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            if values:
                setattr(self, var_name, tk.StringVar())
                ttk.Combobox(input_frame, textvariable=getattr(self, var_name), values=values).grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            else:
                setattr(self, var_name, tk.StringVar())
                ttk.Entry(input_frame, textvariable=getattr(self, var_name)).grid(row=i, column=1, sticky='ew', padx=5, pady=2)

        # Buttons
        ttk.Button(input_frame, text="Auto-fill from Location", 
                  command=lambda: self.run_async(self.autofill_yield_params())
        ).grid(row=len(params), column=0, columnspan=2, pady=5)
        
        ttk.Button(input_frame, text="Estimate Yield", 
                  command=self.estimate_yield
        ).grid(row=len(params)+1, column=0, columnspan=2, pady=5)

        # Results frame
        results_frame = ttk.LabelFrame(yield_frame, text="Estimation Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.yield_results_text = scrolledtext.ScrolledText(results_frame)
        self.yield_results_text.pack(fill='both', expand=True)

    async def autofill_yield_params(self):
        """Auto-fill yield parameters from current location"""
        try:
            if not self.location_var.get():
                raise ValueError("Please enter a location or use location detection")
                
            self.status_var.set("Fetching parameters...")
            weather_data = await self.weather_api.get_weather_data(self.location_var.get())
            
            if weather_data:
                self.yieldTemp.set(str(weather_data.get('temperature', '')))
                self.yieldHumidity.set(str(weather_data.get('humidity', '')))
                self.yieldRainfall.set(str(weather_data.get('rainfall', '')))
                
                # Get current season
                current_season = self.agri_wiz.get_current_season()
                self.yieldSeason.set(current_season)
                
                self.status_var.set("Parameters updated from weather data")
            else:
                raise Exception("Could not fetch weather data")
                
        except Exception as e:
            self.status_var.set(f"Error auto-filling parameters: {str(e)}")
            messagebox.showerror("Error", str(e))

    def estimate_yield(self):
        """Estimate crop yield based on parameters"""
        try:
            # Validate required fields
            if not self.yieldCrop.get():
                raise ValueError("Please select a crop")
            
            # Prepare conditions
            conditions = {
                "temperature": float(self.yieldTemp.get() or 25),
                "rainfall": float(self.yieldRainfall.get() or 0),
                "humidity": float(self.yieldHumidity.get() or 60),
                "soil_ph": float(self.yieldSoilPh.get() or 6.5),
                "soil_fertility": self.yieldSoilFertility.get() or "medium",
                "water_availability": self.yieldWater.get() or "medium",
                "season": self.yieldSeason.get() or self.agri_wiz.get_current_season()
            }
            
            # Get yield estimate
            crop_name = self.yieldCrop.get()
            yield_estimate = self.agri_wiz.yield_estimator.predict_yield(crop_name, conditions)
            
            if "error" not in yield_estimate:
                # Get optimization suggestions
                optimization = self.agri_wiz.yield_estimator.get_optimization_suggestions(crop_name, conditions)
                
                # Display results
                self.yield_results_text.delete(1.0, tk.END)
                self.yield_results_text.insert(tk.END, f"""Yield Estimation Results:
----------------------------------------
Crop: {crop_name}
Estimated Yield: {yield_estimate['estimated_yield']} {yield_estimate['unit']}
Confidence Interval: {yield_estimate['confidence_interval'][0]} - {yield_estimate['confidence_interval'][1]} {yield_estimate['unit']}

Optimization Suggestions:
""")
                if "error" not in optimization:
                    for suggestion in optimization["suggestions"]:
                        self.yield_results_text.insert(tk.END, f"\n- {suggestion['suggestion']}")
                        self.yield_results_text.insert(tk.END, 
                            f"\n  Potential improvement: {suggestion['potential_improvement']} {yield_estimate['unit']}\n")
                
                self.status_var.set("Yield estimation completed successfully")
            else:
                raise Exception(yield_estimate["error"])
                
        except ValueError as e:
            self.status_var.set(f"Invalid input: {str(e)}")
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            self.status_var.set(f"Error estimating yield: {str(e)}")
            messagebox.showerror("Error", str(e))

    def update_scheme_search(self):
        """Update scheme search form based on search type"""
        # Clear existing widgets
        for widget in self.scheme_params_frame.winfo_children():
            widget.destroy()
            
        if self.scheme_search_var.get() == "category":
            # Category search
            ttk.Label(self.scheme_params_frame, text="Category:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
            categories = self.agri_wiz.scheme_manager.get_categories()
            self.scheme_category = tk.StringVar()
            ttk.Combobox(self.scheme_params_frame, textvariable=self.scheme_category, values=categories).grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        else:
            # Crop search
            ttk.Label(self.scheme_params_frame, text="Crop:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
            self.scheme_crop = tk.StringVar()
            ttk.Combobox(self.scheme_params_frame, textvariable=self.scheme_crop, values=self.crops).grid(row=0, column=1, sticky='ew', padx=5, pady=2)
            
            ttk.Label(self.scheme_params_frame, text="State:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
            self.scheme_state = tk.StringVar()
            ttk.Entry(self.scheme_params_frame, textvariable=self.scheme_state).grid(row=1, column=1, sticky='ew', padx=5, pady=2)
            
            ttk.Label(self.scheme_params_frame, text="Land Area (ha):").grid(row=2, column=0, sticky='w', padx=5, pady=2)
            self.scheme_area = tk.StringVar()
            ttk.Entry(self.scheme_params_frame, textvariable=self.scheme_area).grid(row=2, column=1, sticky='ew', padx=5, pady=2)
            
        # Search button
        ttk.Button(self.scheme_params_frame, text="Search Schemes", 
                  command=self.search_schemes
        ).grid(row=3, column=0, columnspan=2, pady=10)

    def search_schemes(self):
        """Search for government schemes"""
        try:
            if self.scheme_search_var.get() == "category":
                if not self.scheme_category.get():
                    raise ValueError("Please select a category")
                    
                schemes = self.agri_wiz.scheme_manager.get_schemes_by_category(self.scheme_category.get())
                self.display_schemes(schemes)
            else:
                if not self.scheme_crop.get():
                    raise ValueError("Please select a crop")
                    
                scheme_info = self.agri_wiz.get_schemes_for_crop(
                    self.scheme_crop.get(),
                    self.scheme_state.get(),
                    float(self.scheme_area.get()) if self.scheme_area.get() else None
                )
                self.display_schemes(scheme_info['schemes'], scheme_info.get('subsidies'))
                
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error searching schemes: {str(e)}")

    def display_schemes(self, schemes, subsidies=None):
        """Display schemes in the text widget"""
        self.schemes_text.delete(1.0, tk.END)
        
        if not schemes:
            self.schemes_text.insert(tk.END, "No schemes found matching your criteria.\n")
            return
            
        self.schemes_text.insert(tk.END, "Available Schemes:\n\n")
        for scheme in schemes:
            self.schemes_text.insert(tk.END, f"{scheme['name']} - {scheme.get('full_name', '')}\n")
            self.schemes_text.insert(tk.END, f"Description: {scheme['description']}\n")
            if 'benefits' in scheme:
                self.schemes_text.insert(tk.END, "Benefits:\n")
                for benefit in scheme['benefits']:
                    self.schemes_text.insert(tk.END, f"- {benefit}\n")
            self.schemes_text.insert(tk.END, "\n")
            
        if subsidies:
            self.schemes_text.insert(tk.END, "\nAvailable Subsidies:\n")
            for category, subsidy in subsidies.items():
                if subsidy:
                    self.schemes_text.insert(tk.END, f"\n{category.title()}:\n{subsidy}")
                    
    def add_crop(self):
        """Add a new crop to the database"""
        try:
            if not self.new_crop_var.get():
                raise ValueError("Please enter a crop name")
                
            # Open dialog for crop details
            dialog = CropDialog(self.root, "Add New Crop")
            if (dialog.result):
                # Add crop to database
                self.agri_wiz.add_crop(dialog.result)
                
                # Refresh crop lists
                self._initialize_crop_lists()
                
                # Clear input
                self.new_crop_var.set("")
                
                # Update crops tree
                self.update_crops_tree()
                
                messagebox.showinfo("Success", "Crop added successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error adding crop: {str(e)}")

    def update_crops_tree(self):
        """Update the crops treeview"""
        # Clear existing items
        for item in self.crops_tree.get_children():
            self.crops_tree.delete(item)
            
        # Add crops
        for crop in self.agri_wiz.crop_data:
            self.crops_tree.insert('', 'end', values=(
                crop['crop_name'],
                crop['soil_types'],
                crop['climates'],
                crop['seasons'],
                crop['water_needs']
            ))

    def _initialize_crop_lists(self):
        """Initialize crop data for dropdowns"""
        self.crops = [crop['crop_name'] for crop in self.agri_wiz.crop_data]

    def get_recommendations(self):
        """Get crop recommendations based on input parameters"""
        try:
            if self.location_var.get():
                recommendations, details = self.agri_wiz.get_recommendations_by_location(
                    self.location_var.get(),
                    self.humidity_var.get() or None,
                    self.soil_fertility_var.get() or None
                )
                
                if recommendations is None:
                    messagebox.showerror("Error", details)
                    return
                    
                self.display_recommendations(recommendations, details)
            else:
                recommendations, scored_recommendations = self.agri_wiz.get_recommendations(
                    self.soil_type_var.get(),
                    self.climate_var.get(),
                    self.season_var.get(),
                    self.rainfall_var.get() or None,
                    self.humidity_var.get() or None,
                    self.soil_fertility_var.get() or None
                )
                
                self.display_recommendations(recommendations)
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_recommendations(self, recommendations, details=None):
        """Display recommendations in the text widget"""
        self.recommendations_text.delete(1.0, tk.END)
        
        if details:
            self.recommendations_text.insert(tk.END, "Location Details:\n")
            self.recommendations_text.insert(tk.END, f"Soil Type: {details['soil_type']}\n")
            self.recommendations_text.insert(tk.END, f"Climate: {details['climate']}\n")
            self.recommendations_text.insert(tk.END, f"Season: {details['season']}\n")
            self.recommendations_text.insert(tk.END, f"Rainfall: {details['rainfall']}\n")
            if details['humidity']:
                self.recommendations_text.insert(tk.END, f"Humidity: {details['humidity']}\n")
            if details['soil_fertility']:
                self.recommendations_text.insert(tk.END, f"Soil Fertility: {details['soil_fertility']}\n")
            self.recommendations_text.insert(tk.END, "\n")
        
        self.recommendations_text.insert(tk.END, "Recommended Crops:\n\n")
        for i, crop in enumerate(recommendations, 1):
            self.recommendations_text.insert(tk.END, f"{i}. {crop['crop_name']}\n")
            self.recommendations_text.insert(tk.END, f"   Water needs: {crop['water_needs']}\n")
            if 'humidity_preference' in crop:
                self.recommendations_text.insert(tk.END, f"   Humidity preference: {crop['humidity_preference']}\n")
            if 'soil_fertility' in crop:
                self.recommendations_text.insert(tk.END, f"   Soil fertility needs: {crop['soil_fertility']}\n")
            self.recommendations_text.insert(tk.END, "\n")

    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        try:
            self.root.mainloop()
        finally:
            # Ensure the event loop is stopped
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
                self.async_thread.join(timeout=1)

def main():
    """Main function to start the GUI application"""
    app = AgriWizGUI()
    app.run()

if __name__ == "__main__":
    main()