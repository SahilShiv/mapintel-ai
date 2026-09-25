"""
Google Maps Scraper Selector Registry
Isolates all DOM selectors, XPath queries, and UI exclusion rules
to make scraper resilient to Google Maps UI variations and layout updates.
"""

# Cookie and Consent Dialogs
CONSENT_BUTTON_XPATHS = [
    "//button[contains(., 'Accept all') or contains(., 'Agree') or contains(., 'Tout accepter') or contains(., 'Alle akzeptieren')]",
    "//form[@action='https://consent.google.com/save']//button",
    "//button[contains(@aria-label, 'Accept')]"
]

# Navigation / Updates Tab Selectors
UPDATES_TAB_XPATHS = [
    "//button[@role='tab' and (contains(., 'Updates') or contains(@aria-label, 'Updates'))]",
    "//button[contains(@aria-label, 'Updates') or contains(., 'Updates')]",
    "//div[@role='tablist']//button[contains(., 'Updates') or contains(@aria-label, 'Updates')]",
    "//button[contains(@aria-label, 'Posts') or contains(., 'Posts')]",
    "//button[contains(@aria-label, 'Actus') or contains(., 'Actus')]",
    "//button[contains(@aria-label, 'Novedades') or contains(., 'Novedades')]"
]

# Post / Update Container Selectors (Strictly isolated to updates)
POST_CONTAINER_XPATHS = [
    "//div[@role='article' and not(ancestor::div[@role='navigation'])]",
    "//div[contains(@data-post-id, '') and string-length(@data-post-id) > 0]",
    "//div[contains(@class, 'gws-local-posts')]",
    "//div[contains(@class, 'm6QErb')]//div[@role='article']",
    "//div[contains(@class, 'dS8AEf')]//div[@role='article']"
]

# CSS Selectors for post containers
POST_CONTAINER_CSS = [
    "div[role='article']",
    "div.gws-local-posts__post",
    "div[data-post-id]"
]

# Selectors within a post container for the actual post body text
POST_TEXT_XPATHS = [
    ".//div[contains(@class, 'fontBodyMedium')]",
    ".//span[contains(@class, 'fontBodyMedium')]",
    ".//div[contains(@class, 'w70Dg')]",
    ".//div[@data-attrid='post_snippet']",
    ".//div[contains(@class, 'KTaOIe')]"
]

# "Read more" / Expand button within post card
EXPAND_BUTTON_XPATHS = [
    ".//button[contains(., 'More') or contains(@aria-label, 'More') or contains(., 'more')]",
    ".//span[contains(., '... More') or contains(., '...More')]/parent::button",
    ".//button[contains(@class, 'w8nwRe')]"
]

# Date timestamp selectors within a post card
POST_DATE_XPATHS = [
    ".//span[contains(@class, 'rsqaWe')]",
    ".//span[contains(@aria-label, 'ago') or contains(., 'ago')]",
    ".//span[contains(., 'weeks ago') or contains(., 'days ago') or contains(., 'months ago') or contains(., 'hours ago')]",
    ".//div[contains(@class, 'z3HNbe')]"
]

# Call-to-action button or link within a post card
POST_CTA_XPATHS = [
    ".//a[contains(@class, 'CsO0F') or contains(@data-url, 'http') or @role='button']",
    ".//button[contains(@class, 'CsO0F') or @aria-label]",
    ".//a[contains(@href, 'http') and not(contains(@href, 'google.com/maps'))]"
]

# Media / Image elements inside a post card
POST_IMAGE_XPATHS = [
    ".//img[contains(@src, 'googleusercontent.com') and not(contains(@src, 'avatar')) and not(contains(@src, 'icon'))]",
    ".//button[contains(@data-photo-index, '')]//img",
    ".//div[contains(@class, 'm6QErb')]//img[contains(@src, 'googleusercontent')]"
]

# Google Maps Navigation & Page UI Terms Blacklist
# ANY text composed primarily of these phrases is page UI garbage and MUST be rejected
UI_KEYWORD_BLACKLIST = {
    "directions",
    "restaurants",
    "hotels",
    "things to do",
    "transit",
    "parking",
    "pharmacies",
    "atms",
    "saved",
    "recents",
    "get app",
    "send to phone",
    "share",
    "about this data",
    "google maps sign in",
    "sign in",
    "layers",
    "map data",
    "privacy",
    "terms",
    "send product feedback",
    "1 km",
    "2 km",
    "500 m",
    "search google maps",
    "suggest an edit",
    "claim this business",
    "add missing place",
    "your places",
    "your contributions",
    "location sharing",
    "search here",
    "collapse side panel",
    "expand side panel",
    "street view",
    "see photos",
    "all",
    "reviews",
    "about",
    "photos",
    "overview",
    "menu",
    "website",
    "call",
    "save",
    "nearby",
    "send to your phone"
}
