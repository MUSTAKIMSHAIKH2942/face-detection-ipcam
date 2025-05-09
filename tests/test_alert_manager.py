# test_alert_manager.py (temporary)
from core.alert_manager import AlertManager

if __name__ == "__main__":
    alert_mgr = AlertManager()

    alert_mgr.add_alert(camera_id=0, plugin_name="helmet_detection", detection_info="Helmet detected", severity="High")
    alert_mgr.add_alert(camera_id=1, plugin_name="fire_detection", detection_info="Fire detected", severity="Critical")

    active_alerts = alert_mgr.get_active_alerts()
    print("\nActive Alerts:")
    for alert in active_alerts:
        print(alert)

    alert_mgr.acknowledge_alert(0)

    active_alerts = alert_mgr.get_active_alerts()
    print("\nAlerts after acknowledging one:")
    for alert in active_alerts:
        print(alert)

    alert_mgr.clear_alerts()
