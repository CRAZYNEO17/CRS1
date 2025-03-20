package com.agriwiz.data.model

data class OptimalConditions(
    val avgYield: Float,
    val avgTemp: Float,
    val avgRain: Float,
    val avgHumidity: Float,
    val avgPH: Float,
    val count: Int
) {
    fun toMap() = mapOf(
        "Average Yield" to "$avgYield qt/ha",
        "Average Temperature" to "$avgTemp°C",
        "Average Rainfall" to "$avgRain mm",
        "Average Humidity" to "$avgHumidity%",
        "Average Soil pH" to avgPH.toString(),
        "Sample Size" to count.toString()
    )
}