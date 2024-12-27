from utils.astro_calc import AstroCalc
from datetime import datetime
import pytz

def test_nakshatra():
    # Create an instance
    calc = AstroCalc()
    
    # Set current time
    tz = pytz.timezone("Asia/Kolkata")
    current_dt = datetime.now(tz)
    
    # Calculate chart
    chart = calc.calculate_chart(current_dt, 13.0827, 80.2707)
    
    # Get first house details
    house_1 = chart["houses"]["House_1"]
    
    print("\nFirst House (Ascendant) Details:")
    print(f"Longitude: {house_1['longitude']:.2f}°")
    print(f"Sign: {house_1['sign']}")
    print(f"Nakshatra: {house_1['nakshatra']}")
    print(f"Pada: {house_1['pada']}")
    print(f"Star Lord: {house_1['star_lord']}")
    print(f"Sub Lord: {house_1['sub_lord']}")

if __name__ == "__main__":
    test_nakshatra()
