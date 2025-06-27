import json
import os
from typing import List, Dict, Optional

class SchemeManager:
    def __init__(self):
        self.schemes_data = {}
        self.load_schemes()
    
    def load_schemes(self):
        """Load schemes data from JSON file."""
        try:
            with open("data/raw/agricultural_schemes.json", "r") as file:
                self.schemes_data = json.load(file)
        except Exception as e:
            print(f"Error loading schemes data: {e}")
            self.schemes_data = {"schemes": [], "state_specific_schemes": {}, "subsidy_rates": {}}
    
    def get_relevant_schemes(self, crop_name: str, state: str, land_area: float = None) -> List[Dict]:
        """Get relevant schemes for a given crop and state."""
        relevant_schemes = []
        
        # Check national schemes
        for scheme in self.schemes_data.get("schemes", []):
            # Add schemes that are relevant for all crops
            if scheme["name"] in ["PM-KISAN", "PMFBY", "KCC"]:
                relevant_schemes.append(scheme)
            
            # Add PMKSY for crops with high water needs
            elif scheme["name"] == "PMKSY":
                relevant_schemes.append(scheme)
            
            # Add PKVY for organic farming potential
            elif scheme["name"] == "PKVY":
                relevant_schemes.append(scheme)
            
            # Add NFSM for food crops
            elif scheme["name"] == "NFSM":
                if crop_name.lower() in ["rice", "wheat", "pulses", "maize", "barley"]:
                    relevant_schemes.append(scheme)
        
        # Add state-specific schemes
        state_schemes = self.schemes_data.get("state_specific_schemes", {}).get(state.lower(), [])
        relevant_schemes.extend(state_schemes)
        
        return relevant_schemes
    
    def get_subsidy_info(self, category: str, subcategory: str = None) -> Optional[str]:
        """Get subsidy information for a specific category."""
        subsidy_rates = self.schemes_data.get("subsidy_rates", {})
        
        if category in subsidy_rates:
            if subcategory and subcategory in subsidy_rates[category]:
                return subsidy_rates[category][subcategory]
            return subsidy_rates[category]
        return None
    
    def get_scheme_details(self, scheme_name: str) -> Optional[Dict]:
        """Get detailed information about a specific scheme."""
        # Check national schemes
        for scheme in self.schemes_data.get("schemes", []):
            if scheme["name"].lower() == scheme_name.lower():
                return scheme
        
        # Check state schemes
        for state_schemes in self.schemes_data.get("state_specific_schemes", {}).values():
            for scheme in state_schemes:
                if scheme["name"].lower() == scheme_name.lower():
                    return scheme
        
        return None
    
    def get_all_schemes(self) -> List[Dict]:
        """Get list of all available schemes."""
        all_schemes = self.schemes_data.get("schemes", []).copy()
        
        # Add state schemes
        for state_schemes in self.schemes_data.get("state_specific_schemes", {}).values():
            all_schemes.extend(state_schemes)
        
        return all_schemes

    def get_schemes_by_category(self, category: str) -> List[Dict]:
        """Get schemes by category (e.g., 'irrigation', 'insurance', 'credit')."""
        schemes = []
        categories = {
            'irrigation': ['PMKSY'],
            'insurance': ['PMFBY'],
            'credit': ['KCC'],
            'income_support': ['PM-KISAN'],
            'organic_farming': ['PKVY'],
            'marketing': ['eNAM'],
            'food_security': ['NFSM']
        }
        
        if category in categories:
            scheme_names = categories[category]
            for scheme in self.schemes_data.get("schemes", []):
                if scheme["name"] in scheme_names:
                    schemes.append(scheme)
        
        return schemes

    def get_categories(self) -> List[str]:
        """Get list of all available scheme categories."""
        return [
            'irrigation',
            'insurance',
            'credit',
            'income_support',
            'organic_farming',
            'marketing',
            'food_security'
        ]

    def get_eligible_schemes(self, farmer_details: Dict) -> List[Dict]:
        """Get schemes that a farmer is eligible for based on their details."""
        eligible_schemes = []
        
        for scheme in self.schemes_data.get("schemes", []):
            is_eligible = True
            
            # Check PM-KISAN eligibility
            if scheme["name"] == "PM-KISAN":
                if not farmer_details.get("land_ownership"):
                    is_eligible = False
            
            # Check PMFBY eligibility
            elif scheme["name"] == "PMFBY":
                if not farmer_details.get("has_bank_account"):
                    is_eligible = False
            
            # Add more eligibility checks for other schemes
            
            if is_eligible:
                eligible_schemes.append(scheme)
        
        # Check state-specific schemes
        state = farmer_details.get("state", "").lower()
        if state in self.schemes_data.get("state_specific_schemes", {}):
            eligible_schemes.extend(self.schemes_data["state_specific_schemes"][state])
        
        return eligible_schemes
        
    def get_schemes_for_state(self, state: str) -> List[Dict]:
        """Get schemes specific to a state plus national schemes.
        
        Args:
            state: The name of the state (case-insensitive)
            
        Returns:
            A list of scheme dictionaries applicable to the state
        """
        # Normalize state name to lowercase for case-insensitive comparison
        state_lower = state.lower()
        
        # Get all national schemes
        national_schemes = self.schemes_data.get("schemes", [])
        
        # Get state-specific schemes if available
        state_specific_schemes = self.schemes_data.get("state_specific_schemes", {}).get(state_lower, [])
        
        # Combine national and state-specific schemes
        all_applicable_schemes = national_schemes + state_specific_schemes
        
        return all_applicable_schemes
