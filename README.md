# ALX Travel App

A Django REST API for managing property listings and bookings. This application provides endpoints for creating and managing property listings, handling bookings, and managing reviews.

## Features

- Property Listings Management
- Booking System
- Review System
- User Authentication
- API Documentation with Swagger/ReDoc
- MySQL Database Integration
- Celery Task Queue Integration
- Database Seeding for Development

## Tech Stack

- Python 3.x
- Django 4.x
- Django REST Framework
- MySQL
- Redis (for Celery)
- Swagger/ReDoc for API documentation

## Prerequisites

- Python 3.x
- MySQL
- Redis
- Docker (optional)

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd alx_travel_app
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up MySQL database:

```bash
# Using Docker
docker run --name alx_travel_mysql \
    -e MYSQL_ROOT_PASSWORD=rootpassword \
    -e MYSQL_DATABASE=alx_travel_db \
    -e MYSQL_USER=alx_travel_user \
    -e MYSQL_PASSWORD=alx_travel_pass \
    -p 3306:3306 -d mysql:latest
```

5. Create a `.env` file in the project root (use `.env.example` as a template):

```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Run migrations:

```bash
python manage.py migrate
```

7. Create a superuser:

```bash
python manage.py createsuperuser
```

8. (Optional) Seed the database with sample data:

```bash
python manage.py seed
```

This will create:

- 7 sample users (5 regular users, 2 staff users)
- 14 property listings (2 per user)
- Multiple bookings and reviews
  All sample users have the password: `password123`

## Running the Application

1. Start the development server:

```bash
python manage.py runserver
```

2. Start Celery worker (in a separate terminal):

```bash
celery -A alx_travel_app worker -l info
```

## API Endpoints

The API provides the following endpoints:

- `/api/listings/` - Property listings management
- `/api/bookings/` - Booking management
- `/api/reviews/` - Review management
- `/swagger/` - Swagger API documentation
- `/redoc/` - ReDoc API documentation
- `/admin/` - Admin interface
- `/api-auth/` - Authentication endpoints

## Authentication

The API uses Django REST Framework's built-in authentication. To access protected endpoints:

1. Create a user account or use the superuser account
2. Use the login endpoint or session authentication
3. Include authentication credentials in your requests

## API Documentation

The API is fully documented using Swagger/OpenAPI specification. You can explore and test the API endpoints using the interactive documentation.

### Swagger UI

![Swagger UI](assets/swagger.png)

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Development

1. Make sure to create and activate a virtual environment
2. Install development dependencies
3. Follow PEP 8 style guide
4. Write tests for new features
5. Update documentation as needed

## Testing

Run the test suite:

```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Background Tasks with Celery

This project uses Celery with RabbitMQ for handling background tasks such as sending email notifications.

### Setting up RabbitMQ

1. Install RabbitMQ:

```bash
sudo apt-get install rabbitmq-server
```

2. Start RabbitMQ service:

```bash
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

### Running Celery

1. Start the Celery worker:

```bash
celery -A alx_travel_app worker -l info
```

2. (Optional) Start Celery beat for periodic tasks:

```bash
celery -A alx_travel_app beat -l info
```

### Email Configuration

The application uses SMTP for sending emails. To configure email settings:

1. Copy the email configuration from `.env.example` to your `.env` file
2. Update the email settings with your SMTP credentials
3. For Gmail, you'll need to:
   - Enable 2-factor authentication
   - Generate an App Password
   - Use the App Password as EMAIL_HOST_PASSWORD

### Features

- Asynchronous email notifications for booking confirmations
- Background task processing with Celery
- Email notifications using SMTP

## Docker Setup

You can run the entire application stack using Docker Compose:

1. Create a `.env` file from the template:

```bash
cp .env.example .env
# Edit .env with your configuration
```

2. Build and start the containers:

```bash
docker-compose up --build
```

This will start the following services:

- Django web application (http://localhost:8000)
- MySQL database
- Redis for Celery results backend
- RabbitMQ for message broker
- Celery worker for background tasks

You can access:

- RabbitMQ management interface at http://localhost:15672 (guest/guest)
- Django admin interface at http://localhost:8000/admin
- API documentation at http://localhost:8000/swagger/
- Mailpit web interface at http://localhost:8025

3. Run migrations inside the container:

```bash
docker-compose exec web python manage.py migrate
```

4. Create a superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

5. (Optional) Seed the database:

```bash
docker-compose exec web python manage.py seed
```

To stop the services:

```bash
docker-compose down
```

To stop the services and remove all data (volumes):

```bash
docker-compose down -v
```

### Email Testing with Mailpit

The application uses Mailpit for email testing in the development environment. When running with Docker Compose:

- SMTP server is available at port 1025
- Web interface to view emails is available at http://localhost:8025
- No authentication required for SMTP
- All emails are caught by Mailpit and won't be actually sent
- You can view HTML and plain text versions of emails
- Supports attachments and different email clients

You can access:

- RabbitMQ management interface at http://localhost:15672 (guest/guest)
- Django admin interface at http://localhost:8000/admin
- API documentation at http://localhost:8000/swagger/
- Mailpit web interface at http://localhost:8025

## Running the Project with Docker Compose

### Prerequisites

- Docker and Docker Compose installed on your system
- Git installed on your system

### Setup Steps

1. Clone the repository:

```bash
git clone <repository-url>
cd alx_travel_app_0x03
```

2. Create a `.env` file in the project root with the following environment variables:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=alx_travel_app
MYSQL_USER=alx_travel_app_user
MYSQL_PASSWORD=password123
MYSQL_HOST=db
MYSQL_PORT=3306

# RabbitMQ Settings
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email Settings (Using Mailpit for local development)
EMAIL_HOST=mailpit
EMAIL_PORT=1025
EMAIL_USE_TLS=False
DEFAULT_FROM_EMAIL=test@alxtravelapp.com
```

3. Build and start the Docker containers:

```bash
docker compose up --build
```

4. Once all services are running, in a new terminal, run the database migrations:

```bash
docker compose exec web python manage.py migrate
```

5. Create a superuser account:

```bash
docker compose exec web python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Accessing the Services

After completing the setup, you can access the following services:

- **Django Application**: http://localhost:8000
- **Django Admin Interface**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs/
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Mailpit Web Interface**: http://localhost:8025 (for viewing sent emails)

### Testing Email Functionality

The project uses Mailpit for local email testing. All emails sent by the application in development will be caught by Mailpit and can be viewed in its web interface at http://localhost:8025. No emails will actually be sent to real email addresses.

### Common Commands

- Stop all services:

```bash
docker compose down
```

- View logs of all services:

```bash
docker compose logs
```

- View logs of a specific service:

```bash
docker compose logs [service_name]  # e.g., docker compose logs web
```

- Restart a specific service:

```bash
docker compose restart [service_name]  # e.g., docker compose restart web
```

- Run Django management commands:

```bash
docker compose exec web python manage.py [command]
```

### Troubleshooting

1. **Database Connection Issues**:

   - Ensure the MySQL container is running: `docker compose ps`
   - Check MySQL logs: `docker compose logs db`
   - Verify database credentials in `.env` file

2. **Email Testing Issues**:

   - Ensure Mailpit container is running
   - Check Mailpit logs: `docker compose logs mailpit`
   - Verify email settings in Django settings

3. **Container Start-up Issues**:
   - Remove all containers and volumes: `docker compose down -v`
   - Rebuild all containers: `docker compose up --build`

### Development Workflow

1. Make changes to your code
2. The Django development server will automatically reload
3. If you modify dependencies:
   - Update `requirements.txt`
   - Rebuild containers: `docker compose up --build`
4. If you modify models:
   - Create migrations: `docker compose exec web python manage.py makemigrations`
   - Apply migrations: `docker compose exec web python manage.py migrate`

## Testing Chapa Payment Integration

The application uses Chapa for payment processing. Here's how to test the payment flow:

### 1. Create a Payment

First, create a payment for a booking using the `/api/payments/` endpoint:

```json
{
  "booking": "YOUR_BOOKING_ID",
  "amount": "1250.00",
  "currency": "ETB",
  "email": "user@example.com",
  "phone_number": "+251911234567",
  "first_name": "Test",
  "last_name": "User",
  "payment_title": "Booking Payment",
  "description": "Payment for 5 nights stay"
}
```

![Get Payments](assets/get_payment.png)

### 2. Initialize Payment

After creating the payment, initialize it using:

```
POST /api/payments/{payment_id}/initialize/
```

The response will include a `checkout_url` and the system will automatically send an email to the user with:

- A link to complete the payment
- Booking details
- Payment amount
- Expiry information

You can check the email in Mailpit (http://localhost:8025):

![Get Payment Response](assets/get_payent_response.png)

### 3. Complete Test Payment

You can complete the payment in two ways:

1. Click the payment link in your email
2. Use the `checkout_url` from the API response

Both will take you to the Chapa checkout interface:

1. Click the payment link in your email
2. Use the `checkout_url` from the API response

Both will take you to the Chapa checkout interface:

### 4. Payment Success

After successful payment, you'll be redirected to the success page:

![Payment Success](assets/success.png)

### 5. Verify Payment Status

You can verify the payment status in two ways:

1. Check the payment details:

```
GET /api/payments/{payment_id}/
```

2. Explicitly verify with Chapa:

```
GET /api/payments/{payment_id}/verify/
```

The verification response will show the updated payment status:

![Payment Verification](assets/verify_payment.png)

After successful verification, you can check the payment details to confirm the status has been updated to "completed":

![Payment Completion](assets/completed.png)

### 6. Testing Email Notifications

The system sends several types of email notifications throughout the booking and payment process:

1. **Booking Confirmation Email**
   - Sent automatically when a booking is created
   - Contains booking details and reference number

![Booking Email](assets/booking_email.png)

2. **Payment Checkout Email**
   - Sent when a payment is initialized
   - Contains the payment link and booking details
   - Includes amount to be paid and expiry information

![Checkout Email](assets/checkout_email.png)

3. **Payment Confirmation Email**
   - Sent after successful payment verification
   - Contains transaction details and booking confirmation

You can view all emails in the Mailpit interface at http://localhost:8025

### 7. Testing Complete Flow

1. Create a new payment:

```bash
curl -X POST http://localhost:8000/api/payments/ \
  -H "Content-Type: application/json" \
  -d '{
    "booking": "YOUR_BOOKING_ID",
    "amount": "1250.00",
    "currency": "ETB",
    "email": "test@example.com",
    "phone_number": "+251911234567",
    "first_name": "Test",
    "last_name": "User",
    "payment_title": "Booking Payment",
    "description": "Test payment"
  }'
```

2. Initialize the payment:

```bash
curl -X POST http://localhost:8000/api/payments/{payment_id}/initialize/
```

3. Complete the payment using the test card:

   - Open the checkout URL in your browser
   - Use test card: 4242424242424242
   - Any future expiry date
   - Any 3-digit CVC
   - Any 4-digit PIN

4. Verify the payment:

```bash
curl -X GET http://localhost:8000/api/payments/{payment_id}/verify/
```

5. Check the results:
   - Payment status should be "completed"
   - Booking status should be "confirmed"
   - Check Mailpit (http://localhost:8025) for confirmation email
   - View payment details in Django admin (http://localhost:8000/admin/listings/payment/)

### Troubleshooting Payment Testing

1. **Payment Initialization Fails**:

   - Check your Chapa API key in `.env`
   - Ensure all required fields are provided
   - Check the error message in the response

2. **Email Not Received**:

   - Ensure Celery worker is running: `docker compose logs celery`
   - Check Mailpit is running: `docker compose ps`
   - View Mailpit logs: `docker compose logs mailpit`

3. **Payment Status Not Updating**:
   - Check Chapa webhook logs
   - Try manual verification using the verify endpoint
   - Check Django logs: `docker compose logs web`

Note: This is using Chapa's test mode. For production, you'll need to:

1. Create a Chapa business account
2. Get production API keys
3. Update the `CHAPA_SECRET_KEY` in your environment variables
