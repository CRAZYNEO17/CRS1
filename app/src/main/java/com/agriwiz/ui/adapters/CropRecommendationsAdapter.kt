package com.agriwiz.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.agriwiz.data.model.Crop
import com.agriwiz.databinding.ItemCropRecommendationBinding

class CropRecommendationsAdapter : ListAdapter<Crop, CropRecommendationsAdapter.ViewHolder>(CropDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemCropRecommendationBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(
        private val binding: ItemCropRecommendationBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(crop: Crop) {
            binding.apply {
                cropNameText.text = crop.cropName
                waterNeedsText.text = "Water needs: ${crop.waterNeeds}"
                humidityText.text = "Humidity: ${crop.humidityPreference}"
                soilFertilityText.text = "Soil fertility: ${crop.soilFertility}"
                soilTypesText.text = "Soil types: ${crop.soilTypes}"
                climatesText.text = "Climates: ${crop.climates}"
                seasonsText.text = "Seasons: ${crop.seasons}"
            }
        }
    }

    private class CropDiffCallback : DiffUtil.ItemCallback<Crop>() {
        override fun areItemsTheSame(oldItem: Crop, newItem: Crop): Boolean {
            return oldItem.cropName == newItem.cropName
        }

        override fun areContentsTheSame(oldItem: Crop, newItem: Crop): Boolean {
            return oldItem == newItem
        }
    }
}