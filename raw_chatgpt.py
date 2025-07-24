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

print(chatgpt('Napisz referat na 500 słów o dupie. nie pytaj o szczegóły tylko po prostu pisz. Zakończ ją słowem skończyłem.'))
"""
"""
from contextlib import suppress
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def chatgpt(prompt, headless_mode=True):
    #Automatyzuje interakcję z ChatGPT, z obsługą przełączania trybu headless
    #w przypadku napotkania CAPTCHA.
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

from seleniumbase import SB
from contextlib import suppress
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def chatgpt(prompt, headless_mode=True):
    """
    Automatyzuje interakcję z ChatGPT, z obsługą przełączania trybu headless
    w przypadku, gdy pole do wprowadzania tekstu nie pojawi się w oczekiwanym czasie.
    """
    # Zewnętrzny blok try-except dla obsługi błędów na najwyższym poziomie
    try:
        with SB(uc=True, headless=headless_mode, test=True) as sb:
            url = "https://chatgpt.com/"
            sb.activate_cdp_mode(url)
            sb.sleep(1) # Krótka pauza na załadowanie początkowe

            try:
                # Czekamy na pole tekstowe z timeoutem
                # W trybie CDP, jeśli element nie zostanie znaleziony, rzuci generyczny Exception
                sb.wait_for_element("#prompt-textarea", timeout=20)
                    
                # Jeśli pole się pojawiło, kontynuujemy normalnie
                print("Pole do wpisywania tekstu (#prompt-textarea) jest widoczne. Kontynuuję.")
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

            except Exception as e: # Zmieniamy z TimeoutException na ogólny Exception
                # Sprawdzamy, czy komunikat błędu wskazuje na timeout elementu
                if "was not found after" in str(e) and "#prompt-textarea" in str(e):
                    print(f">>> Timeout: {e}") # Wypisujemy cały komunikat błędu
                    
                    if headless_mode:
                        print("Wykryto timeout w trybie headless. Próbuję ponownie w trybie GUI...")
                        # Zwracamy wynik rekurencyjnego wywołania, aby przekazać odpowiedź w górę stosu
                        return chatgpt(prompt, headless_mode=False)
                    else:
                        print("Wykryto timeout w trybie GUI. Prawdopodobnie CAPTCHA lub inna blokada wymaga interwencji.")
                        print("Próbuję rozwiązać CAPTCHA za pomocą sb.uc_gui_click_captcha() i sb.uc_gui_handle_captcha()...")
                        try:
                            # W trybie GUI próbujemy obsłużyć CAPTCHA
                            sb.uc_gui_click_captcha()
                            sb.sleep(3) # Daj czas na interakcję z CAPTCHA
                            sb.uc_gui_handle_captcha()
                            sb.sleep(5) # Daj czas na załadowanie strony po rozwiązaniu CAPTCHA
                            
                            # Po próbie rozwiązania CAPTCHA, spróbuj ponownie poczekać na pole tekstowe
                            print("Ponowna próba znalezienia pola tekstowego po obsłudze CAPTCHA...")
                            sb.wait_for_element("#prompt-textarea", timeout=15) # Krótszy timeout po próbie rozwiązania
                            
                            # Jeśli dotarliśmy tutaj, CAPTCHA została rozwiązana i pole jest widoczne
                            print("CAPTCHA rozwiązana, pole do wpisywania tekstu jest widoczne. Kontynuuję.")
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

                        except Exception as inner_e: # Używamy ogólnego Exception dla wewnętrznego bloku
                            # Sprawdzamy, czy to nadal timeout, czy inny błąd
                            if "was not found after" in str(inner_e) and "#prompt-textarea" in str(inner_e):
                                print(f"!!! BŁĄD: Pole do wpisywania tekstu nadal niewidoczne nawet po próbie rozwiązania CAPTCHA w trybie GUI. {inner_e}")
                            else:
                                print(f"!!! BŁĄD: Wystąpił inny problem podczas obsługi CAPTCHA w trybie GUI: {inner_e}")
                            raise # Jeśli nadal nie działa, rzuć wyjątek

                else:
                    # To nie był błąd timeoutu elementu, tylko inny rodzaj Exception
                    print(f"!!! BŁĄD: Wystąpił nieoczekiwany błąd wewnątrz sesji SeleniumBase: {e}")
                    raise # Rzuć oryginalny wyjątek

    except Exception as e:
        print(f"!!! KRYTYCZNY BŁĄD: Wystąpił nieoczekiwany problem na najwyższym poziomie: {e}")
        raise # Rzuć wyjątek, jeśli cała operacja zawiodła

# Przykładowe użycie:
response = chatgpt("Po prostu powiedz ala ma kota.")
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