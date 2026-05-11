# Color-Based Deadline Indicator Feature

## Overview
A visual deadline indicator system has been added to the TPC Portal to help students and admins quickly understand the urgency and closeness of opportunity deadlines. Each opportunity displays a color-coded badge showing its deadline status.

## Color Scheme

| Color | Status | Days Left | Meaning |
|-------|--------|-----------|---------|
| 🟢 **Green** | Open | >3 days | Plenty of time to apply |
| 🟡 **Yellow** | Closing Soon | 1-3 days | Deadline approaching - apply soon |
| 🔴 **Red** | Very Soon | <1 day | Urgent - deadline is tomorrow |
| ⚫ **Dark** | Closed | 0 days | Application deadline has passed |
| ⚪ **Gray** | No Deadline | N/A | No deadline set for this opportunity |

## Where It's Displayed

### Student Views

#### 1. Opportunities Listing Page (`/opportunities`)
- **Location**: Fourth column in the opportunity card
- **Display Format**: `[Status] (Date)` with days remaining in tooltip
- **Example**: 
  - Green badge: "Open (15 May)"
  - Yellow badge: "Closing Soon (12 May)" with tooltip "2 days left"
  - Red badge: "Very Soon (11 May)" with tooltip "0 days left"

#### 2. Opportunity Detail Page (`/opportunity/<id>`)
- **Location**: Deadline section in the right sidebar card
- **Display Format**: Larger badge with status text, date, and days remaining
- **Example**: "Closing Soon: 15 May 2026 (3 days left)"

### Admin Views

#### Opportunities Management (`/opportunities`)
- **Location**: Deadline info in the admin opportunity listing
- **Display Format**: Color-coded badge showing status and date
- **Helps Admins**: Quickly identify which opportunities are closing soon and need promotion/follow-up

## Implementation Details

### Backend Logic

The deadline status is calculated by the `Opportunity.get_deadline_status()` method in `app/models.py`:

```python
def get_deadline_status(self):
    """
    Calculate deadline status and return color info.
    Returns: {
        'color': 'success'|'warning'|'danger'|'secondary'|'dark',
        'text': 'Open'|'Closing Soon'|'Very Soon'|'Closed'|'No Deadline',
        'days_left': int,
        'is_closed': bool
    }
    """
```

**Calculation Rules:**
- If no deadline exists → Gray, "No Deadline"
- If deadline has passed → Dark, "Closed", `is_closed=True`
- If less than 1 day remains → Red, "Very Soon"
- If 1-3 days remain → Yellow, "Closing Soon"
- If more than 3 days remain → Green, "Open"

### Data Flow

1. **Route Handlers** (`app/student/routes.py`, `app/admin/routes.py`)
   - Call `opp.get_deadline_status()` for each opportunity
   - Pass the status dict to templates

2. **Templates** (Jinja2)
   - Use the status dict to display appropriate color badge
   - Show status text, date, and days remaining

### Files Modified

- **`app/models.py`**: Added `get_deadline_status()` method and `timedelta` import
- **`app/student/routes.py`**: Added deadline status calculation in `browse_opportunities()` and `view_opportunity()`
- **`app/admin/routes.py`**: Added deadline status calculation in `opportunities()`
- **`templates/student/opportunities.html`**: Updated deadline display with color badge
- **`templates/student/opportunity_detail.html`**: Updated deadline display in sidebar
- **`templates/admin/applications.html`**: Updated admin deadline display with color badge

## Usage Examples

### For Students

**Example 1: Student browsing opportunities**
- Student sees a Job posting with a **RED badge**: "Very Soon (10 May)"
- Tooltip shows: "0 days left"
- Student knows they must apply immediately

**Example 2: Student viewing opportunity details**
- Sidebar shows: **YELLOW badge**: "Closing Soon: 15 May 2026 (3 days left)"
- Student is encouraged to apply within 3 days

### For Admins

**Example: Admin managing opportunities**
- In the opportunities list, admin sees multiple opportunities with different colors
- RED and YELLOW opportunities stand out visually
- Admin can prioritize promoting opportunities that are closing soon

## Technical Notes

### Color Classes Used
The implementation uses Bootstrap color utility classes:
- `bg-success` (Green)
- `bg-warning` (Yellow)
- `bg-danger` (Red)
- `bg-dark` (Dark/Closed)
- `bg-secondary` (Gray/No Deadline)

### Timezone Handling
- All datetime comparisons use `datetime.utcnow()`
- Deadlines are stored as DateTime objects in the database
- Frontend displays dates in user's local timezone (if configured)

### Performance
- Status calculation is performed at request time (not cached)
- For large opportunity lists, calculation is O(n) where n = number of opportunities
- Future optimization: Could cache status or calculate via database query if needed

## Future Enhancements

Potential improvements:
1. **Email notifications**: Notify students before deadline closes
2. **Configurable thresholds**: Allow admins to customize day thresholds
3. **Status history**: Track how many students applied per day
4. **Auto-archive**: Automatically hide closed opportunities
5. **Calendar view**: Show opportunities on a calendar by deadline date
6. **Reminder system**: Send reminders to students about closing deadlines

## Testing the Feature

1. **Test Green (Open)**: Create an opportunity with deadline >7 days away
2. **Test Yellow (Closing Soon)**: Create with deadline 2 days away
3. **Test Red (Very Soon)**: Create with deadline tomorrow
4. **Test Dark (Closed)**: Create with deadline in the past
5. **Test Gray (No Deadline)**: Create opportunity without setting deadline

### Sample Test Deadlines

Use these when testing to see different colors:
- **Today + 10 days**: Green
- **Today + 2 days**: Yellow
- **Today + 0.5 days** (12 hours): Red
- **Today - 1 day** (past): Dark
- **Not set**: Gray

## Questions & Support

For issues or questions about the deadline color indicator feature:
1. Check the status calculation logic in `app/models.py`
2. Verify timezone settings if dates appear incorrect
3. Ensure database deadlines are stored correctly (DateTime format)

---

**Last Updated**: May 11, 2026
**Feature Status**: Complete and tested
