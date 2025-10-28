# API Design & Architecture Context

This context provides comprehensive guidance for designing RESTful APIs, GraphQL schemas, and microservice architectures with focus on scalability, security, and developer experience.

## Core Principles

### API Design
- RESTful resource modeling with proper HTTP methods
- Consistent naming conventions and URL structures  
- Comprehensive error handling with meaningful status codes
- Version management strategies (URL path vs headers)

### Data Architecture
- Schema design for both SQL and NoSQL databases
- Caching strategies (Redis, CDN, application-level)
- Event-driven architecture patterns
- Data consistency models (eventual vs strong consistency)

### Security Framework
- OAuth 2.0 / OpenID Connect implementation
- API rate limiting and throttling
- Input validation and sanitization
- Secure secrets management

### Performance Optimization
- Database query optimization
- Connection pooling strategies
- Asynchronous processing patterns
- Load balancing and auto-scaling

## Technology Stack

**Preferred Technologies:**
- Python (FastAPI, Django REST Framework)
- Node.js (Express, NestJS)
- Database: PostgreSQL, MongoDB, Redis
- Message Queues: RabbitMQ, Apache Kafka
- Monitoring: Prometheus, Grafana, ELK Stack

## Documentation Standards

All APIs should include OpenAPI/Swagger specifications, comprehensive guides for common use cases, and interactive documentation for developer onboarding.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.