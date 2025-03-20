# Add project specific ProGuard rules here.
# Room
-keep class * extends androidx.room.RoomDatabase
-dontwarn androidx.room.paging.**

# OpenCSV
-keepattributes Signature
-keep class com.opencsv.** { *; }

# Model classes
-keep class com.agriwiz.data.model.** { *; }