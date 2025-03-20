package com.agriwiz.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "crops")
data class Crop(
    @PrimaryKey val cropName: String,
    val soilTypes: String,
    val climates: String,
    val seasons: String,
    val waterNeeds: String,
    val humidityPreference: String,
    val soilFertility: String,
    val baseYieldMin: Double,
    val baseYieldMax: Double,
    val yieldUnit: String = "tons"
)