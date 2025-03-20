package com.agriwiz.data.dao

import androidx.room.*
import com.agriwiz.data.model.Crop
import kotlinx.coroutines.flow.Flow

@Dao
interface CropDao {
    @Query("SELECT * FROM crops")
    fun getAllCrops(): Flow<List<Crop>>
    
    @Query("SELECT * FROM crops WHERE cropName = :name")
    suspend fun getCropByName(name: String): Crop?
    
    @Query("""
        SELECT * FROM crops 
        WHERE soilTypes LIKE '%' || :soilType || '%'
        AND climates LIKE '%' || :climate || '%'
        AND seasons LIKE '%' || :season || '%'
        AND (:humidity IS NULL OR humidityPreference LIKE '%' || :humidity || '%')
        AND (:soilFertility IS NULL OR soilFertility LIKE '%' || :soilFertility || '%')
    """)
    suspend fun getRecommendedCrops(
        soilType: String,
        climate: String,
        season: String,
        humidity: String? = null,
        soilFertility: String? = null
    ): List<Crop>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCrop(crop: Crop)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAllCrops(crops: List<Crop>)
    
    @Delete
    suspend fun deleteCrop(crop: Crop)
}