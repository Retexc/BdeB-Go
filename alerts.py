
from utils import get_weather_alerts

def get_text(text_source):
    """
    Accepts either:
      - a dictionary with keys 'language' and 'text'
      - a list of such dictionaries, or even strings,
      - or a plain string.
    Returns the text. First, it tries to find one where language is 'fr';
    if not found, it returns the first available translation.
    """
    # If it's a dict, return its text (fallback to its text regardless of language)
    if isinstance(text_source, dict):
        return text_source.get("text", "")
    # If it's a plain string, just return it.
    if isinstance(text_source, str):
        return text_source
    # If it's not a list, wrap it into a list.
    if not isinstance(text_source, list):
        text_source = [text_source]
    # Try to find a French translation.
    for item in text_source:
        if isinstance(item, dict) and item.get("language") == "fr":
            return item.get("text", "")
    # If no French translation exists, return the first available text.
    for item in text_source:
        if isinstance(item, dict):
            return item.get("text", "")
        elif isinstance(item, str):
            return item
    return ""

def process_stm_alerts(stm_alerts_data, weather_api_key):
    """
    Process STM alerts for display alongside EXO alerts.
    Only alerts with at least one informed entity matching the allowed criteria are kept.
    """
    filtered_alerts = []
    if not stm_alerts_data:
        return filtered_alerts

    # Allowed sets.
    allowed_routes = {"171", "180", "164"}
    allowed_directions = {"W", "E"}
    allowed_stop_codes = {"50270", "62374"}

    # Mapping for friendly stop names.
    stop_code_to_name = {
        "50270": "Collège de Bois-de-Boulogne",
        "62374": "Henri-Bourassa/du Bois-de-Boulogne"  # Adjust as necessary.
    }

    for alert in stm_alerts_data.get('alerts', []):
        # Extract French texts using our helper.
        desc_text = get_text(alert.get('description_texts', []))
        header_text = get_text(alert.get('header_texts', []))

        available_routes = set()
        available_directions = set()
        available_stop_codes = set()
        for entity in alert.get('informed_entities', []):
            if 'route_short_name' in entity:
                available_routes.add(str(entity['route_short_name']).strip())
            if 'direction_id' in entity:
                available_directions.add(str(entity['direction_id']).strip())
            if 'stop_code' in entity:
                available_stop_codes.add(str(entity['stop_code']).strip())
        
        # --- Exception: if route "164" and direction "W", skip the alert for route 164.
        if "164" in available_routes and "W" in available_directions:
            available_routes.discard("164")
        # ------------------------------------------------

        if (available_routes & allowed_routes and
            available_directions & allowed_directions and
            available_stop_codes & allowed_stop_codes):

            valid_routes = sorted(available_routes & allowed_routes)
            valid_stops = sorted(available_stop_codes & allowed_stop_codes)
            friendly_stops = [stop_code_to_name.get(s, s) for s in valid_stops]

            routes_str = ", ".join(valid_routes) if valid_routes else "Non spécifié"
            stops_str = ", ".join(friendly_stops) if friendly_stops else "Inconnu"

            final_header = f"🚍 Info Bus: {header_text}" if header_text else "🚍 Info Bus"

            filtered_alerts.append({
                'header': final_header,
                'description': desc_text,
                'severity': alert.get('effect', 'alert'),
                'routes': routes_str,
                'stop': stops_str,
            })

    # === Append Weather Alerts ===
    weather_alerts = get_weather_alerts(weather_api_key)
    if weather_alerts:
        for _ in weather_alerts:
            filtered_alerts.append({
                'header': "🚨 Avertissement météorologique",
                'description': "Retards possibles en raison des conditions météo. Vérifiez l’horaire avant de partir.",
                'severity': "weather_alert",
                'routes': "Tous",
                'stop': "STM et Exo"
            })

    return filtered_alerts





def process_exo_alerts(exo_alert_entities):
    """
    Filter EXO alerts for certain stop_ids/routes, returning structured data.
    This function remains unchanged.
    """
    filtered_alerts = []

    if not exo_alert_entities:
        return filtered_alerts

    stop_id_to_route = {
        "MTL7D": "Dir Lucien l'Allier",
        "MTL7B": "Saint-Jérôme",
        "MTL59A": "Mascouche",
        "MTL59C": "Ahuntsic"
    }
    valid_stop_ids = set(stop_id_to_route.keys())

    for entity in exo_alert_entities:
        if entity.HasField('alert'):
            alert = entity.alert

            for informed_entity in alert.informed_entity:
                if informed_entity.HasField('stop_id'):
                    stop_id = informed_entity.stop_id
                    if stop_id in valid_stop_ids:
                        train_route = stop_id_to_route[stop_id]

                        fr_description = ""
                        for translation in alert.description_text.translation:
                            if translation.language == 'fr':
                                fr_description = translation.text
                                break
                        if not fr_description:
                            fr_description = "Description non disponible en français"

                        filtered_alerts.append({
                            'header': "🚨🚊 Info Train",
                            'description': fr_description,
                            'severity': alert.effect,
                            'stop_id': stop_id,
                            'train_route': train_route,
                        })

    return filtered_alerts

