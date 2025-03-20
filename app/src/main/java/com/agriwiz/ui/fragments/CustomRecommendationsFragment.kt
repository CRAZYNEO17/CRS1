package com.agriwiz.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.agriwiz.databinding.FragmentCustomRecommendationsBinding
import com.agriwiz.ui.viewmodels.CropRecommendationViewModel
import com.agriwiz.ui.adapters.CropRecommendationsAdapter

class CustomRecommendationsFragment : Fragment() {
    private var _binding: FragmentCustomRecommendationsBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: CropRecommendationViewModel by viewModels()
    private lateinit var recommendationsAdapter: CropRecommendationsAdapter
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCustomRecommendationsBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupDropdowns()
        setupRecyclerView()
        setupObservers()
        setupClickListeners()
    }
    
    private fun setupDropdowns() {
        val soilTypes = arrayOf("clay", "loamy", "sandy", "black soil", "alluvial", "laterite")
        val climates = arrayOf("tropical", "subtropical", "temperate", "mediterranean")
        val seasons = arrayOf("summer", "winter", "rainy", "spring", "fall")
        val levels = arrayOf("low", "medium", "high")
        
        binding.soilTypeInput.setAdapter(ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, soilTypes))
        binding.climateInput.setAdapter(ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, climates))
        binding.seasonInput.setAdapter(ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, seasons))
        binding.rainfallInput.setAdapter(ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, levels))
        binding.humidityInput.setAdapter(ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, levels))
        binding.soilFertilityInput.setAdapter(ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, levels))
    }
    
    private fun setupRecyclerView() {
        recommendationsAdapter = CropRecommendationsAdapter()
        binding.recommendationsRecyclerView.apply {
            adapter = recommendationsAdapter
            layoutManager = LinearLayoutManager(context)
        }
    }
    
    private fun setupObservers() {
        viewModel.recommendations.observe(viewLifecycleOwner) { crops ->
            binding.recommendationsRecyclerView.visibility = if (crops.isNotEmpty()) View.VISIBLE else View.GONE
            recommendationsAdapter.submitList(crops)
        }
    }
    
    private fun setupClickListeners() {
        binding.getRecommendationsButton.setOnClickListener {
            val soilType = binding.soilTypeInput.text.toString()
            val climate = binding.climateInput.text.toString()
            val season = binding.seasonInput.text.toString()
            val rainfall = binding.rainfallInput.text.toString().takeIf { it.isNotEmpty() }
            val humidity = binding.humidityInput.text.toString().takeIf { it.isNotEmpty() }
            val soilFertility = binding.soilFertilityInput.text.toString().takeIf { it.isNotEmpty() }
            
            viewModel.getRecommendations(
                soilType = soilType,
                climate = climate,
                season = season,
                rainfall = rainfall,
                humidity = humidity,
                soilFertility = soilFertility
            )
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
    
    companion object {
        fun newInstance() = CustomRecommendationsFragment()
    }
}