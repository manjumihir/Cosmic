import swisseph as swe
import math
from datetime import datetime, timezone
import pytz

class AstroCalc:
    """Class for handling astrological calculations"""
    
    SIGNS = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]

    HOUSE_SYSTEMS = {
        'Placidus': b'P',
        'Koch': b'K',
        'Equal (Asc)': b'A',
        'Equal (MC)': b'E',
        'Whole Sign': b'W',
        'Campanus': b'C',
        'Regiomontanus': b'R',
        'Porphyry': b'O',
        'Morinus': b'M',
        'Meridian': b'X',
        'Alcabitius': b'B',
        'Azimuthal': b'H',
        'Polich/Page (Topocentric)': b'T',
        'Vehlow Equal': b'V'
    }

    AYANAMSA_TYPES = {
        'Lahiri': swe.SIDM_LAHIRI,
        'Raman': swe.SIDM_RAMAN,
        'Krishnamurti': swe.SIDM_KRISHNAMURTI,
        'Fagan/Bradley': swe.SIDM_FAGAN_BRADLEY,
        'True Chitrapaksha': swe.SIDM_TRUE_CITRA,
        'Yukteswar': swe.SIDM_YUKTESWAR
    }

    NAKSHATRAS = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
        'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
        'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
        'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
    ]

    NAKSHATRA_LORDS = {
        'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun', 
        'Rohini': 'Moon', 'Mrigashira': 'Mars', 'Ardra': 'Rahu',
        'Punarvasu': 'Jupiter', 'Pushya': 'Saturn', 'Ashlesha': 'Mercury',
        'Magha': 'Ketu', 'Purva Phalguni': 'Venus', 'Uttara Phalguni': 'Sun',
        'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu',
        'Vishakha': 'Jupiter', 'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury',
        'Mula': 'Ketu', 'Purva Ashadha': 'Venus', 'Uttara Ashadha': 'Sun',
        'Shravana': 'Moon', 'Dhanishta': 'Mars', 'Shatabhisha': 'Rahu',
        'Purva Bhadrapada': 'Jupiter', 'Uttara Bhadrapada': 'Saturn', 'Revati': 'Mercury'
    }

    # Vimsottari Dasha periods for each planet (in years)
    VIMSOTTARI_PERIODS = {
        'Ketu': 7,
        'Venus': 20,
        'Sun': 6,
        'Moon': 10,
        'Mars': 7,
        'Rahu': 18,
        'Jupiter': 16,
        'Saturn': 19,
        'Mercury': 17
    }

    def __init__(self, lat=0.0, lon=0.0, alt=0.0, timezone='UTC'):
        """Initialize AstroCalc with location and timezone"""
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.timezone = timezone
        self.house_system = 'Placidus'
        self.ayanamsa_type = 'Lahiri'
        self.zodiac_type = 'Sidereal'
        self.calculation_type = 'Topocentric'
        self.node_type = 'True'
        
        # Initialize Swiss Ephemeris
        swe.set_ephe_path()  # Use default ephemeris path
        
    def set_location(self, lat, lon, alt=0.0):
        """Set geographical location"""
        self.lat = lat
        self.lon = lon
        self.alt = alt

    def set_timezone(self, timezone):
        """Set timezone"""
        self.timezone = timezone

    def set_house_system(self, system):
        """Set house system"""
        if system in self.HOUSE_SYSTEMS:
            self.house_system = system

    def set_ayanamsa(self, ayanamsa):
        """Set ayanamsa type"""
        if ayanamsa in self.AYANAMSA_TYPES:
            self.ayanamsa_type = ayanamsa

    def set_zodiac_type(self, zodiac_type):
        """Set zodiac type (Tropical/Sidereal)"""
        if zodiac_type in ['Tropical', 'Sidereal']:
            self.zodiac_type = zodiac_type

    def set_calculation_type(self, calc_type):
        """Set calculation type (Geocentric/Topocentric)"""
        if calc_type in ['Geocentric', 'Topocentric']:
            self.calculation_type = calc_type

    def set_node_type(self, node_type):
        """Set node type (True/Mean)"""
        if node_type in ['True', 'Mean']:
            self.node_type = node_type

    def get_julian_day(self, date_time):
        """Convert datetime to Julian Day"""
        tz = pytz.timezone(self.timezone)
        local_dt = tz.localize(date_time)
        utc_dt = local_dt.astimezone(timezone.utc)
        
        jd = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
        )
        return jd

    def get_nakshatra_data(self, longitude):
        """Get nakshatra details for a given longitude"""
        # Each nakshatra is 13°20' (13.3333... degrees)
        nakshatra_length = 360 / 27
        
        # Calculate nakshatra index (0-26)
        nakshatra_index = int(longitude / nakshatra_length)
        
        # Calculate pada (1-4)
        pada_length = nakshatra_length / 4
        pada = int((longitude % nakshatra_length) / pada_length) + 1
        
        # Calculate sub-lord based on Vimsottari dasha periods
        total_dasha_years = sum(self.VIMSOTTARI_PERIODS.values())
        portion_in_nakshatra = (longitude % nakshatra_length) / nakshatra_length
        
        # Get the nakshatra lord
        nakshatra_name = self.NAKSHATRAS[nakshatra_index]
        nakshatra_lord = self.NAKSHATRA_LORDS[nakshatra_name]
        
        # Calculate sub-lord
        lords_cycle = list(self.VIMSOTTARI_PERIODS.keys())
        start_index = lords_cycle.index(nakshatra_lord)
        
        # Rotate lords list to start with the nakshatra lord
        rotated_lords = lords_cycle[start_index:] + lords_cycle[:start_index]
        
        # Calculate which portion of the nakshatra we're in
        cumulative_portion = 0
        sub_lord = rotated_lords[0]  # Default to nakshatra lord
        
        for lord in rotated_lords:
            lord_portion = self.VIMSOTTARI_PERIODS[lord] / total_dasha_years
            if portion_in_nakshatra <= (cumulative_portion + lord_portion):
                sub_lord = lord
                break
            cumulative_portion += lord_portion
        
        return {
            'nakshatra': self.NAKSHATRAS[nakshatra_index],
            'pada': pada,
            'lord': nakshatra_lord,
            'sub_lord': sub_lord
        }

    def calculate_houses(self, jd):
        """Calculate house cusps"""
        houses = swe.houses(
            jd,
            self.lat,
            self.lon,
            self.HOUSE_SYSTEMS[self.house_system]
        )
        return houses

    def calculate_planet_position(self, jd, planet_id):
        """Calculate position of a planet"""
        flags = swe.FLG_SWIEPH
        if self.calculation_type == 'Topocentric':
            flags |= swe.FLG_TOPOCTR
        
        # Apply ayanamsa settings if using sidereal zodiac
        if self.zodiac_type == 'Sidereal':
            swe.set_sid_mode(self.AYANAMSA_TYPES[self.ayanamsa_type])
            flags |= swe.FLG_SIDEREAL
        
        result = swe.calc_ut(jd, planet_id, flags)
        return result

    def determine_house(self, longitude, house_cusps):
        """Determine which house a planet is in"""
        for i in range(12):
            next_i = (i + 1) % 12
            cusp = house_cusps[i]
            next_cusp = house_cusps[next_i]
            
            if next_cusp < cusp:  # House spans 0° Aries
                if longitude >= cusp or longitude < next_cusp:
                    return i + 1
            else:
                if cusp <= longitude < next_cusp:
                    return i + 1
        return 1  # Default to 1st house if not found

    def calculate_chart(self, date_time):
        """Calculate complete chart data"""
        jd = self.get_julian_day(date_time)
        
        # Calculate house cusps
        houses = self.calculate_houses(jd)
        house_cusps = list(houses[0])
        
        # Define planets to calculate
        planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mars': swe.MARS,
            'Mercury': swe.MERCURY,
            'Jupiter': swe.JUPITER,
            'Venus': swe.VENUS,
            'Saturn': swe.SATURN
        }
        
        # Add nodes based on settings
        if self.node_type == 'True':
            planets.update({'Rahu': swe.TRUE_NODE, 'Ketu': swe.TRUE_NODE})
        else:
            planets.update({'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE})
        
        # Calculate positions
        points = {}
        for planet_name, planet_id in planets.items():
            try:
                result = self.calculate_planet_position(jd, planet_id)
                longitude = result[0]
                
                # Special handling for Ketu (180° opposite to Rahu)
                if planet_name == 'Ketu':
                    longitude = (longitude + 180) % 360
                
                # Calculate sign and degree
                sign_num = int(longitude / 30)
                degree = longitude % 30
                
                # Get nakshatra information
                nakshatra_info = self.get_nakshatra_data(longitude)
                
                # Determine house placement
                house = self.determine_house(longitude, house_cusps)
                
                points[planet_name] = {
                    'longitude': longitude,
                    'latitude': result[1] if len(result) > 1 else 0,
                    'speed': result[3] if len(result) > 3 else 0,
                    'sign': self.SIGNS[sign_num],
                    'degree': degree,
                    'nakshatra': nakshatra_info['nakshatra'],
                    'pada': nakshatra_info['pada'],
                    'star_lord': nakshatra_info['lord'],
                    'sub_lord': nakshatra_info['sub_lord'],
                    'house': house
                }
            
            except Exception as e:
                print(f"Error calculating position for {planet_name}: {str(e)}")
        
        # Prepare house data
        house_data = {}
        for i in range(12):
            house_num = i + 1
            longitude = house_cusps[i]
            sign_num = int(longitude / 30)
            degree = longitude % 30
            
            # Get nakshatra information for house cusp
            nakshatra_info = self.get_nakshatra_data(longitude)
            
            house_data[f'House_{house_num}'] = {
                'longitude': longitude,
                'sign': self.SIGNS[sign_num],
                'degree': degree,
                'nakshatra': nakshatra_info['nakshatra'],
                'pada': nakshatra_info['pada'],
                'star_lord': nakshatra_info['lord'],
                'sub_lord': nakshatra_info['sub_lord']
            }
        
        return {
            'points': points,
            'houses': house_data,
            'ayanamsa': swe.get_ayanamsa_ut(jd) if self.zodiac_type == 'Sidereal' else 0
        }

    def calculate_transits(self, date_time):
        """Calculate current planetary positions for transits"""
        return self.calculate_chart(date_time)
