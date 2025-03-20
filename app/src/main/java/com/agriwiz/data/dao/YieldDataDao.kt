package com.agriwiz.data.dao

import androidx.room.*
import com.agriwiz.data.model.YieldData
import kotlinx.coroutines.flow.Flow

@Dao
interface YieldDataDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertYieldData(yieldData: YieldData)

    @Query("SELECT * FROM yield_data WHERE cropName = :cropName ORDER BY createdAt DESC")
    fun getYieldDataForCrop(cropName: String): Flow<List<YieldData>>

    @Query("SELECT * FROM yield_data WHERE location = :location ORDER BY createdAt DESC")
    fun getYieldDataForLocation(location: String): Flow<List<YieldData>>

    @Query("""
        SELECT * FROM yield_data 
        WHERE cropName = :cropName 
        AND location = :location 
        AND season = :season
        ORDER BY year DESC
    """)
    fun getHistoricalYieldData(
        cropName: String,
        location: String,
        season: String
    ): Flow<List<YieldData>>

    @Query("""
        SELECT AVG(actualYield) FROM yield_data
        WHERE cropName = :cropName
        AND location = :location
        AND season = :season
        AND year >= :startYear
    """)
    suspend fun getAverageYield(
        cropName: String,
        location: String,
        season: String,
        startYear: Int
    ): Float?

    @Query("""
        SELECT MAX(actualYield) FROM yield_data
        WHERE cropName = :cropName
        AND location = :location
    """)
    suspend fun getMaxYield(cropName: String, location: String): Float?

    @Query("SELECT DISTINCT cropName FROM yield_data ORDER BY cropName")
    fun getAllCrops(): Flow<List<String>>

    @Query("SELECT DISTINCT location FROM yield_data ORDER BY location")
    fun getAllLocations(): Flow<List<String>>

    @Query("DELETE FROM yield_data WHERE id = :id")
    suspend fun deleteYieldData(id: Long)

    @Query("""
        SELECT * FROM yield_data
        WHERE cropName = :cropName
        AND temperature BETWEEN :minTemp AND :maxTemp
        AND rainfall BETWEEN :minRain AND :maxRain
        AND humidity BETWEEN :minHumidity AND :maxHumidity
        ORDER BY actualYield DESC
        LIMIT 5
    """)
    suspend fun getBestConditions(
        cropName: String,
        minTemp: Float,
        maxTemp: Float,
        minRain: Float,
        maxRain: Float,
        minHumidity: Float,
        maxHumidity: Float
    ): List<YieldData>

    @Transaction
    @Query("""
        SELECT AVG(actualYield) as avgYield,
               AVG(temperature) as avgTemp,
               AVG(rainfall) as avgRain,
               AVG(humidity) as avgHumidity,
               AVG(soilPH) as avgPH,
               COUNT(*) as count
        FROM yield_data
        WHERE cropName = :cropName
        AND actualYield > (
            SELECT AVG(actualYield)
            FROM yield_data
            WHERE cropName = :cropName
        )
    """)
    suspend fun getOptimalConditions(cropName: String): OptimalConditions?

    @Query("""
        SELECT * FROM yield_data
        WHERE farmerId = :farmerId
        ORDER BY createdAt DESC
    """)
    fun getFarmerYieldHistory(farmerId: String): Flow<List<YieldData>>
}