package com.agriwiz.data.repository

import com.agriwiz.data.dao.CropDao
import com.agriwiz.data.model.Crop
import kotlinx.coroutines.flow.Flow
import org.json.JSONObject

class CropRepository(private val cropDao: CropDao) {
    val allCrops: Flow<List<Crop>> = cropDao.getAllCrops()
    
    suspend fun insertCrop(crop: Crop) = cropDao.insertCrop(crop)
    
    suspend fun insertAllCrops(crops: List<Crop>) = cropDao.insertAllCrops(crops)
    
    suspend fun getRecommendations(
        soilType: String,
        climate: String,
        season: String,
        humidity: String? = null,
        soilFertility: String? = null
    ): List<Crop> {
        return cropDao.getRecommendedCrops(soilType, climate, season, humidity, soilFertility)
    }
    
    suspend fun estimateYield(
        crop: Crop,
        soilFertility: String,
        waterAvailability: String,
        climateMatch: String,
        farmManagement: Double,
        landArea: Double
    ): YieldEstimate {
        // Soil fertility factors
        val soilFactor = when (soilFertility) {
            "low" -> 0.7
            "medium" -> 1.0
            "high" -> 1.3
            else -> 1.0
        }
        
        // Water availability factors
        val waterFactor = when (waterAvailability) {
            "low" -> 0.6
            "medium" -> 1.0
            "high" -> 1.2
            else -> 1.0
        }
        
        // Climate match factors
        val climateFactor = when (climateMatch) {
            "poor" -> 0.6
            "fair" -> 0.9
            "good" -> 1.0
            "excellent" -> 1.2
            else -> 0.9
        }
        
        // Calculate combined factor
        val combinedFactor = soilFactor * waterFactor * climateFactor
        
        // Calculate yields
        val adjustedMinYield = crop.baseYieldMin * combinedFactor * 0.9
        val adjustedMaxYield = crop.baseYieldMax * combinedFactor * 1.1
        
        // Calculate expected yield based on farm management
        val normalizedManagement = farmManagement.coerceIn(0.0, 1.0)
        val expectedYield = adjustedMinYield + normalizedManagement * (adjustedMaxYield - adjustedMinYield)
        
        // Calculate total yield for given land area
        val totalYield = expectedYield * landArea
        
        return YieldEstimate(
            cropName = crop.cropName,
            yieldPerHectare = expectedYield,
            totalYield = totalYield,
            yieldRange = YieldRange(
                low = totalYield * 0.8,
                expected = totalYield,
                high = totalYield * 1.2
            ),
            landArea = landArea,
            unit = crop.yieldUnit,
            factors = YieldFactors(
                soilFertility = soilFertility,
                soilFactor = soilFactor,
                waterAvailability = waterAvailability,
                waterFactor = waterFactor,
                climateMatch = climateMatch,
                climateFactor = climateFactor,
                farmManagement = farmManagement,
                combinedFactor = combinedFactor
            )
        )
    }
}

data class YieldEstimate(
    val cropName: String,
    val yieldPerHectare: Double,
    val totalYield: Double,
    val yieldRange: YieldRange,
    val landArea: Double,
    val unit: String,
    val factors: YieldFactors
)

data class YieldRange(
    val low: Double,
    val expected: Double,
    val high: Double
)

data class YieldFactors(
    val soilFertility: String,
    val soilFactor: Double,
    val waterAvailability: String,
    val waterFactor: Double,
    val climateMatch: String,
    val climateFactor: Double,
    val farmManagement: Double,
    val combinedFactor: Double
)