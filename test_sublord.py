from utils.astro_calc import AstroCalc

# Create an instance of AstroCalc
calc = AstroCalc()

# Your Ascendant position: Aries 17°31'29.40"
# Convert to absolute longitude (Aries starts at 0°)
asc_longitude = 17.524833  # 17° + 31/60 + 29.40/3600

# Get nakshatra data
result = calc.get_nakshatra_data(asc_longitude)

print("\nFinal Results:")
print(f"Nakshatra: {result['nakshatra']}")
print(f"Star Lord: {result['star_lord']}")
print(f"Sub Lord: {result['sub_lord']}")
print(f"Pada: {result['pada']}")
