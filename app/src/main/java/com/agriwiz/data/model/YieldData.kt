package com.agriwiz.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "yield_data")
data class YieldData(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val cropName: String,
    val location: String,
    val season: String,
    val year: Int,
    val actualYield: Float,
    val temperature: Float,
    val rainfall: Float,
    val humidity: Float,
    val soilPH: Float,
    val soilFertility: String,
    val waterAvailability: String,
    val farmerId: String? = null,
    val notes: String? = null,
    val createdAt: Long = System.currentTimeMillis()
)