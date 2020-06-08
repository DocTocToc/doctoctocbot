from selenium import webdriver

DRIVER = None

def getOrCreateWebdriver(js=True):
    options = webdriver.FirefoxOptions()
    options.headless = True
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--test-type')
    options.add_argument("-headless")
    if not js:
        options.set_preference('javascript.enabled', False)
    global DRIVER
    DRIVER = DRIVER or webdriver.Firefox(options=options)
    DRIVER.implicitly_wait(1)
    return DRIVER