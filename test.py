import asyncio
import random

import requests

semaphore = asyncio.Semaphore(20)

async def with_semaphore(coro):
    async with semaphore:
        return await coro

def login():
    api_url = "https://script.google.com/macros/s/AKfycbz8xtZlGyRDXoZv_tR2MtBG8pUmf_kBMMlnFsiyvavcWCOIfQ0qRNcKgJ33qE-kG_vahg/exec"
    params = {
        "type": "dsdkhp",
        "mssv": "3123330021"
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        print("Kết quả:")
        for row in data:
            print(row)
        return data
    else:
        print("Lỗi:", response.status_code)

async def xulydkmhsinhvien(self, session=None):
    print(f"🟡 Bắt đầu xử lý: {self['id']}")
    await asyncio.sleep(random.uniform(1, 3))  # Giả lập thời gian xử lý khác nhau
    print(f"✅ Xong: {self}")

async def main():
    # Tạo danh sách 20 học phần giả định
    hoc_phans = login()

    # Tạo các task, mỗi task xử lý một học phần, có giới hạn bằng semaphore
    tasks = [
        with_semaphore(xulydkmhsinhvien(hp))
        for hp in hoc_phans
    ]

    # Chạy tất cả các task song song, nhưng chỉ tối đa 10 cùng lúc
    await asyncio.gather(*tasks)

asyncio.run(main())
