# 📊 Doctor Dashboard - دستورالعمل اجرایی

## 📋 خلاصه

این دستورالعمل برای ایجنتی است که مسئول ساخت داشبورد اختصاصی پزشکان HELSSA است. این داشبورد باید تجربه کاربری عالی با طراحی مدرن و عملکرد بالا ارائه دهد.

## 🎯 مأموریت شما

شما باید:
1. `PLAN.md` را به دقت مطالعه کنید
2. طبق `CHECKLIST.json` پیش بروید
3. هر تغییر را در `LOG.md` ثبت کنید
4. پیشرفت را در `PROGRESS.json` به‌روزرسانی کنید
5. **کیفیت UI/UX را در اولویت قرار دهید**

## 📁 فایل‌های راهنما

- **PLAN.md**: طرح کامل توسعه با جزئیات فنی و طراحی
- **CHECKLIST.json**: لیست دقیق کارها با اولویت‌بندی
- **PROGRESS.json**: وضعیت پیشرفت (شامل UI metrics)
- **LOG.md**: ثبت تصمیمات و تغییرات
- **charts/**: نمودارهای پیشرفت

## 🏗️ ساختار خروجی مورد انتظار

```
agent/doctor_dashboard/
├── backend/                # Backend APIs
│   ├── models/
│   ├── services/
│   ├── api/
│   └── tests/
├── frontend/              # React Application
│   ├── public/
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── store/        # Redux store
│   │   ├── services/     # API services
│   │   ├── hooks/        # Custom hooks
│   │   ├── utils/        # Utilities
│   │   ├── styles/       # Global styles
│   │   └── assets/       # Images, fonts
│   ├── package.json
│   └── tsconfig.json
├── docs/                  # مستندات
│   ├── API.md
│   ├── COMPONENTS.md
│   ├── DEPLOYMENT.md
│   └── USER_GUIDE.md
├── configs/               # تنظیمات نمونه
│   ├── nginx.conf
│   └── docker-compose.yml
└── requirements.txt       # Backend dependencies
```

## 🎨 راهنمای طراحی UI

### Design System

```typescript
// theme/colors.ts
export const colors = {
  primary: {
    main: '#1976D2',
    light: '#42A5F5',
    dark: '#1565C0',
  },
  secondary: {
    main: '#DC004E',
    light: '#E33371',
    dark: '#9A0036',
  },
  grey: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    // ...
  },
  success: '#4CAF50',
  warning: '#FF9800',
  error: '#F44336',
  info: '#2196F3',
};

// theme/typography.ts
export const typography = {
  fontFamily: {
    persian: 'Vazir, Arial, sans-serif',
    english: 'Inter, Arial, sans-serif',
  },
  // ...
};
```

### Component Structure

```jsx
// components/Overview/SummaryCard.tsx
interface SummaryCardProps {
  title: string;
  value: number | string;
  icon: ReactNode;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  loading?: boolean;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({
  title,
  value,
  icon,
  trend,
  loading = false,
}) => {
  // Implementation with proper loading states
  // Smooth animations
  // Responsive design
  // RTL support
};
```

### State Management

```typescript
// store/slices/dashboardSlice.ts
interface DashboardState {
  overview: {
    stats: DashboardStats | null;
    loading: boolean;
    error: string | null;
  };
  appointments: {
    // ...
  };
  // ...
}

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    // Synchronous actions
  },
  extraReducers: (builder) => {
    // Async thunks
  },
});
```

## 🚀 مراحل اجرا

### Backend Development

1. [ ] Django app setup
2. [ ] Models & migrations
3. [ ] Service layer
4. [ ] REST APIs
5. [ ] Tests

### Frontend Development

1. [ ] React + TypeScript setup
2. [ ] Redux configuration
3. [ ] API client setup
4. [ ] Routing setup
5. [ ] Base components

### UI Implementation

1. [ ] Design system
2. [ ] Layout components
3. [ ] Page components
4. [ ] Interactive features
5. [ ] Animations

### Optimization

1. [ ] Code splitting
2. [ ] Lazy loading
3. [ ] Caching strategy
4. [ ] Performance monitoring
5. [ ] Bundle optimization

## 📊 معیارهای موفقیت

### Performance Targets
- [ ] First Contentful Paint < 1s
- [ ] Time to Interactive < 2s
- [ ] Lighthouse Score > 90
- [ ] Bundle size < 500KB (initial)

### UX Targets
- [ ] Task completion rate > 95%
- [ ] Error rate < 1%
- [ ] User satisfaction > 4.5/5
- [ ] Mobile usability: Excellent

### Code Quality
- [ ] Test coverage > 80%
- [ ] TypeScript strict mode
- [ ] ESLint rules passed
- [ ] No accessibility violations

## 🔧 نکات فنی مهم

### API Integration

```typescript
// services/api.ts
class DashboardAPI {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL,
      timeout: 10000,
    });
    
    // Request interceptor for auth
    this.client.interceptors.request.use(
      (config) => {
        const token = store.getState().auth.token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      }
    );
    
    // Response interceptor for errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Global error handling
        return Promise.reject(error);
      }
    );
  }
  
  // API methods
  async getOverviewStats(): Promise<DashboardStats> {
    const { data } = await this.client.get('/dashboard/overview/');
    return data;
  }
}
```

### Responsive Design

```scss
// styles/breakpoints.scss
$breakpoints: (
  'xs': 0,
  'sm': 576px,
  'md': 768px,
  'lg': 992px,
  'xl': 1200px,
  'xxl': 1400px
);

@mixin respond-to($breakpoint) {
  @media (min-width: map-get($breakpoints, $breakpoint)) {
    @content;
  }
}

// Usage
.dashboard-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
  
  @include respond-to('md') {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @include respond-to('lg') {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### RTL Support

```typescript
// hooks/useDirection.ts
export const useDirection = () => {
  const { language } = useSelector((state) => state.settings);
  const direction = language === 'fa' ? 'rtl' : 'ltr';
  
  useEffect(() => {
    document.documentElement.dir = direction;
    document.documentElement.lang = language;
  }, [direction, language]);
  
  return direction;
};
```

## 🆘 در صورت مواجه با مشکل

1. مشکل را در LOG.md ثبت کنید
2. برای UI/UX issues، screenshot اضافه کنید
3. Performance issues را با metrics ثبت کنید
4. Browser compatibility issues را مشخص کنید

---

**یادآوری**: داشبورد پزشک ویترین اصلی محصول برای پزشکان است. کیفیت، زیبایی و کارایی در اولویت قرار دارند. First impression matters!