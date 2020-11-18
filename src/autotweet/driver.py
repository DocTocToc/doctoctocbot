from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DRIVER = None

def getOrCreateWebdriver(js=True):
    options = webdriver.FirefoxOptions()
    options.headless = True
    options.add_argument('--ignore-certificate-errors')
    #options.add_argument('--test-type')
    options.add_argument("-headless")
    if not js:
        options.set_preference('javascript.enabled', False)
    else:
        options.set_preference('javascript.enabled', True)
    global DRIVER
    DRIVER = DRIVER or webdriver.Firefox(options=options)
    DRIVER.implicitly_wait(1)
    return DRIVER

def getChromeRemoteDriver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    #browser = webdriver.Chrome(options=options)  # see edit for recent code change.
    #browser.implicitly_wait(20)
    driver = webdriver.Remote("http://chrome:4444/wd/hub",
        options.to_capabilities())
    driver.implicitly_wait(20)
    return driver

