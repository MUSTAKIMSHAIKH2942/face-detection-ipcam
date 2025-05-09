import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.report_manager import ReportManager

if __name__ == "__main__":
    rpt_mgr = ReportManager()

    rpt_mgr.insert_alert(camera_id=0, plugin_name="helmet_detection", detection_info="Helmet detected", severity="High")
    
    results = rpt_mgr.query_alerts()
    print("\nQueried Alerts:")
    for alert in results:
        print(alert)

    rpt_mgr.close()
