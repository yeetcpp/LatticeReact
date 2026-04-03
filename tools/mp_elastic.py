import re
import requests
from langchain.tools import tool
from config import MP_API_KEY, OLLAMA_BASE_URL


@tool
def search_mp_elastic(query: str) -> str:
    """
    Search Materials Project for elastic/mechanical properties.
    
    Parses query to determine search parameter:
    - If query contains "mp-" -> searches by material_ids
    - If query contains "-" between elements -> searches by chemsys (e.g., "Si-O", "Fe-Ni")
    - Otherwise -> searches by formula
    
    Returns elastic properties including bulk modulus, shear modulus,
    Young's modulus, and universal anisotropy index.
    
    Args:
        query: Natural language query describing elastic data needed
        
    Returns:
        Formatted string of results (max 3000 chars) or error message
    """
    
    # Parse query to determine which parameter to use
    parsed_params = {}
    
    # Common element name mappings
    element_names = {
        'iron': 'Fe', 'copper': 'Cu', 'silver': 'Ag', 'gold': 'Au', 
        'silicon': 'Si', 'carbon': 'C', 'oxygen': 'O', 'nitrogen': 'N',
        'hydrogen': 'H', 'sulfur': 'S', 'phosphorus': 'P', 'chlorine': 'Cl',
        'bromine': 'Br', 'iodine': 'I', 'fluorine': 'F', 'lithium': 'Li',
        'sodium': 'Na', 'potassium': 'K', 'calcium': 'Ca', 'magnesium': 'Mg',
        'aluminum': 'Al', 'tin': 'Sn', 'lead': 'Pb', 'zinc': 'Zn',
        'titanium': 'Ti', 'cobalt': 'Co', 'nickel': 'Ni', 'manganese': 'Mn',
        'tantalum': 'Ta', 'tungsten': 'W', 'molybdenum': 'Mo'
    }
    
    # Check for material IDs (format: mp-XXXXX)
    if "mp-" in query:
        material_ids_match = re.search(r'(mp-\d+)', query)
        if material_ids_match:
            parsed_params['material_ids'] = material_ids_match.group(1)
    
    # Check for chemical system (contains "-" between elements like "Si-O", "Fe-Ni", "Si-O system")
    elif re.search(r'[A-Z][a-z]?-[A-Z][a-z]?', query):
        chemsys_match = re.search(r'([A-Z][a-z]?(?:-[A-Z][a-z]?)+)', query)
        if chemsys_match:
            parsed_params['chemsys'] = chemsys_match.group(1)
    
    # Otherwise assume formula (e.g., "Iron", "Fe", "TiO2")
    else:
        # Check for element names first
        for name, symbol in element_names.items():
            if name in query.lower():
                parsed_params['formula'] = symbol
                break
        
        # If not found by name, try to find chemical formula (Fe2O3, GaN, TiO2, Ba(PdS2)2, etc.)
        if not parsed_params:
            # IMPROVED: Handle complex formulas with parentheses
            complex_formula_match = re.search(
                r'\b([A-Z][a-z]?(?:\([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*\)\d*)?(?:[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*\)\d*)?)*)\b',
                query
            )
            if complex_formula_match:
                formula = complex_formula_match.group(1)
                # Validate it looks like a formula
                if re.search(r'[A-Z]', formula):
                    parsed_params['formula'] = formula
        
        # Fallback to single element symbol
        if not parsed_params:
            element_match = re.search(r'([A-Z][a-z]?)', query)
            if element_match:
                parsed_params['formula'] = element_match.group(1)
    
    if not parsed_params:
        return f"API Error: Could not parse elastic property query from: {query}"
    
    # Build API request - use only valid parameters
    url = "https://api.materialsproject.org/materials/elasticity/"
    headers = {"X-API-Key": MP_API_KEY}
    
    # Build params dict with only API-accepted parameters
    params = {}
    if 'material_ids' in parsed_params:
        params['material_ids'] = parsed_params['material_ids']
    if 'chemsys' in parsed_params:
        params['chemsys'] = parsed_params['chemsys']
    # Note: elasticity endpoint doesn't accept 'formula' parameter
    
    # If no valid search parameters found, try to use formula as chemsys (single element system)
    if not params and 'formula' in parsed_params:
        params['chemsys'] = parsed_params['formula']
    
    # Add fields and limit parameters
    params['_fields'] = 'material_id,formula_pretty,bulk_modulus,shear_modulus,young_modulus,universal_anisotropy,energy_above_hull,is_metal'
    params['_limit'] = 50  # Increased from 5 to get better coverage
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        entries = data.get('data', [])
        
        if not entries:
            return f"No elastic data found for: {query}"
        
        # Format the results
        results = []
        for entry in entries[:5]:
            try:
                material_id = entry.get('material_id', 'N/A')
                formula = entry.get('formula_pretty', 'N/A')
                
                # Extract VRH values (Voigt-Reuss-Hill average) from nested objects
                bulk_modulus_obj = entry.get('bulk_modulus', {})
                shear_modulus_obj = entry.get('shear_modulus', {})
                young_modulus_obj = entry.get('young_modulus', {})
                
                # Access nested vrh values
                bulk_vrh = bulk_modulus_obj.get('vrh', 'N/A') if isinstance(bulk_modulus_obj, dict) else 'N/A'
                shear_vrh = shear_modulus_obj.get('vrh', 'N/A') if isinstance(shear_modulus_obj, dict) else 'N/A'
                young_vrh = young_modulus_obj.get('vrh', 'N/A') if isinstance(young_modulus_obj, dict) else 'N/A'
                
                anisotropy = entry.get('universal_anisotropy', 'N/A')
                
                # Format values with proper type conversion
                bulk_str = f"{float(bulk_vrh):.2f} GPa" if bulk_vrh != 'N/A' and bulk_vrh is not None else "N/A"
                shear_str = f"{float(shear_vrh):.2f} GPa" if shear_vrh != 'N/A' and shear_vrh is not None else "N/A"
                young_str = f"{float(young_vrh):.2f} GPa" if young_vrh != 'N/A' and young_vrh is not None else "N/A"
                aniso_str = f"{float(anisotropy):.4f}" if anisotropy != 'N/A' and anisotropy is not None else "N/A"
                
                result_str = (
                    f"[{material_id}] {formula}\n"
                    f"  Bulk Modulus (VRH): {bulk_str}\n"
                    f"  Shear Modulus (VRH): {shear_str}\n"
                    f"  Young's Modulus (VRH): {young_str}\n"
                    f"  Universal Anisotropy: {aniso_str}"
                )
                results.append(result_str)
            except (KeyError, TypeError, ValueError) as e:
                continue
        
        if not results:
            return f"API Error: Could not parse elastic data from response for: {query}"
        
        formatted = "\n\n".join(results)
        
        # Truncate to 3000 chars
        if len(formatted) > 3000:
            formatted = formatted[:2997] + "..."
        
        return formatted
        
    except requests.exceptions.Timeout:
        return "API Error: Elastic data request timed out (>10s). Please try again or simplify your query."
    except requests.exceptions.HTTPError:
        try:
            error_detail = response.json().get('detail', response.text[:200])
        except:
            error_detail = response.text[:200]
        return f"API Error: HTTP {response.status_code}. {error_detail}"
    except requests.exceptions.ConnectionError:
        return "API Error: Failed to connect to Materials Project API. Check your internet connection."
    except requests.exceptions.RequestException as e:
        return f"API Error: Request failed. {str(e)[:300]}"
    except Exception as e:
        return f"API Error: Unexpected error. {type(e).__name__}: {str(e)[:300]}"


if __name__ == "__main__":
    print("Testing search_mp_elastic tool...\n")
    
    # Test 1: bulk modulus of Iron
    print("Test 1: bulk modulus of Iron")
    result1 = search_mp_elastic("bulk modulus of Iron")
    print(result1)
    print("\n" + "="*80 + "\n")
    
    # Test 2: elastic properties of Si-O system
    print("Test 2: elastic properties of Si-O system")
    result2 = search_mp_elastic("elastic properties of Si-O system")
    print(result2)
    print("\n" + "="*80 + "\n")
    
    # Test 3: stiffness of mp-149
    print("Test 3: stiffness of mp-149")
    result3 = search_mp_elastic("stiffness of mp-149")
    print(result3)
