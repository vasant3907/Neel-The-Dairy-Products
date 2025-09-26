## Neel — The Dairy Products

Modern mobile-first platform for browsing, ordering, and tracking delivery of fresh dairy products. Built as a full‑stack app with a Django REST API backend and a React Native (Expo) frontend.

### Why this project?
People want fresh dairy every day but often lack time to visit stores. This app lets users browse products (milk, curd, paneer, cheese, ghee, lassi, ice cream, and more), add to cart, pay, and track orders from their phone, while helping local dairies reach more customers.

---

## Features
- **Product catalog**: Images, details, pricing, and ratings
- **Cart and checkout**: Persistent cart and order placement
- **Payments**: Stripe ready on backend; Stripe/Razorpay integrations present in frontend
- **Order tracking**: See order status updates
- **Auth**: Token/session-ready API; mobile auth screen in place
- **Responsive mobile UI**: React Native with Expo, navigation, gesture handling
- **CORS enabled API**: Ready for local/mobile development

---

## Tech Stack
- **Frontend**: React Native 0.76 (Expo 52), React Navigation, AsyncStorage, Reanimated
- **Payments (mobile)**: `@stripe/stripe-react-native`, `react-native-razorpay`
- **Backend**: Django 5.x, Django REST Framework, Token Auth, CORS
- **Database**: SQLite by default (can switch to PostgreSQL/MySQL via env)

---

## Repository Structure
```
dairy-app/
  dairy-backend/     # Django project (API, auth, orders, products)
  dairy-frontend/    # React Native (Expo) app
  README.md          # You are here
```

---

## Quick Start

### Prerequisites
- Node.js 18+ and npm (or Yarn)
- Python 3.11+
- Git
- Expo CLI (auto-installed by npm scripts) and an emulator/device for Android/iOS or web

### 1) Backend — Django API
From the repo root:

```bash
cd dairy-backend
python -m venv .venv
. .venv/Scripts/Activate.ps1   # Windows PowerShell
pip install --upgrade pip
pip install django djangorestframework python-decouple django-cors-headers stripe

# Environment (.env in dairy-backend/dairy/ or project root of backend)
# Example values — replace in your local .env file (do not commit secrets)
```

```
SECRET_KEY=replace_me
DEBUG=True
ALLOWED_HOSTS=*

# Database (defaults to SQLite if omitted)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Stripe (optional for local testing)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
```

```bash
python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver 0.0.0.0:8000
```

The API will run at `http://localhost:8000/`.

### 2) Frontend — React Native (Expo)
From the repo root:

```bash
cd dairy-frontend
npm install
```

Create a `.env` in `dairy-frontend/` for the mobile app if using Stripe publishable key:

```
STRIPE_KEY=pk_test_...
```

Update `dairy-frontend/config.js` `apiUrl` to point to your backend (use your LAN IP if testing on a device):

```js
const config = {
  apiUrl: 'http://YOUR_LOCAL_IP:8000/',
  stripePublishableKey: STRIPE_KEY
};
```

Run the app:

```bash
npm run start            # Expo Dev Tools
npm run android          # Android emulator/device
npm run ios              # iOS simulator (macOS)
npm run web              # Web preview
```

---

## Configuration Notes
- `dairy-frontend/config.js` reads `STRIPE_KEY` from `.env` via `react-native-dotenv`.
- `dairy-backend/dairy/settings.py` uses `python-decouple` to load env vars: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, DB settings, and Stripe keys.
- CORS is enabled for development (`CORS_ALLOW_ALL_ORIGINS=True`). Consider restricting in production.
- Media files (product images) are served from the backend `product/` directory (`MEDIA_URL=/media/`).

---

## Common Scripts
### Backend
- `python manage.py migrate`
- `python manage.py runserver 0.0.0.0:8000`

### Frontend
- `npm run start`
- `npm run android | ios | web`

---

## Testing the Flow (Local)
1. Start the backend at `http://localhost:8000/`.
2. Start the frontend via Expo.
3. Ensure the mobile `apiUrl` points to the backend. If using a physical device, replace `localhost` with your PC’s LAN IP.
4. Browse products, add to cart, and proceed to checkout. Payment SDKs are wired; use test keys if needed.

---

## How to Contribute (Great for GitHub and Recruiters)
Follow these steps to make meaningful contributions and showcase collaboration skills:

1. **Fork** the repository on GitHub.
2. **Clone** your fork:
   ```bash
   git clone https://github.com/<your-username>/dairy-app.git
   cd dairy-app
   ```
3. **Create a branch** per feature/fix:
   ```bash
   git checkout -b feat/product-search
   ```
4. **Commit with conventional messages**:
   ```bash
   git commit -m "feat(frontend): add product search bar"
   git commit -m "fix(backend): correct CORS config for Stripe webhook"
   ```
5. **Push and open a Pull Request** to the original repo. Describe:
   - What changed and why
   - Screenshots/GIFs for UI changes
   - Testing steps
   - Any follow-ups or known limitations

### Good First Issues to Try
- Add product search and filters
- Add unit tests for serializers/views
- Improve error states and empty screens in mobile UI
- Replace `CORS_ALLOW_ALL_ORIGINS=True` with domain allowlist for prod
- Add CI (GitHub Actions) for lint and tests

---

## Presenting This Project to Recruiters
- **Clear README**: This file explains the what/why/how succinctly.
- **Screenshots/GIFs**: Add app screens in `dairy-frontend/assets/` and embed below.
- **Demo script**: Show browsing, add-to-cart, checkout, and order tracking in < 2 minutes.
- **Security & scalability**: Mention env‑driven config, token auth, Stripe readiness, and DB swap capability.
- **Clean commits and PRs**: Use conventional commits and small, focused PRs.

You can embed visuals like this:

```
![Home Screen](dairy-frontend/assets/images/cow-milk.png)
![Products](dairy-frontend/assets/product/cow-ghee.png)
```

---

## Troubleshooting
- Mobile device can’t reach API: use your computer’s LAN IP in `apiUrl`.
- Expo cache issues: stop packager and run `expo start -c`.
- Django missing env: create `.env` and ensure PowerShell session is inside `dairy-backend/` when running.
- Payment test keys: use Stripe test keys; do not commit real keys.

---

## License
This project is for educational and portfolio use. Add a license if you plan to distribute commercially.
