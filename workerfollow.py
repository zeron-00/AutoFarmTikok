import subprocess, re
import platform
import requests, json, random, hashlib
from urllib.parse import urlencode
import os
import random
import time, uuid, binascii

def getId():
    return hashlib.md5(bytes(str(subprocess.check_output("wmic csproduct get uuid")).split("\\n")[1].split("  \\r")[0], 'utf-8-sig')).hexdigest()
class Gorgon:
    def __init__(self, params: str, data: str, cookies: str) -> None:

        self.params = params
        self.data = data
        self.cookies = cookies

    def hash(self, data: str) -> str:
        _hash = str(hashlib.md5(data.encode()).hexdigest())

        return _hash

    def get_base_string(self) -> str:
        base_str = self.hash(self.params)
        base_str = (
            base_str + self.hash(self.data) if self.data else base_str + str("0" * 32)
        )
        base_str = (
            base_str + self.hash(self.cookies)
            if self.cookies
            else base_str + str("0" * 32)
        )

        return base_str

    def get_value(self) -> json:
        base_str = self.get_base_string()

        return self.encrypt(base_str)

    def encrypt(self, data: str) -> json:
        unix = int(time.time())
        len = 0x14
        key = [
            0xDF,
            0x77,
            0xB9,
            0x40,
            0xB9,
            0x9B,
            0x84,
            0x83,
            0xD1,
            0xB9,
            0xCB,
            0xD1,
            0xF7,
            0xC2,
            0xB9,
            0x85,
            0xC3,
            0xD0,
            0xFB,
            0xC3,
        ]

        param_list = []

        for i in range(0, 12, 4):
            temp = data[8 * i : 8 * (i + 1)]
            for j in range(4):
                H = int(temp[j * 2 : (j + 1) * 2], 16)
                param_list.append(H)

        param_list.extend([0x0, 0x6, 0xB, 0x1C])

        H = int(hex(unix), 16)

        param_list.append((H & 0xFF000000) >> 24)
        param_list.append((H & 0x00FF0000) >> 16)
        param_list.append((H & 0x0000FF00) >> 8)
        param_list.append((H & 0x000000FF) >> 0)

        eor_result_list = []

        for A, B in zip(param_list, key):
            eor_result_list.append(A ^ B)

        for i in range(len):

            C = self.reverse(eor_result_list[i])
            D = eor_result_list[(i + 1) % len]
            E = C ^ D

            F = self.rbit_algorithm(E)
            H = ((F ^ 0xFFFFFFFF) ^ len) & 0xFF
            eor_result_list[i] = H

        result = ""
        for param in eor_result_list:
            result += self.hex_string(param)

        return {"X-Gorgon": ("0404b0d30000" + result), "X-Khronos": str(unix)}

    def rbit_algorithm(self, num):
        result = ""
        tmp_string = bin(num)[2:]

        while len(tmp_string) < 8:
            tmp_string = "0" + tmp_string

        for i in range(0, 8):
            result = result + tmp_string[7 - i]

        return int(result, 2)

    def hex_string(self, num):
        tmp_string = hex(num)[2:]

        if len(tmp_string) < 2:
            tmp_string = "0" + tmp_string

        return tmp_string

    def reverse(self, num):
        tmp_string = self.hex_string(num)

        return int(tmp_string[1:] + tmp_string[:1], 16)

class TikTok_Api(object):
    def __init__(self, cookie: str) -> None:
        self.cookie = cookie

    def __basic_info(self, user: str) -> dict:
        for x in range(30):
            try:
                headers = {
                        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                        'sec-ch-ua-mobile': '?1',
                        'save-data': 'on',
                        'upgrade-insecure-s': '1',
                        'user-agent': 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Mobile Safari/537.36',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'sec-fetch-site': 'none',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-user': '?1',
                        'sec-fetch-dest': 'document',
                        'Cookie': self.cookie,
                        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                    }
                a = requests.get("https://www.tiktok.com/api/user/detail/?aid=1988&app_language=vi-VN&app_name=tiktok_web&battery_info=0.36&browser_language=vi-VN&browser_name=Mozilla&browser_online=true&browser_platform=Linux%20armv8l&browser_version=5.0%20%28Linux%3B%20Android%2011%3B%20SM-A217F%20Build%2FRP1A.200720.012%3B%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Version%2F4.0%20Chrome%2F103.0.5060.71%20Mobile%20Safari%2F537.36&channel=tiktok_web&cookie_enabled=true&device_id=7122693504992184845&device_platform=web_mobile&focus_state=true&from_page=user&history_len=4&is_fullscreen=false&is_page_visible=true&language=vi-VN&os=android&priority_region=VN&referer=&region=VN&screen_height=854&screen_width=385&secUid=&tz_name=Asia%2FSaigon&uniqueId={}".format(user), headers=headers).json()
                data = a['userInfo']['user']
                return {'secUid': data['secUid'], 'idUser': data['id']}
            except:
                pass     
    def __openudid(self) -> str:
        return binascii.hexlify(os.urandom(8)).decode()

    def __guuid(self) -> str:
        return str(uuid.uuid4())

    def __configDevice(self):
        return random.choice(["SM-G9900", "SM-A136U1", "SM-G965N", "SM-M225FV", "SM-E426B", "SM-M526BR", "SM-M326B", "SM-A528B","SM-F711B", "SM-F926B", "SM-A037G", "SM-A225F", "SM-M325FV", "SM-A226B", "SM-M426B","SM-A525F"])

    def __Params(self, user: str) -> None:
        try:
            info = self.__basic_info(user)
            secId = info['secUid']
            self.cookie = self.cookie
            self.user = user
            idFollow = info['idUser']
            self.url = "https://api.tiktokv.com/aweme/v1/commit/follow/user/?"
            self.params = urlencode ({
                "user_id": idFollow,
                "sec_user_id": secId,
                "type": "1",
                "from": "0",
                "from_label": "39",
                "carrier_region": "VN",
                "manifest_version_code": "-1",
                "ac": "wifi",
                "os_version": "9",
                "channel": "googleplay",
                "version_code": "10008",
                "device_type": self.__configDevice(),
                "language": "vi",
                "resolution": "540*780",
                "openudid": self.__openudid(),
                "update_version_code": "-1",
                "app_name": "TikTok Now",
                "cdid": self.__guuid(),
                "version_name": "1.0.8",
                "os_api": "28",
                "device_brand": "samsung",
                "ssmix": "a",
                "device_platform": "android",
                "dpi": "160",
                "aid": "385522"
            })
            sig = Gorgon(self.params, None, self.cookie).get_value()
            self.headers = {
                "host": "api.tiktokv.com",
                "cookie": self.cookie,
                "x-gorgon": sig["X-Gorgon"],
                "x-khronos": sig["X-Khronos"]
            }
            return self.params, self.headers
        except:
            pass
    
    def Get_cauhinh(self) -> bool:
        try:
            headers = {
                'authority': 'www.tiktok.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'max-age=0',
                'cookie': self.cookie,
                'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            }

            response = requests.get('https://www.tiktok.com/', headers=headers).text
            tach = response.split('"uid":"')[1].split('","nickName":"')
            uid = tach[0]
            nick_name = tach[1].split('","signature"')[0]
            return {'uid': uid, 'nickName': nick_name}
        except:
            return None 
        
    def followUser(self, user: str) -> bool:
        try:
            params, headers = self.__Params(user)
            postFollow = requests.get(self.url, params=params, headers=headers).json()
            if postFollow['follow_status'] == 1:
                return True
            else:
                return False
        except:
            return False
cookie ='[cookie_tiktok]'
tiktok = TikTok_Api(cookie)
print(tiktok.followUser('[username_follow]'))
