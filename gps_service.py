#!/usr/bin/env python
import asyncio
import time
import logging
import os
from typing import Dict, Optional

try:
    import winsdk.windows.devices.geolocation as geo
    HAS_WINDOWS_LOCATION = True
except ImportError:
    HAS_WINDOWS_LOCATION = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPSService:
    """Windows GPS Location Service Handler"""
    def __init__(self, loop=None):
        self.geolocator = None
        self.loop = loop or asyncio.get_event_loop()
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up detailed logging"""
        global logger
        logger.setLevel(logging.DEBUG)
        # Add file handler for debugging
        fh = logging.FileHandler('gps_debug.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    async def _init_geolocator(self) -> bool:
        """Initialize Windows Geolocator if not already initialized"""
        if not self.geolocator:
            try:
                if not HAS_WINDOWS_LOCATION:
                    logger.error("Windows Location API not available")
                    return False
                    
                # Try to create Geolocator instance
                self.geolocator = geo.Geolocator()
                
                # Set desired accuracy to optimize for speed vs precision
                self.geolocator.desired_accuracy = geo.PositionAccuracy.DEFAULT
                
                logger.info("Successfully created Geolocator instance with default accuracy")
                return True
            except Exception as e:
                logger.error(f"Error initializing Windows Geolocator: {str(e)}")
                return False
        return True

    async def get_location(self) -> Optional[Dict]:
        """Get location using Windows Location API"""
        try:
            logger.debug("Starting location detection")
            if await self._init_geolocator():
                try:
                    import winsdk.windows.devices.geolocation as geo
                    
                    # Request location access with timeout
                    logger.debug("Requesting location access")
                    async with asyncio.timeout(5):  # 5 second timeout
                        status = await self.geolocator.request_access_async()
                        logger.debug(f"Location access status: {status}")
                    
                    if status == geo.GeolocationAccessStatus.ALLOWED:
                        try:
                            # Get position with timeout
                            logger.debug("Getting position")
                            async with asyncio.timeout(10):  # 10 second timeout
                                position = await self.geolocator.get_geoposition_async()
                            
                            if position and position.coordinate:
                                logger.info("Successfully obtained position")
                                return {
                                    "latitude": position.coordinate.latitude,
                                    "longitude": position.coordinate.longitude,
                                    "accuracy": position.coordinate.accuracy if hasattr(position.coordinate, 'accuracy') else None,
                                    "altitude": position.coordinate.altitude if hasattr(position.coordinate, 'altitude') else None,
                                    "source": "windows_gps",
                                    "timestamp": time.time()
                                }
                            else:
                                logger.error("No coordinate data in position response")
                                logger.error("This might mean no GPS or Wi-Fi positioning is available")
                                return None
                        except asyncio.TimeoutError:
                            logger.error("Timeout while getting position (10s)")
                            logger.error("Location services might be slow or unresponsive")
                            return None
                        except AttributeError as e:
                            logger.error(f"Attribute error accessing position data: {str(e)}")
                            logger.error("Location data format was unexpected")
                            return None
                        except Exception as e:
                            logger.error(f"Error getting position: {str(e)}")
                            return None
                    elif status == geo.GeolocationAccessStatus.DENIED:
                        logger.error("Location access denied by system or user")
                        logger.error("Please check Windows location privacy settings")
                        return None
                    elif status == geo.GeolocationAccessStatus.UNSPECIFIED:
                        logger.error("Unspecified error getting location access")
                        logger.error("This might mean location services are disabled")
                        return None
                    else:
                        logger.error(f"Unknown location access status: {status}")
                        return None
                except asyncio.TimeoutError:
                    logger.error("Timeout while requesting location access (5s)")
                    logger.error("Windows location services might be unresponsive")
                    return None
                except Exception as e:
                    logger.error(f"Error accessing location: {str(e)}")
                    return None
            else:
                logger.error("Failed to initialize Windows Geolocator")
                return None
        except Exception as e:
            logger.error(f"Error in get_location: {str(e)}")
            return None

async def main():
    """Test the GPS Service"""
    gps = GPSService()
    
    # Try to get location
    location = await gps.get_location()
    
    if location:
        print(f"Location obtained:")
        print(f"Latitude: {location['latitude']}")
        print(f"Longitude: {location['longitude']}")
        if location.get('accuracy'):
            print(f"Accuracy: {location['accuracy']}m")
        if location.get('altitude'):
            print(f"Altitude: {location['altitude']}m")
        print(f"Source: {location['source']}")
    else:
        print("Could not get location")

if __name__ == "__main__":
    asyncio.run(main())