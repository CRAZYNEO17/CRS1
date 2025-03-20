package com.agriwiz.ui.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.agriwiz.data.AgriWizDatabase
import com.agriwiz.data.model.Crop
import com.agriwiz.data.repository.CropRepository
import kotlinx.coroutines.launch

class CropRecommendationViewModel(application: Application) : AndroidViewModel(application) {
    private val cropRepository: CropRepository
    
    private val _recommendations = MutableLiveData<List<Crop>>()
    val recommendations: LiveData<List<Crop>> = _recommendations
    
    init {
        val database = AgriWizDatabase.getDatabase(application)
        cropRepository = CropRepository(database.cropDao())
    }
    
    fun getRecommendations(
        soilType: String,
        climate: String,
        season: String,
        rainfall: String? = null,
        humidity: String? = null,
        soilFertility: String? = null
    ) {
        viewModelScope.launch {
            val crops = cropRepository.getRecommendations(
                soilType = soilType,
                climate = climate,
                season = season,
                humidity = humidity,
                soilFertility = soilFertility
            )
            _recommendations.value = crops
        }
    }
    
    fun estimateYield(
        crop: Crop,
        soilFertility: String,
        waterAvailability: String,
        climateMatch: String,
        farmManagement: Double,
        landArea: Double
    ) = viewModelScope.launch {
        val estimate = cropRepository.estimateYield(
            crop = crop,
            soilFertility = soilFertility,
            waterAvailability = waterAvailability,
            climateMatch = climateMatch,
            farmManagement = farmManagement,
            landArea = landArea
        )
        // Handle yield estimate result if needed
    }
}