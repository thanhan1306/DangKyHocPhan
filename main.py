import asyncio
import aiohttp
from SinhVien import SinhVien

API_URL = "https://script.google.com/macros/s/AKfycbzXJa5hdpcEUSvZcKIC17vtWFUoCRqn9ljDCnqjIsxWjyOmKOe9uZeTMFoB1ffMM-lCQw/exec"
CYCLES = 5

async def process_student_cycle(sv: SinhVien, session: aiohttp.ClientSession) -> int:
    # Lấy ds_dk và gửi lệnh
    await sv.get_ds_dangky(session)
    if not sv.ds_dk:
        print(f"{sv.username}: không có lệnh, bỏ qua.")
        return 0

    tasks = [l.xulydkmhsinhvien(session, sv.auth) for l in sv.ds_dk]
    await asyncio.gather(*tasks)
    count = len(sv.ds_dk)
    print(f"{sv.username}: hoàn thành {count} lệnh vòng này.")
    return count

async def main():
    # 0) Lấy danh sách sinh viên và login 1 lần
    params = {"type": "sinhvien"}
    async with aiohttp.ClientSession() as session:
        try:
            resp = await session.get(API_URL, params=params)
            resp.raise_for_status()
            data = await resp.json()
        except Exception as e:
            print("Lỗi khi lấy DS sinh viên:", e)
            return

        dssv = [SinhVien(row["mssv"], row.get("password", "")) for row in data]
        print(f"Đã tạo {len(dssv)} SinhVien.")

        # Login một lần cho tất cả
        await asyncio.gather(*(sv.login(session) for sv in dssv))
        print("✅ Đã login xong cho tất cả sinh viên.\n")

        # 1) Vòng lặp chính, hỏi lặp lại sau mỗi 10 cycles
        while True:
            total_all = 0
            for cycle in range(1, CYCLES + 1):
                print(f"\n=== Vòng {cycle}/{CYCLES} ===")
                results = await asyncio.gather(
                    *(process_student_cycle(sv, session) for sv in dssv)
                )
                sent = sum(results)
                total_all += sent
                print(f"Vòng {cycle} đã gửi {sent} lệnh.")

            print(f"\n🔔 Hoàn thành {CYCLES} vòng, tổng cộng đã gửi {total_all} lệnh.")

            # Hỏi người dùng có tiếp tục không
            answer = await asyncio.to_thread(input, "Bạn có muốn chạy thêm 10 vòng nữa không? (y/n): ")
            if answer.strip().lower() not in ("y", "yes"):
                print("Kết thúc chương trình.")
                break
            print("\n⏭️ Bắt đầu chạy lại 10 vòng...\n")

if __name__ == "__main__":
    asyncio.run(main())
