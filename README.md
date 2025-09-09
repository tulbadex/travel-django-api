# 🚀 Torrey Travels - Backend API

**Professional Travel Booking Platform Backend** - Complete REST API for flights, hotels, and travel packages with authentication, email notifications, and admin management.

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

## 🌟 Features

- **Complete Travel API** - Flights, hotels, packages, and bookings
- **User Authentication** - Registration, login, password reset with email
- **Email System** - Gmail SMTP integration with professional templates
- **Admin Dashboard** - Comprehensive Django admin interface
- **API Documentation** - Interactive Swagger/OpenAPI documentation
- **Professional Architecture** - SOLID principles, DRY, separation of concerns
- **Security** - Token authentication, CORS, CSRF protection
- **Flexible Database** - SQLite for development, PostgreSQL ready

## 🛠️ Tech Stack

- **Framework**: Django 5.2+ with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Token-based authentication
- **Email**: Gmail SMTP with HTML templates
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Architecture**: RESTful API with modular app structure

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Git

### Installation

```bash
# Clone repository
git clone <repository-url>
cd travel-BE-Django

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Environment Configuration

Create `.env` file with:

```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:9888,http://127.0.0.1:9888

# Email Configuration (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@torreytravels.com

# Leave EMAIL_HOST empty to disable email sending
```

## 📚 API Documentation

### Access Points
- **API Base URL**: `http://localhost:8000/api/`
- **Swagger Documentation**: `http://localhost:8000/swagger/`
- **Admin Panel**: `http://localhost:8000/admin/`

### Authentication Endpoints
```
POST /api/auth/register/          # User registration
POST /api/auth/login/             # User login
POST /api/auth/logout/            # User logout
GET  /api/auth/profile/           # User profile
POST /api/auth/password-reset/    # Request password reset
POST /api/auth/password-reset/confirm/ # Confirm password reset
```

### Travel Endpoints
```
# Flights
GET  /api/flights/airports/       # List airports
GET  /api/flights/search/         # Search flights
POST /api/flights/bookings/       # Create booking
GET  /api/flights/bookings/       # List user bookings

# Hotels
GET  /api/hotels/search/          # Search hotels
GET  /api/hotels/categories/      # Hotel categories

# Packages
GET  /api/packages/search/        # Search packages
GET  /api/packages/categories/    # Package categories
```

## 🏗️ Project Structure

```
travel-BE-Django/
├── accounts/                 # User authentication & management
│   ├── models.py            # User, PasswordResetToken models
│   ├── views.py             # Auth API endpoints
│   ├── serializers.py       # API serializers
│   ├── services.py          # Email service
│   └── admin.py             # Admin configuration
├── flights/                 # Flight management
│   ├── models.py            # Airport, Airline, Flight models
│   ├── views.py             # Flight API endpoints
│   └── admin.py             # Flight admin interface
├── hotels/                  # Hotel management
│   ├── models.py            # Hotel, Destination models
│   ├── views.py             # Hotel API endpoints
│   └── admin.py             # Hotel admin interface
├── packages/                # Travel packages
│   ├── models.py            # Package models
│   ├── views.py             # Package API endpoints
│   └── admin.py             # Package admin interface
├── management/              # Booking management
│   ├── models.py            # Booking, BookingItem models
│   └── admin.py             # Booking admin interface
├── templates/               # Email templates
│   └── emails/              # HTML email templates
├── travel_api/              # Django project settings
│   ├── settings.py          # Main configuration
│   └── urls.py              # URL routing
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## 🔧 Development Commands

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Reset database
python manage.py flush
```

### Testing & Development
```bash
# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Collect static files (production)
python manage.py collectstatic

# Django shell
python manage.py shell
```

## 📧 Email System

### Gmail SMTP Setup
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: Google Account → Security → App passwords
3. Use app password in `EMAIL_HOST_PASSWORD`
4. Configure sender email in `DEFAULT_FROM_EMAIL`

### Email Features
- **Registration Welcome**: Branded welcome email
- **Password Reset**: Secure reset links with expiration
- **Responsive Templates**: Mobile-friendly HTML emails
- **Graceful Fallback**: System works without email configuration

## 🔒 Security Features

- **Token Authentication**: Secure API access
- **Password Reset**: Time-limited, single-use tokens
- **CORS Configuration**: Cross-origin request handling
- **Input Validation**: Comprehensive data validation
- **Admin Security**: Protected admin interface

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment variables
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/torreytravels

# Email configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-production-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Production Commands
```bash
# Install production dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test flights

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### API Testing
- Use Swagger UI at `/swagger/` for interactive testing
- Import API collection into Postman
- Test authentication flows and endpoints

## 🔍 Troubleshooting

### Common Issues

**Email not sending:**
1. Check Gmail app password configuration
2. Verify `EMAIL_HOST` settings in `.env`
3. Check Django console for email output (development)

**Database errors:**
1. Run `python manage.py migrate`
2. Check database connection settings
3. Ensure database exists and is accessible

**CORS errors:**
1. Verify `CORS_ALLOWED_ORIGINS` in settings
2. Check frontend URL configuration
3. Ensure CORS middleware is enabled

### Debug Mode
```bash
# Enable debug logging
DEBUG=True

# Check system configuration
python manage.py check

# View migration status
python manage.py showmigrations
```

## 📊 Admin Interface

### Access
- URL: `http://localhost:8000/admin/`
- Default credentials: `admin` / `password`

### Features
- **User Management**: View and manage user accounts
- **Content Management**: Manage flights, hotels, packages
- **Booking Management**: Track and manage bookings
- **Email Tokens**: Monitor password reset tokens
- **Professional Interface**: Modern, organized admin panels

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow coding standards and architecture principles
4. Add tests for new functionality
5. Update documentation as needed
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open Pull Request

### Code Standards
- Follow Django best practices
- Implement SOLID principles
- Write comprehensive tests
- Document API changes
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Create GitHub issues for bugs and feature requests
- **API Documentation**: Use Swagger UI for API reference
- **Email**: Contact development team for support

## 🔗 Related Projects

- **Frontend**: Torrey Travels React Frontend
- **Mobile**: Torrey Travels Mobile App (coming soon)
- **Admin Dashboard**: Enhanced admin interface (coming soon)

---

**Built with ❤️ using Django REST Framework**

*Professional travel booking platform backend with comprehensive features and modern architecture.*