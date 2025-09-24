# Hướng dẫn cấu hình Firebase cho AICoffeePortal

## 1. Tải Service Account Key

1. Truy cập [Firebase Console](https://console.firebase.google.com/)
2. Chọn project "kmou-aicofee"
3. Vào Project Settings → Service accounts
4. Click "Generate new private key"
5. Lưu file JSON vào thư mục backend (ví dụ: `firebase-admin-key.json`)

## 2. Cập nhật file .env

```bash
SECRET_KEY=your-secret-key-here
FIREBASE_CONFIG_PATH=./firebase-admin-key.json
USE_MOCK_FIREBASE=False
BACKEND_CORS_ORIGINS=["http://localhost:5174","http://sarm.n2nai.io:5174","https://sarm.n2nai.io:5174"]
```

## 3. Cập nhật Firebase Service

File `app/services/firebase_service.py` cần cập nhật storage bucket:

```python
firebase_admin.initialize_app(cred, {
    'storageBucket': 'kmou-aicofee.firebasestorage.app'
})
```

## 4. Tạo collections trong Firestore

Vào Firestore Database và tạo các collections:
- `users`
- `farmers`
- `farms`
- `attendance`
- `coffee_beans_analyses`
- `coffee_leaves_analyses`

## 5. Restart server

```bash
# Stop current server
# Then restart
cd /home/data2/AIFace/AICoffeePortal/backend
source venv/bin/activate
uvicorn app.main:app --port 5200 --host 0.0.0.0 --reload
```

## Lưu ý

Hiện tại backend đang chạy ở chế độ mock (USE_MOCK_FIREBASE=True) nên dữ liệu chỉ lưu trong memory và sẽ mất khi restart server. Sau khi cấu hình Firebase thật, dữ liệu sẽ được lưu vào Firestore.