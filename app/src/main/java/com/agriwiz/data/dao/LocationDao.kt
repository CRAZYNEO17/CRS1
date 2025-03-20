package com.agriwiz.data.dao

import androidx.room.*
import com.agriwiz.data.model.Location
import kotlinx.coroutines.flow.Flow

@Dao
interface LocationDao {
    @Query("SELECT * FROM locations")
    fun getAllLocations(): Flow<List<Location>>
    
    @Query("SELECT * FROM locations WHERE locationName = :name")
    suspend fun getLocationByName(name: String): Location?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertLocation(location: Location)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAllLocations(locations: List<Location>)
    
    @Delete
    suspend fun deleteLocation(location: Location)
}