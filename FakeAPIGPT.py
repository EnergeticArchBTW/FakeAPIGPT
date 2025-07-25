from contextlib import suppress
from seleniumbase import SB

error_messege = "there is some error, please wait few minutes and try again"

#concept with function that always use headless=False (with open browser window)
def chatgpt(prompt, captcha=False, max_tries=3):
    # Set the position to which you want to move the window off-screen
    # These values should be large enough for the window to be outside the visible area.
    # You can adjust them depending on your screen resolution.
    out_of_view_x = -3000
    out_of_view_y = -3000

    if max_tries <= 0:
        return error_messege
    
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

#example:
# print(chatgpt("""przepisz 1:1 co jest na dole:
#                                    /\\
#                     /  \\___
#                    /   /   \\___
#                 ___/   |      \\_
#               /        |        \\
#              |  ~~~~   |   ~~~~  |
#              |         |         |
#              |  CLOUDS |  MOUNTS |
#               \\_______|________/
#                     /_|_\\
#                    /__|__\\
#                  //     \\\\
#                 ||  🌄   ||
#                 ||_______||
#               /____________\\
#              |   EARTHSCAPE |
#               \\____________/\t
# """))

# function that usues headless (without browser window) at deafult but at second try turns off headless mode
def chatgpt_headless(prompt, headless_mode=True, max_tries=3):
    #Automates interaction with ChatGPT, including handling headless mode switching
    #and attempting to force focus on the browser window in GUI mode.
    
    # Set the position to which you want to move the window off-screen
    # These values should be large enough for the window to be outside the visible area.
    # You can adjust them depending on your screen resolution.
    out_of_view_x = -3000
    out_of_view_y = -3000

    if max_tries <= 0:
        return error_messege
    
    #convert text with many lines to some simpler processable object
    prompt = prompt.replace('\n','↩')

    try:
        with SB(uc=True, headless2=headless_mode, do_not_track=True, maximize=True) as sb:
            if not headless_mode:
                # Using set_window_position() to move window
                sb.set_window_position(out_of_view_x, out_of_view_y)
            
            url = "https://chatgpt.com/"
            sb.activate_cdp_mode(url)
            sb.sleep(1)

            # If we are in GUI mode try use captcha solver and focus methods
            if not headless_mode:
                sb.uc_gui_click_captcha()
                sb.sleep(1)
                sb.uc_gui_handle_captcha()
                sb.sleep(1)

                # Method 1: Window activation using JavaScript (more reliable)
                # Opens a new blank window and immediately closes it, which may restore focus
                sb.execute_script("window.open(''); window.close();")
                # Switching back to the original window (if there was more than one)
                sb.switch_to_default_window() 
                sb.sleep(0.5)

                # Method 2: Attempt to activate the current window
                sb.execute_script("window.focus();")
                sb.sleep(0.5)

            try:
                sb.wait_for_element("#prompt-textarea", timeout=3)
                
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
                #I'm adjusting the spacing between lines
                for i in range(4):
                    soup = soup.replace("\n\n\n", "\n\n")
                return soup

            except Exception as e:
                return chatgpt_headless(prompt, False, max_tries-1)

    except Exception as e:
        return error_messege

#example:
# print(chatgpt_headless("Siema, jak tam życie? Opowiedz swoją historię."))

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