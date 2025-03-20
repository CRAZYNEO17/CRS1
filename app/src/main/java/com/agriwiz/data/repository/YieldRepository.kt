package com.agriwiz.data.repository

import com.agriwiz.data.dao.YieldDataDao
import com.agriwiz.data.model.YieldData
import com.agriwiz.data.model.OptimalConditions
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class YieldRepository @Inject constructor(
    private val yieldDataDao: YieldDataDao
) {
    suspend fun addYieldRecord(yieldData: YieldData) {
        withContext(Dispatchers.IO) {
            yieldDataDao.insertYieldData(yieldData)
            updateMLModel(yieldData)
        }
    }
    
    private suspend fun updateMLModel(yieldData: YieldData) {
        // Convert YieldData to ML model format
        val features = arrayOf(
            yieldData.temperature,
            yieldData.rainfall,
            yieldData.humidity,
            yieldData.soilPH,
            when (yieldData.soilFertility.lowercase()) {
                "low" -> 1f
                "medium" -> 2f
                else -> 3f
            },
            when (yieldData.waterAvailability.lowercase()) {
                "low" -> 1f
                "medium" -> 2f
                else -> 3f
            },
            when (yieldData.season.lowercase()) {
                "spring" -> 1f
                "summer" -> 2f
                "fall" -> 3f
                else -> 4f
            }
        )
        
        // Update ML model with new data point
        val modelData = mapOf(
            "features" to listOf(features.toList()),
            "yields" to listOf(yieldData.actualYield)
        )
        
        // Call Python ML model update via JNI
        try {
            System.loadLibrary("yield_estimator")
            updateModel(yieldData.cropName, modelData)
        } catch (e: Exception) {
            // Log error but don't crash
            e.printStackTrace()
        }
    }

    fun getHistoricalData(
        cropName: String,
        location: String,
        season: String
    ): Flow<List<YieldData>> = yieldDataDao.getHistoricalYieldData(cropName, location, season)

    suspend fun getOptimalGrowingConditions(cropName: String): OptimalConditions? =
        withContext(Dispatchers.IO) {
            yieldDataDao.getOptimalConditions(cropName)
        }

    suspend fun getBestPerformingConditions(
        cropName: String,
        tempRange: Pair<Float, Float>,
        rainRange: Pair<Float, Float>,
        humidityRange: Pair<Float, Float>
    ): List<YieldData> = withContext(Dispatchers.IO) {
        yieldDataDao.getBestConditions(
            cropName = cropName,
            minTemp = tempRange.first,
            maxTemp = tempRange.second,
            minRain = rainRange.first,
            maxRain = rainRange.second,
            minHumidity = humidityRange.first,
            maxHumidity = humidityRange.second
        )
    }

    suspend fun getAverageYield(
        cropName: String,
        location: String,
        season: String,
        startYear: Int
    ): Float = withContext(Dispatchers.IO) {
        yieldDataDao.getAverageYield(cropName, location, season, startYear) ?: 0f
    }

    fun getFarmerYieldHistory(farmerId: String): Flow<List<YieldData>> =
        yieldDataDao.getFarmerYieldHistory(farmerId)

    private external fun updateModel(cropName: String, modelData: Map<String, List<Any>>)
}