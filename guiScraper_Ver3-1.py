import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

stop_scraping = False

def scrape_page(driver,url):
    global stop_scraping  # Zugriff auf die globale Variable

    if stop_scraping:
        return
    driver.get(url)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "str-item-card")))
    articles = driver.find_elements(By.CLASS_NAME, "str-item-card")
    main_window = driver.current_window_handle

    max_price = float(max_price_entry.get())  # Den maximalen Preis aus dem Eingabefeld holen

    for article in articles:
        link = None
        try:
            link_element = article.find_element(By.TAG_NAME, "a")
            link = link_element.get_attribute("href")
            driver.execute_script("window.open(arguments[0]);", link)
            time.sleep(random.uniform(0.5, 2))
            driver.switch_to.window(driver.window_handles[-1])

            # Überprüfung des Preises
            price_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".x-price-primary .ux-textspans"))
            )
            price_text = price_element.text.replace("EUR", "").replace("/Stk.", "").strip().replace(',', '.')
            price = float(price_text)

            if price > max_price:
                log_text.insert(tk.END, f"Preis {price:.2f} EUR überschreitet den maximalen Preis {max_price:.2f} EUR. Scraper wird gestoppt.\n")
                stop_scraping = True
                driver.close()
                driver.switch_to.window(main_window)
                return  # Stoppt den Scraping-Prozess

            right_summary_panel = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "RightSummaryPanel"))
            )
            
            time.sleep(random.uniform(0.5, 1))
            
            if 'powerebay' in right_summary_panel.text.lower():
                log_text.insert(tk.END, "POWEREBAY gefunden", "found")
                log_text.insert(tk.END, f" in Artikel: {link}\n")
            else:
                log_text.insert(tk.END, "POWEREBAY nicht gefunden", "not_found")
                log_text.insert(tk.END, f" in Artikel: {link}\n")
            
            driver.close()
            driver.switch_to.window(main_window)
            time.sleep(random.uniform(0.5, 1))
            
        except Exception as e:
            if link:
                log_text.insert(tk.END, f"Fehler bei Artikel {link}: {str(e)}\n")
            else:
                log_text.insert(tk.END, f"Fehler: {str(e)}\n")
            driver.switch_to.window(main_window)
            continue


def get_all_pages(driver,url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "pagination__items")))
    pagination = driver.find_element(By.CLASS_NAME, "pagination__items")
    pages = pagination.find_elements(By.TAG_NAME, "a")
    last_page = int(pages[-1].text) if pages else 1
    return last_page

def start_scraper():
    global stop_scraping
    stop_scraping = False  # Flag initialisieren

    seller_url = url_entry.get()
    if not seller_url:
        messagebox.showerror("Fehler", "Bitte geben Sie eine Verkäufer-URL ein.")
        return

    if not max_price_entry.get().strip():
        messagebox.showerror("Fehler", "Bitte geben Sie einen maximalen Preis ein.")
        return

    log_text.delete(1.0, tk.END)  # Lösche vorherige Logs im Textblock
    
    try:
        max_price = float(max_price_entry.get())  # Sicherstellen, dass der Maximalpreis als Zahl interpretiert wird

        # Initialisiere den Webdriver
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-search-engine-choice-screen")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        
        
        if search_all_pages.get():
            last_page = get_all_pages(driver,seller_url)
            for i in range(1, last_page + 1):
                if stop_scraping:
                    break
                page_url = f"{seller_url}&_pgn={i}"
                scrape_page(driver,page_url)
        else:
            scrape_page(driver,seller_url)

        
    except ValueError:
        messagebox.showerror("Fehler", "Der eingegebene Maximalpreis ist ungültig.")
    except Exception as e:
        messagebox.showerror("Fehler", str(e))
    finally:
        driver.quit()  # Sicherstellen, dass der WebDriver immer geschlossen wird

    log_text.insert(tk.END, "Der Scraping-Prozess ist abgeschlossen.\n")

# Erstellen des Hauptfensters
root = tk.Tk()
root.title("Selenium Scraper")



# Erstellen des Eingabefelds für die URL
tk.Label(root, text="Verkäufer-URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)


# Hinzufügen einer wichtigen Nachricht
important_label = tk.Label(root, text="Wichtig", font=('Helvetica', 12, 'bold', 'underline'))
important_label.pack(pady=5)

# Frame für die Checkbox und den Text daneben
frame = tk.Frame(root)
frame.pack(pady=5)

# Checkbox für die Option "gesamten Verkäufer durchsuchen"
search_all_pages = tk.BooleanVar()
search_all_pages_check = tk.Checkbutton(frame, text="Gesamten Verkäufer durchsuchen", variable=search_all_pages)
search_all_pages_check.pack(side=tk.LEFT)

# Label neben der Checkbox
checkbox_info = tk.Label(frame, text="Wenn ihr den gesamten Verkäufer durchsuchen wollt, ist es zwingend notwendig, dass der Preis nach niedrig sortiert ist.",
                         wraplength=200, justify="left")
checkbox_info.pack(side=tk.LEFT, padx=10)

# Frame für den Betrag und Information
frame2 = tk.Frame(root)
frame2.pack(pady=5)

# Erstellen des Eingabefelds für den Maximalpreis
tk.Label(frame2, text="Maximaler Preis (EUR):").pack(side=tk.LEFT,pady=10)
max_price_entry = tk.Entry(frame2, width=10)
max_price_entry.pack(side=tk.LEFT,pady=5)

# Label neben der Checkbox
money_info = tk.Label(frame2, text="Wenn ein Artikel mit dem Preis oder höher auftaucht wird gestoppt. Wenn ihr also das nicht berücksichtigen wollt gebt einfach 10000 ein.",
                         wraplength=200, justify="left")
money_info.pack(side=tk.LEFT, padx=10)

# Erstellen des Start-Buttons
start_button = tk.Button(root, text="Scraper starten", command=start_scraper)
start_button.pack(pady=20)

# Erstellen des Textblocks für die Logs
log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=160, height=20)
log_text.pack(pady=10)

# Definieren von Tags für farbigen Text
log_text.tag_config("found", background="lightgreen", foreground="black")
log_text.tag_config("not_found", background="lightcoral", foreground="white")

# Starten der GUI
root.mainloop()
