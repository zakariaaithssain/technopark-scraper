# config.py
#contains the xpaths, fallback xpaths, and the driver's options.
XPATHS = {
    "triangle_button": '//*[@id="root"]/div/div/div/div[2]/div[3]/nav/ul/li[9]',
    "name" : "//*[@id='root']/div/div/div/div/div/div[2]/div[1]/h2",
    "sector": "//div[2]/div[2]/p",
    "technologies": "//div[2]/div[3]/p",
    "city": "//div[2]/div[4]/p",
    "description": "//div[2]/div[5]//p",
    "websites_button" : '//*[@id="root"]/div/div/div/div/div/div[1]/div[2]/button[3]'
}

FALLBACKXPATHS  = {"name" : None, 
                   "sector" : ["//div[contains(@class, 'sector')]//p"],
                   "technologies" : ["//div[contains(@class, 'tech')]//p"], 
                   "city" : ["//div[contains(@class, 'city')]//p"], 
                   "description" : ["//div[contains(@class, 'description')]//p"]}


CHROME_OPTIONS = {

    #the interpreter told me to enable this option because of some deprecation error
    "an_error_i_dont_know" : "--enable-unsafe-swiftshader",

     # Disable features causing the TensorFlow errors
    "disable_viz_display_compositor": "--disable-features=VizDisplayCompositor",
    "disable_audio_service_out_of_process": "--disable-features=AudioServiceOutOfProcess", 
    "disable_speech_recognition": "--disable-speech-api",
    "disable_background_networking": "--disable-background-networking",
    
    # More performance optimizations
    "disable_sandbox": "--no-sandbox",
    "disable_gpu_acceleration": "--disable-gpu",
    "disable_browser_extensions": "--disable-extensions",
    "disable_browser_plugins": "--disable-plugins",
    "disable_image_loading": "--disable-images",
    
    # Headless Mode
    "run_headless_mode": "--headless",
    
    # Disable automation detection
    "exclude_automation_switches": ("excludeSwitches", ["enable-automation"]),
    "disable_automation_extension": ("useAutomationExtension", False)
}

