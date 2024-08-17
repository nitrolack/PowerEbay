from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

# Initialisiere den Webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Gehe zur Verkäuferseite
seller_url = "https://www.ebay.de/str/perlesmith"
driver.get(seller_url)

# Warte, bis die Artikel geladen sind
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "str-item-card")))

# Sammle alle Artikel-Elemente auf der Seite
articles = driver.find_elements(By.CLASS_NAME, "str-item-card")

# Speichere das Hauptfenster
main_window = driver.current_window_handle

# Iteriere durch alle gefundenen Artikel
for article in articles:
    try:
        # Klicke auf den Artikel-Link
        link_element = article.find_element(By.TAG_NAME, "a")
        link = link_element.get_attribute("href")
        driver.execute_script("window.open(arguments[0]);", link)
        
        # Warte kurz und überprüfe, ob ein neues Fenster geöffnet wurde
        time.sleep(random.uniform(1, 2))  # Leichte Wartezeit
        driver.switch_to.window(driver.window_handles[-1])
        #new_window_opened = WebDriverWait(driver, 15).until(EC.new_window_is_opened(driver.window_handles))
        #if new_window_opened:
        #    driver.switch_to.window(driver.window_handles[-1])
        #else:
        #    print(f"Konnte nicht zu neuem Fenster wechseln für Artikel: {link}")
        #    continue
        
        # Warte, bis das spezifische div geladen ist
        right_summary_panel = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "RightSummaryPanel"))
        )
        
        # Füge eine kleine Wartezeit hinzu
        time.sleep(random.uniform(0.5, 1))
        
        # Überprüfe, ob "POWEREBAY" im RightSummaryPanel vorhanden ist
        if "powerebay" in right_summary_panel.text.lower():
            print(f"POWEREBAY gefunden in Artikel: {link}")
        else:
            print(f"POWEREBAY nicht gefunden in Artikel: {link}")
        
        # Schließe das aktuelle Fenster und wechsle zurück zur Hauptseite
        driver.close()
        driver.switch_to.window(main_window)
        
        # Füge eine zufällige Verzögerung hinzu, um nicht blockiert zu werden
        time.sleep(random.uniform(0.5, 1))
        
    except Exception as e:
        print(f"Fehler bei Artikel {link}: {str(e)}")
        try:
            # Ausgabe des genauen Fehlers
            import traceback
            print(traceback.format_exc())
            
            driver.switch_to.window(main_window)
        except Exception as inner_e:
            print(f"Fehler beim Zurückwechseln zum Hauptfenster: {str(inner_e)}")
        continue

# Schließe den Webdriver
driver.quit()
