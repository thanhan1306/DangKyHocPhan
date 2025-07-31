import aiohttp
from Lenh import Lenh

class SinhVien:
    def __init__(self, mssv, password, auth=None):
        self.username = mssv
        self.password = password
        self.name = None
        self.auth = auth
        self.ds_dk = []           # danh sách Lenh
        self.ds_nhom_to = None
        self.ds_mon_hoc = None

    async def login(self, session):
        url = "https://thongtindaotao.sgu.edu.vn/api/auth/login"
        payload = f"username={self.username}&password={self.password}&grant_type=password"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "text/plain",
            "Idpc": "0",
        }
        try:
            async with session.post(url, headers=headers, data=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.auth = f"{data['token_type']} {data['access_token']}"
                    self.name = data["name"]
                    #print(f"{self.username} {self.name} đã login.")
                else:
                    print(f"{self.username} login lỗi: {resp.status}")
        except Exception as e:
            print(f"{self.username} login exception: {e}")

    async def get_ds_dangky(self, session):
        """Lấy danh sách đăng ký từ API Google Sheets và nạp thành Lenh vào self.ds_dk"""
        api_url = "https://script.google.com/macros/s/AKfycbz8xtZlGyRDXoZv_tR2MtBG8pUmf_kBMMlnFsiyvavcWCOIfQ0qRNcKgJ33qE-kG_vahg/exec"
        params = {
            "type": "dsdkhp",
            "mssv": self.username,
        }
        try:
            async with session.get(api_url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # tạo danh sách Lenh, truyền luôn auth để tự động gửi sau
                    self.ds_dk = [Lenh(item["id"], item["id_to_hoc"], auth=self.auth, mssv=self.username)
                                  for item in data]
                    print(f"{self.username}: nạp {len(self.ds_dk)} lệnh đăng ký.")
                else:
                    print(f"{self.username}: lỗi get_ds_dangky {resp.status}")
        except Exception as e:
            print(f"{self.username}: exception get_ds_dangky {e}")
