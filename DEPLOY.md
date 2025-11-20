# Hướng dẫn Deploy ứng dụng lên Streamlit Cloud

## Bước 1: Chuẩn bị files

Bạn cần 3 files sau:
1. `app.py` - File ứng dụng chính
2. `requirements.txt` - Danh sách thư viện cần cài đặt
3. `1.xlsx` - File Excel mẫu (tùy chọn)

## Bước 2: Tạo GitHub Repository

1. Đăng nhập vào GitHub (https://github.com)
2. Tạo repository mới:
   - Click nút "New" hoặc "Create repository"
   - Đặt tên: `gantt-timeline-app` (hoặc tên bạn muốn)
   - Chọn "Public"
   - Click "Create repository"

3. Upload files lên repository:
   - Click "Add file" > "Upload files"
   - Kéo thả hoặc chọn 3 files: `app.py`, `requirements.txt`, `1.xlsx`
   - Click "Commit changes"

## Bước 3: Deploy lên Streamlit Cloud

1. Truy cập https://share.streamlit.io

2. Đăng nhập bằng tài khoản GitHub của bạn

3. Click "New app"

4. Điền thông tin:
   - **Repository**: Chọn repository bạn vừa tạo (vd: `gantt-timeline-app`)
   - **Branch**: `main` hoặc `master`
   - **Main file path**: `app.py`

5. Click "Deploy!"

6. Đợi 2-3 phút để Streamlit Cloud cài đặt và deploy ứng dụng

7. Xong! Bạn sẽ có URL dạng: `https://[tên-app].streamlit.app`

## Bước 4: Sử dụng ứng dụng

1. Truy cập URL của ứng dụng
2. Upload file Excel của bạn
3. Xem biểu đồ Gantt timeline được tạo tự động
4. Sử dụng nút camera 📷 trên biểu đồ để download PNG

## Nếu gặp lỗi

### Lỗi import:
```
ModuleNotFoundError: No module named 'xxx'
```
**Giải pháp**: Thêm tên thư viện vào file `requirements.txt`

### Lỗi memory:
```
MemoryError
```
**Giải pháp**: File Excel quá lớn. Hãy giảm số lượng tasks hoặc chia nhỏ file

### Lỗi Plotly:
Nếu biểu đồ không hiển thị, thử refresh lại trang (Ctrl + R)

## Chỉnh sửa ứng dụng

Nếu muốn chỉnh sửa:
1. Sửa file `app.py` trên GitHub
2. Commit changes
3. Streamlit Cloud sẽ tự động redeploy (mất ~2 phút)

## Local Development (Chạy trên máy tính)

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
streamlit run app.py
```

Ứng dụng sẽ mở tại: http://localhost:8501

## Support

Nếu gặp vấn đề, có thể:
1. Check logs trên Streamlit Cloud (click "Manage app" > "Logs")
2. Xem lại format file Excel
3. Đảm bảo có cột "WBS" trong file

---

**Chúc bạn deploy thành công! 🚀**
