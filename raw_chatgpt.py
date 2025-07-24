from contextlib import suppress
from seleniumbase import SB
"""
import win32gui
import time

def hide_tab():
    # --- Nowe linie do ukrywania okna ---
    try:
        # Czekamy chwilę na otwarcie okna przeglądarki
        time.sleep(2)
        # Znajdujemy uchwyt okna Chrome po jego tytule (może być potrzebna korekta)
        # Tytuł okna Chrome to zazwyczaj tytuł strony, na której jest.
        # Możesz go sprawdzić ręcznie, otwierając przeglądarkę i patrząc na pasek tytułu.
        # W przypadku chatgpt.com to "ChatGPT"
        hwnd = win32gui.FindWindow(None, "ChatGPT - Google Chrome") # Zmień na rzeczywisty tytuł okna Chrome
        if hwnd:
            win32gui.ShowWindow(hwnd, 0) # 0 to SW_HIDE (ukryj okno)
            print("Ukryto okno przeglądarki.")
        else:
            print("Nie znaleziono okna przeglądarki do ukrycia.")
    except Exception as e:
        print(f"Błąd podczas ukrywania okna: {e}")
    # --- Koniec nowych linii ---
"""
"""
def chatgpt(prompt):    
    with SB(uc=True, test=True) as sb:
        url = "https://chatgpt.com/"
        sb.activate_cdp_mode(url)
        sb.sleep(1)
        
        sb.uc_gui_click_captcha()
        sb.sleep(1)
        sb.uc_gui_handle_captcha()
        sb.sleep(1)
        
        sb.click_if_visible('button[aria-label="Close dialog"]')
        sb.press_keys("#prompt-textarea", prompt)
        sb.click('button[data-testid="send-button"]')

        #hide_tab()

        #print('*** Input for ChatGPT: ***\n"%s"' % prompt)
        sb.sleep(3)
        with suppress(Exception):
            # The "Stop" button disappears when ChatGPT is done typing a response
            sb.wait_for_element_not_visible(
                'button[data-testid="stop-button"]', timeout=1000
            )
        chat = sb.find_element('[data-message-author-role="assistant"] .markdown')
        soup = sb.get_beautiful_soup(chat.get_html()).get_text("\n").strip()
        soup = soup.replace("\n\n\n", "\n\n")
        soup = soup.replace("\n\n\n", "\n\n")
        return soup

print(chatgpt('Napisz referat na 2000 słów o polsce. nie pytaj o szczegóły tylko po prostu pisz. Zakończ ją słowem skończyłem.'))
"""

from contextlib import suppress
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def chatgpt(prompt, headless_mode=True):
    """
    Automatyzuje interakcję z ChatGPT, z obsługą przełączania trybu headless
    w przypadku napotkania CAPTCHA.
    """
    try:
        with SB(uc=True, headless=headless_mode, test=True) as sb:
            url = "https://chatgpt.com/"
            sb.activate_cdp_mode(url)
            sb.sleep(1)

            # Sprawdź, czy pojawiła się CAPTCHA
            # Zamiast bezpośredniego wywołania sb.uc_gui_click_captcha(),
            # spróbujmy sprawdzić widoczność elementów CAPTCHA.
            # UWAGA: Te selektory mogą się różnić w zależności od rodzaju CAPTCHA
            # i mogą wymagać dostosowania.
            captcha_detected = False
            try:
                # Przykład sprawdzenia obecności typowych elementów CAPTCHA
                # Mogą to być ramki iframe, specyficzne przyciski, itp.
                if sb.is_element_visible("iframe[title*='captcha']") or \
                   sb.is_element_visible('div#cf-challenge-wrapper') or \
                   sb.is_element_visible('div.g-recaptcha'):
                    captcha_detected = True
            except NoSuchElementException:
                pass # Element nie znaleziony, czyli brak CAPTCHA

            if captcha_detected and headless_mode:
                print("CAPTCHA wykryta w trybie headless. Ponowna próba w trybie GUI...")
                # Zamknij bieżącą sesję SB i spróbuj ponownie w trybie GUI
                return chatgpt(prompt, headless_mode=False)
            elif captcha_detected and not headless_mode:
                print("CAPTCHA wykryta w trybie GUI. Próbuję rozwiązać...")
                # Jeśli jesteśmy w trybie GUI i CAPTCHA nadal jest, spróbuj ją rozwiązać
                # Odkomentuj poniższe linie, gdy jesteś w trybie GUI
                sb.uc_gui_click_captcha()
                sb.sleep(2) # Daj czas na interakcję z CAPTCHA
                sb.uc_gui_handle_captcha()
                sb.sleep(2) # Daj czas na załadowanie strony po rozwiązaniu CAPTCHA

            # Kontynuacja standardowej logiki po obsłużeniu CAPTCHA lub jej braku
            sb.click_if_visible('button[aria-label="Close dialog"]')
            sb.press_keys("#prompt-textarea", prompt)
            sb.click('button[data-testid="send-button"]')

            sb.sleep(3)
            with suppress(Exception):
                sb.wait_for_element_not_visible(
                    'button[data-testid="stop-button"]', timeout=1000
                )
            
            chat = sb.find_element('[data-message-author-role="assistant"] .markdown')
            soup = sb.get_beautiful_soup(chat.get_html()).get_text("\n").strip()
            soup = soup.replace("\n\n\n", "\n\n")
            soup = soup.replace("\n\n\n", "\n\n")
            return soup

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        if headless_mode:
            print("Wystąpił błąd w trybie headless. Ponowna próba w trybie GUI...")
            return chatgpt(prompt, headless_mode=False)
        else:
            print("Wystąpił błąd w trybie GUI. Nie można kontynuować.")
            raise # Rzuć wyjątek, jeśli błąd wystąpił już w trybie GUI

# Przykładowe użycie:
response = chatgpt("Wytłumacz mi kwantowy splątanie w prostych słowach.")
print(response)


"""
with SB(uc=True, headless=True, test=True) as sb:
    url = "https://chatgpt.com/"
    sb.activate_cdp_mode(url)
    sb.sleep(1)
    sb.uc_gui_click_captcha()
    sb.sleep(1)
    sb.uc_gui_handle_captcha()
    sb.sleep(1)
    sb.click_if_visible('button[aria-label="Close dialog"]')
    prompt = "Opowiedz mi o najnowszych informacjach z bliskiego wschodu."
    sb.press_keys("#prompt-textarea", prompt)
    sb.click('button[data-testid="send-button"]')
    #print('*** Input for ChatGPT: ***\n"%s"' % prompt)
    sb.sleep(3)
    with suppress(Exception):
        # The "Stop" button disappears when ChatGPT is done typing a response
        sb.wait_for_element_not_visible(
            'button[data-testid="stop-button"]', timeout=20
        )
    chat = sb.find_element('[data-message-author-role="assistant"] .markdown')
    soup = sb.get_beautiful_soup(chat.get_html()).get_text("\n").strip()
    soup = soup.replace("\n\n\n", "\n\n")
    soup = soup.replace("\n\n\n", "\n\n")
    #print("*** Response from ChatGPT: ***\n%s" % soup)
    #sb.sleep(3)
    print(soup)
"""