This is a script that frees you from relying on paid OpenAI API access.
It’s completely free to use — and flexible enough to be integrated into
various applications. It has two versions - one more stable it must
open real browser and bot types prompt to chatgpt and and answer is
imported as return from function or less stable (browser at a first
attempt don't have to even open any browser but it opens in the
background.

If you want to bot to use internet browsing do this (only works in chatgpt() function):
```
chatgpt("prompt", WEB_SEARCH)
```

if you want to upload some .gif, .jpg, .jpeg, .png or .webp image:
```
chatgpt("prompt", "DIRECT\\SOURCE\\To\\THE\\FILE")
```

if you upload photo in automate chatgpt have access to the search engine.
(you need to install pynput library:
```
pip install pynput --user
```
)

---

-> first of all: download visual studio code

-> go to some workspace folder
```
git clone https://github.com/EnergeticArchBTW/FakeAPIGPT.git
```
-> install chrome browser

-> download at least python 3.8

-> download extension for vsc called python (when you want to code something additionally)

-> type ctrl + shift + P and type:
```
Python: Create Environment
```
-> choose Venv and some installed python version at least 3.8

-> in vsc in windows type ctrl + ~ or on mac cmd + ~

-> type
```
git clone https://github.com/seleniumbase/SeleniumBase.git
cd SeleniumBase/
pip install . --user
cd ..
```
-> now you can import this package to your code like any other package
outside of that folder when the your python file is a neighbourhood
of the FakeAPIGPT folder module
```
from FakeAPIGPT import chatgpt, chatgpt_headless
```
-> or test my examples by uncomment them.

If there is any problems with script, try this:
```
pip uninstall setuptools
pip install setuptools==65.5.0
pip install --upgrade setuptools
```
then try to run script again