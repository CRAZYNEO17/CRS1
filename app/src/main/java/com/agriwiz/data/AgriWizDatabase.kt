package com.agriwiz.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.agriwiz.data.dao.CropDao
import com.agriwiz.data.dao.LocationDao
import com.agriwiz.data.dao.YieldDataDao
import com.agriwiz.data.model.Crop
import com.agriwiz.data.model.Location
import com.agriwiz.data.model.YieldData

@Database(
    entities = [
        Crop::class,
        Location::class,
        YieldData::class
    ],
    version = 1,
    exportSchema = false
)
abstract class AgriWizDatabase : RoomDatabase() {
    abstract fun cropDao(): CropDao
    abstract fun locationDao(): LocationDao
    abstract fun yieldDataDao(): YieldDataDao
    
    companion object {
        @Volatile
        private var INSTANCE: AgriWizDatabase? = null
        
        fun getDatabase(context: Context): AgriWizDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AgriWizDatabase::class.java,
                    "agriwiz_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}