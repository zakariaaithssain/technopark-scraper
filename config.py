# config.py
#contains the xpaths, fallback xpaths, and the driver's options.
import logging as log



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
    # A deprecation error I don't understand
    "enable_unsafe_swiftshader": "--enable-unsafe-swiftshader",
    
    # Disable features causing TensorFlow errors
    "disable_viz_display_compositor": "--disable-features=VizDisplayCompositor",
    "disable_audio_service_out_of_process": "--disable-features=AudioServiceOutOfProcess",
    "disable_speech_recognition": "--disable-speech-api",
    "disable_background_networking": "--disable-background-networking",
    
    # Performance optimizations
    "disable_sandbox": "--no-sandbox",
    "disable_gpu_acceleration": "--disable-gpu",
    "disable_browser_extensions": "--disable-extensions",
    "disable_browser_plugins": "--disable-plugins",
    "disable_image_loading": "--disable-images",
    
    # Headless Mode
    "run_headless_mode": "--headless",
    
    # Performance-critical options from the optimal configuration
    "disable_software_rasterizer": "--disable-software-rasterizer",
    "disable_background_timer_throttling": "--disable-background-timer-throttling",
    "disable_backgrounding_occluded_windows": "--disable-backgrounding-occluded-windows",
    "disable_renderer_backgrounding": "--disable-renderer-backgrounding",
    "disable_translate_ui": "--disable-features=TranslateUI",
    "disable_ipc_flooding_protection": "--disable-ipc-flooding-protection",
    "disable_hang_monitor": "--disable-hang-monitor",
    "disable_prompt_on_repost": "--disable-prompt-on-repost",
    "disable_domain_reliability": "--disable-domain-reliability",
    "disable_component_extensions_background": "--disable-component-extensions-with-background-pages",
    
    # Memory optimization
    "memory_pressure_off": "--memory-pressure-off",
    "max_old_space_size": "--max_old_space_size=4096",
    "aggressive_cache_discard": "--aggressive-cache-discard",
    
    # Error suppression and logging
    "log_level": "--log-level=3",
    "silent_mode": "--silent",
    "disable_logging": "--disable-logging",
    "ignore_ssl_errors": "--ignore-ssl-errors",
    "ignore_certificate_errors": "--ignore-certificate-errors",
    "disable_voice_interaction": "--disable-features=VoiceInteraction",
    "disable_optimization_hints": "--disable-features=OptimizationHints",
    "disable_media_router": "--disable-features=MediaRouter",
    
    # SSL and security (for scraping performance)
    "allow_running_insecure_content": "--allow-running-insecure-content",
    "disable_web_security": "--disable-web-security",
    "ignore_ssl_errors_bugs": "--ignore-ssl-errors-bugs",
    "ignore_certificate_errors_spki": "--ignore-certificate-errors-spki-list",
    "disable_features_network_service": "--disable-features=NetworkService",
    
    # Essential stability
    "disable_dev_shm_usage": "--disable-dev-shm-usage",
    
    # Disable automation detection
    "exclude_automation_switches": ("excludeSwitches", ["enable-automation"]),
    "disable_automation_extension": ("useAutomationExtension", False),
    "disable_blink_features": ("excludeSwitches", ["enable-blink-features=AutomationControlled"])
}

REGEX = {"phones_pattern" : r'(?:\+212[\s\.\-]?(?:0)?|0)?[5-7]\d(?:[\s\.\-]?\d{2}){3}',
         
        "emails_pattern" : r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        }


DATAPATH = "data/technopark_startups.json"

LOG_OPTIONS = {"level" : log.INFO,
                "format" : '%(asctime)s - %(levelname)s - %(message)s',
                "file_handler": "project.log",
                "mode" : "w"}
