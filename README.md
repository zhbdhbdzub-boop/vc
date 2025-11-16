# Modular Platform - Odoo-Inspired Architecture

A highly modular, extensible platform for purchasing and integrating independent business modules. Built with **Django (Backend)** and **React (Frontend)**.

## 🎯 Project Overview

This platform enables users to purchase individual modules (like CV Analysis or Interview Simulation) and link them together for combined workflows. Inspired by Odoo's modular architecture.

### Example Modules
- **CV Analysis Module**: Upload CV + Job Description → Get match analysis report
- **Interview Simulation Module**: Upload CV + Job Description → AI-generated interview with scoring
- **Combined Mode**: When both modules are owned, interview questions are tailored using CV analysis insights

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [UML Diagrams](#uml-diagrams)
4. [Database Schema](#database-schema)
5. [API Design](#api-design)
6. [Module Communication](#module-communication)
7. [Setup Instructions](#setup-instructions)
8. [Implementation Roadmap](#implementation-roadmap)

## 🏗️ System Architecture

### Architecture Pattern: Modular Monolith (MVP) → Microservices (Scale)

**Phase 1 (MVP)**: Modular monolith with plugin architecture
- Single Django application with app-based modules
- Shared PostgreSQL database with tenant isolation
- Celery for async tasks
- Redis for caching and message passing

**Phase 2 (Scale)**: Microservices transition
- Each module becomes independent service
- Event-driven communication via Kafka/RabbitMQ
- API Gateway for routing
- Service mesh (Istio/Linkerd)

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Users / Clients                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    React SPA (Frontend)                      │
│  - Dashboard  - Module Marketplace  - Module UIs             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Django API Gateway                         │
│  - Authentication (JWT/OAuth2)  - Rate Limiting              │
│  - Request Routing  - Response Aggregation                   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Auth &     │  │   Billing &  │  │   Module     │
│   Identity   │  │  Marketplace │  │   Registry   │
│   Service    │  │   Service    │  │   Service    │
└──────────────┘  └──────────────┘  └──────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ CV Analysis  │  │  Interview   │  │   Future     │
│   Module     │  │  Simulation  │  │   Modules    │
│             │  │   Module     │  │              │
└──────┬───────┘  └──────┬───────┘  └──────────────┘
       │                 │
       └────────┬────────┘
                ▼
┌─────────────────────────────────────────────────────────────┐
│              Shared Services Layer                           │
│  - Celery Workers  - Redis Cache  - S3 Storage               │
│  - PostgreSQL  - Elasticsearch  - LLM APIs                   │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles
1. **Module Independence**: Each module can function standalone
2. **Loose Coupling**: Modules communicate via events and standardized APIs
3. **Multi-Tenancy**: Tenant-scoped data isolation
4. **Extensibility**: Plugin architecture for adding new modules
5. **Scalability**: Clear migration path to microservices

## 📚 Documentation Structure

- `docs/architecture/` - System architecture diagrams
- `docs/uml/` - Use case, class, and sequence diagrams
- `docs/database/` - Database schema and migrations
- `docs/api/` - API specifications (OpenAPI/Swagger)
- `docs/workflows/` - Workflow and integration patterns
- `docs/deployment/` - Deployment and infrastructure guides

## 🚀 Quick Start

### Windows Users (WSL Required)

This project uses Docker and requires WSL on Windows. See [WSL Docker Guide](./WSL_DOCKER_GUIDE.md) for setup.

**Quick setup:**

```powershell
# Use the helper script (recommended)
.\docker.ps1 up --build -d

# Or prefix with wsl
wsl docker-compose up --build -d
```

### Linux/macOS Users

```bash
docker-compose up --build -d
```

### Complete Setup Guide

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed instructions.

## 📖 Additional Documentation

- [Complete Setup Guide](./SETUP_GUIDE.md) - Detailed installation and configuration
- [WSL Docker Guide](./WSL_DOCKER_GUIDE.md) - Windows-specific Docker setup
- [Docker Commands](./DOCKER_COMMANDS.md) - Common Docker operations
- [Quick Start Fix](./QUICK_START_FIX.md) - Troubleshooting and fixes

## 🚀 Quick Start

See [SETUP.md](./SETUP.md) for detailed setup instructions.

## 📄 License

Proprietary - All rights reserved
