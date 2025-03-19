# Park Vision Roles and Requirements

## OpenCV / Backend (2 Members)
### Cooper, Ben
- Implement OpenCV-based spot detection
- Test with webcam in small lot/simulated environment, or with video feeds
- Deliver updates to database/backend, can either implement with Modules/Packages *boo* or JSON deliveries *yay*

## Database / Backend (1 Member)
### <Enter Name>
- Set up a PostgreSQL/MongoDB database
- Build API endpoints for status updates
- Handle spot status logic (occupied/available)
- Generate reports

**Database Tables (Example)**
1. Parking Spots - `spot_id`, `lot_name`, `x_coord`, `y_coord`, `status`, `last_updated`
2. Parking Lots - `lot_id`, `lot_name`, `total_spots`, `available_spots`
3. User Accounts - `user_id`, `username`, `password_hash`, `role`


## Frontend (2 Members)
### Justin, Brant
- Build a React-based dashboard. If you believe React will take too long to learn, implement with Flask or DJango (Python)
- Integrate with backend APIs
- Create a map view of the lot with spot indicators

## Integrators (Everyone)
- Make sure components communicated correctly
- Handle documentation and testing
