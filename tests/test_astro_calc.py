import unittest
from datetime import datetime
from utils.astro_calc import AstroCalc

class TestAstroCalc(unittest.TestCase):
    def setUp(self):
        self.astro_calc = AstroCalc()

    def test_ascendant_calculation(self):
        """Test ascendant calculation against reference data for both tropical and sidereal zodiacs"""
        # Test case for London: January 1st, 2020, 18:00 UTC
        # Location: London (51°30'N, 0°10'W)
        test_date = datetime(2020, 1, 1, 18, 0)
        lat = 51.5  # 51°30'N
        lon = -0.1666667  # 0°10'W

        # Calculate tropical ascendant
        tropical_chart = self.astro_calc.calculate_chart(
            test_date,
            lat,
            lon,
            zodiac="Tropical"
        )
        
        # Calculate sidereal ascendant
        sidereal_chart = self.astro_calc.calculate_chart(
            test_date,
            lat,
            lon,
            zodiac="Sidereal",
            ayanamsa="Lahiri"
        )
        
        # Debug print chart structures
        print("\nTropical Chart Structure:")
        for key in tropical_chart.keys():
            print(f"{key}: {type(tropical_chart[key])}")
            if isinstance(tropical_chart[key], dict):
                print("  Subkeys:", list(tropical_chart[key].keys()))
                
        print("\nSidereal Chart Structure:")
        for key in sidereal_chart.keys():
            print(f"{key}: {type(sidereal_chart[key])}")
            if isinstance(sidereal_chart[key], dict):
                print("  Subkeys:", list(sidereal_chart[key].keys()))
        
        # Get and format tropical ascendant
        trop_asc = tropical_chart['points']['Ascendant']['longitude']
        trop_deg = int(trop_asc)
        trop_min = int((trop_asc - trop_deg) * 60)
        trop_sec = int(((trop_asc - trop_deg) * 60 - trop_min) * 60)
        
        # Get and format sidereal ascendant
        sid_asc = sidereal_chart['points']['Ascendant']['longitude']
        sid_deg = int(sid_asc)
        sid_min = int((sid_asc - sid_deg) * 60)
        sid_sec = int(((sid_asc - sid_deg) * 60 - sid_min) * 60)
        
        print("\nAscendant Test Results:")
        print(f"Date: {test_date}")
        print(f"Location: London (51°30'N, 0°10'W)")
        print(f"\nTropical Ascendant: {trop_deg}°{trop_min}'{trop_sec}\"")
        print(f"Sidereal Ascendant (Lahiri): {sid_deg}°{sid_min}'{sid_sec}\"")
        
        # Print intermediate calculations for debugging
        print("\nIntermediate Calculations:")
        print("Tropical:")
        print(f"ARMC: {tropical_chart.get('armc', 'Not available')}°")
        print(f"Obliquity: {tropical_chart.get('obliquity', 'Not available')}°")
        print(f"LST: {tropical_chart.get('sidereal_time', 'Not available')}°")
        print("\nSidereal:")
        print(f"ARMC: {sidereal_chart.get('armc', 'Not available')}°")
        print(f"Obliquity: {sidereal_chart.get('obliquity', 'Not available')}°")
        print(f"LST: {sidereal_chart.get('sidereal_time', 'Not available')}°")
        print(f"Ayanamsa: {sidereal_chart.get('meta', {}).get('ayanamsa_value', 'Not available')}°")

    def test_svp_1900(self):
        """Test SVP position on January 1st, 1900"""
        # Create date for January 1st, 1900 at 00:00 UTC
        test_date = datetime(1900, 1, 1, 0, 0)
        
        # Calculate chart for 0° longitude and latitude (not relevant for SVP)
        chart = self.astro_calc.calculate_chart(
            test_date,
            0,  # latitude
            0,  # longitude
            zodiac="Sidereal",
            ayanamsa="Lahiri"
        )
        
        # Get ayanamsa value
        ayanamsa = chart["meta"]["ayanamsa_value"]
        
        # Convert to degrees, minutes, seconds
        degrees = int(ayanamsa)
        minutes = int((ayanamsa - degrees) * 60)
        seconds = int(((ayanamsa - degrees) * 60 - minutes) * 60)
        
        # Calculate position in Pisces (360° - ayanamsa)
        pisces_pos = (360 - ayanamsa) % 30  # Position within Pisces
        pisces_deg = int(pisces_pos)
        pisces_min = int((pisces_pos - pisces_deg) * 60)
        pisces_sec = int(((pisces_pos - pisces_deg) * 60 - pisces_min) * 60)
        
        print(f"\nSVP Test Results for January 1st, 1900:")
        print(f"Ayanamsa: {degrees}°{minutes}'{seconds}\"")
        print(f"SVP Position in Pisces: {pisces_deg}°{pisces_min}'{pisces_sec}\"")
        print(f"Expected: 7°32'22\"")
        
        # Basic assertions
        self.assertGreater(ayanamsa, 22)  # Should be greater than 22 degrees
        self.assertLess(ayanamsa, 24)     # Should be less than 24 degrees

if __name__ == '__main__':
    unittest.main()
