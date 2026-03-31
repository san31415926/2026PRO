# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SmartMall_BiShe is a full-stack e-commerce graduation project (毕设) with three services:
- **Flask backend** (`backend/`) — REST API on port 5000
- **Admin dashboard** (`admin-web/`) — Vue 3 + Element Plus, port 5173
- **Mobile customer app** (`mobile-web/`) — Vue 3 + Vant, port 5174

## Commands

### Start Everything
```bash
python start.py   # Launches all 3 services in parallel
```

### Backend
```bash
cd backend
# Activate virtual environment
source venv/Scripts/activate       # Windows Git Bash
venv\Scripts\activate.bat          # Windows CMD

python app.py                      # Run server
python init_data.py                # Initialize DB with seed data
python reset_db.py                 # Reset DB (destructive)
```

### Frontend (admin-web or mobile-web)
```bash
cd admin-web   # or mobile-web
npm install
npm run dev     # Development with hot reload
npm run build   # Production build
npm run preview # Preview production build
```

## Database Setup

MySQL database required:
- Database: `smart_mall`
- User: `root` / Password: `panweiyu123`
- Connection string in `backend/app.py`

Default admin login: `admin` / `123456`

Run `python init_data.py` once to create tables and insert seed data (coupons, system config, admin account).

## Architecture

### Backend (`backend/app.py`)

Single-file Flask app (~868 lines) with SQLAlchemy ORM models and ~48 REST endpoints organized into namespaces:
- `/api/admin/*` — admin auth, product/coupon/comment/order management
- `/api/mobile/*` — user auth, cart, orders, favorites, comments
- `/api/common/*` — system configuration reads
- `/api/products`, `/api/banners` — public catalog
- `/uploads/<filename>` — uploaded image serving

**API response format:** `{'code': 200|400|401|500, 'msg': '...', 'data': {...}}`

**CORS:** Custom `before_request`/`after_request` handlers allow all origins with credentials (required for session cookies).

### Key SQLAlchemy Models
`Admin`, `Member` (customers with balance/points/VIP level), `Product`, `Order`, `Cart`, `Address`, `Banner`, `SystemCoupon`, `UserCoupon`, `Favorite`, `Comment`, `GroupTeam`

### Admin Panel (`admin-web/`)

Vue 3 SPA with tab-based pseudo-routing (no Vue Router). `activeMenu` ref in `App.vue` controls which view component renders. Uses Element Plus UI. No global state management — all state is local `ref()`s.

### Mobile App (`mobile-web/`)

Nearly the entire app lives in one large `App.vue` (~2000 lines). Tab navigation (0=Home, 1=Cart, 2=Profile) with nested view states. Uses Vant mobile UI. No global state management.

Both frontends use `axios.defaults.withCredentials = true` — critical for session cookie auth.

### Business Logic Features
- **VIP System:** 3 tiers (Normal/Gold/Diamond) with progressive discounts
- **Coupon System:** Inventory-based, level-restricted, single-use per user
- **Group Purchase (拼团):** Team creation with shareable code, minimum member threshold
- **Flash Sale (秒杀):** Special product category with time-limited discounts
- **Points:** Earned on signup (500pts), daily sign-in (+100pts), redeemable at checkout
- **Balance:** Users start with ¥10,000 virtual balance

### Image Uploads
Files saved to `backend/uploads/` with UUID-based filenames. Served at `http://localhost:5000/uploads/{filename}`.
