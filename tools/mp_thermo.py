import re
import json
import requests
from langchain.tools import tool
from config import MP_API_KEY


def _normalize_formula_token(token: str) -> str:
    """Normalize common formula typos from natural language prompts."""
    token = token.strip().strip(",.;:")
    # Common typo: letter O written as zero, e.g. Ag203 -> Ag2O3
    if re.search(r"[A-Za-z]", token) and "0" in token:
        token = token.replace("0", "O")
    return token


def _extract_formula_candidates(query: str):
    """Extract all explicit chemical formulas from a query."""
    def _is_formula_like(token: str) -> bool:
        # Accept sequences of element symbols with optional counts/parentheses.
        # Examples: BN, GaN, SiC, BaTiO3, Ba(PdS2)2
        return re.fullmatch(
            r"(?:[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*\)\d*)?)+",
            token,
        ) is not None

    # First pass: parse explicit comma-separated list after "following materials:".
    list_match = re.search(r"following\s+materials\s*:\s*(.+?)(?:\.|$)", query, re.IGNORECASE)
    if list_match:
        tokens = [t.strip() for t in list_match.group(1).split(",") if t.strip()]
        formulas = []
        for token in tokens:
            # Keep only the first word-like segment (drop trailing instructions).
            candidate = re.split(r"\s+", token)[0]
            candidate = _normalize_formula_token(candidate)
            candidate = re.sub(r"[^A-Za-z0-9()]+", "", candidate)
            if _is_formula_like(candidate):
                formulas.append(candidate)

        if formulas:
            deduped = []
            seen = set()
            for f in formulas:
                if f not in seen:
                    seen.add(f)
                    deduped.append(f)
            return deduped

    # Fallback pass: regex extraction across full query.
    pattern = (
        r"\b([A-Z][a-z]?(?:\([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*\)\d*)?"
        r"(?:[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*\)\d*)?)*)\b"
    )
    raw = re.findall(pattern, query)
    cleaned = []
    excluded_words = {"If", "Give", "Please", "What", "The", "For"}
    for token in raw:
        norm = _normalize_formula_token(token)
        if norm in excluded_words:
            continue
        if _is_formula_like(norm):
            cleaned.append(norm)

    # Preserve order while removing duplicates.
    deduped = []
    seen = set()
    for f in cleaned:
        if f not in seen:
            seen.add(f)
            deduped.append(f)
    return deduped


def _choose_best_entry(entries):
    """
    Select one representative entry per formula.

    Priority:
    1) Minimum energy_above_hull (most stable polymorph)
    2) Minimum formation_energy_per_atom as tie-breaker
    """
    valid = [e for e in entries if e.get("formation_energy_per_atom") is not None]
    if not valid:
        return None

    return sorted(
        valid,
        key=lambda e: (
            e.get("energy_above_hull", float("inf")),
            e.get("formation_energy_per_atom", float("inf")),
        ),
    )[0]


@tool
def search_mp_thermo(query: str) -> str:
    """
    Search Materials Project for thermodynamic data.
    
    Extracts parameters from natural language query:
    - formula: Chemical formula (e.g., "TiO2", "LiFePO4")
    - chemsys: Chemical system (e.g., "Ti-O", "Li-Fe-P-O")
    - material_ids: Specific Materials Project IDs
    
    Returns thermodynamic properties including formation energy,
    energy above hull, and decomposition enthalpy.
    
    Args:
        query: Natural language query describing thermodynamic data needed
        
    Returns:
        Formatted string of results (max 3000 chars) or error message
    """
    
    # Parse query for parameters using simple string matching
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
    
    # Check for material_ids parameter first (mp-XXXXX)
    material_ids_match = re.search(r'(mp-\d+)', query)
    if material_ids_match:
        parsed_params['material_ids'] = material_ids_match.group(1)
    
    # Check for chemsys parameter (element-element pattern like Ti-O)
    if not parsed_params:
        chemsys_match = re.search(r'([A-Z][a-z]?(?:-[A-Z][a-z]?)+)', query)
        if chemsys_match:
            parsed_params['chemsys'] = chemsys_match.group(1)
    
    # Check for explicit formula parameter
    if not parsed_params:
        formula_match = re.search(r'formula[:\s]+([A-Za-z0-9]+)', query, re.IGNORECASE)
        if formula_match:
            parsed_params['formula'] = formula_match.group(1)
    
    # Check for element names
    if not parsed_params:
        for name, symbol in element_names.items():
            if name in query.lower():
                parsed_params['formula'] = symbol
                break
    
    # Fallback: extract chemical formula (including complex ones with parentheses)
    if not parsed_params:
        extracted_formulas = _extract_formula_candidates(query)
        if extracted_formulas:
            # Keep first for backward compatibility in single-formula path.
            parsed_params['formula'] = extracted_formulas[0]
    
    if not parsed_params:
        return (
            "Error: Could not parse parameters from query. "
            "Please specify: formula:<name>, chemsys:<system>, or material_ids:<ids>"
        )
    
    # Build API request
    url = "https://api.materialsproject.org/materials/thermo/"
    headers = {"X-API-Key": MP_API_KEY}

    base_params = {
        '_fields': 'material_id,formula_pretty,formation_energy_per_atom,energy_above_hull,decomposition_energy_per_atom',
        '_limit': 100,
        # Align with common Materials Project formation-energy default behavior.
        'thermo_types': 'GGA_GGA+U',
    }
    
    try:
        # Multi-formula path: query each formula explicitly to avoid parser ambiguity.
        formula_list = _extract_formula_candidates(query)

        entries_filtered = []
        if formula_list:
            for formula in formula_list:
                params = dict(base_params)
                params['formula'] = formula
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                entries = data.get('data', [])
                if not entries:
                    continue
                best = _choose_best_entry(entries)
                if best:
                    entries_filtered.append(best)
        else:
            # Legacy single-target path using parsed params.
            params = dict(base_params)
            if 'material_ids' in parsed_params:
                params['material_ids'] = parsed_params['material_ids']
            elif 'chemsys' in parsed_params:
                params['chemsys'] = parsed_params['chemsys']
            elif 'formula' in parsed_params:
                params['formula'] = parsed_params['formula']

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            entries = data.get('data', [])
            if not entries:
                return "No thermodynamic data found for the given query."

            # Keep one best entry per formula.
            grouped = {}
            for entry in entries:
                f = entry.get('formula_pretty')
                if not f:
                    continue
                grouped.setdefault(f, []).append(entry)
            for _, grouped_entries in grouped.items():
                best = _choose_best_entry(grouped_entries)
                if best:
                    entries_filtered.append(best)

        if not entries_filtered:
            return "No thermodynamic data found for the given query."

        # Stable and deterministic order in output.
        entries_filtered = sorted(
            entries_filtered,
            key=lambda x: (x.get('formula_pretty', ''), x.get('energy_above_hull', float('inf')))
        )

        results = []
        for entry in entries_filtered[:20]:
            try:
                formula = entry.get('formula_pretty', 'N/A')
                formation_energy = entry.get('formation_energy_per_atom', 'N/A')
                energy_above_hull = entry.get('energy_above_hull', 'N/A')
                decomposition_enthalpy = entry.get('decomposition_energy_per_atom', 'N/A')
                material_id = entry.get('material_id', 'N/A')
                
                # Format numeric values
                if formation_energy != 'N/A' and formation_energy is not None:
                    formation_energy = f"{float(formation_energy):.4f}"
                if energy_above_hull != 'N/A' and energy_above_hull is not None:
                    energy_above_hull = f"{float(energy_above_hull):.4f}"
                if decomposition_enthalpy != 'N/A' and decomposition_enthalpy is not None:
                    decomposition_enthalpy = f"{float(decomposition_enthalpy):.4f}"
                
                result_str = (
                    f"[{material_id}] {formula}\n"
                    f"  Formation Energy: {formation_energy} eV/atom\n"
                    f"  Energy Above Hull: {energy_above_hull} eV/atom\n"
                    f"  Decomposition Enthalpy: {decomposition_enthalpy} eV/atom"
                )
                results.append(result_str)
            except (KeyError, TypeError, ValueError):
                continue
        
        if not results:
            return "Error: Could not parse thermodynamic data from API response."
        
        formatted = "\n\n".join(results)
        
        # Truncate to 3000 chars
        if len(formatted) > 3000:
            formatted = formatted[:2997] + "..."
        
        return formatted
        
    except requests.exceptions.Timeout:
        return "Error: API request timed out (>10s). Please try again or simplify your query."
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {response.status_code}: {response.reason}"
        try:
            error_detail = response.json().get('detail', response.text[:200])
        except:
            error_detail = response.text[:200]
        return f"Error: {error_msg}. {error_detail}"
    except requests.exceptions.ConnectionError as e:
        return "Error: Failed to connect to Materials Project API. Check your internet connection."
    except requests.exceptions.RequestException as e:
        return f"Error: API request failed. {str(e)[:300]}"
    except json.JSONDecodeError:
        return "Error: Invalid API response format. Please check your API key and query."
    except Exception as e:
        return f"Error: Unexpected error. {type(e).__name__}: {str(e)[:300]}"
