import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

def start_scraper():
    seller_url = url_entry.get()
    if not seller_url:
        messagebox.showerror("Fehler", "Bitte geben Sie eine Verkäufer-URL ein.")
        return

    log_text.delete(1.0, tk.END)  # Lösche vorherige Logs im Textblock
    
    try:
        # Initialisiere den Webdriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(seller_url)
        
        # Warte, bis die Artikel geladen sind
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "str-item-card")))

        # Sammle alle Artikel-Elemente auf der Seite
        articles = driver.find_elements(By.CLASS_NAME, "str-item-card")

        # Speichere das Hauptfenster
        main_window = driver.current_window_handle

        # Iteriere durch alle gefundenen Artikel
        for article in articles:
            link = None  # Initialisiere die Variable link
            try:
                # Klicke auf den Artikel-Link
                link_element = article.find_element(By.TAG_NAME, "a")
                link = link_element.get_attribute("href")
                driver.execute_script("window.open(arguments[0]);", link)
                
                # Warte kurz und überprüfe, ob ein neues Fenster geöffnet wurde
                time.sleep(random.uniform(0, 2))  # Leichte Wartezeit
                driver.switch_to.window(driver.window_handles[-1])
                
                # Warte, bis das spezifische div geladen ist
                right_summary_panel = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "RightSummaryPanel"))
                )
                
                # Füge eine kleine Wartezeit hinzu
                time.sleep(random.uniform(0.5, 1))
                
                # Überprüfe, ob "POWEREBAY" im RightSummaryPanel vorhanden ist
                if "powerebay" in right_summary_panel.text.lower():
                    log_text.insert(tk.END, f"POWEREBAY gefunden in Artikel: {link}\n")
                else:
                    log_text.insert(tk.END, f"POWEREBAY nicht gefunden in Artikel: {link}\n")
                
                # Schließe das aktuelle Fenster und wechsle zurück zur Hauptseite
                driver.close()
                driver.switch_to.window(main_window)
                
                # Füge eine zufällige Verzögerung hinzu, um nicht blockiert zu werden
                time.sleep(random.uniform(0.5, 1))
                
            except Exception as e:
                if link:  # Überprüfe, ob link gesetzt ist
                    log_text.insert(tk.END, f"Fehler bei Artikel {link}: {str(e)}\n")
                else:
                    log_text.insert(tk.END, f"Fehler: {str(e)}\n")
                driver.switch_to.window(main_window)
                continue

        # Schließe den Webdriver
        driver.quit()
        
        log_text.insert(tk.END, "Der Scraping-Prozess ist abgeschlossen.\n")
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

# Erstellen des Hauptfensters
root = tk.Tk()
root.title("Selenium Scraper")

# Erstellen des Eingabefelds für die URL
tk.Label(root, text="Verkäufer-URL:").pack(pady=10)
url_entry = tk.Entry(root, width=80)
url_entry.pack(pady=5)

# Erstellen des Start-Buttons
start_button = tk.Button(root, text="Scraper starten", command=start_scraper)
start_button.pack(pady=20)

# Erstellen des Textblocks für die Logs
log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=160, height=20)  # Breite auf 100 Zeichen erhöht
log_text.pack(pady=10)

# Starten der GUI
root.mainloop()
