from contextlib import suppress
from seleniumbase import SB

#from selenium.webdriver.common.by import By

#concept with function that always use headless=False
def chatgpt(prompt, captcha=False, max_tries=3):
    # Set the position to which you want to move the window off-screen
    # These values should be large enough for the window to be outside the visible area.
    # You can adjust them depending on your screen resolution.
    out_of_view_x = -3000
    out_of_view_y = -3000

    if max_tries <= 0:
        return "there is some error, please wait few minutes and try again"
    
    #convert text with many lines to some simpler processable object
    prompt = prompt.replace('\n','↩')

    with SB(uc=True) as sb:
        try:
            #moving the window away from screen
            sb.set_window_position(out_of_view_x, out_of_view_y)

            #go to the chatgpt page
            url = "https://chatgpt.com/"
            sb.activate_cdp_mode(url)
            sb.sleep(1)

            #when you must solve a captcha
            if captcha:
                sb.uc_gui_click_captcha()
                sb.sleep(1)

                sb.uc_gui_handle_captcha()
                sb.sleep(1)
        
            sb.click_if_visible('button[aria-label="Close dialog"]')

            sb.press_keys("#prompt-textarea", prompt)
            sb.click('button[data-testid="send-button"]')

            sb.sleep(3)
            with suppress(Exception):
                # The "Stop" button disappears when ChatGPT is done typing a response
                sb.wait_for_element_not_visible(
                    'button[data-testid="stop-button"]', timeout=200
                )
            chat = sb.find_element('[data-message-author-role="assistant"] .markdown')
            soup = sb.get_beautiful_soup(chat.get_html()).get_text("\n").strip()
            #remove spaces between lines
            for i in range(4):
                soup = soup.replace("\n\n\n", "\n\n")
            return soup
        except Exception as e:
            #when something goes wrong do it once again but with captcha solver
            return chatgpt(prompt, True, max_tries-1)

print(chatgpt("""przepisz 1:1 co jest na dole:
                                   /\\
                    /  \\___
                   /   /   \\___
                ___/   |      \\_
              /        |        \\
             |  ~~~~   |   ~~~~  |
             |         |         |
             |  CLOUDS |  MOUNTS |
              \\_______|________/
                    /_|_\\
                   /__|__\\
                 //     \\\\
                ||  🌄   ||
                ||_______||
              /____________\\
             |   EARTHSCAPE |
              \\____________/\t
"""))


def chatgpt_headless(prompt, headless_mode=True, max_tries=3):
    #Automatyzuje interakcję z ChatGPT, z obsługą przełączania trybu headless
    #i próbą wymuszenia fokusu na oknie przeglądarki w trybie GUI.
    
    # Ustal pozycję, na którą chcesz przesunąć okno poza widokiem
    # Te wartości powinny być wystarczająco duże, aby okno było poza ekranem.
    # Możesz je dostosować w zależności od rozdzielczości Twojego ekranu.
    out_of_view_x = -3000
    out_of_view_y = -3000

    if max_tries <= 0:
        return "there is some error, please wait few minutes and try again"
    
    #convert text with many lines to some simpler processable object
    prompt = prompt.replace('\n','↩')

    try:
        with SB(uc=True, headless2=headless_mode, test=True, do_not_track=True, maximize=True) as sb:
            if not headless_mode:
                # Używamy set_window_position() do przesunięcia okna
                sb.set_window_position(out_of_view_x, out_of_view_y)
                print(f"Ustawiłem pozycję okna przeglądarki na ({out_of_view_x}, {out_of_view_y}) poza widokiem.")
            
            url = "https://chatgpt.com/"
            sb.activate_cdp_mode(url)
            sb.sleep(1) # Krótka pauza na załadowanie początkowe

            # Jeśli jesteśmy w trybie GUI, spróbuj wymusić fokus na starcie
            if not headless_mode:
                sb.uc_gui_click_captcha()
                sb.sleep(1)
                sb.uc_gui_handle_captcha()
                sb.sleep(1)

                print("Wymuszam fokus na oknie przeglądarki...")
                # Metoda 1: Aktywacja okna za pomocą JavaScript (bardziej niezawodna)
                # Otwiera nowe puste okno i natychmiast je zamyka, co może przywrócić fokus
                sb.execute_script("window.open(''); window.close();")
                # Przejście z powrotem do oryginalnego okna (jeśli było ich więcej)
                sb.switch_to_default_window() 
                sb.sleep(0.5) # Krótka pauza

                # Metoda 2: Proba aktywacji obecnego okna
                sb.execute_script("window.focus();")
                sb.sleep(0.5) # Krótka pauza

            try:
                #debugowanie
                html = sb.get_page_source()
                with open("debug_headless.html", "w", encoding="utf-8") as f:
                    f.write(html)
                
                sb.wait_for_element("#prompt-textarea", timeout=3)
                    
                print("Pole do wpisywania tekstu (#prompt-textarea) jest widoczne. Kontynuuję.")
                sb.click_if_visible('button[aria-label="Close dialog"]')
                sb.press_keys("#prompt-textarea", prompt)
                sb.click('button[data-testid="send-button"]')

                sb.sleep(3)
                with suppress(Exception):
                    sb.wait_for_element_not_visible(
                        'button[data-testid="stop-button"]', timeout=200
                    )
                    
                chat = sb.find_element('[data-message-author-role="assistant"] .markdown')
                soup = sb.get_beautiful_soup(chat.get_html()).get_text("\n").strip()
                #poprawiam odległości między linijkami
                for i in range(4):
                    soup = soup.replace("\n\n\n", "\n\n")
                return soup

            except Exception as e:
                if ("was not found after" in str(e) and "#prompt-textarea" in str(e)) or "object has no attribute" in str(e):
                    print(f">>> Timeout: {e}")
                    
                    if headless_mode:
                        print("Wykryto timeout w trybie headless. Próbuję ponownie w trybie GUI...")
                        return chatgpt_headless(prompt, False, max_tries-1)
                    else:
                        print("Wykryto timeout w trybie GUI. Prawdopodobnie CAPTCHA lub inna blokada wymaga interwencji.")
                        print("Próbuję rozwiązać CAPTCHA za pomocą sb.uc_gui_click_captcha() i sb.uc_gui_handle_captcha()...")
                        return chatgpt_headless(prompt, False, max_tries-1)
                else:
                    print(f"!!! BŁĄD: Wystąpił nieoczekiwany błąd wewnątrz sesji SeleniumBase: {e}")
                    raise

    except Exception as e:
        print(f"!!! KRYTYCZNY BŁĄD: Wystąpił nieoczekiwany problem na najwyższym poziomie: {e}")
        raise
print(chatgpt_headless("Siema, jak tam życie? Opowiedz swoją historię."))

"""
def chatgpt(prompt, headless_mode=True):
    #Automatyzuje interakcję z ChatGPT, z obsługą przełączania trybu headless
    #w przypadku, gdy pole do wprowadzania tekstu nie pojawi się w oczekiwanym czasie.

    # Zewnętrzny blok try-except dla obsługi błędów na najwyższym poziomie
    try:
        with SB(uc=True, headless=headless_mode, test=True) as sb:
            url = "https://chatgpt.com/"
            sb.activate_cdp_mode(url)
            sb.sleep(1) # Krótka pauza na załadowanie początkowe

            try:
                # Czekamy na pole tekstowe z timeoutem
                # W trybie CDP, jeśli element nie zostanie znaleziony, rzuci generyczny Exception
                sb.wait_for_element("#prompt-textarea", timeout=2)
                    
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
                if ("was not found after" in str(e) and "#prompt-textarea" in str(e)) or "object has no attribute" in str(e):
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
response = chatgpt("Ta wiadomość jest zaszyfrowana, spróbuj ją odszyfrować i powiedz jak to zrobiłeś (podpowiedź, to nie jest staropolski): Pnaó, pnaój jśę uęiwńł!")
print(response)
"""
"""
import win32gui
import time

def hide_tab():
    #hiding browser that worked but It couldn't copy the text after use of this
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
#original function that worked
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