package com.agriwiz

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.google.android.material.tabs.TabLayoutMediator
import com.agriwiz.databinding.ActivityMainBinding
import com.agriwiz.ui.fragments.CustomRecommendationsFragment
import com.agriwiz.ui.fragments.LocationRecommendationsFragment

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setSupportActionBar(binding.toolbar)
        
        setupViewPager()
        setupTabs()
    }
    
    private fun setupViewPager() {
        binding.viewPager.adapter = MainPagerAdapter(this)
    }
    
    private fun setupTabs() {
        TabLayoutMediator(binding.tabLayout, binding.viewPager) { tab, position ->
            tab.text = when (position) {
                0 -> "Custom"
                1 -> "Location"
                else -> throw IllegalStateException("Invalid tab position $position")
            }
        }.attach()
    }
}

private class MainPagerAdapter(activity: FragmentActivity) : FragmentStateAdapter(activity) {
    override fun getItemCount() = 2
    
    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> CustomRecommendationsFragment.newInstance()
            1 -> LocationRecommendationsFragment.newInstance()  // Now using proper fragment
            else -> throw IllegalStateException("Invalid position $position")
        }
    }
}