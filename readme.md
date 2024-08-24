# Online Mart API

Welcome to the **Online Mart API** project! This project is made by Munazza Zahid and Sana Zahid. This project is a modern, scalable solution built using the latest technologies. It was a thrilling journey to develop this application, with a few setbacks along the way, but the learning experience was invaluable. Working on this project has significantly expanded our skill set, and we are excited to share the results with you.

## Overview

The Online Mart API is an e-commerce platform built with cutting-edge technology, designed to provide a seamless shopping experience. In our architecture, each microservice is designed with its own dedicated database, ensuring data encapsulation and service independence. This approach allows each service to manage its own data storage, enhancing scalability, security, and flexibility across the entire system. The architecture is based on microservices, each responsible for a specific domain. This modular approach ensures flexibility, and ease of maintenance.

### Key Technologies

- **FastAPI**: High-performance framework for building APIs with Python.
- **SQLModel**: ORM for interacting with PostgreSQL databases.
- **Python**: Core programming language used throughout the project.
- **Docker**: Containerization of services for consistency across environments.
- **Docker Compose**: Orchestrates multi-container Docker applications.
- **Event-Driven Architecture**: Using Kafka for decoupling services and ensuring real-time communication.
- **Stripe**: Integration for payment processing.
- **Etheriel.email**: Sending notifications to users using Python's built-in email library "Etheriel.email".
- **PostgreSQL**: Robust and scalable relational database management system.
- **JSON**: For data serialization and communication between services.
- **Poetry**: Dependency management and packaging for Python.

## Microservices

The Online Mart API is composed of six distinct microservices, each serving a crucial role in the system:

1. **Product Service**
 - The Product Service API is a comprehensive solution for managing product data within your application. It provides endpoints for creating, updating, retrieving, and deleting product information, ensuring that your product catalog is always up-to-date.
 - **Usage**: Navigate to [http://127.0.0.1:8005](http://127.0.0.1:8005) to use this service.

2. **Order Service**
 - The Order Service API is a robust backend solution designed to manage and process customer orders efficiently.
 - **Usage**: Navigate to [http://127.0.0.1:8006](http://127.0.0.1:8006) to use this service.

3. **Inventory Service**
 - The Inventory Service API is a crucial component for managing stock levels and ensuring product availability across your platform.
 - **Usage**: Navigate to [http://127.0.0.1:8007](http://127.0.0.1:8007) to use this service.

4. **User Service**
 - The User Service API is a foundational component for managing user registration, authentication, and authorization, ensuring secure access to your platform.
 - **Usage**: Navigate to [http://127.0.0.1:8008](http://127.0.0.1:8008) to use this service.

5. **Notification Service**
 - The Notification Service API is designed to streamline communication with your users by delivering timely and relevant notifications.
 - **Usage**: Navigate to [http://127.0.0.1:8009](http://127.0.0.1:8009) to use this service.

6. **Payment Service**
 - The Payment Service API is designed to seamlessly manage and process payments for your orders.
 - **Usage**: Navigate to [http://127.0.0.1:8010](http://127.0.0.1:8010) to use this service.

### Kafka Topic Viewer

- **Kafka**: Navigate to [http://127.0.0.1:8080](http://127.0.0.1:8080) to view Kafka topics.


### Starting the Project

To start the project, use the following command:

```bash
docker compose up -d ```

### Architecture Diagram

To understand the connections between these services, please view the architecture diagram below:

![Architecture Diagram](Screenshot (275).png)


### Final Thoughts

Building the Online Mart API has been an incredibly rewarding experience. The journey was filled with challenges that pushed us to learn new techniques and tools, making us more capable developers. This project highlights the power of modern technology and the importance of perseverance in software development.

Thank you for exploring the Online Mart API. We hope you find it as exciting to use as We did to build!
