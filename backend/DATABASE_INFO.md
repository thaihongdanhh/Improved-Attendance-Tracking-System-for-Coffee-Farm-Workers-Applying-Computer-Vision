# 🗃️ Database Configuration - AI Coffee Portal

## 📊 Primary Firebase Database

**Current Active Database**: `kmou-aicofee` ✅

### 🔧 Configuration Details

- **Project ID**: `kmou-aicofee`
- **Credentials File**: `app/credentials/firebase-admin.json`
- **Service Account**: `firebase-adminsdk-fbsvc@kmou-aicofee.iam.gserviceaccount.com`
- **Environment Variable**: `FIREBASE_CONFIG_PATH=app/credentials/firebase-admin.json`

### 📈 Database Content (as of 2025-08-21)

#### Collections:
- **attendance**: Complete attendance records
- **farmers**: 50 farmer profiles 
- **farms**: 11 coffee farm locations

#### 📅 Attendance Data:
- **Total Records**: 5,753 attendance records
- **Date Range**: 2025-01-01 to 2025-08-21 (233 days)
- **Coverage**: 100% complete (no missing dates)
- **Features**: 
  - Real-time check-in/check-out
  - Face recognition confidence scores
  - Weather conditions tracking
  - Work type classification
  - Farm-farmer associations

#### 🏢 Farm Locations (11 Total):
1. **Future Coffee Farm Vietnam** - Bảo Lộc, Lâm Đồng (35ha, 900m)
2. **Sơn Pacamara Specialty Coffee Farm** - Đà Lạt, Lâm Đồng (18ha, 1600m)
3. **Em Tà Nung Coffee Farm** - Tà Nung, Đà Lạt (25ha, 1500m)
4. **Cầu Đất Coffee Estate** - Cầu Đất, Đà Lạt (42.5ha, 1350m)
5. **Mê Linh Coffee Plantation** - Mê Linh, Lâm Hà (28ha, 1200m)
6. **Chu Yang Sin Highland Farm** - Chu Yang Sin, Đắk Lắk (67.2ha, 800m)
7. **Buôn Ma Thuột Heritage Coffee** - Buôn Ma Thuột, Đắk Lắk (85.5ha, 500m)
8. **Kon Tum Mountain Coffee** - Kon Tum Province (31.8ha, 650m)
9. **Gia Lai Sustainable Coffee Farm** - Pleiku, Gia Lai (55.7ha, 780m)
10. **Cu Chi Specialty Coffee Garden** - Cu Chi, Ho Chi Minh City (22.3ha, 25m)
11. **Đồng Nai Highland Estate** - Cát Tiên, Lâm Đồng (38.9ha, 420m)

**Geographic Coverage**: 6 provinces (Lâm Đồng, Đắk Lắk, Kon Tum, Gia Lai, Ho Chi Minh City)
**Elevation Range**: 25m - 1,600m above sea level
**Total Area**: 469.7 hectares

#### 👥 Farmer Profiles:
- **Total**: 50 active farmers
- **Distributed across**: 11 farms (4-5 farmers per farm)
- **Face enrollment**: Partial (some farmers enrolled)
- **Work assignments**: Field-specific assignments with multiple fields per farm

### 🔄 Alternative Database

**Backup/Alternative**: `kmou-aiface-v2`
- **Credentials File**: `app/credentials/firebase-aiface.json` 
- **Status**: Available but not currently used
- **Purpose**: Backup or development environment

## 🛠️ Usage Notes

### Current Setup:
```python
# Default configuration in app/core/config.py
FIREBASE_CONFIG_PATH: str = "app/credentials/firebase-admin.json"  # kmou-aicofee
```

### To Switch Database:
```bash
# Change environment variable
export FIREBASE_CONFIG_PATH="app/credentials/firebase-aiface.json"
# Or update config.py
```

## 📊 Recent Updates

**2025-08-21**: 
- ✅ Filled 41 missing attendance dates
- ✅ Added 1,147 new records
- ✅ Database now 100% complete for Jan-Aug 2025
- ✅ Ready for production use

## 🔐 Security Notes

- Credentials stored in `/app/credentials/` directory
- Files are gitignored for security
- Service account has appropriate Firestore permissions
- Database rules configured for authenticated access only

---
**Last Updated**: August 21, 2025  
**Status**: ✅ Production Ready  
**Database**: kmou-aicofee (Primary)