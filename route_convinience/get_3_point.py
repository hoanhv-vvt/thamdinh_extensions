import requests
from datetime import datetime
import os
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RouteCalculator:
    """
    Class to handle geocoding, distance calculation, and travel time estimation
    using Goong Maps API (Vietnam mapping service).
    """
    
    def __init__(self, api_key):
        """
        Initialize the RouteCalculator with Goong Maps API key.
        
        Args:
            api_key (str): Your Goong Maps API key
        """
        self.api_key = api_key
        self.geocode_url = "https://rsapi.goong.io/geocode"
        self.distance_matrix_url = "https://rsapi.goong.io/DistanceMatrix"
    
    def geocode_address(self, address):
        """
        Convert text address to coordinates (latitude, longitude).
        
        Args:
            address (str): Text address to geocode
            
        Returns:
            dict: Dictionary containing address and coordinates
                  {'address': str, 'lat': float, 'lng': float}
        """
        try:
            # URL encode the address
            params = {
                'address': address,
                'api_key': self.api_key
            }
            
            response = requests.get(self.geocode_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                result = data['results'][0]
                location = result['geometry']['location']
                formatted_address = result.get('formatted_address', address)
                
                return {
                    'address': formatted_address,
                    'lat': location['lat'],
                    'lng': location['lng']
                }
            else:
                print(f"Không tìm thấy tọa độ cho địa chỉ: {address}")
                return None
                
        except Exception as e:
            print(f"Lỗi khi geocode địa chỉ '{address}': {str(e)}")
            return None
    
    def geocode_multiple_addresses(self, addresses):
        """
        Geocode multiple addresses.
        
        Args:
            addresses (list): List of text addresses
            
        Returns:
            list: List of geocoded results
        """
        results = []
        for i, address in enumerate(addresses, 1):
            result = self.geocode_address(address)
            if result:
                results.append(result)
            else:
                results.append(None)
        
        return results
    
    def calculate_distance_matrix(self, origins, destinations, vehicle='car'):
        """
        Calculate distance and travel time between multiple origins and destinations.
        
        Args:
            origins (list): List of origin coordinates as tuples (lat, lng)
            destinations (list): List of destination coordinates as tuples (lat, lng)
            vehicle (str): Vehicle type - 'car', 'bike', 'taxi', 'truck', 'hd'
            
        Returns:
            dict: Distance matrix results
        """
        try:
            # Format origins and destinations as "lat,lng" strings
            origins_str = '|'.join([f"{lat},{lng}" for lat, lng in origins])
            destinations_str = '|'.join([f"{lat},{lng}" for lat, lng in destinations])
            
            params = {
                'origins': origins_str,
                'destinations': destinations_str,
                'vehicle': vehicle,
                'api_key': self.api_key
            }
            
            response = requests.get(self.distance_matrix_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            print(f"Lỗi khi tính khoảng cách: {str(e)}")
            return None
    
    def get_distances_and_times(self, location1, location2, location3, vehicle='bike'):
        """
        Simplified function: Get 3 distances (km) and 3 times (minutes) for 3 locations.
        
        Args:
            location1, location2, location3: Dictionaries with 'lat' and 'lng'
            vehicle (str): Vehicle type - 'car', 'bike', 'taxi', 'truck', 'hd'
            
        Returns:
            tuple: (distances, times) where:
                - distances: dict with keys '1->2', '2->3', '1->3' (values in km)
                - times: dict with keys '1->2', '2->3', '1->3' (values in minutes)
            Returns (None, None) if error occurs
        """
        if not all([location1, location2, location3]):
            print("Lỗi: Một hoặc nhiều địa chỉ không có tọa độ hợp lệ")
            return None, None
        
        # Create coordinate tuples
        coord1 = (location1['lat'], location1['lng'])
        coord2 = (location2['lat'], location2['lng'])
        coord3 = (location3['lat'], location3['lng'])
        
        # Calculate all pairwise distances
        route_1_2 = self.calculate_single_route(coord1, coord2, vehicle)
        route_2_3 = self.calculate_single_route(coord2, coord3, vehicle)
        route_1_3 = self.calculate_single_route(coord1, coord3, vehicle)
        
        # Check if all routes were calculated successfully
        if not all([route_1_2, route_2_3, route_1_3]):
            print("Lỗi: Không thể tính toán tuyến đường")
            return None, None
        
        # Extract distances (km) and times (minutes)
        distances = {
            '1->2': route_1_2['distance'],
            '2->3': route_2_3['distance'],
            '1->3': route_1_3['distance']
        }
        
        times = {
            '1->2': round(route_1_2['duration_seconds'] / 60, 1),
            '2->3': round(route_2_3['duration_seconds'] / 60, 1),
            '1->3': round(route_1_3['duration_seconds'] / 60, 1)
        }
        
        return distances, times
    
    def calculate_single_route(self, origin, destination, vehicle='car'):
        """
        Calculate distance and time for a single route.
        
        Args:
            origin: Tuple (lat, lng)
            destination: Tuple (lat, lng)
            vehicle: Vehicle type
            
        Returns:
            dict: Route information
        """
        result = self.calculate_distance_matrix([origin], [destination], vehicle)
        
        if result and 'rows' in result and len(result['rows']) > 0:
            elements = result['rows'][0].get('elements', [])
            if elements and elements[0].get('status') == 'OK':
                element = elements[0]
                
                distance_meters = element['distance']['value']
                distance_km = distance_meters / 1000
                
                duration_seconds = element['duration']['value']
                duration_text = element['duration']['text']
                
                return {
                    'distance': round(distance_km, 2),
                    'distance_text': element['distance']['text'],
                    'duration': duration_text,
                    'duration_seconds': duration_seconds
                }
        
        return None
  
    def get_location_n_time(self, work_location, home_location, gym_location):
        addressed = [work_location, home_location, gym_location]
        locations = self.geocode_multiple_addresses(addressed)
        
        if all(locations):
            work_location = locations[0]
            home_location = locations[1]
            gym_location = locations[2]
            
            distances, times = self.get_distances_and_times(
                work_location, 
                home_location, 
                gym_location,
                vehicle='bike'
            )
            
            if distances and times:
                dis_workhome = distances['1->2']
                time_workhome = times['1->2']
                
                dis_homegym = distances['2->3']
                time_homegym = times['2->3']
                
                dis_workgym = distances['1->3']
                time_workgym = times['1->3']
                
                return dis_workhome, time_workhome, dis_homegym, time_homegym, dis_workgym, time_workgym
        
        return None

def calculate_points_G_n_T(dis_workhome, time_workhome, dis_homegym, time_homegym, dis_workgym, time_workgym, max_scale=5):
    """
    Tính điểm đánh giá dựa trên khoảng cách và thời gian.
    
    Args:
        dis_workhome: Khoảng cách Work -> Home (km)
        time_workhome: Thời gian Work -> Home (phút)
        dis_homegym: Khoảng cách Home -> Gym (km)
        time_homegym: Thời gian Home -> Gym (phút)
        dis_workgym: Khoảng cách Work -> Gym (km)
        time_workgym: Thời gian Work -> Gym (phút)
        max_scale: Thang điểm tối đa (default=5, có thể thay đổi thành 10, 100, etc.)
    
    Returns:
        tuple: (evaluation, G, T, dRate, tRate)
            - evaluation: Điểm đánh giá tổng (0-max_scale)
            - G: Điểm dựa trên khoảng cách (0-max_scale)
            - T: Điểm dựa trên thời gian (0-max_scale)
            - dRate: Tỷ lệ khoảng cách (0-1)
            - tRate: Tỷ lệ thời gian (0-1)
    """
    # Tính dRate = dHomeWork / (dWorkGym + dHomeGym)
    dRate = dis_workhome / (dis_workgym + dis_homegym)
    
    # Tính ra thang điểm: G = max_scale * dRate
    G = max_scale * dRate
    
    # Tính tRate = tHomeWork / (tWorkGym + tHomeGym)
    tRate = time_workhome / (time_workgym + time_homegym)
    
    # Tính ra thang điểm: T = max_scale * tRate
    T = max_scale * tRate
    
    # Đánh giá = (0.65 * G) + (0.35 * T)
    evaluation = (0.65 * G) + (0.35 * T)
    
    return evaluation, G, T, dRate, tRate

def main():
    """
    Main function to demonstrate the route calculation.
    """
    # Get API key from environment variable or set it here
    from dotenv import load_dotenv
    import os

    load_dotenv()
    API_KEY = os.getenv('GOONG_API_KEY', 'YOUR_API_KEY_HERE')
    if API_KEY == 'YOUR_API_KEY_HERE':
        print("⚠️  Cảnh báo: Vui lòng thiết lập Goong Maps API key!")
        return
    
    # Initialize calculator
    calculator = RouteCalculator(API_KEY)
    
    # Get max_scale from environment variable (default=5)
    MAX_SCALE = int(os.getenv('MAX_SCALE', '5'))
    
    # Define the 3 addresses
    work_address = "Đại học Thương Mại, Hà Nội"
    home_address = "Công viên Cầu Giấy, Hà Nội"
    gym_address = "Bến xe Mỹ Đình, Hà Nội"
    
    # GET DISTANCE, TIME
    dis_workhome, time_workhome, dis_homegym, time_homegym, dis_workgym, time_workgym = calculator.get_location_n_time(work_address, home_address, gym_address)
    
    # CALCULATE POINTS G AND T
    evaluation, G, T, dRate, tRate = calculate_points_G_n_T(
        dis_workhome, time_workhome, 
        dis_homegym, time_homegym, 
        dis_workgym, time_workgym,
        max_scale=MAX_SCALE
    )

    if evaluation > MAX_SCALE:
        evaluation = MAX_SCALE
    
    return evaluation, G, T, dRate, tRate
    

if __name__ == "__main__":
    main()
