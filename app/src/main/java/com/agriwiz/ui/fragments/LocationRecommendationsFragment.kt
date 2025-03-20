package com.agriwiz.ui.fragments

import android.Manifest
import android.content.pm.PackageManager
import android.location.Geocoder
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.gms.location.LocationServices
import com.agriwiz.databinding.FragmentLocationRecommendationsBinding
import com.agriwiz.ui.viewmodels.LocationRecommendationViewModel
import com.agriwiz.ui.adapters.CropRecommendationsAdapter
import java.util.Locale

class LocationRecommendationsFragment : Fragment() {
    private var _binding: FragmentLocationRecommendationsBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: LocationRecommendationViewModel by viewModels()
    private lateinit var recommendationsAdapter: CropRecommendationsAdapter
    
    private val locationPermissionRequest = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            detectLocation()
        } else {
            Toast.makeText(
                requireContext(),
                "Location permission is required for automatic detection",
                Toast.LENGTH_LONG
            ).show()
        }
    }
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLocationRecommendationsBinding.inflate(inflater, container, false)
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
        val levels = arrayOf("low", "medium", "high")
        
        binding.humidityInput.setAdapter(
            ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, levels)
        )
        binding.soilFertilityInput.setAdapter(
            ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, levels)
        )
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
        
        viewModel.currentLocation.observe(viewLifecycleOwner) { location ->
            location?.let {
                binding.locationNameText.text = it
                binding.getRecommendationsButton.isEnabled = true
            }
        }
    }
    
    private fun setupClickListeners() {
        binding.detectLocationButton.setOnClickListener {
            checkLocationPermissionAndDetect()
        }
        
        binding.getRecommendationsButton.setOnClickListener {
            val humidity = binding.humidityInput.text.toString().takeIf { it.isNotEmpty() }
            val soilFertility = binding.soilFertilityInput.text.toString().takeIf { it.isNotEmpty() }
            
            viewModel.getRecommendations(humidity, soilFertility)
        }
    }
    
    private fun checkLocationPermissionAndDetect() {
        when {
            ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.ACCESS_FINE_LOCATION
            ) == PackageManager.PERMISSION_GRANTED -> {
                detectLocation()
            }
            else -> {
                locationPermissionRequest.launch(Manifest.permission.ACCESS_FINE_LOCATION)
            }
        }
    }
    
    private fun detectLocation() {
        val fusedLocationClient = LocationServices.getFusedLocationProviderClient(requireActivity())
        
        try {
            fusedLocationClient.lastLocation.addOnSuccessListener { location ->
                location?.let {
                    val geocoder = Geocoder(requireContext(), Locale.getDefault())
                    val addresses = geocoder.getFromLocation(it.latitude, it.longitude, 1)
                    
                    addresses?.firstOrNull()?.let { address ->
                        val locationName = buildString {
                            append(address.locality ?: address.subAdminArea ?: "")
                            append(", ")
                            append(address.adminArea ?: address.countryName ?: "")
                        }
                        viewModel.setLocation(locationName)
                    }
                }
            }
        } catch (e: SecurityException) {
            Toast.makeText(
                requireContext(),
                "Unable to access location. Please check permissions.",
                Toast.LENGTH_LONG
            ).show()
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
    
    companion object {
        fun newInstance() = LocationRecommendationsFragment()
    }
}