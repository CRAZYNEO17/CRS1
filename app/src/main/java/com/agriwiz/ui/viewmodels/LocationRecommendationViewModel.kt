package com.agriwiz.ui.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.agriwiz.data.AgriWizDatabase
import com.agriwiz.data.model.Crop
import com.agriwiz.data.model.Location
import com.agriwiz.data.repository.CropRepository
import com.agriwiz.data.repository.LocationRepository
import kotlinx.coroutines.launch

class LocationRecommendationViewModel(application: Application) : AndroidViewModel(application) {
    private val cropRepository: CropRepository
    private val locationRepository: LocationRepository
    
    private val _recommendations = MutableLiveData<List<Crop>>()
    val recommendations: LiveData<List<Crop>> = _recommendations
    
    private val _currentLocation = MutableLiveData<String>()
    val currentLocation: LiveData<String> = _currentLocation
    
    private var currentLocationData: Location? = null
    
    init {
        val database = AgriWizDatabase.getDatabase(application)
        cropRepository = CropRepository(database.cropDao())
        locationRepository = LocationRepository(database.locationDao())
    }
    
    fun setLocation(locationName: String) {
        viewModelScope.launch {
            locationRepository.getLocationByName(locationName)?.let { location ->
                currentLocationData = location
                _currentLocation.value = locationName
            }
        }
    }
    
    fun getRecommendations(humidity: String?, soilFertility: String?) {
        viewModelScope.launch {
            currentLocationData?.let { location ->
                val season = locationRepository.getCurrentSeasonForLocation(location)
                
                val crops = cropRepository.getRecommendations(
                    soilType = location.commonSoilTypes.split(",")[0].trim(),
                    climate = location.climate,
                    season = season ?: "summer",
                    humidity = humidity ?: location.humidity,
                    soilFertility = soilFertility
                )
                
                _recommendations.value = crops
            }
        }
    }
    
    fun estimateYield(
        crop: Crop,
        soilFertility: String,
        landArea: Double
    ) = viewModelScope.launch {
        currentLocationData?.let { location ->
            val climateMatch = locationRepository.determineClimateMatch(
                crop.climates.split(",")[0].trim(),
                location.climate
            )
            
            val waterAvailability = locationRepository.determineWaterAvailability(
                crop.waterNeeds,
                location.rainfall
            )
            
            cropRepository.estimateYield(
                crop = crop,
                soilFertility = soilFertility,
                waterAvailability = waterAvailability,
                climateMatch = climateMatch,
                farmManagement = 0.8, // Default to good management
                landArea = landArea
            )
        }
    }
}