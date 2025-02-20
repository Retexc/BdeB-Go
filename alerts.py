# alerts.py

from utils import get_weather_alerts

def process_stm_alerts(stm_alerts_data, weather_api_key):
    """
    1. Filter STM alerts for certain routes/directions/stops.
    2. Append weather alerts if present.
    """
    filtered_alerts = []

    if not stm_alerts_data:
        return filtered_alerts  # No STM alerts => return empty list

    # Loop over all STM alerts. The STM API returns JSON with a top-level "alerts" list.
    # Each alert in that list can have fields like 'informed_entities', 'effect', 'header_texts', etc.
    for alert in stm_alerts_data.get('alerts', []):
        affected_routes = set()
        direction_match = False
        stop_match = False

        # Check each informed_entity (i.e. which routes/stops this alert applies to)
        for entity in alert.get('informed_entities', []):
            # Example filter: watch for routes 171, 164, 180
            if entity.get('route_short_name') in ['171', '164', '180']:
                affected_routes.add(entity.get('route_short_name'))
            # Example: only eastbound is relevant
            if entity.get('direction_id') == 'E':
                direction_match = True
            # Example: looking specifically for stop_code "50270"
            if entity.get('stop_code') == '50270':
                stop_match = True

        # If this alert matches your criteria, add it to filtered_alerts
        if affected_routes and direction_match and stop_match:
            # Try to get French text from header/description
            fr_text = next((t['text'] for t in alert.get('header_texts', []) if t['language'] == 'fr'), '')
            fr_desc = next((t['text'] for t in alert.get('description_texts', []) if t['language'] == 'fr'), '')

            route_numbers = ", ".join(sorted(affected_routes))  
            filtered_alerts.append({
                'header': fr_text,
                'description': fr_desc,
                'severity': alert.get('effect', 'alert'),
                'routes': route_numbers,
                'stop': "Collège de Bois-de-Boulogne"  # or whichever name is relevant
            })

    # === Add Weather Alerts ===
    # If you want to automatically append weather alerts to STM alerts:
    weather_alerts = get_weather_alerts(weather_api_key)
    for _ in weather_alerts:
        # You can parse more weather info if you want. This is a simplified message.
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
    Each entity in exo_alert_entities has .alert with .informed_entity, effect, etc.
    """
    filtered_alerts = []

    if not exo_alert_entities:
        return filtered_alerts

    # Example: map certain stop_ids to a named route or direction
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

            # Check which stops are informed by this alert
            for informed_entity in alert.informed_entity:
                if informed_entity.HasField('stop_id'):
                    stop_id = informed_entity.stop_id
                    if stop_id in valid_stop_ids:
                        # e.g. "Saint-Jérôme" or "Dir Lucien l'Allier"
                        train_route = stop_id_to_route[stop_id]

                        # Attempt to get a French description
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
                            'severity': alert.effect,  # e.g. 'MODIFIED_SERVICE', etc.
                            'stop_id': stop_id,
                            'train_route': train_route,
                        })

    return filtered_alerts
