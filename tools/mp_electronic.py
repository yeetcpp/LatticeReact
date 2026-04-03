import re
import requests
from langchain.tools import tool
from config import MP_API_KEY


@tool
def search_mp_electronic(query: str) -> str:
    """
    Search Materials Project for electronic structure data.
    
    Parses query to determine search parameters:
    - If query contains "mp-" -> searches by material_ids
    - If query contains range words ("between", "greater than", "less than") -> extracts band_gap_min/max
    - If query contains "-" between elements -> searches by chemsys (e.g., "Ga-N", "Si-Ge")
    - Otherwise -> searches by formula
    
    Returns electronic properties including band gap, CBM, VBM, Fermi level,
    gap type (direct/indirect), and metallicity.
    
    Args:
        query: Natural language query describing electronic structure data needed
        
    Returns:
        Formatted string of results (max 3000 chars) or error message
    """
    
    # Parse query to determine which parameters to use
    parsed_params = {}
    
    # Common element name mappings
    element_names = {
        'iron': 'Fe', 'copper': 'Cu', 'silver': 'Ag', 'gold': 'Au', 
        'silicon': 'Si', 'carbon': 'C', 'oxygen': 'O', 'nitrogen': 'N',
        'hydrogen': 'H', 'sulfur': 'S', 'phosphorus': 'P', 'chlorine': 'Cl',
        'gallium': 'Ga', 'arsenic': 'As', 'bromine': 'Br', 'iodine': 'I', 'fluorine': 'F', 
        'lithium': 'Li', 'sodium': 'Na', 'potassium': 'K', 'calcium': 'Ca', 'magnesium': 'Mg',
        'aluminum': 'Al', 'tin': 'Sn', 'lead': 'Pb', 'zinc': 'Zn',
        'titanium': 'Ti', 'cobalt': 'Co', 'nickel': 'Ni', 'manganese': 'Mn',
        'tantalum': 'Ta', 'tungsten': 'W', 'molybdenum': 'Mo'
    }
    
    # Check for material IDs (format: mp-XXXXX)
    if "mp-" in query:
        material_ids_match = re.search(r'(mp-\d+)', query)
        if material_ids_match:
            parsed_params['material_ids'] = material_ids_match.group(1)
    
    # Check for band gap ranges
    # "between X and Y eV"
    between_match = re.search(r'between\s+([\d.]+)\s+and\s+([\d.]+)', query, re.IGNORECASE)
    if between_match:
        try:
            parsed_params['band_gap_min'] = float(between_match.group(1))
            parsed_params['band_gap_max'] = float(between_match.group(2))
        except ValueError:
            pass
    
    # "greater than X" or "gt X"
    if not between_match:
        greater_match = re.search(r'(?:greater than|>|gt)\s+([\d.]+)', query, re.IGNORECASE)
        if greater_match:
            try:
                parsed_params['band_gap_min'] = float(greater_match.group(1))
            except ValueError:
                pass
    
    # "less than X" or "lt X"
    if not between_match:
        less_match = re.search(r'(?:less than|<|lt)\s+([\d.]+)', query, re.IGNORECASE)
        if less_match:
            try:
                parsed_params['band_gap_max'] = float(less_match.group(1))
            except ValueError:
                pass
    
    # Check for chemical system (contains "-" between elements like "Ga-N", "Si-Ge")
    if 'material_ids' not in parsed_params and 'band_gap_min' not in parsed_params and 'band_gap_max' not in parsed_params:
        if re.search(r'[A-Z][a-z]?-[A-Z][a-z]?', query):
            chemsys_match = re.search(r'([A-Z][a-z]?(?:-[A-Z][a-z]?)+)', query)
            if chemsys_match:
                parsed_params['chemsys'] = chemsys_match.group(1)
        else:
            # Check for element names first
            for name, symbol in element_names.items():
                if name in query.lower():
                    parsed_params['formula'] = symbol
                    break
            
            # If not found by name, try to find chemical formula (GaN, TiO2, Ba(PdS2)2, etc.)
            if not parsed_params:
                # Handle complex formulas with parentheses: Ba(PdS2)2, Ca(OH)2, etc.
                complex_formula_match = re.search(
                    r'\b([A-Z][a-z]?(?:\([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*\)\d*)?(?:[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*\)\d*)?)*)\b',
                    query
                )
                if complex_formula_match:
                    formula = complex_formula_match.group(1)
                    # Validate it looks like a formula
                    if re.search(r'[A-Z]', formula):
                        parsed_params['formula'] = formula
    
    if not parsed_params:
        return f"API Error: Could not parse electronic structure query from: {query}"
    
    # Build API request - use only valid API parameters
    url = "https://api.materialsproject.org/materials/electronic_structure/"
    headers = {"X-API-Key": MP_API_KEY}
    
    # Build params dict with only API-accepted parameters
    params = {}
    if 'material_ids' in parsed_params:
        params['material_ids'] = parsed_params['material_ids']
    if 'chemsys' in parsed_params:
        params['chemsys'] = parsed_params['chemsys']
    if 'formula' in parsed_params:
        params['formula'] = parsed_params['formula']
    if 'band_gap_min' in parsed_params:
        params['band_gap_min'] = parsed_params['band_gap_min']
    if 'band_gap_max' in parsed_params:
        params['band_gap_max'] = parsed_params['band_gap_max']
    
    # If no valid search parameters found, try to use formula as chemsys (single element system)
    if not params and 'formula' in parsed_params:
        params['chemsys'] = parsed_params['formula']
    
    # Add fields and limit parameters
    params['_fields'] = 'material_id,formula_pretty,band_gap,cbm,vbm,efermi,is_gap_direct,is_metal,magnetic_ordering,energy_above_hull'
    params['_limit'] = 50  # Increased from 5 to get better coverage of polymorphs
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        entries = data.get('data', [])
        
        if not entries:
            return f"No electronic structure data found for: {query}"
        
        # Sort entries to prefer most stable polymorph (lowest energy_above_hull)
        # This ensures we return the most thermodynamically stable structure first
        entries_sorted = sorted(
            entries,
            key=lambda x: (x.get('is_metal', True), x.get('energy_above_hull', float('inf')))
        )
        
        # Format the results - only take top 5 for display
        results = []
        for entry in entries_sorted[:5]:
            try:
                material_id = entry.get('material_id', 'N/A')
                formula = entry.get('formula_pretty', 'N/A')
                is_metal = entry.get('is_metal', False)
                
                if is_metal is True:
                    # Material is metallic - no bandgap
                    efermi = entry.get('efermi', 'N/A')
                    efermi_str = f"{float(efermi):.3f}" if efermi != 'N/A' and efermi is not None else "N/A"
                    result_str = (
                        f"[{material_id}] {formula}\n"
                        f"  ⚠ Metallic material - bandgap not applicable\n"
                        f"  Fermi Level: {efermi_str} eV"
                    )
                else:
                    # Semiconductor or insulator
                    band_gap = entry.get('band_gap', 'N/A')
                    cbm = entry.get('cbm', 'N/A')
                    vbm = entry.get('vbm', 'N/A')
                    efermi = entry.get('efermi', 'N/A')
                    is_direct = entry.get('is_gap_direct', 'N/A')
                    magnetic = entry.get('magnetic_ordering', None)
                    
                    # Format band gap
                    if band_gap != 'N/A' and band_gap is not None:
                        band_gap_str = f"{float(band_gap):.3f} eV"
                    else:
                        band_gap_str = "N/A"
                    
                    # Format gap type
                    if is_direct == 'N/A':
                        gap_type = "Unknown"
                    elif is_direct:
                        gap_type = "Direct"
                    else:
                        gap_type = "Indirect"
                    
                    # Format CBM/VBM
                    cbm_str = f"{float(cbm):.3f}" if cbm != 'N/A' and cbm is not None else "N/A"
                    vbm_str = f"{float(vbm):.3f}" if vbm != 'N/A' and vbm is not None else "N/A"
                    efermi_str = f"{float(efermi):.3f}" if efermi != 'N/A' and efermi is not None else "N/A"
                    
                    result_str = (
                        f"[{material_id}] {formula}\n"
                        f"  Band Gap: {band_gap_str} ({gap_type})\n"
                        f"  CBM: {cbm_str} eV, VBM: {vbm_str} eV\n"
                        f"  Fermi Level: {efermi_str} eV"
                    )
                    
                    if magnetic and magnetic != 'None':
                        result_str += f"\n  Magnetic Ordering: {magnetic}"
                
                results.append(result_str)
            except (KeyError, TypeError, ValueError) as e:
                continue
        
        if not results:
            return f"API Error: Could not parse electronic structure data from response for: {query}"
        
        formatted = "\n\n".join(results)
        
        # Truncate to 3000 chars
        if len(formatted) > 3000:
            formatted = formatted[:2997] + "..."
        
        return formatted
        
    except requests.exceptions.Timeout:
        return "API Error: Electronic structure request timed out (>10s). Please try again or simplify your query."
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
    print("Testing search_mp_electronic tool...\n")
    
    # Test 1: bandgap of GaN
    print("Test 1: bandgap of GaN")
    result1 = search_mp_electronic("bandgap of GaN")
    print(result1)
    print("\n" + "="*80 + "\n")
    
    # Test 2: electronic structure of Si
    print("Test 2: electronic structure of Si")
    result2 = search_mp_electronic("electronic structure of Si")
    print(result2)
    print("\n" + "="*80 + "\n")
    
    # Test 3: bandgap of mp-804
    print("Test 3: bandgap of mp-804")
    result3 = search_mp_electronic("bandgap of mp-804")
    print(result3)
    print("\n" + "="*80 + "\n")
    
    # Test 4: semiconductors in Ga-N system
    print("Test 4: semiconductors in Ga-N system")
    result4 = search_mp_electronic("semiconductors in Ga-N system")
    print(result4)
