import asyncio
import random
import time

import aiohttp

def my_btoa(s):
    bytes_data = [ord(c) for c in s]
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    base64_result = ''
    for i in range(0, len(bytes_data), 3):
        byte1 = bytes_data[i]
        byte2 = bytes_data[i + 1] if i + 1 < len(bytes_data) else 0
        byte3 = bytes_data[i + 2] if i + 2 < len(bytes_data) else 0
        base64_result += chars[byte1 >> 2]
        base64_result += chars[((byte1 & 3) << 4) | (byte2 >> 4)]
        base64_result += chars[((byte2 & 15) << 2) | (byte3 >> 6)]
        base64_result += chars[byte3 & 63]
    if len(bytes_data) % 3 == 1:
        base64_result = base64_result[:-2] + '=='
    elif len(bytes_data) % 3 == 2:
        base64_result = base64_result[:-1] + '='
    return base64_result

def rnd(num):
    return random.randint(1, num)

def ec(str, key):
    def rk(key):
        P = [4, 165, 110, 3, 44, 202, 186, 28, 118, 177, 32, 94, 219, 6, 199, 27, 101, 191, 66, 115, 234, 120, 10, 236, 104, 108, 74, 247, 68, 198, 62, 203]
        Q = key % 3 + 1
        return [P[(key + T * Q) % len(P)] for T in range(10)]
    Q = rk(key)[::-1]
    R = [ord(c) for c in str]
    T = []
    while len(T) < len(R):
        T.extend(Q)
    return [U ^ T[V] for V, U in enumerate(R)]

def gc(P, k):
    if len(P) > 22:
        P = P[:22]
    P = P.upper()
    offset = k
    current_time_millis = int(time.time() * 1000)
    Q = str(rnd(89) + 10) + str(current_time_millis - offset) + str(rnd(89) + 10) + P
    R = rnd(31)
    T = [R + 32] + ec(Q, R)
    T = ''.join([chr(U) for U in T])
    return my_btoa(T.encode('utf-8').decode("utf-8"))

class Lenh:
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScPSvuYFFJkqthsQN8nGmdi-hQOQU_2qQ98EkQPGb4TuG7QfA/formResponse"

    def __init__(self, id, id_to_hoc, auth=None, mssv = None):
        self.id = id
        self.id_to_hoc = id_to_hoc
        self.mssv = mssv
        self.auth = auth
        self.status = None
        self.result = None

    async def send_to_google_form(self, session):
        form_payload = {
            'entry.31662442': str(self.id),
            'entry.955688115': str(self.id_to_hoc),
            'entry.963488546': self.status,
            'entry.645101552': self.result,
        }
        try:
            async with session.post(self.FORM_URL, data=form_payload) as resp:
                if resp.status == 200:
                    print(f"[{self.status}] ID: {self.id} | {self.mssv} | {self.result}")
                else:
                    print(f"Google Form lỗi {resp.status} cho ID {self.id}")
        except Exception as e:
            print(f"Exception gửi Form ID {self.id}: {e}")

    async def xulydkmhsinhvien(self, session, auth):
        if self.status == "Thành công!":
            return

        url = "https://thongtindaotao.sgu.edu.vn/dkmh/api/dkmh/w-xulydkmhsinhvien"
        payload = {"filter": {"id_to_hoc": f"-{self.id_to_hoc}", "is_checked": True, "sv_nganh": 1}}
        headers = {"Accept": "application/json, text/plain, */*",
                   "Authorization": auth,
                   "Content-Type": "application/json",
                   "Postman-Token": "<Postman-Token>",  #
                   "Host": "thongtindaotao.sgu.edu.vn",
                   "Connection": "keep-alive",
                   "Accept-Encoding": "gzip, deflate, br",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                 " (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
                   "ua": f"{gc('dkmh/w-xulydkmhsinhvien', -2132)}",
                   "idpc": "-7648466455965434478",
                   "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                   "sec-ch-ua-mobile": "?0",
                   "sec-ch-ua-platform": "\"Windows\"",
                   "Sec-Fetch-Dest": "empty",
                   "Sec-Fetch-Mode": "cors",
                   "Sec-Fetch-Site": "same-origin",
                   }

        for attempt in range(3):
            try:
                async with session.post(url, headers=headers, json=payload) as resp:
                    data = await resp.json()
                    info = data.get("data", {})
                    # THÀNH CÔNG
                    if resp.status == 200 and info.get("is_thanh_cong"):
                        self.status = "Thành công!"
                        self.result = info["ket_qua_dang_ky"]["ngay_dang_ky"][:19]
                        print(f"Lenh {self.id}: {self.status} at {self.result}")
                        await self.send_to_google_form(session)
                        return

                    # LỖI: Trùng lịch
                    err = info.get("thong_bao_loi", "")
                    if "Trùng TKB MH" in err:
                        self.status = "Trùng lịch!"
                        self.result = err[4:34]
                        await self.send_to_google_form(session)
                    # LỖI: Hết slot
                    if "Vui lòng" in err:
                        self.status = "Hết slot!"
                        self.result = err
                        await self.send_to_google_form(session)
                    # LỖI KHÁC
                    else:
                        self.status = f"Lỗi ({resp.status})"
                        self.result = err or f"HTTP {resp.status}"

                    print(f"Lenh {self.id}:{self.mssv} - {self.status} - {self.result}")
                    #await self.send_to_google_form(session)
                    return

            except Exception as e:
                self.status = "Exception"
                self.result = str(e)
                print(f"Lenh {self.id}:{self.mssv} - {self.status} - {self.result}")

            await asyncio.sleep(2)

        # nếu thử 3 lần vẫn chưa return, in thêm
        print(f"Lenh {self.id}: Không hoàn thành sau 3 attempts, cuối cùng: {self.status} - {self.result}")

    """async def xulydkmhsinhvien(self, session, auth):
        if self.status == "Thành công!":
            return

        url = "https://thongtindaotao.sgu.edu.vn/dkmh/api/dkmh/w-xulydkmhsinhvien"
        payload = {
            "filter": {
                "id_to_hoc": f"-{self.id_to_hoc}",
                "is_checked": True,
                "sv_nganh": 1
            }
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": auth,
            "Content-Type": "application/json",
        }

        for attempt in range(3):
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    data = await response.json()
                    info = data.get("data", {})
                    if response.status == 200 and info.get("is_thanh_cong"):
                        self.status = "Thành công!"
                        self.result = info["ket_qua_dang_ky"]["ngay_dang_ky"][:19]
                        return await self.send_to_google_form(session)
                    # lỗi không thành công:
                    err = info.get("thong_bao_loi", "")
                    if "Trùng TKB MH" in err:
                        self.status = "Trùng lịch!"
                        self.result = err[4:34]
                        return await self.send_to_google_form(session)
                    if "Vui lòng" in err:
                        self.status = "Hết slot!"
                        self.result = err
                        return await self.send_to_google_form(session)
            except Exception as e:
                self.result = f"Exception: {e}"
            await asyncio.sleep(2)"""
