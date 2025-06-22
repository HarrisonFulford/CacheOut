# Compute Nexus Market - Frontend

A modern React-based frontend for the CacheOut distributed compute marketplace. This application provides an intuitive interface for buying and selling compute resources.

## 🚀 Features

### Buyer Dashboard
- **Job Submission**: Create and submit compute jobs with resource requirements
- **Real-time Monitoring**: Live updates of job status and progress
- **Credit Management**: View and manage credit balances
- **Resource Configuration**: Specify CPU cores, RAM, and job priority
- **Job History**: Track all submitted jobs and their outcomes

### Seller Dashboard
- **Worker Registration**: Register machines as compute workers
- **Resource Management**: Configure CPU cores and RAM allocation
- **Earnings Tracking**: Monitor credit earnings from completed jobs
- **Status Monitoring**: Real-time worker status and job assignments

### Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Dark Theme**: Modern dark interface with glassmorphism effects
- **Real-time Updates**: Auto-refreshing data with TanStack Query
- **Interactive Components**: Rich UI components from shadcn/ui
- **Smooth Animations**: CSS transitions and hover effects

## 🏗️ Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: shadcn/ui component library
- **State Management**: TanStack Query for server state
- **Routing**: React Router DOM
- **Icons**: Lucide React icons
- **Forms**: React Hook Form with Zod validation

## 📋 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   ├── BuyerDashboard.tsx
│   ├── SellerDashboard.tsx
│   ├── BuyComputePanel.tsx
│   ├── SellComputePanel.tsx
│   └── Header.tsx
├── pages/              # Page components
│   ├── Index.tsx       # Landing page
│   ├── BuyerDashboard.tsx
│   ├── SellerDashboard.tsx
│   └── Layout.tsx
├── lib/                # Utility libraries
│   ├── api.ts          # API client functions
│   └── utils.ts        # Helper utilities
├── hooks/              # Custom React hooks
│   ├── use-toast.ts    # Toast notifications
│   └── use-mobile.tsx  # Mobile detection
└── App.tsx             # Main application component
```

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 18+ and npm
- CacheOut backend running on `http://localhost:8000`

### Quick Start

1. **Install dependencies**:
```bash
npm install
```

2. **Start development server**:
```bash
npm run dev
```

3. **Open in browser**:
Navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## 🔧 Configuration

### API Configuration
The frontend connects to the CacheOut backend API. Update the API base URL in `src/lib/api.ts` if needed:

```typescript
const API_BASE = "http://localhost:8000/api/v1";
```

### Environment Variables
Create a `.env` file for environment-specific configuration:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=Compute Nexus Market
```

## 📊 API Integration

### Backend Endpoints Used
- `GET /api/v1/workers` - Fetch all registered workers
- `POST /api/v1/register` - Register a new worker
- `GET /api/v1/jobs` - Fetch all jobs
- `POST /api/v1/submit` - Submit a new job
- `GET /api/v1/credits/{user_id}` - Get user credit balance
- `GET /api/v1/health` - System health check

### Data Flow
1. **Real-time Updates**: TanStack Query automatically refreshes data every 5 seconds
2. **Error Handling**: Comprehensive error handling with user-friendly messages
3. **Loading States**: Skeleton loaders and loading indicators
4. **Optimistic Updates**: Immediate UI updates with background sync

## 🎨 UI Components

### Design System
- **Color Palette**: Dark theme with accent colors
- **Typography**: Inter font family with consistent sizing
- **Spacing**: Tailwind CSS spacing scale
- **Shadows**: Subtle shadows and glows for depth

### Key Components
- **Cards**: Information containers with hover effects
- **Tables**: Sortable job and worker lists
- **Forms**: Validated job submission forms
- **Dialogs**: Modal dialogs for confirmations
- **Toasts**: Notification system for user feedback

## 🔒 Security Features

- **Input Validation**: Client-side validation with Zod schemas
- **XSS Protection**: Sanitized user inputs
- **CORS Handling**: Proper CORS configuration for API calls
- **Error Boundaries**: Graceful error handling

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Optimizations
- Touch-friendly interface
- Optimized layouts for small screens
- Swipe gestures for navigation
- Mobile-specific UI components

## 🧪 Testing

### Development Testing
```bash
# Run linting
npm run lint

# Type checking
npm run type-check
```

### Manual Testing
1. **Buyer Flow**:
   - Navigate to Buyer Dashboard
   - Submit a test job
   - Monitor job status updates
   - Check credit balance changes

2. **Seller Flow**:
   - Navigate to Seller Dashboard
   - Register as a worker
   - Monitor job assignments
   - Track earnings

## 🚀 Performance

### Optimizations
- **Code Splitting**: Automatic route-based code splitting
- **Lazy Loading**: Components loaded on demand
- **Caching**: TanStack Query caching for API responses
- **Bundle Optimization**: Vite optimizations for production builds

### Metrics
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **First Input Delay**: < 100ms

## 🔧 Development

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

### Code Style
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **TypeScript**: Strict type checking
- **Conventional Commits**: Git commit message format

## 🚨 Recent Updates

### v1.0.0 - Production Ready
- ✅ Real-time job and worker monitoring
- ✅ Enhanced job submission form
- ✅ Improved error handling and user feedback
- ✅ Mobile-responsive design
- ✅ Integration with improved backend API
- ✅ Comprehensive input validation
- ✅ Modern UI with glassmorphism effects

## 🔮 Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Advanced job scheduling interface
- [ ] Worker performance analytics
- [ ] Multi-language support
- [ ] PWA capabilities
- [ ] Advanced filtering and search
- [ ] Job templates and presets
- [ ] Dark/light theme toggle

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the browser console for errors
2. Verify the backend API is running
3. Check network connectivity
4. Review the API documentation

## 🔗 Related Projects

- **Backend**: [CacheOut Backend](../CacheOut_init) - FastAPI coordinator
- **Worker Script**: [CacheOut Worker](../CacheOut_init/backend/worker.py) - Worker agent
- **Testing**: [Integration Tests](../testing) - System testing suite
