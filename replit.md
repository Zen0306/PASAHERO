# JeepTrack PH

## Overview

JeepTrack PH is a real-time jeepney tracking and management system for Batangas, Philippines. The application enables commuters to track jeepney locations in real-time and allows drivers to manage their trips, capacity, and routes. The system supports multiple routes (Balagtas, Alangilan, Balete, Soro-soro, and Lipa) with distinct color coding for easy identification on maps.

## Recent Changes (November 2025)

1. **Persistent Database Storage**: Implemented SQLite database for user data and trip history, replacing in-memory storage
2. **Login System**: Added authentication flows for returning drivers (via license plate) and commuters (via contact number)
3. **Rating & Review System**: Commuters can now rate drivers (1-5 stars) and leave comments; drivers can view their average rating and review history
4. **Trip Analytics Dashboard**: Drivers have access to comprehensive analytics including trip history charts, distance distribution graphs, and performance metrics using Plotly visualizations
5. **Optimized UI**: Reduced driver information popup size on maps for better mobile responsiveness and readability

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with real-time updates
- **Visualization Components**:
  - Folium for interactive mapping with streamlit-folium integration
  - Plotly for analytics dashboards and data visualization
  - PIL for image handling and photo management
- **State Management**: Session-based state management using Streamlit's session_state for user roles (driver/commuter), trip tracking, and UI state
- **Layout**: Wide layout with expandable sidebar for navigation and controls

**Rationale**: Streamlit provides rapid development of data-driven applications with built-in state management, eliminating the need for complex frontend frameworks. The combination of Folium and Plotly offers comprehensive mapping and analytics capabilities.

### Backend Architecture
- **Database Layer**: SQLite with direct Python integration via sqlite3
- **Data Models**:
  - Drivers: Registration, credentials, route assignment, capacity management, location tracking, and performance metrics
  - Commuters: User registration and location tracking
  - Trips: Journey tracking with start/end times, distance, and passenger counts
- **Business Logic**: Modular database operations separated into `database.py`
- **Geospatial Calculations**: GeoPy for distance calculations between coordinates

**Rationale**: SQLite provides a lightweight, serverless database solution suitable for local deployments without requiring external database infrastructure. The schema supports both operational tracking (current trips, locations) and historical analytics (total trips, distances, ratings).

### Data Storage Solutions
- **Primary Database**: SQLite (jeeptrack.db)
- **Schema Design**:
  - Normalized structure with separate tables for drivers, commuters, and trips
  - Foreign key relationships linking trips to drivers
  - BLOB storage for driver photos
  - Timestamp tracking for registration and trip events
  - Aggregated metrics (total trips, distance, ratings) stored denormalized for performance
- **Location Data**: Real-time latitude/longitude coordinates stored for both drivers and commuters
- **Metrics**: Performance tracking including average ratings, total distances, and trip counts

**Alternatives Considered**: PostgreSQL would provide better concurrent access and scalability but adds deployment complexity. MongoDB could handle geospatial queries more efficiently but lacks relational integrity.

**Pros**: Simple deployment, no external dependencies, sufficient for regional tracking application
**Cons**: Limited concurrent write performance, may require migration for large-scale deployment

### Authentication and Authorization
- **Role-Based Access**: Two-tier system (driver vs. commuter)
- **Session Management**: Streamlit session_state for maintaining user context
- **Registration System**: Separate registration flows for drivers (with license verification) and commuters
- **Credential Storage**: License numbers and plate numbers serve as unique identifiers for drivers

**Rationale**: Role-based access separates driver capabilities (trip management, capacity updates) from commuter features (tracking, viewing). Simple session-based auth is appropriate for the current scale without requiring complex JWT or OAuth implementations.

### Route Management
- **Predefined Routes**: Five fixed routes covering Batangas area
- **Color Coding System**: Distinct colors assigned to each route for visual differentiation
- **Center Point**: Batangas City coordinates [13.7565, 121.0583] as map center
- **Route Assignment**: One route per driver, enforced at registration

**Rationale**: Fixed routes simplify the user experience and match the actual jeepney system in Philippines where vehicles operate on established routes.

### Real-time Tracking Features
- **Location Updates**: Continuous tracking of driver coordinates
- **Capacity Management**: Real-time passenger count tracking against maximum capacity
- **Distance Calculation**: Geodesic distance calculations for trip metrics
- **Trip State**: Active trip tracking with start/end timestamps

**Rationale**: Real-time features enable commuters to make informed decisions about wait times and vehicle availability, while helping drivers optimize routes and capacity.

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework and UI components
- **streamlit-folium**: Integration layer for Folium maps in Streamlit
- **folium**: Interactive mapping library for route and location visualization
- **geopy**: Geospatial calculations, specifically geodesic distance measurements
- **pandas**: Data manipulation and analytics data structures
- **plotly**: Interactive charts for analytics dashboards (express and graph_objects)
- **Pillow (PIL)**: Image processing for driver photo uploads

### Database
- **sqlite3**: Built-in Python database interface (no external service required)
- **Database File**: Local storage at `jeeptrack.db`

### Python Standard Library
- **datetime**: Timestamp management for trips and registrations
- **base64**: Image encoding for web display
- **io.BytesIO**: In-memory binary streams for image handling
- **json**: Data serialization (likely for trip route coordinates)
- **os**: File system operations for database path management

### No External Services
The application currently operates as a standalone system without external API integrations, cloud services, or third-party authentication providers. All data is stored locally and all computations are performed in-process.