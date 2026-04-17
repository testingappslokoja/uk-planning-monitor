from typing import List, Dict

import config


def filter_applications(applications: List[Dict], keywords: List[str] = None) -> List[Dict]:
    if keywords is None:
        keywords = config.KEYWORDS
    
    filtered = []
    for app in applications:
        text = f"{app.get('description', '')} {app.get('address', '')}".lower()
        for keyword in keywords:
            if keyword.lower() in text:
                app["matched_keyword"] = keyword
                filtered.append(app)
                break
    
    return filtered