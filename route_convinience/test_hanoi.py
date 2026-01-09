#!/usr/bin/env python3
"""
Test script với 10 địa điểm ngẫu nhiên ở Hà Nội
"""

from get_3_point import RouteCalculator, calculate_points_G_n_T
import os

def test_hanoi_locations():
    """Test với 10 địa điểm ở Hà Nội"""
    
    # Danh sách 10 địa điểm phổ biến ở Hà Nội
    hanoi_locations = [
        "Hồ Hoàn Kiếm, Hà Nội",
        "Đại học Bách Khoa Hà Nội",
        "Bến xe Mỹ Đình, Hà Nội",
        "Bệnh viện Bạch Mai, Hà Nội",
        "Sân bay Nội Bài, Hà Nội",
        "Chợ Đồng Xuân, Hà Nội",
        "Công viên Cầu Giấy, Hà Nội",
        "Đại học Thương Mại, Hà Nội",
        "Royal City, Hà Nội",
        "Times City, Hà Nội"
    ]
    
    # Lấy API key
    API_KEY = os.getenv('GOONG_API_KEY')
    if not API_KEY:
        print("⚠️  Vui lòng set GOONG_API_KEY trong file .env")
        return
    
    # Initialize calculator
    calculator = RouteCalculator(API_KEY)
    
    print("="*70)
    print("TEST VỚI 10 ĐỊA ĐIỂM Ở HÀ NỘI")
    print("="*70)
    
    # Test các tổ hợp khác nhau
    test_cases = [
        {
            "name": "Test 1: Khu vực trung tâm",
            "work": hanoi_locations[0],  # Hồ Hoàn Kiếm
            "home": hanoi_locations[5],  # Chợ Đồng Xuân
            "gym": hanoi_locations[1]    # ĐH Bách Khoa
        },
        {
            "name": "Test 2: Khu vực phía Tây",
            "work": hanoi_locations[7],  # ĐH Thương Mại
            "home": hanoi_locations[6],  # Công viên Cầu Giấy
            "gym": hanoi_locations[2]    # Bến xe Mỹ Đình
        },
        {
            "name": "Test 3: Xa trung tâm",
            "work": hanoi_locations[4],  # Sân bay Nội Bài
            "home": hanoi_locations[2],  # Bến xe Mỹ Đình
            "gym": hanoi_locations[0]    # Hồ Hoàn Kiếm
        },
        {
            "name": "Test 4: Royal City - Times City",
            "work": hanoi_locations[8],  # Royal City
            "home": hanoi_locations[3],  # Bệnh viện Bạch Mai
            "gym": hanoi_locations[9]    # Times City
        },
        {
            "name": "Test 5: Mix các khu vực",
            "work": hanoi_locations[1],  # ĐH Bách Khoa
            "home": hanoi_locations[8],  # Royal City
            "gym": hanoi_locations[5]    # Chợ Đồng Xuân
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"{test_case['name']}")
        print(f"{'='*70}")
        print(f"🏢 Work: {test_case['work']}")
        print(f"🏠 Home: {test_case['home']}")
        print(f"💪 Gym:  {test_case['gym']}")
        print()
        
        try:
            # Get distances and times
            dis_workhome, time_workhome, dis_homegym, time_homegym, dis_workgym, time_workgym = \
                calculator.get_location_n_time(
                    test_case['work'],
                    test_case['home'],
                    test_case['gym']
                )
            
            if dis_workhome:
                # Calculate evaluation
                evaluation, G, T, dRate, tRate = calculate_points_G_n_T(
                    dis_workhome, time_workhome,
                    dis_homegym, time_homegym,
                    dis_workgym, time_workgym,
                    10
                )
                
                # Display results
                # print(f"📏 Khoảng cách:")
                # print(f"   Work → Home: {dis_workhome} km")
                # print(f"   Home → Gym:  {dis_homegym} km")
                # print(f"   Work → Gym:  {dis_workgym} km")
                # print()
                # print(f"⏱️  Thời gian:")
                # print(f"   Work → Home: {time_workhome} phút")
                # print(f"   Home → Gym:  {time_homegym} phút")
                # print(f"   Work → Gym:  {time_workgym} phút")
                print()
                print(f"⭐ Đánh giá:")
                print(f"   Evaluation: {evaluation:.2f}/5.0")
                # print(f"   G (distance): {G:.2f}/5.0")
                # print(f"   T (time): {T:.2f}/5.0")
                
                results.append({
                    'name': test_case['name'],
                    'evaluation': evaluation,
                    'G': G,
                    'T': T
                })
            else:
                print("❌ Không thể tính toán route")
                
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
    
    # Summary
    if results:
        print(f"\n{'='*70}")
        print("TÓM TẮT KẾT QUẢ")
        print(f"{'='*70}")
        
        # Sort by evaluation score
        results_sorted = sorted(results, key=lambda x: x['evaluation'], reverse=True)
        
        print("\nXếp hạng theo điểm đánh giá:")
        for i, result in enumerate(results_sorted, 1):
            print(f"{i}. {result['name']}: {result['evaluation']:.2f}/5.0 "
                  f"(G={result['G']:.2f}, T={result['T']:.2f})")

if __name__ == "__main__":
    test_hanoi_locations()
