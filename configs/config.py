import os

BASE_DOWNLOAD_DIR = os.path.join(os.getcwd(), "ice_rto_wise_data")
BASE_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"

# Needs to be changed everyday
STATE_DROPDOWN_LABEL = 'j_idt40_label'
LEFT_REFRESH_BUTTON_LABEL = "j_idt75"
RIGHT_REFRESH_BUTTON_LABEL = "j_idt70"

YEAR_STATE_MAPPING = {
    "2022" : [
        "Andaman & Nicobar Island(3)", "Andhra Pradesh(83)", "Arunachal Pradesh(29)",
        "Assam(33)", "Bihar(48)", "Chandigarh(1)", "Chhattisgarh(31)", "Delhi(16)",
        "Goa(13)", "Gujarat(37)", "Haryana(98)", "Himachal Pradesh(96)", "Jammu and Kashmir(21)",
        "Jharkhand(25)", "Karnataka(68)", "Kerala(87)", "Ladakh(3)", "Lakshadweep(5)",
        "Madhya Pradesh(53)", "Maharashtra(57)", "Manipur(13)", "Meghalaya(13)", "Mizoram(10)",
        "Nagaland(9)", "Odisha(39)", "Puducherry(8)", "Punjab(96)", "Rajasthan(59)",
        "Sikkim(9)", "Tamil Nadu(148)", "Tripura(9)", "Uttarakhand(21)", "Uttar Pradesh(77)",
        "UT of DNH and DD(3)", "West Bengal(57)"
    ],    

    "2023" : [
        "Andaman & Nicobar Island(3)", "Andhra Pradesh(83)", "Arunachal Pradesh(29)",
        "Assam(33)", "Bihar(48)", "Chandigarh(1)", "Chhattisgarh(31)", "Delhi(16)",
        "Goa(13)", "Gujarat(37)", "Haryana(98)", "Himachal Pradesh(96)", "Jammu and Kashmir(21)",
        "Jharkhand(25)", "Karnataka(68)", "Kerala(87)", "Ladakh(3)", "Lakshadweep(5)",
        "Madhya Pradesh(53)", "Maharashtra(57)", "Manipur(13)", "Meghalaya(13)", "Mizoram(10)",
        "Nagaland(9)", "Odisha(39)", "Puducherry(8)", "Punjab(96)", "Rajasthan(59)",
        "Sikkim(9)", "Tamil Nadu(148)", "Tripura(9)", "Uttarakhand(21)", "Uttar Pradesh(77)",
        "UT of DNH and DD(3)", "West Bengal(57)"
    ],

    "2024" : [
        "Andaman & Nicobar Island(3)", "Andhra Pradesh(83)", "Arunachal Pradesh(29)",
        "Assam(33)", "Bihar(48)", "Chandigarh(1)", "Chhattisgarh(31)", "Delhi(16)",
        "Goa(13)", "Gujarat(37)", "Haryana(98)", "Himachal Pradesh(96)", "Jammu and Kashmir(21)",
        "Jharkhand(25)", "Karnataka(68)", "Kerala(87)", "Ladakh(3)", "Lakshadweep(5)",
        "Madhya Pradesh(53)", "Maharashtra(57)", "Manipur(13)", "Meghalaya(13)", "Mizoram(10)",
        "Nagaland(9)", "Odisha(39)", "Puducherry(8)", "Punjab(96)", "Rajasthan(59)",
        "Sikkim(9)", "Tamil Nadu(148)", "Tripura(9)", "Uttarakhand(21)", "Uttar Pradesh(77)",
        "UT of DNH and DD(3)", "West Bengal(57)"
    ],  

    "2025" : [
        "Andaman & Nicobar Island(3)", "Andhra Pradesh(83)", "Arunachal Pradesh(29)",
        "Assam(33)", "Bihar(48)", "Chandigarh(1)", "Chhattisgarh(31)", "Delhi(16)",
        "Goa(13)", "Gujarat(37)", "Haryana(98)", "Himachal Pradesh(96)", "Jammu and Kashmir(21)",
        "Jharkhand(25)", "Karnataka(68)", "Kerala(87)", "Ladakh(3)", "Lakshadweep(5)",
        "Madhya Pradesh(53)", "Maharashtra(57)", "Manipur(13)", "Meghalaya(13)", "Mizoram(10)",
        "Nagaland(9)", "Odisha(39)", "Puducherry(8)", "Punjab(96)", "Rajasthan(59)",
        "Sikkim(9)", "Tamil Nadu(148)", "Tripura(9)", "Uttarakhand(21)", "Uttar Pradesh(77)",
        "UT of DNH and DD(3)", "West Bengal(57)"
    ]
}

# CONSTANTS
YEAR_DROPDOWN_LABEL = "selectedYear_label"
X_AXIS_LABEL = "xaxisVar_label"
Y_AXIS_LABEL = "yaxisVar_label"

# S3 CREDENTIALS
S3_BUCKET_NAME = ""
S3_ACCESS_KEY = ""
S3_SECRET_KEY = ""
S3_REGION = ""

# EV and ICE
FUEL_TYPES_EV = [7, 21]
FUEL_TYPES_ICE = [14, 15, 16, 17, 18, 19]
FUEL_TYPES = FUEL_TYPES_ICE


# Vehicle Categories
TWO_WHEELER = [0, 1, 2]
FOUR_WHEELER = []
VEHICLE_CATEGORIES = TWO_WHEELER


# CHROME OPTIONS
CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-notifications",
    "--disable-blink-features=AutomationControlled"
]

CHROME_EXPERIMENTAL_OPTIONS = {
    "excludeSwitches": ["enable-automation"],
    "useAutomationExtension": False
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
]

PREFS = {
    "download.default_directory": BASE_DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

