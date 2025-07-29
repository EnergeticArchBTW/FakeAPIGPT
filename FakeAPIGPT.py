from contextlib import suppress
from seleniumbase import SB
import os

# Set the position to which you want to move the window off-screen
# These values should be large enough for the window to be outside the visible area.
# You can adjust them depending on your screen resolution.
out_of_view_x = 0
out_of_view_y = 0

error_messege = "There is some error, please wait few minutes and try again."

url = "https://chatgpt.com/"

#use this const for second argument in function chatgpt() to get acces to the search web
WEB_SEARCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default.png")

#preprocessing prompt
def preprocess_prompt(prompt):
    return "(pre prompt:↩=newLine)" + prompt.replace('\n','↩')

#concept with function that always use headless=False (with open browser window) and you can upload photos
def chatgpt(prompt, photo=None, captcha=False, max_tries=3):
    # we are checking max tries and the attached file exists
    if max_tries <= 0 or (photo!=None and not os.path.isfile(photo)):
        return error_messege
    
    #convert text with many lines to some simpler processable object
    prompt = preprocess_prompt(prompt)

    with SB(uc=True) as sb:
        try:
            #moving the window away from screen
            sb.set_window_position(out_of_view_x, out_of_view_y)

            #go to the chatgpt page
            sb.activate_cdp_mode(url)
            sb.sleep(1)

            #when you must solve a captcha
            if captcha:
                sb.uc_gui_click_captcha()
                sb.sleep(1)

                sb.uc_gui_handle_captcha()
                sb.sleep(1)
        
            sb.click_if_visible('button[aria-label="Close dialog"]')

            #writing prompt
            sb.press_keys("#prompt-textarea", prompt)

            #photo
            if photo != None:
                # 1. Import the appropriate libraries and ensure the page is fully loaded
                from pynput.keyboard import Key, Controller
                sb.wait_for_ready_state_complete()

                # 2. Define a new, precise CSS selector for the "Attach" button
                # Hierarchy: div with data-testid="composer-action-file-upload" → direct div → span → direct div → button
                attach_button_selector = 'div[data-testid="composer-action-file-upload"] > div > span > div > button'

                # 3. Wait until the "Attach" button is visible and ready for interaction, then click it
                sb.wait_for_element(attach_button_selector, timeout=15)
                sb.click(attach_button_selector)

                # 4. Click the visible “Attach photo” option in the menu
                file_attach_option_selector = """div[role='menuitem']:last-of-type"""

                keyboard = Controller()

                #To prevent overlapping input events when using pynput, the typing logic should be placed inside a critical section protected by a lock.
                import threading
                lock = threading.Lock()
                
                with lock:
                    # Hold key esc to quit full-screen mode
                    if photo != WEB_SEARCH:
                        keyboard.press(Key.esc)
                        sb.sleep(3)
                        keyboard.release(Key.esc)

                    sb.wait_for_element(file_attach_option_selector, timeout=10)
                    sb.click(file_attach_option_selector)

                    # Add a short pause to give the application time to close the menu
                    # And wait for the system file picker window to open before starting to type the file path
                    sb.sleep(1)

                    # 5. Next, handle the file selection window
                    keyboard.type(photo)
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)

                # 6. wait for file to upload
                sb.sleep(3)
                sb.wait_for_element_clickable("#composer-submit-button")

            sb.wait_for_element('button[data-testid="send-button"]')
            sb.click('button[data-testid="send-button"]')

            sb.sleep(3)
            with suppress(Exception):
                # The "Stop" button disappears when ChatGPT is done typing a response
                sb.wait_for_element_not_visible(
                    'button[data-testid="stop-button"]', timeout=120
                )
            chat = sb.find_element('[data-message-author-role="assistant"] .markdown')
            #print(chat.text)
            try:
                soup = sb.get_beautiful_soup(chat.get_html()).get_text("\n").strip()
            except AttributeError as e:
                soup = chat.text
            
            #remove spaces between lines
            for i in range(4):
                soup = soup.replace("\n\n\n", "\n\n")
            return soup
        except Exception as e:
            # Optionally: Take a screenshot in case of an error to facilitate debugging
            sb.save_screenshot_to_logs()
            # Optionally: Print the page source to inspect the current DOM if the issue recurs
            # print(sb.get_page_source())
            #when something goes wrong do it once again but with captcha solver
            return chatgpt(prompt, photo, True, max_tries-1)

#examples:
# print(chatgpt("""Copy 1:1 what’s at the bottom:
#                      /\\
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

# print(chatgpt("""
# what this drawing shows?
# """, "C:\\Users\\User\\Downloads\\photo.jpg"))

print(chatgpt("""
What are the news today from the world?
""", WEB_SEARCH))

# function that usues headless (without browser window) at deafult but at second try turns off headless mode
def chatgpt_headless(prompt, headless_mode=True, max_tries=3):
    #Automates interaction with ChatGPT, including handling headless mode switching
    #and attempting to force focus on the browser window in GUI mode.

    if max_tries <= 0:
        return error_messege
    
    #convert text with many lines to some simpler processable object
    prompt = preprocess_prompt(prompt)

    try:
        with SB(uc=True, headless2=headless_mode, do_not_track=True, maximize=True) as sb:
            if not headless_mode:
                # Using set_window_position() to move window
                sb.set_window_position(out_of_view_x, out_of_view_y)
            
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
# print(chatgpt_headless("Hey, how's life? Tell your story and quote exactly what I just said."))

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