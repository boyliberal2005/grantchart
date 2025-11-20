# Ứng dụng Kế hoạch Tổng quan - Gantt Timeline

Ứng dụng Streamlit để tạo biểu đồ Gantt Timeline chuyên nghiệp từ dữ liệu Excel.

## Tính năng

- ✅ Import dữ liệu từ file Excel
- ✅ Tự động phân loại tasks theo category (SAP, NonSAP, CM, IFRS & Accounting Data Review)
- ✅ Hiển thị timeline với 5 giai đoạn: Vision, Validate, Construct, Deploy, Evolve
- ✅ Biểu đồ Gantt tương tác với màu sắc chuyên nghiệp
- ✅ Milestone "Go-live"
- ✅ Download biểu đồ dưới dạng PNG
- ✅ Hiển thị bảng dữ liệu chi tiết
- ✅ Thống kê tổng quan dự án

## Cài đặt

### 1. Cài đặt Python packages

```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

```bash
streamlit run gantt_app_final.py
```

Ứng dụng sẽ mở tự động trên trình duyệt tại địa chỉ: http://localhost:8501

## Cách sử dụng

### 1. Chuẩn bị file Excel

File Excel cần có các cột sau (theo thứ tự):

| Cột | Tên | Mô tả | Ví dụ |
|-----|-----|-------|-------|
| A | WBS | Mã công việc | 1, 1.1, 2, 2.1 |
| B | Task | Tên công việc | Khảo sát hệ thống |
| C | Lead | Người phụ trách | Geso & khách hàng |
| D | Start | Ngày bắt đầu | 2025-11-18 |
| E | End | Ngày kết thúc | 2025-11-24 |
| F | Cal Days | Số ngày lịch | 7 |
| G | %Done | Phần trăm hoàn thành | 0 |
| H | Work Days | Số ngày làm việc | 5 |
| I | Days Done | Số ngày đã hoàn thành | 0 |

**Lưu ý**: 
- Dòng đầu tiên chứa từ "WBS" sẽ được tự động nhận diện là header
- Các dòng trước header có thể chứa thông tin dự án (tên, ngày, người phụ trách...)

### 2. Upload file và xem kết quả

1. Mở ứng dụng
2. Click nút "Browse files" để upload file Excel
3. Biểu đồ sẽ được tạo tự động
4. Có thể hover chuột lên các task bar để xem chi tiết
5. Click nút "Download biểu đồ (PNG)" để tải về

### 3. Phân loại tự động

Ứng dụng tự động phân loại các tasks dựa vào:

- **SAP**: Tasks có từ khóa "sap", "erp", "steercom"
- **NonSAP**: Tasks có từ khóa "qr code", "sales portal", "travel", "expense"
- **CM**: Tasks có từ khóa "ux", "ui", "design", "khảo sát", "giới thiệu"
- **IFRS & Accounting Data Review**: Tasks có từ khóa "ifrs", "accounting", "dln", "số dư", "bctc"

## Màu sắc

### Phases (Giai đoạn)
- 🔵 **Vision**: #B8D8F0 (Xanh nhạt)
- 🔵 **Validate**: #4FA3D1 (Xanh vừa)
- 🟣 **Construct**: #7B3F9B (Tím)
- 🟣 **Deploy**: #5B1F70 (Tím đậm)
- 🟠 **Evolve**: #FF9933 (Cam)

### Categories (Phân loại)
- 🔵 **SAP**: #1e5a9e (Xanh dương)
- 🟤 **NonSAP**: #8B4513 (Nâu)
- 🟢 **CM**: #2ca02c (Xanh lá)
- 🔵 **IFRS & Accounting Data Review**: #17becf (Xanh cyan)

## Ví dụ dữ liệu

Xem file `1.xlsx` đã được cung cấp để tham khảo format dữ liệu.

## Yêu cầu hệ thống

- Python 3.8 trở lên
- Trình duyệt web hiện đại (Chrome, Firefox, Edge, Safari)

## Troubleshooting

### Lỗi khi import file Excel
- Đảm bảo file Excel có định dạng `.xlsx`
- Kiểm tra có cột "WBS" trong file
- Đảm bảo cột Start và End có định dạng ngày tháng

### Biểu đồ không hiển thị
- Kiểm tra dữ liệu có ngày Start và End hợp lệ
- Đảm bảo có ít nhất 1 task có đầy đủ thông tin

### Không download được biểu đồ
- Cài đặt package `kaleido`: `pip install kaleido`
- Khởi động lại ứng dụng

## Tác giả

Phát triển bởi Claude AI
Phiên bản: 1.0
Ngày: 2025-11-20

## License

MIT License
