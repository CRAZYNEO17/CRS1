package com.agriwiz.data.repository

import com.agriwiz.data.dao.LocationDao
import com.agriwiz.data.model.Location
import kotlinx.coroutines.flow.Flow
import org.json.JSONObject
import java.time.Month

class LocationRepository(private val locationDao: LocationDao) {
    val allLocations: Flow<List<Location>> = locationDao.getAllLocations()
    
    suspend fun insertLocation(location: Location) = locationDao.insertLocation(location)
    
    suspend fun insertAllLocations(locations: List<Location>) = locationDao.insertAllLocations(locations)
    
    suspend fun getLocationByName(name: String): Location? = locationDao.getLocationByName(name)
    
    suspend fun getCurrentSeasonForLocation(location: Location): String? {
        val currentMonth = Month.of(java.time.LocalDate.now().monthValue).name.lowercase()
        val seasonData = JSONObject(location.seasonData)
        
        for (season in seasonData.keys()) {
            val months = seasonData.getJSONArray(season)
            for (i in 0 until months.length()) {
                if (months.getString(i).lowercase() == currentMonth) {
                    return season
                }
            }
        }
        
        // Default seasons based on month if no specific mapping found
        return when (currentMonth) {
            "december", "january", "february" -> "winter"
            "march", "april", "may" -> "spring"
            "june", "july", "august" -> "summer"
            else -> "fall"
        }
    }
    
    suspend fun determineClimateMatch(cropClimate: String, locationClimate: String): String {
        val climateCompatibility = mapOf(
            "tropical" to mapOf(
                "tropical" to "excellent",
                "subtropical" to "good",
                "temperate" to "poor",
                "mediterranean" to "fair"
            ),
            "subtropical" to mapOf(
                "tropical" to "good",
                "subtropical" to "excellent",
                "temperate" to "fair",
                "mediterranean" to "good"
            ),
            "temperate" to mapOf(
                "tropical" to "poor",
                "subtropical" to "fair",
                "temperate" to "excellent",
                "mediterranean" to "good"
            ),
            "mediterranean" to mapOf(
                "tropical" to "fair",
                "subtropical" to "good",
                "temperate" to "good",
                "mediterranean" to "excellent"
            )
        )
        
        return climateCompatibility[cropClimate.lowercase()]
            ?.get(locationClimate.lowercase())
            ?: "poor"
    }
    
    suspend fun determineWaterAvailability(cropWaterNeeds: String, locationRainfall: String): String {
        val waterNeedsMapping = mapOf(
            "low" to mapOf(
                "low" to "medium",
                "medium" to "high",
                "high" to "high"
            ),
            "medium" to mapOf(
                "low" to "low",
                "medium" to "medium",
                "high" to "high"
            ),
            "high" to mapOf(
                "low" to "low",
                "medium" to "low",
                "high" to "medium"
            )
        )
        
        return waterNeedsMapping[cropWaterNeeds.lowercase()]
            ?.get(locationRainfall.lowercase())
            ?: "medium"
    }
}