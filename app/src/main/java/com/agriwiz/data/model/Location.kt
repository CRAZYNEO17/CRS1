package com.agriwiz.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "locations")
data class Location(
    @PrimaryKey val locationName: String,
    val commonSoilTypes: String, // Stored as comma-separated string
    val climate: String,
    val rainfall: String,
    val humidity: String?,
    val seasonData: String // JSON string of season to months mapping
)