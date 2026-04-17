"""Interactive documentation app for Dash Mantine DataTable.

This module doubles as a local sandbox and a curated example gallery. Each
section is designed to be copy-paste friendly for Dash users while still
showing how the wrapper extends Mantine DataTable with Dash-native patterns
such as callback payloads, selector rules, chainable update helpers, and
component-based templates.
"""

import json
import os
from copy import deepcopy
from datetime import date, datetime

import dash_mantine_components as dmc
import dash_mantine_datatable as dmdt
from dash import ALL, Dash, Input, Output, State, callback, callback_context, dcc, html, no_update
from dash_iconify import DashIconify as _DashIconifyComponent


USE_LIVE_ICONIFY = os.environ.get("DMDT_USAGE_ENABLE_ICONIFY", "").strip() == "1"
USE_FULL_RUNTIME_DEMOS = (
    os.environ.get("DMDT_USAGE_ENABLE_FULL_RUNTIME_DEMOS", "").strip() == "1"
)


def DashIconify(*args, **kwargs):
    """Return a safe live icon placeholder unless iconify is explicitly enabled."""

    if USE_LIVE_ICONIFY:
        return _DashIconifyComponent(*args, **kwargs)

    icon_name = kwargs.get("icon")
    if not icon_name and args:
        icon_name = args[0]

    token = str(icon_name or "icon").split(":")[-1].replace("-", " ").strip()
    label = (token[:1] or "I").upper()
    width = kwargs.get("width", 16)
    color = kwargs.get("color", "var(--mantine-color-gray-6)")

    return html.Span(
        label,
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "justifyContent": "center",
            "width": f"{int(width)}px" if isinstance(width, (int, float)) else str(width),
            "height": f"{int(width)}px" if isinstance(width, (int, float)) else str(width),
            "border": f"1px solid {color}",
            "borderRadius": "999px",
            "color": color,
            "fontSize": "0.7rem",
            "fontWeight": 700,
            "lineHeight": 1,
            "boxSizing": "border-box",
        },
    )


EMPLOYEES = [
    {
        "id": 1,
        "name": "Avery Stone",
        "team": "Platform",
        "role": "Senior Engineer",
        "location": "Berlin",
        "salary": 128000,
        "startDate": "2021-03-15",
        "deliveryScore": 91,
        "status": "On Track",
        "statusColor": "green",
        "profileUrl": "https://example.com/avery",
        "bio": "Owns the deployment pipeline and release tooling.",
    },
    {
        "id": 2,
        "name": "Mina Patel",
        "team": "Growth",
        "role": "Product Designer",
        "location": "London",
        "salary": 112000,
        "startDate": "2022-01-10",
        "deliveryScore": 84,
        "status": "Planning",
        "statusColor": "blue",
        "profileUrl": "https://example.com/mina",
        "bio": "Leads onboarding and activation UX work.",
    },
    {
        "id": 3,
        "name": "Jonah Kim",
        "team": "Platform",
        "role": "Data Engineer",
        "location": "Toronto",
        "salary": 118500,
        "startDate": "2020-09-07",
        "deliveryScore": 88,
        "status": "On Track",
        "statusColor": "green",
        "profileUrl": "https://example.com/jonah",
        "bio": "Maintains analytics models and warehouse ingestion.",
    },
    {
        "id": 4,
        "name": "Nora Diaz",
        "team": "Operations",
        "role": "Program Manager",
        "location": "Madrid",
        "salary": 105000,
        "startDate": "2019-11-18",
        "deliveryScore": 77,
        "status": "Needs Review",
        "statusColor": "orange",
        "profileUrl": "https://example.com/nora",
        "bio": "Coordinates launches and cross-team dependencies.",
    },
    {
        "id": 5,
        "name": "Leo Andersen",
        "team": "Growth",
        "role": "Full Stack Engineer",
        "location": "Copenhagen",
        "salary": 121000,
        "startDate": "2023-02-13",
        "deliveryScore": 93,
        "status": "On Track",
        "statusColor": "green",
        "profileUrl": "https://example.com/leo",
        "bio": "Builds experiments and conversion reporting.",
    },
    {
        "id": 6,
        "name": "Priya Shah",
        "team": "Support",
        "role": "Knowledge Lead",
        "location": "Dublin",
        "salary": 98000,
        "startDate": "2021-06-28",
        "deliveryScore": 81,
        "status": "Planning",
        "statusColor": "blue",
        "profileUrl": "https://example.com/priya",
        "bio": "Owns support docs and escalation patterns.",
    },
    {
        "id": 7,
        "name": "Cam Ross",
        "team": "Security",
        "role": "Security Engineer",
        "location": "Edinburgh",
        "salary": 134000,
        "startDate": "2018-05-21",
        "deliveryScore": 96,
        "status": "On Track",
        "statusColor": "green",
        "profileUrl": "https://example.com/cam",
        "bio": "Runs audits, threat modeling, and incident prep.",
    },
    {
        "id": 8,
        "name": "Iris Novak",
        "team": "Operations",
        "role": "Analyst",
        "location": "Prague",
        "salary": 91000,
        "startDate": "2024-01-08",
        "deliveryScore": 72,
        "status": "Needs Review",
        "statusColor": "orange",
        "profileUrl": "https://example.com/iris",
        "bio": "Tracks delivery metrics and staffing trends.",
    },
    {
        "id": 9,
        "name": "Ethan Brooks",
        "team": "Platform",
        "role": "SRE",
        "location": "Austin",
        "salary": 129500,
        "startDate": "2022-08-01",
        "deliveryScore": 87,
        "status": "On Track",
        "statusColor": "green",
        "profileUrl": "https://example.com/ethan",
        "bio": "Improves uptime, observability, and autoscaling.",
    },
    {
        "id": 10,
        "name": "Sofia Marin",
        "team": "Growth",
        "role": "Content Strategist",
        "location": "Lisbon",
        "salary": 97000,
        "startDate": "2020-04-06",
        "deliveryScore": 79,
        "status": "Planning",
        "statusColor": "blue",
        "profileUrl": "https://example.com/sofia",
        "bio": "Shapes campaign messaging and landing page copy.",
    },
]


OVERVIEW_COLUMNS = [
    {"accessor": "name", "sortable": True},
    {"accessor": "team", "sortable": True},
    {"accessor": "role"},
    {
        "accessor": "salary",
        "presentation": "currency",
        "currency": "USD",
        "textAlign": "right",
    },
    {"accessor": "deliveryScore", "title": "Delivery", "presentation": "progress"},
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
    },
    {
        "accessor": "profileUrl",
        "title": "Profile",
        "presentation": "link",
        "hrefAccessor": "profileUrl",
        "template": "Open",
    },
]

ADVANCED_CONTROLS_COLUMNS = [
    {"accessor": "name", "sortable": True},
    {"accessor": "team", "sortable": True},
    {"accessor": "role"},
    {"accessor": "location", "sortable": True},
    {
        "accessor": "deliveryScore",
        "title": "Delivery",
        "presentation": "progress",
    },
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
        "sortable": True,
    },
]

TABLE_PROPERTIES_COLUMNS = [
    {"accessor": "name", "sortable": True},
    {"accessor": "role"},
    {
        "accessor": "bio",
        "title": "Mission statement",
        "width": 320,
    },
    {"accessor": "location", "title": "City"},
    {"accessor": "team", "title": "Team"},
]

TABLE_PROPERTIES_DEFAULTS = {
    "withRowBorders": True,
    "withColumnBorders": False,
    "striped": False,
    "highlightOnHover": False,
    "withTableBorder": False,
    "noHeader": False,
    "shadow": None,
    "horizontalSpacing": "lg",
    "verticalSpacing": None,
    "fontSize": None,
    "borderRadius": None,
    "verticalAlign": None,
}

TABLE_SIZE_OPTIONS = ["xs", "sm", "md", "lg", "xl"]
TABLE_ALIGN_OPTIONS = ["top", "center", "bottom"]
STATES_DEMO_COLUMNS = OVERVIEW_COLUMNS[:4]
STATES_VIEW_OPTIONS = [
    {"label": "Loaded", "value": "loaded"},
    {"label": "Loading", "value": "loading"},
    {"label": "Empty", "value": "empty"},
]
STATES_LOADER_TYPES = [
    {"label": "Oval", "value": "oval"},
    {"label": "Bars", "value": "bars"},
    {"label": "Dots", "value": "dots"},
]
STATES_COLOR_OPTIONS = [
    {"label": "Blue", "value": "blue"},
    {"label": "Green", "value": "green"},
    {"label": "Grape", "value": "grape"},
    {"label": "Orange", "value": "orange"},
]
STATES_DEMO_DEFAULTS = {
    "state_mode": "loading",
    "loader_type": "oval",
    "loader_color": "blue",
    "loader_size": "md",
    "loader_blur": 2,
    "empty_text": "No employees found",
    "table_min_height": 220,
}
TABLE_PROPERTIES_VISUAL_STYLE = {
    "--mantine-datatable-striped-color-light": "#fff3bf",
    "--mantine-datatable-striped-color-dark": "#5c4500",
    "--mantine-datatable-highlight-on-hover-color-light": "#d0ebff",
    "--mantine-datatable-highlight-on-hover-color-dark": "#1c3f5e",
}

COLUMN_PROPERTIES_RECORDS = EMPLOYEES[:5]
COLUMN_PROPERTIES_TRENDS = {
    1: [74, 79, 83, 81, 88, 91],
    2: [62, 68, 72, 76, 80, 84],
    3: [70, 75, 77, 82, 85, 88],
    4: [55, 61, 66, 70, 73, 77],
    5: [71, 78, 82, 86, 89, 93],
}
COLUMN_PROPERTIES_RECORDS = [
    {
        **record,
        "trend": COLUMN_PROPERTIES_TRENDS[record["id"]],
        "actions": True,
    }
    for record in COLUMN_PROPERTIES_RECORDS
]
COLUMN_PROPERTIES_BASE_COLUMNS = [
    {"accessor": "name"},
    {"accessor": "role"},
    {"accessor": "bio"},
    {"accessor": "salary"},
    {"accessor": "deliveryScore"},
    {"accessor": "trend"},
    {"accessor": "status"},
    {"accessor": "actions"},
]
COLUMN_PROPERTIES_AVERAGE_SALARY = round(
    sum(record["salary"] for record in COLUMN_PROPERTIES_RECORDS)
    / len(COLUMN_PROPERTIES_RECORDS)
)
GROUP_COLUMNS_RECORDS = EMPLOYEES[:6]
GROUP_COLUMNS_BASE_COLUMNS = [
    {"accessor": "name", "title": "Employee", "width": 180},
    {"accessor": "role", "width": 200},
    {"accessor": "team", "width": 140},
    {"accessor": "location", "title": "City", "width": 130},
    {
        "accessor": "salary",
        "title": "Annual salary",
        "presentation": "currency",
        "currency": "USD",
        "textAlign": "right",
        "width": 140,
    },
    {
        "accessor": "deliveryScore",
        "title": "Delivery",
        "presentation": "progress",
        "width": 140,
    },
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
        "width": 120,
    },
]
ROW_ACTIONS = [
    {
        "action": "save-row",
        "label": "Save",
        "color": "green",
        "icon": "tabler:device-floppy",
    },
    {
        "action": "edit-row",
        "label": "Edit",
        "color": "blue",
        "icon": "tabler:pencil",
    },
    {
        "action": "delete-row",
        "label": "Delete",
        "color": "red",
        "icon": "tabler:trash",
    },
]
ROW_PROPERTIES_RECORDS = EMPLOYEES[:6]
ROW_PROPERTIES_COLUMNS = [
    {"accessor": "name", "width": 180},
    {"accessor": "team", "width": 140},
    {"accessor": "location", "title": "City", "width": 140},
    {
        "accessor": "deliveryScore",
        "title": "Delivery",
        "presentation": "progress",
        "width": 140,
    },
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
        "width": 140,
    },
]
ROW_IDS_RECORDS = [
    {
        "name": record["name"],
        "team": record["team"],
        "location": record["location"],
        "status": record["status"],
        "statusColor": record["statusColor"],
        "profile": {
            "slug": f'{record["team"].lower().replace(" ", "-")}:{record["name"].lower().replace(" ", "-")}'
        },
    }
    for record in EMPLOYEES[:5]
]
INTERACTIVITY_RECORDS = EMPLOYEES[:6]
INTERACTIVITY_COLUMNS = [
    {"accessor": "name", "title": "Employee", "width": 180},
    {"accessor": "team", "width": 140},
    {"accessor": "role", "width": 220},
    {"accessor": "location", "title": "City", "width": 140},
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
        "width": 140,
    },
]
RTL_RECORDS = EMPLOYEES[:6]
RTL_COLUMNS = [
    {"accessor": "name", "title": "Employee", "width": 180},
    {"accessor": "team", "width": 140},
    {"accessor": "role", "width": 220},
    {"accessor": "location", "title": "City", "width": 140},
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
        "width": 140,
    },
]
INLINE_EDIT_CATEGORY_OPTIONS = [
    {"value": "Draft", "label": "Draft"},
    {"value": "Review", "label": "In Review"},
    {"value": "Approved", "label": "Approved"},
]
INLINE_EDIT_TAG_OPTIONS = [
    "Backend",
    "Frontend",
    "Analytics",
    "Mentoring",
    "Docs",
]
INLINE_EDIT_RECORDS = [
    {
        "id": 1,
        "name": "Avery Stone",
        "category": "Review",
        "tags": ["Backend", "Mentoring"],
        "reviewDate": "2026-04-07",
        "adjustment": 2,
    },
    {
        "id": 2,
        "name": "Mina Patel",
        "category": "Draft",
        "tags": ["Frontend", "Docs"],
        "reviewDate": "2026-04-09",
        "adjustment": -1,
    },
    {
        "id": 3,
        "name": "Jonah Kim",
        "category": "Approved",
        "tags": ["Analytics", "Backend"],
        "reviewDate": "2026-04-11",
        "adjustment": 4,
    },
    {
        "id": 4,
        "name": "Nora Diaz",
        "category": "Review",
        "tags": ["Docs", "Mentoring"],
        "reviewDate": "2026-04-15",
        "adjustment": 1,
    },
]
INLINE_EDITABLE_ACCESSORS = (
    "name",
    "category",
    "tags",
    "reviewDate",
    "adjustment",
)
COLUMN_CUSTOMIZATION_RECORDS = EMPLOYEES[:6]
COLUMN_CUSTOMIZATION_COLUMNS = [
    {"accessor": "name", "title": "Employee", "width": 180},
    {"accessor": "team", "width": 140},
    {"accessor": "role", "width": 220},
    {"accessor": "location", "title": "City", "width": 140},
    {
        "accessor": "salary",
        "title": "Annual salary",
        "presentation": "currency",
        "currency": "USD",
        "textAlign": "right",
        "width": 150,
    },
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
        "width": 130,
    },
]
COLUMN_FILTERING_BASE_COLUMNS = [
    {"accessor": "name", "title": "Employee", "sortable": True},
    {"accessor": "team", "sortable": True},
    {
        "accessor": "startDate",
        "title": "Start date",
        "presentation": "date",
        "sortable": True,
    },
    {
        "accessor": "deliveryScore",
        "title": "Delivery",
        "presentation": "progress",
        "sortable": True,
    },
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
    },
]
COLUMN_FILTERING_TEAM_OPTIONS = sorted({record["team"] for record in EMPLOYEES})
COLUMN_FILTERING_STATUS_OPTIONS = ["all"] + sorted(
    {record["status"] for record in EMPLOYEES}
)
COLUMN_FILTERING_DEFAULT_SCORE_RANGE = [
    min(record["deliveryScore"] for record in EMPLOYEES),
    max(record["deliveryScore"] for record in EMPLOYEES),
]


def repeat_employees(cycles, *, include_batch_suffix=False):
    repeated = []
    total_per_cycle = len(EMPLOYEES)

    for cycle in range(cycles):
        for index, employee in enumerate(EMPLOYEES, start=1):
            repeated.append(
                {
                    **employee,
                    "id": cycle * total_per_cycle + index,
                    "cohort": f"Batch {cycle + 1}",
                    "name": (
                        f'{employee["name"]} ({cycle + 1})'
                        if include_batch_suffix
                        else employee["name"]
                    ),
                }
            )

    return repeated


SCROLLING_RECORDS = repeat_employees(3, include_batch_suffix=True)
SCROLLING_COLUMNS = [
    {"accessor": "name", "width": 220},
    {"accessor": "team", "width": 140},
    {"accessor": "role", "width": 220},
    {"accessor": "location", "title": "City", "width": 140},
    {"accessor": "cohort", "width": 120},
]
ROW_DRAGGING_RECORDS = EMPLOYEES[:6]
ROW_DRAGGING_COLUMNS = [
    {"accessor": "name", "title": "Employee", "width": 220},
    {"accessor": "team", "width": 140},
    {"accessor": "role", "width": 220},
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
        "width": 140,
    },
]
INFINITE_SCROLL_RECORDS = repeat_employees(5, include_batch_suffix=True)
INFINITE_SCROLL_COLUMNS = [
    {"accessor": "name", "width": 220},
    {"accessor": "team", "width": 140},
    {"accessor": "location", "title": "City", "width": 140},
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
        "width": 140,
    },
    {"accessor": "cohort", "width": 120},
]
INFINITE_SCROLL_BATCH_SIZE = 12
EXPANDING_ROWS_COLUMNS = [
    {"accessor": "name", "sortable": True},
    {"accessor": "team", "sortable": True},
    {"accessor": "role"},
    {
        "accessor": "status",
        "presentation": "badge",
        "badgeColorAccessor": "statusColor",
    },
]
NESTED_COMPANY_COLUMNS = [
    {
        "accessor": "name",
        "title": "Company / Department / Employee",
        "width": 360,
    },
    {
        "accessor": "employees",
        "title": "Employees / Birth date",
        "textAlign": "right",
        "width": 200,
    },
]
NESTED_DEPARTMENT_COLUMNS = [
    {"accessor": "name", "width": 360},
    {"accessor": "employees", "textAlign": "right", "width": 200},
]
NESTED_EMPLOYEE_COLUMNS = [
    {"accessor": "name", "width": 360},
    {
        "accessor": "birthDate",
        "title": "Birth date",
        "presentation": "date",
        "textAlign": "right",
        "width": 200,
    },
]
NESTED_GROUPED_COLUMNS = [
    {
        "accessor": "employeeLabel",
        "title": "Company / Department / Employee",
        "width": 360,
    },
    {"accessor": "role", "width": 200},
    {"accessor": "location", "title": "City", "width": 140},
    {
        "accessor": "birthDate",
        "title": "Birth date",
        "presentation": "date",
        "textAlign": "right",
        "width": 200,
    },
]
NESTED_GROUP_AGGREGATIONS = {
    "role": "lambda values, records: `${records.length} employees`",
    "birthDate": "min",
}
NESTED_COMPANIES = [
    {
        "id": "northwind",
        "name": "Northwind Labs",
        "location": "Berlin",
        "industry": "SaaS",
        "departments": 2,
        "employees": 4,
    },
    {
        "id": "aperture",
        "name": "Aperture Analytics",
        "location": "Amsterdam",
        "industry": "Data",
        "departments": 2,
        "employees": 4,
    },
    {
        "id": "summit",
        "name": "Summit Support",
        "location": "Dublin",
        "industry": "Operations",
        "departments": 2,
        "employees": 4,
    },
]
NESTED_DEPARTMENTS = [
    {
        "id": "northwind-platform",
        "companyId": "northwind",
        "name": "Platform",
        "lead": "Avery Stone",
        "employees": 2,
        "budget": 420000,
    },
    {
        "id": "northwind-growth",
        "companyId": "northwind",
        "name": "Growth",
        "lead": "Mina Patel",
        "employees": 2,
        "budget": 275000,
    },
    {
        "id": "aperture-data",
        "companyId": "aperture",
        "name": "Data",
        "lead": "Jonah Kim",
        "employees": 2,
        "budget": 365000,
    },
    {
        "id": "aperture-sales",
        "companyId": "aperture",
        "name": "Sales",
        "lead": "Sofia Marin",
        "employees": 2,
        "budget": 310000,
    },
    {
        "id": "summit-support",
        "companyId": "summit",
        "name": "Support",
        "lead": "Priya Shah",
        "employees": 2,
        "budget": 240000,
    },
    {
        "id": "summit-ops",
        "companyId": "summit",
        "name": "Operations",
        "lead": "Nora Diaz",
        "employees": 2,
        "budget": 295000,
    },
]
NESTED_EMPLOYEES = [
    {
        "id": "northwind-platform-1",
        "companyId": "northwind",
        "departmentId": "northwind-platform",
        "name": "Avery Stone",
        "role": "Senior Engineer",
        "location": "Berlin",
        "birthDate": "1990-04-12",
    },
    {
        "id": "northwind-platform-2",
        "companyId": "northwind",
        "departmentId": "northwind-platform",
        "name": "Ethan Brooks",
        "role": "SRE",
        "location": "Austin",
        "birthDate": "1992-09-03",
    },
    {
        "id": "northwind-growth-1",
        "companyId": "northwind",
        "departmentId": "northwind-growth",
        "name": "Mina Patel",
        "role": "Product Designer",
        "location": "London",
        "birthDate": "1994-02-18",
    },
    {
        "id": "northwind-growth-2",
        "companyId": "northwind",
        "departmentId": "northwind-growth",
        "name": "Leo Andersen",
        "role": "Full Stack Engineer",
        "location": "Copenhagen",
        "birthDate": "1996-07-29",
    },
    {
        "id": "aperture-data-1",
        "companyId": "aperture",
        "departmentId": "aperture-data",
        "name": "Jonah Kim",
        "role": "Data Engineer",
        "location": "Toronto",
        "birthDate": "1989-11-06",
    },
    {
        "id": "aperture-data-2",
        "companyId": "aperture",
        "departmentId": "aperture-data",
        "name": "Iris Novak",
        "role": "Analyst",
        "location": "Prague",
        "birthDate": "1998-01-22",
    },
    {
        "id": "aperture-sales-1",
        "companyId": "aperture",
        "departmentId": "aperture-sales",
        "name": "Sofia Marin",
        "role": "Content Strategist",
        "location": "Lisbon",
        "birthDate": "1991-05-14",
    },
    {
        "id": "aperture-sales-2",
        "companyId": "aperture",
        "departmentId": "aperture-sales",
        "name": "Cam Ross",
        "role": "Solutions Engineer",
        "location": "Edinburgh",
        "birthDate": "1988-12-01",
    },
    {
        "id": "summit-support-1",
        "companyId": "summit",
        "departmentId": "summit-support",
        "name": "Priya Shah",
        "role": "Knowledge Lead",
        "location": "Dublin",
        "birthDate": "1993-03-27",
    },
    {
        "id": "summit-support-2",
        "companyId": "summit",
        "departmentId": "summit-support",
        "name": "Iris Hale",
        "role": "Support Engineer",
        "location": "Glasgow",
        "birthDate": "1997-08-09",
    },
    {
        "id": "summit-ops-1",
        "companyId": "summit",
        "departmentId": "summit-ops",
        "name": "Nora Diaz",
        "role": "Program Manager",
        "location": "Madrid",
        "birthDate": "1987-06-16",
    },
    {
        "id": "summit-ops-2",
        "companyId": "summit",
        "departmentId": "summit-ops",
        "name": "Owen Hart",
        "role": "Operations Analyst",
        "location": "Manchester",
        "birthDate": "1995-10-31",
    },
]
COMPANY_NAMES_BY_ID = {
    company["id"]: company["name"] for company in NESTED_COMPANIES
}
DEPARTMENT_NAMES_BY_ID = {
    department["id"]: department["name"] for department in NESTED_DEPARTMENTS
}
NESTED_GROUPED_RECORDS = [
    {
        **employee,
        "companyGroup": COMPANY_NAMES_BY_ID.get(employee["companyId"], ""),
        "departmentGroup": DEPARTMENT_NAMES_BY_ID.get(
            employee["departmentId"], ""
        ),
        "employeeLabel": employee["name"],
    }
    for employee in NESTED_EMPLOYEES
]
DEPARTMENTS_BY_COMPANY = {
    company["id"]: [
        department
        for department in NESTED_DEPARTMENTS
        if department["companyId"] == company["id"]
    ]
    for company in NESTED_COMPANIES
}
EMPLOYEES_BY_DEPARTMENT = {
    department["id"]: [
        employee
        for employee in NESTED_EMPLOYEES
        if employee["departmentId"] == department["id"]
    ]
    for department in NESTED_DEPARTMENTS
}
NESTED_DEPARTMENTS = [
    {
        **department,
        "employeesData": EMPLOYEES_BY_DEPARTMENT.get(department["id"], []),
    }
    for department in NESTED_DEPARTMENTS
]
DEPARTMENTS_BY_COMPANY = {
    company["id"]: [
        department
        for department in NESTED_DEPARTMENTS
        if department["companyId"] == company["id"]
    ]
    for company in NESTED_COMPANIES
}
NESTED_COMPANIES = [
    {
        **company,
        "departmentsData": DEPARTMENTS_BY_COMPANY.get(company["id"], []),
    }
    for company in NESTED_COMPANIES
]


def build_async_employee_record(employee):
    return {
        **deepcopy(employee),
        "employeeLabel": employee["name"],
    }


def build_async_department_record(department):
    return {
        key: deepcopy(value)
        for key, value in department.items()
        if key != "employeesData"
    } | {
        "employeeLabel": department["name"],
        "role": "Expand to load employees",
        "location": "",
        "birthDate": None,
        "childrenData": [],
        "childrenLoaded": False,
        "childrenLoading": False,
        "nodeType": "department",
    }


def build_async_company_record(company):
    return {
        key: deepcopy(value)
        for key, value in company.items()
        if key != "departmentsData"
    } | {
        "employeeLabel": company["name"],
        "role": "Expand to load departments",
        "birthDate": None,
        "childrenData": [],
        "childrenLoaded": False,
        "childrenLoading": False,
        "nodeType": "company",
    }


def build_async_nested_company_records():
    return [build_async_company_record(company) for company in NESTED_COMPANIES]


def iter_async_nested_rows(rows):
    for row in rows or []:
        yield row
        yield from iter_async_nested_rows(row.get("childrenData") or [])


SECTION_LINKS = [
    ("section-basic", "1. Basic formatting"),
    ("section-selection", "2. Client-side selection"),
    ("section-expansion", "3. Row expansion and nesting"),
    ("section-server", "4. Server pagination"),
    ("section-states", "5. Empty and loading"),
    ("section-scrolling", "6. Fixed-height scrolling"),
    ("section-infinite-scroll", "7. Infinite scrolling"),
    ("section-table-props", "8. Table properties"),
    ("section-column-props", "9. Column properties"),
    ("section-column-filtering", "10. Column searching and filtering"),
    ("section-column-dragging", "11. Column dragging and toggling"),
    ("section-column-resizing", "12. Column resizing"),
    ("section-grouping", "13. Column grouping"),
    ("section-row-props", "14. Row properties"),
    ("section-row-dragging", "15. Row dragging"),
    ("section-row-ids", "16. Row IDs"),
    ("section-interactivity", "17. Interactivity"),
    ("section-rtl", "18. RTL support"),
    ("section-advanced-controls", "19. Advanced selection and pagination"),
    ("section-custom-components", "20. Custom loaders and empty icons"),
]

CATEGORY_LINK_GROUPS = [
    (
        "Core workflows",
        "Start with the essential table patterns most Dash apps need first.",
        [
            ("section-basic", "1. Basic formatting"),
            ("section-selection", "2. Client-side selection"),
            ("section-expansion", "3. Row expansion and nesting"),
            ("section-server", "4. Server pagination"),
        ],
    ),
    (
        "States and layout",
        "Examples for loading, empty states, scrolling, sizing, and direction.",
        [
            ("section-states", "5. Empty and loading"),
            ("section-scrolling", "6. Fixed-height scrolling"),
            ("section-infinite-scroll", "7. Infinite scrolling"),
            ("section-table-props", "8. Table properties"),
            ("section-rtl", "18. RTL support"),
        ],
    ),
    (
        "Columns and structure",
        "Examples focused on columns, grouped headers, filters, and persistence.",
        [
            ("section-column-props", "9. Column properties"),
            ("section-column-filtering", "10. Column searching and filtering"),
            ("section-column-dragging", "11. Column dragging and toggling"),
            ("section-column-resizing", "12. Column resizing"),
            ("section-grouping", "13. Column grouping"),
        ],
    ),
    (
        "Rows and interaction",
        "Row-level styling, IDs, drag-and-drop, callbacks, and editing.",
        [
            ("section-row-props", "14. Row properties"),
            ("section-row-dragging", "15. Row dragging"),
            ("section-row-ids", "16. Row IDs"),
            ("section-interactivity", "17. Interactivity"),
        ],
    ),
    (
        "Advanced patterns",
        "Newer helper APIs and highly customized state presentation.",
        [
            ("section-advanced-controls", "19. Advanced selection and pagination"),
            ("section-custom-components", "20. Custom loaders and empty icons"),
        ],
    ),
]


def format_payload(payload):
    if not payload:
        return "Interact with the table to see callback payloads."
    return json.dumps(payload, indent=2)


def strip_inline_edit_metadata(records):
    cleaned = []
    for record in records or []:
        cleaned.append(
            {
                key: value
                for key, value in record.items()
                if not key.startswith("_edit_")
            }
        )
    return cleaned


def record_ids_match(left, right):
    return str(left) == str(right)


def get_inline_edit_adjustment_color(value):
    if value is None:
        return "gray"
    if value < 0:
        return "red"
    if value <= 2:
        return "yellow"
    return "green"


def decorate_inline_edit_records(records, active_cell=None):
    decorated = []
    base_records = strip_inline_edit_metadata(records)

    for record in base_records:
        next_record = dict(record)
        next_record["_edit_tags_label"] = ", ".join(record.get("tags") or []) or "None"
        next_record["_edit_reviewDate_label"] = record.get("reviewDate") or "Pick a date"
        next_record["_edit_adjustment_color"] = get_inline_edit_adjustment_color(
            record.get("adjustment")
        )

        decorated.append(next_record)

    return decorated


def find_inline_edit_record(records, row_id):
    for record in strip_inline_edit_metadata(records):
        if record_ids_match(record.get("id"), row_id):
            return record
    return None


def filter_and_sort(records, query, sort_status):
    query = (query or "").strip().lower()
    filtered = [
        record
        for record in records
        if not query
        or query in record["name"].lower()
        or query in record["team"].lower()
        or query in record["role"].lower()
        or query in record["location"].lower()
    ]

    if sort_status and sort_status.get("columnAccessor"):
        accessor = sort_status.get("sortKey") or sort_status["columnAccessor"]
        reverse = sort_status.get("direction") == "desc"
        filtered = sorted(filtered, key=lambda row: row.get(accessor), reverse=reverse)

    return filtered


def parse_date_value(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None

    return None


def normalize_date_range(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None, None

    return parse_date_value(value[0]), parse_date_value(value[1])


def normalize_score_range(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return list(COLUMN_FILTERING_DEFAULT_SCORE_RANGE)

    lower = int(value[0])
    upper = int(value[1])
    return [min(lower, upper), max(lower, upper)]


def filter_column_search_records(
    records,
    name_query="",
    selected_teams=None,
    start_date_range=None,
    score_range=None,
    selected_status="all",
):
    normalized_name_query = (name_query or "").strip().lower()
    normalized_teams = set(selected_teams or [])
    start_date, end_date = normalize_date_range(start_date_range)
    minimum_score, maximum_score = normalize_score_range(score_range)
    normalized_status = (selected_status or "all").strip()

    filtered = []
    for record in records:
        if (
            normalized_name_query
            and normalized_name_query not in record["name"].lower()
        ):
            continue

        if normalized_teams and record["team"] not in normalized_teams:
            continue

        record_start_date = parse_date_value(record.get("startDate"))
        if start_date and (
            record_start_date is None or record_start_date < start_date
        ):
            continue

        if end_date and (record_start_date is None or record_start_date > end_date):
            continue

        delivery_score = int(record.get("deliveryScore") or 0)
        if delivery_score < minimum_score or delivery_score > maximum_score:
            continue

        if normalized_status != "all" and record["status"] != normalized_status:
            continue

        filtered.append(record)

    return filtered


def resolve_optional_value(enabled, value):
    return value if enabled else None


def format_table_property_value(value):
    if isinstance(value, str):
        return f'"{value}"'
    return repr(value)


def format_infinite_scroll_status(records):
    shown = len(records or [])
    total = len(INFINITE_SCROLL_RECORDS)
    suffix = ", scroll to bottom to load more" if shown < total else ""
    return f"Showing {shown} records of {total}{suffix}"


def normalize_inline_edit_value(accessor, value):
    if accessor == "name":
        return value or ""

    if accessor == "category":
        return value or INLINE_EDIT_CATEGORY_OPTIONS[0]["value"]

    if accessor == "tags":
        return list(value or [])

    if accessor == "reviewDate":
        parsed = parse_date_value(value)
        return parsed.isoformat() if parsed else None

    if accessor == "adjustment":
        numeric = 0 if value is None else float(value)
        bounded = max(-2, min(6, numeric))
        return int(bounded) if float(bounded).is_integer() else bounded

    return value


def get_inline_edit_trigger_value(editor_ids, editor_values, row_id):
    for component_id, value in zip(editor_ids or [], editor_values or []):
        if record_ids_match(component_id.get("rowId"), row_id):
            return value
    return None


def update_inline_edit_record(records, row_id, accessor, value):
    next_records = []
    for record in strip_inline_edit_metadata(records):
        next_record = dict(record)
        if record_ids_match(record.get("id"), row_id):
            next_record[accessor] = normalize_inline_edit_value(accessor, value)
        next_records.append(next_record)
    return next_records


def build_basic_formatting_code():
    return "\n".join(
        [
            "table = dmdt.DataTable(",
            '    id="overview-table",',
            "    data=EMPLOYEES[:6],",
            "    columns=OVERVIEW_COLUMNS,",
            '    sortStatus={"columnAccessor": "name", "direction": "asc"},',
            "    striped=True,",
            "    withTableBorder=True,",
            "    withColumnBorders=True,",
            '    paginationMode="none",',
            '    radius="md",',
            '    bg="var(--mantine-color-body)",',
            ")",
        ]
    )


def build_selection_code():
    return "\n".join(
        [
            "table = dmdt.DataTable(",
            '    id="selection-table",',
            "    data=EMPLOYEES,",
            "    columns=OVERVIEW_COLUMNS[:5],",
            "    striped=True,",
            '    selectionTrigger="checkbox",',
            "    selectedRecordIds=[1, 3],",
            '    paginationMode="client",',
            "    page=1,",
            "    recordsPerPage=5,",
            "    pageSize=5,",
            '    sortStatus={"columnAccessor": "team", "direction": "asc"},',
            ")",
            "",
            "@callback(",
            '    Output("selection-output", "children"),',
            '    Input("selection-table", "selectedRecordIds"),',
            ")",
            "def show_selected_rows(selected_ids):",
            "    return f\"Selected record ids: {selected_ids or []}\"",
        ]
    )


def build_advanced_controls_code():
    """Generate example code for advanced selection, sorting, and pagination."""

    return "\n".join(
        [
            "selection = dmdt.SelectionConfig(",
            '    selectionTrigger="checkbox",',
            '    selectionColumnClassName="advanced-selection-column",',
            '    selectionColumnStyle={"width": 54},',
            '    selectionCheckboxProps={"radius": "xl", "size": "sm"},',
            '    allRecordsSelectionCheckboxProps={"aria-label": "Select all visible teammates"},',
            "    disabledSelectionRowRules=[",
            '        {"selector": {"status": "Needs Review"}, "value": True},',
            "    ],",
            "    selectionCheckboxRules=[",
            '        {"selector": {"status": "On Track"}, "value": {"color": "green"}},',
            '        {"selector": {"status": "Planning"}, "value": {"color": "blue"}},',
            '        {"selector": {"status": "Needs Review"}, "value": {"color": "orange"}},',
            "    ],",
            ")",
            "",
            "pagination = dmdt.PaginationConfig(",
            '    paginationMode="client",',
            "    page=1,",
            "    recordsPerPage=4,",
            "    recordsPerPageOptions=[4, 6],",
            '    paginationSize="sm",',
            '    paginationActiveTextColor="white",',
            '    paginationActiveBackgroundColor="blue",',
            '    loadingText="Loading teammates...",',
            ")",
            "",
            "table = (",
            "    dmdt.DataTable(",
            '        id="advanced-controls-table",',
            "        data=EMPLOYEES[:8],",
            "        columns=ADVANCED_CONTROLS_COLUMNS,",
            '        selectedRecordIds=[1, 3],',
            '        sortStatus={"columnAccessor": "name", "direction": "asc"},',
            "    )",
            "    .update_selection(**selection)",
            "    .update_pagination(**pagination)",
            "    .update_sorting(",
            '        sortIcons={',
            '            "sorted": DashIconify(icon="tabler:arrows-sort", width=16),',
            '            "unsorted": DashIconify(icon="tabler:selector", width=16),',
            "        },",
            "    )",
            "    .update_search(",
            '        searchMode="client",',
            '        searchableAccessors=["name", "team", "location", "status"],',
            "    )",
            '    .update_layout(radius="lg", withTableBorder=True, striped=True)',
            ")",
        ]
    )


def make_advanced_controls_demo_table():
    """Build a live table that exercises selection, sorting, and pagination helpers."""

    selection = dmdt.SelectionConfig(
        selectionTrigger="checkbox",
        selectionColumnClassName="advanced-selection-column",
        selectionColumnStyle={"width": 54},
        selectionCheckboxProps={"radius": "xl", "size": "sm"},
        allRecordsSelectionCheckboxProps={
            "aria-label": "Select all visible teammates"
        },
        disabledSelectionRowRules=[
            {"selector": {"status": "Needs Review"}, "value": True},
        ],
        selectionCheckboxRules=[
            {"selector": {"status": "On Track"}, "value": {"color": "green"}},
            {"selector": {"status": "Planning"}, "value": {"color": "blue"}},
            {"selector": {"status": "Needs Review"}, "value": {"color": "orange"}},
        ],
    )
    pagination = dmdt.PaginationConfig(
        paginationMode="client",
        page=1,
        recordsPerPage=4,
        recordsPerPageOptions=[4, 6],
        paginationSize="sm",
        paginationActiveTextColor="white",
        paginationActiveBackgroundColor="blue",
        loadingText="Loading teammates...",
    )

    return (
        dmdt.DataTable(
            id="advanced-controls-table",
            data=EMPLOYEES[:8],
            columns=ADVANCED_CONTROLS_COLUMNS,
            selectedRecordIds=[1, 3],
            sortStatus={"columnAccessor": "name", "direction": "asc"},
        )
        .update_selection(**selection)
        .update_pagination(**pagination)
        .update_sorting(
            **(
                {
                    "sortIcons": {
                        "sorted": DashIconify(icon="tabler:arrows-sort", width=16),
                        "unsorted": DashIconify(icon="tabler:selector", width=16),
                    }
                }
                if USE_FULL_RUNTIME_DEMOS
                else {}
            )
        )
        .update_search(
            searchMode="client",
            searchableAccessors=["name", "team", "location", "status"],
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            striped=True,
        )
    )


def build_server_pagination_code():
    return "\n".join(
        [
            'search = dmc.TextInput(id="server-search")',
            "",
            "table = dmdt.DataTable(",
            '    id="server-table",',
            "    columns=OVERVIEW_COLUMNS[:6],",
            '    paginationMode="server",',
            '    sortMode="server",',
            '    searchMode="server",',
            "    page=1,",
            "    recordsPerPage=4,",
            '    sortStatus={"columnAccessor": "name", "direction": "asc"},',
            ")",
            "",
            "@callback(",
            '    Output("server-table", "data"),',
            '    Output("server-table", "totalRecords"),',
            '    Output("server-table", "page"),',
            '    Input("server-search", "value"),',
            '    Input("server-table", "page"),',
            '    Input("server-table", "recordsPerPage"),',
            '    Input("server-table", "sortStatus"),',
            ")",
            "def update_server_table(search_value, page, records_per_page, sort_status):",
            "    filtered = filter_and_sort(EMPLOYEES, search_value, sort_status)",
            "    ...",
        ]
    )


def build_custom_components_code():
    """Generate example code for component-based loaders and empty-state icons."""

    return "\n\n".join(
        [
            "\n".join(
                [
                    "loading_table = (",
                    "    dmdt.DataTable(",
                    '        id="custom-loader-table",',
                    "        data=EMPLOYEES[:4],",
                    "        columns=STATES_DEMO_COLUMNS,",
                    "        fetching=True,",
                    "        customLoader=dmc.Stack(",
                    "            [",
                    '                DashIconify(icon="tabler:refresh", width=22),',
                    '                dmc.Text("Syncing employee records", size="sm"),',
                    "            ],",
                    '            align="center",',
                    "            gap=6,",
                    "        ),",
                    '        paginationMode="none",',
                    "    )",
                    "    .update_layout(",
                    '        radius="lg",',
                    "        withTableBorder=True,",
                    '        bd="1px solid var(--mantine-color-blue-2)",',
                    '        bdrs="lg",',
                    "        minHeight=220,",
                    "    )",
                    ")",
                ]
            ),
            "\n".join(
                [
                    "empty_table = (",
                    "    dmdt.DataTable(",
                    '        id="no-records-icon-table",',
                    "        data=[],",
                    "        columns=STATES_DEMO_COLUMNS,",
                    '        noRecordsText="No employees are waiting for review.",',
                    '        noRecordsIcon=DashIconify(icon="tabler:clipboard-off", width=28),',
                    '        paginationMode="none",',
                    "    )",
                    "    .update_layout(",
                    '        radius="lg",',
                    "        withTableBorder=True,",
                    '        bd="1px dashed var(--mantine-color-gray-4)",',
                    '        bdrs="lg",',
                    "        minHeight=220,",
                    "    )",
                    ")",
                ]
            ),
        ]
    )


def make_custom_loader_demo_table():
    """Build the live custom-loader example."""

    table = dmdt.DataTable(
        id="custom-loader-table",
        data=EMPLOYEES[:4],
        columns=STATES_DEMO_COLUMNS,
        fetching=True,
        paginationMode="none",
    )

    if USE_FULL_RUNTIME_DEMOS:
        table = table.update_layout(
            customLoader=dmc.Stack(
                [
                    DashIconify(
                        icon="tabler:refresh",
                        width=22,
                        color="var(--mantine-color-blue-6)",
                    ),
                    dmc.Text("Syncing employee records", size="sm"),
                ],
                align="center",
                gap=6,
            )
        )

    return table.update_layout(
        radius="lg",
        withTableBorder=True,
        bd="1px solid var(--mantine-color-blue-2)",
        bdrs="lg",
        minHeight=220,
    )


def make_no_records_icon_demo_table():
    """Build the live no-records-icon example."""

    table = dmdt.DataTable(
        id="no-records-icon-table",
        data=[],
        columns=STATES_DEMO_COLUMNS,
        noRecordsText="No employees are waiting for review.",
        paginationMode="none",
    )

    if USE_FULL_RUNTIME_DEMOS:
        table = table.update_layout(
            noRecordsIcon=DashIconify(
                icon="tabler:clipboard-off",
                width=28,
                color="var(--mantine-color-gray-6)",
            )
        )

    return table.update_layout(
        radius="lg",
        withTableBorder=True,
        bd="1px dashed var(--mantine-color-gray-4)",
        bdrs="lg",
        minHeight=220,
    )


def serialize_states_code_value(value):
    return json.dumps(value) if isinstance(value, str) else repr(value)


def resolve_states_demo_config(
    *,
    state_mode=None,
    loader_type=None,
    loader_color=None,
    loader_size=None,
    loader_blur=None,
    empty_text=None,
    table_min_height=None,
):
    return {
        "state_mode": state_mode or STATES_DEMO_DEFAULTS["state_mode"],
        "loader_type": loader_type or STATES_DEMO_DEFAULTS["loader_type"],
        "loader_color": loader_color or STATES_DEMO_DEFAULTS["loader_color"],
        "loader_size": loader_size or STATES_DEMO_DEFAULTS["loader_size"],
        "loader_blur": int(loader_blur or STATES_DEMO_DEFAULTS["loader_blur"]),
        "empty_text": (empty_text or "").strip()
        or STATES_DEMO_DEFAULTS["empty_text"],
        "table_min_height": int(
            table_min_height or STATES_DEMO_DEFAULTS["table_min_height"]
        ),
    }


def make_states_demo_table(
    component_id,
    *,
    state_mode=None,
    loader_type=None,
    loader_color=None,
    loader_size=None,
    loader_blur=None,
    empty_text=None,
    table_min_height=None,
):
    """Build the live empty/loading-state demo table."""

    config = resolve_states_demo_config(
        state_mode=state_mode,
        loader_type=loader_type,
        loader_color=loader_color,
        loader_size=loader_size,
        loader_blur=loader_blur,
        empty_text=empty_text,
        table_min_height=table_min_height,
    )
    has_records = config["state_mode"] != "empty"
    table = dmdt.DataTable(
        id=component_id,
        data=EMPLOYEES[:4] if has_records else [],
        columns=STATES_DEMO_COLUMNS,
        fetching=config["state_mode"] == "loading",
        loaderType=config["loader_type"],
        loaderColor=config["loader_color"],
        loaderSize=config["loader_size"],
        loaderBackgroundBlur=config["loader_blur"],
        noRecordsText=config["empty_text"],
        paginationMode="none",
    )

    if USE_FULL_RUNTIME_DEMOS:
        table = table.update_layout(
            emptyState=dmc.Stack(
                [
                    DashIconify(
                        icon="tabler:database-off",
                        width=28,
                        color="var(--mantine-color-gray-6)",
                    ),
                    dmc.Text(config["empty_text"], c="dimmed", ta="center"),
                ],
                align="center",
                gap=6,
            )
        )

    return table.update_layout(
        radius="lg",
        withTableBorder=True,
        minHeight=config["table_min_height"],
    )


def build_states_code(
    *,
    state_mode=None,
    loader_type=None,
    loader_color=None,
    loader_size=None,
    loader_blur=None,
    empty_text=None,
    table_min_height=None,
):
    """Generate the copy-pasteable code shown under the state demo."""

    config = resolve_states_demo_config(
        state_mode=state_mode,
        loader_type=loader_type,
        loader_color=loader_color,
        loader_size=loader_size,
        loader_blur=loader_blur,
        empty_text=empty_text,
        table_min_height=table_min_height,
    )
    records_expression = "EMPLOYEES[:4]" if config["state_mode"] != "empty" else "[]"

    return "\n".join(
        [
            "table = (",
            "    dmdt.DataTable(",
            '        id="states-table",',
            f"        data={records_expression},",
            "        columns=STATES_DEMO_COLUMNS,",
            f"        fetching={config['state_mode'] == 'loading'},",
            f"        loaderType={serialize_states_code_value(config['loader_type'])},",
            f"        loaderColor={serialize_states_code_value(config['loader_color'])},",
            f"        loaderSize={serialize_states_code_value(config['loader_size'])},",
            f"        loaderBackgroundBlur={config['loader_blur']},",
            "        emptyState=dmc.Stack(",
            "            [",
            '                DashIconify(icon="tabler:database-off", width=28),',
            f"                dmc.Text({serialize_states_code_value(config['empty_text'])}, c=\"dimmed\", ta=\"center\"),",
            "            ],",
            '            align="center",',
            "            gap=6,",
            "        ),",
            '        paginationMode="none",',
            "    )",
            "    .update_layout(",
            '        radius="lg",',
            "        withTableBorder=True,",
            f"        minHeight={config['table_min_height']},",
            "    )",
            ")",
        ]
    )


def build_table_properties_code(config):
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="table-properties-table",',
        "        data=EMPLOYEES[:5],",
        "        columns=TABLE_PROPERTIES_COLUMNS,",
        '        paginationMode="none",',
        "        style=TABLE_PROPERTIES_VISUAL_STYLE,",
        "    )",
        '    .update_layout(radius="lg")',
    ]

    prop_order = [
        "withRowBorders",
        "withColumnBorders",
        "striped",
        "highlightOnHover",
        "withTableBorder",
        "noHeader",
        "shadow",
        "horizontalSpacing",
        "verticalSpacing",
        "fontSize",
        "borderRadius",
        "verticalAlign",
    ]
    dynamic_props = [
        key
        for key in prop_order
        if config[key] != TABLE_PROPERTIES_DEFAULTS[key]
        or (key == "horizontalSpacing" and config[key] is not None)
    ]

    if dynamic_props:
        lines.append("    .update_table_properties(")
        for key in dynamic_props:
            lines.append(f"        {key}={format_table_property_value(config[key])},")
        lines.append("    )")
    else:
        lines.append("    .update_table_properties()")

    lines.append(")")
    return "\n".join(lines)


def build_column_properties_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="column-properties-table",',
        "        data=EMPLOYEES[:5],",
        "        columns=[",
        '            {"accessor": "name"},',
        '            {"accessor": "role"},',
        '            {"accessor": "bio"},',
        '            {"accessor": "salary"},',
        '            {"accessor": "deliveryScore"},',
        '            {"accessor": "trend"},',
        '            {"accessor": "status"},',
        '            {"accessor": "actions"},',
        "        ],",
        '        paginationMode="none",',
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True, withColumnBorders=True, striped=True)',
        "    .update_columns(",
        '        selector="name",',
        '        title="Employee",',
        "        width=180,",
        '        cellsStyle={"fontWeight": 600},',
        '        footer="5 shown",',
        '        footerStyle={"fontWeight": 700},',
        "    )",
        "    .update_columns(",
        '        selector="bio",',
        '        title="Mission statement",',
        "        width=320,",
        "        ellipsis=True,",
        '        visibleMediaQuery="(min-width: 62em)",',
        '        titleStyle={"letterSpacing": "0.08em", "textTransform": "uppercase"},',
        '        cellsStyle={"color": "var(--mantine-color-dimmed)"},',
        '        footer="Responsive + ellipsis",',
        '        footerStyle={"color": "var(--mantine-color-dimmed)"},',
        "    )",
        "    .update_columns(",
        '        selector="salary",',
        '        title="Annual salary",',
        '        presentation="currency",',
        '        currency="USD",',
        '        textAlign="right",',
        "        width=140,",
        '        cellsStyle={"fontVariantNumeric": "tabular-nums"},',
        f'        footer="${COLUMN_PROPERTIES_AVERAGE_SALARY:,.0f} avg",',
        '        footerStyle={"color": "var(--mantine-color-blue-6)", "fontWeight": 700},',
        "    )",
        "    .update_columns(",
        '        selector=["role", "deliveryScore", "trend"],',
        '        visibleMediaQuery="(min-width: 48em)",',
        "    )",
        "    .update_columns(",
        '        selector="deliveryScore",',
        '        title="Delivery",',
        '        presentation="progress",',
        "        width=140,",
        "    )",
        "    .update_columns(",
        '        selector="trend",',
        '        title="6-week trend",',
        "        width=150,",
        "        render=dmc.Sparkline(",
        '            data="{trend}",',
        '            color="{statusColor}",',
        "            w=120,",
        "            h=32,",
        "        ),",
        '        footer="Sparkline render",',
        "    )",
        "    .update_columns(",
        '        selector="status",',
        '        presentation="badge",',
        '        badgeColorAccessor="statusColor",',
        "        width=120,",
        '        cellsStyle={"whiteSpace": "nowrap"},',
        "    )",
        "    .update_columns(",
        '        selector="actions",',
        '        title="Actions",',
        "        width=190,",
        '        render=dmc.ActionIconGroup(',
        "            [",
        '                dmc.ActionIcon(',
        '                    DashIconify(icon="tabler:device-floppy", width=16),',
        '                    **{"aria-label": "Save {name}"},',
        '                    color="green",',
        '                    n_clicks=0,',
        '                    radius="xl",',
        '                    size="sm",',
        '                    variant="light",',
        '                    id={"action": "save-row", "recordId": "{id}"},',
        "                ),",
        '                dmc.ActionIcon(',
        '                    DashIconify(icon="tabler:pencil", width=16),',
        '                    **{"aria-label": "Edit {name}"},',
        '                    color="blue",',
        '                    n_clicks=0,',
        '                    radius="xl",',
        '                    size="sm",',
        '                    variant="light",',
        '                    id={"action": "edit-row", "recordId": "{id}"},',
        "                ),",
        '                dmc.ActionIcon(',
        '                    DashIconify(icon="tabler:trash", width=16),',
        '                    **{"aria-label": "Delete {name}"},',
        '                    color="red",',
        '                    n_clicks=0,',
        '                    radius="xl",',
        '                    size="sm",',
        '                    variant="light",',
        '                    id={"action": "delete-row", "recordId": "{id}"},',
        "                ),",
        "            ],",
        "        ),",
        '        cellsStyle={"paddingBlock": "0.35rem"},',
        "    )",
        ")",
    ]
    return "\n".join(lines)


def make_row_action_icon_set():
    return dmc.ActionIconGroup(
        [
            dmc.ActionIcon(
                DashIconify(icon=action["icon"], width=16),
                **{"aria-label": f'{action["label"]} ' + "{name}"},
                color=action["color"],
                n_clicks=0,
                radius="xl",
                size="sm",
                variant="light",
                id={"action": action["action"], "recordId": "{id}"},
            )
            for action in ROW_ACTIONS
        ],
    )


def make_column_properties_demo_table():
    base_columns = (
        COLUMN_PROPERTIES_BASE_COLUMNS
        if USE_FULL_RUNTIME_DEMOS
        else COLUMN_PROPERTIES_BASE_COLUMNS[:-2]
    )
    table = (
        dmdt.DataTable(
            id="column-properties-table",
            data=COLUMN_PROPERTIES_RECORDS,
            columns=base_columns,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            withColumnBorders=True,
            striped=True,
        )
        .update_columns(
            selector="name",
            title="Employee",
            width=180,
            cellsStyle={"fontWeight": 600},
            footer="5 shown",
            footerStyle={"fontWeight": 700},
        )
        .update_columns(
            selector="bio",
            title="Mission statement",
            width=320,
            ellipsis=True,
            visibleMediaQuery="(min-width: 62em)",
            titleStyle={
                "letterSpacing": "0.08em",
                "textTransform": "uppercase",
            },
            cellsStyle={"color": "var(--mantine-color-dimmed)"},
            footer="Responsive + ellipsis",
            footerStyle={"color": "var(--mantine-color-dimmed)"},
        )
        .update_columns(
            selector="salary",
            title="Annual salary",
            presentation="currency",
            currency="USD",
            textAlign="right",
            width=140,
            cellsStyle={"fontVariantNumeric": "tabular-nums"},
            footer=f"${COLUMN_PROPERTIES_AVERAGE_SALARY:,.0f} avg",
            footerStyle={
                "color": "var(--mantine-color-blue-6)",
                "fontWeight": 700,
            },
        )
        .update_columns(
            selector=(
                ["role", "deliveryScore", "trend"]
                if USE_FULL_RUNTIME_DEMOS
                else ["role", "deliveryScore"]
            ),
            visibleMediaQuery="(min-width: 48em)",
        )
        .update_columns(
            selector="deliveryScore",
            title="Delivery",
            presentation="progress",
            width=140,
        )
        .update_columns(
            selector="status",
            presentation="badge",
            badgeColorAccessor="statusColor",
            width=120,
            cellsStyle={"whiteSpace": "nowrap"},
        )
    )

    if USE_FULL_RUNTIME_DEMOS:
        table = table.update_columns(
            selector="trend",
            title="6-week trend",
            width=150,
            render=dmc.Sparkline(
                data="{trend}",
                color="{statusColor}",
                w=120,
                h=32,
            ),
            footer="Sparkline render",
        ).update_columns(
            selector="actions",
            title="Actions",
            width=190,
            render=make_row_action_icon_set(),
            cellsStyle={"paddingBlock": "0.35rem"},
        )

    return table


def build_column_filtering_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="column-filtering-table",',
        "        data=filtered_records,",
        "        columns=COLUMN_FILTERING_BASE_COLUMNS,",
        '        emptyState="No employees match the current filters.",',
        '        paginationMode="none",',
        "    )",
        "    .update_layout(",
        '        radius="lg",',
        "        withTableBorder=True,",
        "        withColumnBorders=True,",
        "        striped=True,",
        "    )",
        "    .update_columns(",
        '        selector="name",',
        "        width=220,",
        "        filter=dmc.TextInput(",
        '            id="column-name-filter",',
        '            label="Employee",',
        '            placeholder="Search employees...",',
        "            value=name_query,",
        "        ),",
        "        filtering=bool(name_query),",
        "    )",
        "    .update_columns(",
        '        selector="team",',
        "        width=180,",
        "        filter=dmc.MultiSelect(",
        '            id="column-team-filter",',
        '            label="Teams",',
        "            data=COLUMN_FILTERING_TEAM_OPTIONS,",
        "            value=selected_teams,",
        '            comboboxProps={"withinPortal": False},',
        "            searchable=True,",
        "            clearable=True,",
        "        ),",
        "        filtering=bool(selected_teams),",
        "    )",
        "    .update_columns(",
        '        selector="startDate",',
        "        width=190,",
        "        filter=dmc.Stack(",
        "            [",
        '                dmc.DateInput(',
        '                    id="column-start-date-from-filter",',
        '                    label="Start date from",',
        "                    value=start_date_range[0] if len(start_date_range) > 0 else None,",
        '                    valueFormat="YYYY-MM-DD",',
        '                    placeholder="Earliest date",',
        '                    clearable=True,',
        '                    popoverProps={"withinPortal": False},',
        "                ),",
        '                dmc.DateInput(',
        '                    id="column-start-date-to-filter",',
        '                    label="Start date to",',
        "                    value=start_date_range[1] if len(start_date_range) > 1 else None,",
        '                    valueFormat="YYYY-MM-DD",',
        '                    placeholder="Latest date",',
        '                    clearable=True,',
        '                    popoverProps={"withinPortal": False},',
        "                ),",
        "            ],",
        '            gap="xs",',
        "        ),",
        "        filtering=bool(start_date_range and any(start_date_range)),",
        '        filterPopoverProps={"width": 320},',
        "    )",
        "    .update_columns(",
        '        selector="deliveryScore",',
        "        width=220,",
        "        filter=dmc.Stack(",
        "            [",
        '                dmc.Text("Delivery score", fw=600, size="sm"),',
        "                dmc.RangeSlider(",
        '                    id="column-score-filter",',
        "                    min=COLUMN_FILTERING_DEFAULT_SCORE_RANGE[0],",
        "                    max=COLUMN_FILTERING_DEFAULT_SCORE_RANGE[1],",
        "                    value=score_range,",
        "                    minRange=5,",
        "                ),",
        "            ],",
        '            gap="xs",',
        "        ),",
        "        filtering=score_range != COLUMN_FILTERING_DEFAULT_SCORE_RANGE,",
        '        filterPopoverProps={"width": 320},',
        "    )",
        "    .update_columns(",
        '        selector="status",',
        "        width=160,",
        "        filter=dmc.RadioGroup(",
        '            id="column-status-filter",',
        '            label="Status",',
        "            value=selected_status,",
        "            children=dmc.Stack(",
        "                [",
        '                    dmc.Radio(label="All", value="all"),',
        '                    dmc.Radio(label="On Track", value="On Track"),',
        '                    dmc.Radio(label="Planning", value="Planning"),',
        '                    dmc.Radio(label="Needs Review", value="Needs Review"),',
        "                ],",
        "                gap=6,",
        "            ),",
        "        ),",
        '        filtering=selected_status not in (None, "all"),',
        '        filterPopoverProps={"width": 220},',
        "    )",
        ")",
        "",
        "@callback(",
        '    Output("column-filtering-table", "data"),',
        '    Output("column-filtering-table", "columns"),',
        '    Input("column-name-filter", "value"),',
        '    Input("column-team-filter", "value"),',
        '    Input("column-start-date-from-filter", "value"),',
        '    Input("column-start-date-to-filter", "value"),',
        '    Input("column-score-filter", "value"),',
        '    Input("column-status-filter", "value"),',
        ")",
        "def update_filtered_table(",
        "    name_query,",
        "    selected_teams,",
        "    start_date_from,",
        "    start_date_to,",
        "    score_range,",
        "    selected_status,",
        "):",
        "    table = make_column_filtering_demo_table(",
        "        name_query=name_query,",
        "        selected_teams=selected_teams,",
        "        start_date_range=[start_date_from, start_date_to],",
        "        score_range=score_range,",
        "        selected_status=selected_status,",
        "    )",
        "    return table.data, table.columns",
    ]
    return "\n".join(lines)


def make_column_filtering_demo_table(
    name_query="",
    selected_teams=None,
    start_date_range=None,
    score_range=None,
    selected_status="all",
):
    selected_teams = selected_teams or []
    normalized_score_range = normalize_score_range(score_range)
    start_date_range = list(start_date_range or [])
    start_date_filter_active = bool(start_date_range and any(start_date_range))
    status_filter_value = selected_status or "all"
    filtered_records = filter_column_search_records(
        EMPLOYEES,
        name_query=name_query,
        selected_teams=selected_teams,
        start_date_range=start_date_range,
        score_range=normalized_score_range,
        selected_status=status_filter_value,
    )

    table = (
        dmdt.DataTable(
            id="column-filtering-table",
            data=filtered_records,
            columns=COLUMN_FILTERING_BASE_COLUMNS,
            emptyState="No employees match the current filters.",
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            withColumnBorders=True,
            striped=True,
        )
    )

    if not USE_FULL_RUNTIME_DEMOS:
        return table.update_columns(selector="name", width=220).update_columns(
            selector="team", width=180
        ).update_columns(selector="startDate", width=190).update_columns(
            selector="deliveryScore", width=220
        ).update_columns(selector="status", width=160)

    return table.update_columns(
        selector="name",
        width=220,
        filter=dmc.TextInput(
            id="column-name-filter",
            label="Employee",
            description="Search names with a DMC text input.",
            placeholder="Search employees...",
            value=name_query or "",
        ),
        filtering=bool((name_query or "").strip()),
    ).update_columns(
        selector="team",
        width=180,
        filter=dmc.MultiSelect(
            id="column-team-filter",
            label="Teams",
            description="Filter down to one or more teams.",
            data=COLUMN_FILTERING_TEAM_OPTIONS,
            value=selected_teams,
            placeholder="Pick teams",
            searchable=True,
            clearable=True,
            comboboxProps={"withinPortal": False},
        ),
        filtering=bool(selected_teams),
        filterPopoverProps={"width": 280},
    ).update_columns(
        selector="startDate",
        width=190,
        filter=dmc.Stack(
            [
                dmc.DateInput(
                    id="column-start-date-from-filter",
                    label="Start date from",
                    description="Filter employees with a minimum start date.",
                    value=start_date_range[0] if len(start_date_range) > 0 else None,
                    valueFormat="YYYY-MM-DD",
                    placeholder="Earliest date",
                    clearable=True,
                    popoverProps={"withinPortal": False},
                ),
                dmc.DateInput(
                    id="column-start-date-to-filter",
                    label="Start date to",
                    description="Filter employees with a maximum start date.",
                    value=start_date_range[1] if len(start_date_range) > 1 else None,
                    valueFormat="YYYY-MM-DD",
                    placeholder="Latest date",
                    clearable=True,
                    popoverProps={"withinPortal": False},
                ),
            ],
            gap="xs",
        ),
        filtering=start_date_filter_active,
        filterPopoverProps={"width": 320},
    ).update_columns(
        selector="deliveryScore",
        width=220,
        filter=dmc.Stack(
            [
                dmc.Text("Delivery score", fw=600, size="sm"),
                dmc.RangeSlider(
                    id="column-score-filter",
                    min=COLUMN_FILTERING_DEFAULT_SCORE_RANGE[0],
                    max=COLUMN_FILTERING_DEFAULT_SCORE_RANGE[1],
                    value=normalized_score_range,
                    minRange=5,
                    step=1,
                ),
            ],
            gap="xs",
        ),
        filtering=normalized_score_range != COLUMN_FILTERING_DEFAULT_SCORE_RANGE,
        filterPopoverProps={"width": 320},
    ).update_columns(
        selector="status",
        width=160,
        filter=dmc.RadioGroup(
            id="column-status-filter",
            label="Status",
            description="Use radio buttons for a single status filter.",
            value=status_filter_value,
            children=dmc.Stack(
                [
                    dmc.Radio(label="All", value="all"),
                    dmc.Radio(label="On Track", value="On Track"),
                    dmc.Radio(label="Planning", value="Planning"),
                    dmc.Radio(label="Needs Review", value="Needs Review"),
                ],
                gap=6,
            ),
        ),
        filtering=status_filter_value != "all",
        filterPopoverProps={"width": 240},
    )


def build_column_dragging_code(store_key="demo-column-dragging"):
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="column-dragging-table",',
        "        data=EMPLOYEES[:6],",
        "        columns=COLUMN_CUSTOMIZATION_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        "    .update_layout(",
        '        radius="lg",',
        "        withTableBorder=True,",
        "        withColumnBorders=True,",
        f'        storeColumnsKey="{store_key}",',
        "    )",
        "    .update_columns(",
        '        selector=["team", "role", "location", "salary", "status"],',
        "        draggable=True,",
        "        toggleable=True,",
        "    )",
        "    .update_columns(",
        '        selector="location",',
        "        defaultToggle=False,",
        "    )",
        "    .update_columns(",
        '        selector=["salary", "status"],',
        '        visibleMediaQuery="(min-width: 48em)",',
        "    )",
        ")",
    ]
    return "\n".join(lines)


def make_column_dragging_demo_table(store_key="demo-column-dragging"):
    return (
        dmdt.DataTable(
            id="column-dragging-table",
            data=COLUMN_CUSTOMIZATION_RECORDS,
            columns=COLUMN_CUSTOMIZATION_COLUMNS,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            withColumnBorders=True,
            storeColumnsKey=store_key,
        )
        .update_columns(
            selector=["team", "role", "location", "salary", "status"],
            draggable=True,
            toggleable=True,
        )
        .update_columns(
            selector="location",
            defaultToggle=False,
        )
        .update_columns(
            selector=["salary", "status"],
            visibleMediaQuery="(min-width: 48em)",
        )
    )


def build_column_resizing_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="column-resizing-table",',
        "        data=EMPLOYEES[:6],",
        "        columns=COLUMN_CUSTOMIZATION_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        "    .update_layout(",
        '        radius="lg",',
        "        withTableBorder=True,",
        "        withColumnBorders=True,",
        '        storeColumnsKey="demo-column-resizing",',
        "    )",
        "    .update_columns(",
        '        selector=["name", "team", "role", "location", "salary", "status"],',
        "        resizable=True,",
        "    )",
        ")",
    ]
    return "\n".join(lines)


def make_column_resizing_demo_table():
    return (
        dmdt.DataTable(
            id="column-resizing-table",
            data=COLUMN_CUSTOMIZATION_RECORDS,
            columns=COLUMN_CUSTOMIZATION_COLUMNS,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            withColumnBorders=True,
            storeColumnsKey="demo-column-resizing",
        )
        .update_columns(
            selector=["name", "team", "role", "location", "salary", "status"],
            resizable=True,
        )
    )


def build_group_columns_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="group-columns-table",',
        "        data=EMPLOYEES[:6],",
        "        columns=GROUP_COLUMNS_BASE_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True, withColumnBorders=True)',
        "    .group_columns(",
        '        dmdt.ColumnGroup(',
        '            "profile",',
        '            title="Profile",',
        '            style={"fontStyle": "italic"},',
        "            groups=[",
        '                dmdt.ColumnGroup("identity", title="Identity", columns=["name", "role"]),',
        '                dmdt.ColumnGroup("organization", title="Organization", columns=["team", "location"]),',
        "            ],",
        "        ),",
        '        dmdt.ColumnGroup(',
        '            "performance",',
        '            title="Performance",',
        '            textAlign="center",',
        '            style={"backgroundColor": "var(--mantine-color-blue-0)"},',
        '            columns=["deliveryScore", "status", "salary"],',
        "        ),",
        "    )",
        "    .group_columns(",
        '        selector="profile",',
        '        style={"backgroundColor": "var(--mantine-color-gray-0)"},',
        "    )",
        "    .group_columns(",
        '        selector="organization",',
        '        textAlign="center",',
        '        style={"color": "var(--mantine-color-blue-6)"},',
        "    )",
        ")",
    ]
    return "\n".join(lines)


def make_group_columns_demo_table():
    return (
        dmdt.DataTable(
            id="group-columns-table",
            data=GROUP_COLUMNS_RECORDS,
            columns=GROUP_COLUMNS_BASE_COLUMNS,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            withColumnBorders=True,
        )
        .group_columns(
            dmdt.ColumnGroup(
                "profile",
                title="Profile",
                style={"fontStyle": "italic"},
                groups=[
                    dmdt.ColumnGroup(
                        "identity",
                        title="Identity",
                        columns=["name", "role"],
                    ),
                    dmdt.ColumnGroup(
                        "organization",
                        title="Organization",
                        columns=["team", "location"],
                    ),
                ],
            ),
            dmdt.ColumnGroup(
                "performance",
                title="Performance",
                textAlign="center",
                style={"backgroundColor": "var(--mantine-color-blue-0)"},
                columns=["deliveryScore", "status", "salary"],
            ),
        )
        .group_columns(
            selector="profile",
            style={"backgroundColor": "var(--mantine-color-gray-0)"},
        )
        .group_columns(
            selector="organization",
            textAlign="center",
            style={"color": "var(--mantine-color-blue-6)"},
        )
    )


def build_row_properties_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="row-properties-table",',
        "        data=EMPLOYEES[:6],",
        "        columns=ROW_PROPERTIES_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True, striped=True)',
        "    .update_rows(",
        '        selector={"status": "Needs Review"},',
        '        color="orange.9",',
        '        backgroundColor={"light": "#fff4e6", "dark": "#4a2a12"},',
        '        className="dmdt-row-review",',
        "    )",
        "    .update_rows(",
        '        selector={"team": "Platform"},',
        '        style={"borderInlineStart": "4px solid var(--mantine-color-blue-5)"},',
        "    )",
        "    .update_rows(",
        '        selector={"deliveryScore": {"gte": 90}},',
        '        style={"fontWeight": 700},',
        "    )",
        "    .update_rows(",
        '        selector={"status": "Needs Review"},',
        '        attributes={"title": "This row needs review", "data-status": "needs-review"},',
        "    )",
        ")",
    ]
    return "\n".join(lines)


def make_row_properties_demo_table():
    return (
        dmdt.DataTable(
            id="row-properties-table",
            data=ROW_PROPERTIES_RECORDS,
            columns=ROW_PROPERTIES_COLUMNS,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            striped=True,
        )
        .update_rows(
            selector={"status": "Needs Review"},
            color="orange.9",
            backgroundColor={"light": "#fff4e6", "dark": "#4a2a12"},
            className="dmdt-row-review",
        )
        .update_rows(
            selector={"team": "Platform"},
            style={"borderInlineStart": "4px solid var(--mantine-color-blue-5)"},
        )
        .update_rows(
            selector={"deliveryScore": {"gte": 90}},
            style={"fontWeight": 700},
        )
        .update_rows(
            selector={"status": "Needs Review"},
            attributes={
                "title": "This row needs review",
                "data-status": "needs-review",
            },
        )
    )


def build_scrolling_code(height=None):
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="scrolling-table",',
        "        data=SCROLLING_RECORDS,",
        "        columns=SCROLLING_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        "    .update_layout(",
        '        radius="lg",',
        "        withTableBorder=True,",
    ]

    if height is not None:
        lines.append(f"        height={height},")

    lines.extend(
        [
            "    )",
            ")",
        ]
    )
    return "\n".join(lines)


def make_scrolling_demo_table(component_id, *, height=None):
    table = dmdt.DataTable(
        id=component_id,
        data=SCROLLING_RECORDS,
        columns=SCROLLING_COLUMNS,
        paginationMode="none",
    ).update_layout(
        radius="lg",
        withTableBorder=True,
    )

    if height is not None:
        table.update_layout(height=height)

    return table


def build_infinite_scrolling_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="infinite-scroll-table",',
        "        data=INFINITE_SCROLL_RECORDS[:INFINITE_SCROLL_BATCH_SIZE],",
        "        columns=INFINITE_SCROLL_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        "    .update_layout(",
        '        radius="lg",',
        "        withTableBorder=True,",
        "        height=300,",
        "    )",
        ")",
        "",
        "@callback(",
        '    Output("infinite-scroll-table", "data"),',
        '    Input("infinite-scroll-table", "scrollEdge"),',
        '    State("infinite-scroll-table", "data"),',
        ")",
        "def load_more_rows(scroll_edge, current_rows):",
        "    if scroll_edge and scroll_edge.get('edge') == 'bottom':",
        "        next_size = len(current_rows or []) + INFINITE_SCROLL_BATCH_SIZE",
        "        return INFINITE_SCROLL_RECORDS[:next_size]",
        "    return current_rows",
    ]
    return "\n".join(lines)


def build_rtl_support_code(direction="rtl", height=260):
    lines = [
        "rtl_table = (",
        "    dmdt.DataTable(",
        '        id="rtl-table",',
        "        data=EMPLOYEES[:6],",
        "        columns=RTL_COLUMNS,",
        "        recordsPerPage=4,",
        "        pageSizeOptions=[4, 6],",
        "        withColumnBorders=True,",
        "        pinFirstColumn=True,",
        "        pinLastColumn=True,",
        "    )",
        "    .update_layout(",
        '        radius="lg",',
        "        withTableBorder=True,",
        "        striped=True,",
        f"        height={height},",
        f'        direction="{direction}",',
        "    )",
        ")",
    ]
    return "\n".join(lines)


def make_rtl_support_demo_table(component_id, *, direction, height=260):
    return (
        dmdt.DataTable(
            id=component_id,
            data=RTL_RECORDS,
            columns=RTL_COLUMNS,
            recordsPerPage=4,
            pageSizeOptions=[4, 6],
            withColumnBorders=True,
            pinFirstColumn=True,
            pinLastColumn=True,
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            striped=True,
            height=height,
            direction=direction,
        )
    )


def make_infinite_scroll_demo_table():
    return (
        dmdt.DataTable(
            id="infinite-scroll-table",
            data=INFINITE_SCROLL_RECORDS[:INFINITE_SCROLL_BATCH_SIZE],
            columns=INFINITE_SCROLL_COLUMNS,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            height=300,
        )
    )


def build_row_dragging_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="row-dragging-table",',
        "        data=EMPLOYEES[:6],",
        "        columns=ROW_DRAGGING_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        "    .update_layout(",
        '        radius="lg",',
        "        withTableBorder=True,",
        "        height=280,",
        "    )",
        "    .update_rows(",
        "        draggable=True,",
        "    )",
        ")",
    ]
    return "\n".join(lines)


def make_row_dragging_demo_table():
    return (
        dmdt.DataTable(
            id="row-dragging-table",
            data=ROW_DRAGGING_RECORDS,
            columns=ROW_DRAGGING_COLUMNS,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            height=280,
        )
        .update_rows(
            draggable=True,
        )
    )


def build_row_ids_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="row-ids-table",',
        "        data=ROW_IDS_RECORDS,",
        "        columns=[",
        '            {"accessor": "name", "width": 200},',
        '            {"accessor": "team", "width": 140},',
        '            {"accessor": "location", "title": "City", "width": 140},',
        '            {"accessor": "status", "presentation": "badge", "badgeColorAccessor": "statusColor"},',
        "        ],",
        '        paginationMode="none",',
        '        selectionTrigger="checkbox",',
        "    )",
        "    .update_rows(",
        '        idAccessor={"template": "{team}:{name}"},',
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True)',
        ")",
    ]
    return "\n".join(lines)


def make_row_ids_demo_table():
    return (
        dmdt.DataTable(
            id="row-ids-table",
            data=ROW_IDS_RECORDS,
            columns=[
                {"accessor": "name", "width": 200},
                {"accessor": "team", "width": 140},
                {"accessor": "location", "title": "City", "width": 140},
                {
                    "accessor": "status",
                    "presentation": "badge",
                    "badgeColorAccessor": "statusColor",
                },
            ],
            paginationMode="none",
            selectionTrigger="checkbox",
            selectedRecordIds=["Platform:Avery Stone"],
        )
        .update_rows(
            idAccessor={"template": "{team}:{name}"},
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
        )
    )


def build_expanding_rows_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="expanding-rows-table",',
        "        data=EMPLOYEES[:8],",
        "        columns=EXPANDING_ROWS_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True, striped=True)',
        "    .update_rows(",
        "        expandedRecordIds=[1],",
        "        rowExpansion=dmdt.RowExpansionConfig(",
        '            dmc.Paper(',
        "                dmc.Stack([...]),",
        '                p="md",',
        '                radius="md",',
        "                withBorder=True,",
        "            ),",
        "            allowMultiple=True,",
        "        ),",
        "    )",
        ")",
    ]
    return "\n".join(lines)


def make_expanding_rows_demo_table():
    return (
        dmdt.DataTable(
            id="expanding-rows-table",
            data=EMPLOYEES[:8],
            columns=EXPANDING_ROWS_COLUMNS,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            striped=True,
        )
        .update_rows(
            expandedRecordIds=[1],
            rowExpansion=dmdt.RowExpansionConfig(
                dmc.Paper(
                    dmc.Stack(
                        [
                            dmc.Group(
                                [
                                    dmc.Badge("{team}", variant="light", color="blue"),
                                    dmc.Badge(
                                        "{status}",
                                        variant="light",
                                        color="{statusColor}",
                                    ),
                                ],
                                gap="xs",
                            ),
                            dmc.Text("{bio}", c="dimmed", size="sm"),
                            dmc.Group(
                                [
                                    dmc.Stack(
                                        [
                                            dmc.Text("Location", size="xs", c="dimmed"),
                                            dmc.Text("{location}", fw=600),
                                        ],
                                        gap=0,
                                    ),
                                    dmc.Stack(
                                        [
                                            dmc.Text("Start date", size="xs", c="dimmed"),
                                            dmc.Text("{startDate}", fw=600),
                                        ],
                                        gap=0,
                                    ),
                                ],
                                gap="xl",
                            ),
                            dmc.Stack(
                                [
                                    dmc.Text("Delivery score", size="xs", c="dimmed"),
                                    dmc.Progress(
                                        value="{deliveryScore}",
                                        color="{statusColor}",
                                        radius="xl",
                                    ),
                                ],
                                gap=6,
                            ),
                            dmc.Anchor(
                                "Open profile",
                                href="{profileUrl}",
                                target="_blank",
                                size="sm",
                            ),
                        ],
                        gap="sm",
                    ),
                    p="md",
                    radius="md",
                    withBorder=True,
                ),
                allowMultiple=True,
            ),
        )
    )


def make_nested_employees_table(department_id, *, component_id=None, fetching=False):
    data = [] if fetching else EMPLOYEES_BY_DEPARTMENT.get(department_id, [])
    if isinstance(department_id, str) and department_id.startswith("{") and department_id.endswith("}"):
        data = department_id

    table_kwargs = {}
    if component_id is not None:
        table_kwargs["id"] = component_id

    return (
        dmdt.DataTable(
            data=data,
            columns=NESTED_EMPLOYEE_COLUMNS,
            paginationMode="none",
            noHeader=True,
            minHeight=120,
            fetching=fetching,
            **table_kwargs,
        )
        .update_layout(
            radius="md",
            withTableBorder=True,
            withColumnBorders=True,
        )
    )


def make_nested_departments_table(
    company_id,
    *,
    component_id=None,
    fetching=False,
):
    expanded_ids = []
    if not fetching and DEPARTMENTS_BY_COMPANY.get(company_id):
        expanded_ids = [DEPARTMENTS_BY_COMPANY[company_id][0]["id"]]

    table_kwargs = {}
    if component_id is not None:
        table_kwargs["id"] = component_id

    return (
        dmdt.DataTable(
            data=[] if fetching else DEPARTMENTS_BY_COMPANY.get(company_id, []),
            columns=NESTED_DEPARTMENT_COLUMNS,
            paginationMode="none",
            noHeader=True,
            minHeight=120,
            fetching=fetching,
            **table_kwargs,
        )
        .update_layout(
            radius="md",
            withTableBorder=True,
            withColumnBorders=True,
        )
        .update_rows(
            expandedRecordIds=expanded_ids,
            rowExpansion={
                "allowMultiple": True,
                "content": make_nested_employees_table("{employeesData}"),
            },
        )
    )


def make_nested_tables_demo_table():
    return (
        dmdt.DataTable(
            id="nested-tables-table",
            data=NESTED_GROUPED_RECORDS,
            columns=NESTED_GROUPED_COLUMNS,
            paginationMode="none",
            group_by=["companyGroup", "departmentGroup"],
            group_aggregations=NESTED_GROUP_AGGREGATIONS,
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            withColumnBorders=True,
            highlightOnHover=True,
            striped=True,
        )
    )


def build_nested_tables_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="nested-tables-table",',
        "        data=NESTED_GROUPED_RECORDS,",
        "        columns=NESTED_GROUPED_COLUMNS,",
        '        paginationMode="none",',
        '        group_by=["companyGroup", "departmentGroup"],',
        "        group_aggregations=NESTED_GROUP_AGGREGATIONS,",
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True, withColumnBorders=True, striped=True)',
        ")",
    ]
    return "\n".join(lines)


def make_async_nested_tables_demo_table(records=None):
    return (
        dmdt.DataTable(
            id="async-nested-tables-table",
            data=records or build_async_nested_company_records(),
            columns=NESTED_GROUPED_COLUMNS,
            paginationMode="none",
            child_rows_accessor="childrenData",
            group_aggregations=NESTED_GROUP_AGGREGATIONS,
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            withColumnBorders=True,
            highlightOnHover=True,
            striped=True,
        )
        .update_rows(
            expandedRecordIds=["northwind"],
        )
    )


def build_async_nested_tables_code():
    lines = [
        "pending_ids = dcc.Store(id=\"async-nested-pending-company-ids\", data=[])",
        "loader = dcc.Interval(id=\"async-nested-loader\", interval=450, disabled=True, n_intervals=0)",
        "",
        "table = (",
        "    dmdt.DataTable(",
        '        id="async-nested-tables-table",',
        "        data=build_async_nested_company_records(),",
        "        columns=NESTED_GROUPED_COLUMNS,",
        '        paginationMode="none",',
        '        child_rows_accessor="childrenData",',
        "        group_aggregations=NESTED_GROUP_AGGREGATIONS,",
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True, withColumnBorders=True, striped=True)',
        '    .update_rows(expandedRecordIds=["northwind"])',
        ")",
        "",
        "@callback(",
        '    Output("async-nested-tables-table", "data"),',
        '    Output("async-nested-pending-company-ids", "data"),',
        '    Output("async-nested-loader", "disabled"),',
        '    Output("async-nested-loader", "n_intervals"),',
        '    Input("async-nested-tables-table", "expandedRecordIds"),',
        '    State("async-nested-tables-table", "data"),',
        ")",
        "def queue_async_company_load(expanded_ids, current_rows):",
        "    ...",
        "",
        "@callback(",
        '    Output("async-nested-tables-table", "data", allow_duplicate=True),',
        '    Output("async-nested-pending-company-ids", "data", allow_duplicate=True),',
        '    Output("async-nested-loader", "disabled", allow_duplicate=True),',
        '    Input("async-nested-loader", "n_intervals"),',
        '    State("async-nested-pending-company-ids", "data"),',
        '    State("async-nested-tables-table", "data"),',
        "    prevent_initial_call=True,",
        ")",
        "def hydrate_async_company_load(n_intervals, pending_ids, current_rows):",
        "    ...",
    ]
    return "\n".join(lines)


def build_row_click_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="interactive-row-click-table",',
        "        data=EMPLOYEES[:6],",
        "        columns=INTERACTIVITY_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True)',
        "    .add_interactivity(",
        "        rowClick=True,",
        "    )",
        ")",
        "",
        "@callback(",
        '    Output("interactive-row-click-output", "children"),',
        '    Input("interactive-row-click-table", "rowClick"),',
        ")",
        "def show_row_click_payload(payload):",
        '    return json.dumps(payload, indent=2) if payload else "Click a row to inspect the payload."',
    ]
    return "\n".join(lines)


def make_row_click_demo_table():
    return (
        dmdt.DataTable(
            id="interactive-row-click-table",
            data=INTERACTIVITY_RECORDS,
            columns=INTERACTIVITY_COLUMNS,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
        )
        .add_interactivity(
            rowClick=True,
        )
    )


def build_cell_click_code():
    lines = [
        "table = (",
        "    dmdt.DataTable(",
        '        id="interactive-cell-click-table",',
        "        data=EMPLOYEES[:6],",
        "        columns=INTERACTIVITY_COLUMNS,",
        '        paginationMode="none",',
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True)',
        "    .add_interactivity(",
        "        cellClick=True,",
        '        cellSelector=["name", "status"],',
        "    )",
        ")",
        "",
        "@callback(",
        '    Output("interactive-cell-click-output", "children"),',
        '    Input("interactive-cell-click-table", "cellClick"),',
        ")",
        "def show_cell_click_payload(payload):",
        '    return json.dumps(payload, indent=2) if payload else "Click a Name or Status cell to inspect the payload."',
    ]
    return "\n".join(lines)


def make_cell_click_demo_table():
    return (
        dmdt.DataTable(
            id="interactive-cell-click-table",
            data=INTERACTIVITY_RECORDS,
            columns=INTERACTIVITY_COLUMNS,
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
        )
        .add_interactivity(
            cellClick=True,
            cellSelector=["name", "status"],
        )
    )


def build_inline_edit_columns():
    if not USE_FULL_RUNTIME_DEMOS:
        return [
            {
                "accessor": "name",
                "title": "Name",
                "width": 190,
            },
            {
                "accessor": "category",
                "title": "Category",
                "width": 150,
                "presentation": "badge",
                "badgeColorAccessor": "_edit_adjustment_color",
            },
            {
                "accessor": "_edit_tags_label",
                "title": "Multi-select",
                "width": 260,
            },
            {
                "accessor": "reviewDate",
                "title": "Date",
                "width": 170,
                "presentation": "date",
            },
            {
                "accessor": "adjustment",
                "title": "Adjustment",
                "width": 150,
                "textAlign": "right",
            },
        ]

    return [
        {
            "accessor": "name",
            "title": "Name",
            "width": 190,
            "editable": True,
            "editor": dmc.TextInput(
                label="Name",
                placeholder="Rename teammate",
                size="xs",
            ),
        },
        {
            "accessor": "category",
            "title": "Category",
            "width": 150,
            "editable": True,
            "editor": dmc.RadioGroup(
                label="Category",
                children=dmc.Stack(
                    [
                        dmc.Radio(label="Draft", value="Draft"),
                        dmc.Radio(label="In Review", value="Review"),
                        dmc.Radio(label="Approved", value="Approved"),
                    ],
                    gap=6,
                ),
            ),
            "render": dmc.Badge("{category}", variant="light", color="blue"),
        },
        {
            "accessor": "tags",
            "title": "Multi-select",
            "width": 260,
            "editable": True,
            "editor": dmc.MultiSelect(
                label="Tags",
                data=INLINE_EDIT_TAG_OPTIONS,
                searchable=True,
            ),
        },
        {
            "accessor": "reviewDate",
            "title": "Date",
            "width": 170,
            "presentation": "date",
            "editable": True,
            "editor": dmc.DateInput(
                label="Review date",
                valueFormat="YYYY-MM-DD",
            ),
        },
        {
            "accessor": "adjustment",
            "title": "Adjustment",
            "width": 150,
            "textAlign": "right",
            "editable": True,
            "editor": dmc.NumberInput(
                label="Adjustment",
                min=-2,
                max=6,
                clampBehavior="strict",
                step=1,
                hideControls=True,
            ),
        },
    ]

def build_inline_edit_code():
    lines = [
        "editable_table = (",
        "    dmdt.DataTable(",
        '        id="inline-edit-table",',
        "        data=INLINE_EDIT_RECORDS,",
        "        columns=[",
        '            {"accessor": "name", "editable": True, "editor": dmc.TextInput(label="Name")},',
        '            {"accessor": "category", "editable": True, "editor": dmc.RadioGroup(',
        '                label="Category",',
        "                children=dmc.Stack([",
        '                    dmc.Radio(label="Draft", value="Draft"),',
        '                    dmc.Radio(label="In Review", value="Review"),',
        '                    dmc.Radio(label="Approved", value="Approved"),',
        "                ], gap=6),",
        '            ), "render": dmc.Badge("{category}", variant="light", color="blue")},',
        '            {"accessor": "tags", "editable": True, "editor": dmc.MultiSelect(label="Tags", data=INLINE_EDIT_TAG_OPTIONS, searchable=True)},',
        '            {"accessor": "reviewDate", "presentation": "date", "editable": True, "editor": dmc.DateInput(label="Review date", valueFormat="YYYY-MM-DD")},',
        '            {"accessor": "adjustment", "textAlign": "right", "editable": True, "editor": dmc.NumberInput(label="Adjustment", min=-2, max=6, step=1, hideControls=True)},',
        "        ],",
        '        paginationMode="none",',
        "    )",
        '    .update_layout(radius="lg", withTableBorder=True, textSelectionDisabled=True)',
        "    .add_interactivity(",
        "        cellDoubleClick=True,",
        "        cellSelector=INLINE_EDITABLE_ACCESSORS,",
        "    )",
        ")",
        "",
        "@callback(",
        '    Output("inline-edit-records-output", "children"),',
        '    Input("inline-edit-table", "data"),',
        ")",
        "def preview_records(rows):",
        "    return json.dumps(rows or [], indent=2)",
    ]
    return "\n".join(lines)


def make_inline_edit_demo_table():
    return (
        dmdt.DataTable(
            id="inline-edit-table",
            data=(
                decorate_inline_edit_records(INLINE_EDIT_RECORDS)
                if not USE_FULL_RUNTIME_DEMOS
                else INLINE_EDIT_RECORDS
            ),
            columns=build_inline_edit_columns(),
            paginationMode="none",
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            textSelectionDisabled=True,
        )
        .add_interactivity(
            cellDoubleClick=True,
            cellSelector=list(INLINE_EDITABLE_ACCESSORS),
        )
    )


def boolean_table_control(component_id, label, checked):
    return dmc.Switch(
        id=component_id,
        label=label,
        checked=checked,
        size="md",
    )


def option_table_control(
    label,
    checkbox_id,
    control_id,
    options,
    checked=False,
    value=None,
):
    return dmc.Stack(
        [
            dmc.Group(
                [
                    dmc.Checkbox(id=checkbox_id, checked=checked),
                    dmc.Text(label, size="sm"),
                ],
                gap="sm",
            ),
            dmc.SegmentedControl(
                id=control_id,
                data=options,
                value=value or options[0],
                fullWidth=True,
                disabled=not checked,
            ),
        ],
        gap="xs",
    )


def method_badges(methods):
    return dmc.Group(
        [
            dmc.Badge(method, variant="light", color="blue", radius="sm")
            for method in methods or []
        ],
        gap="xs",
    )


def highlight_points(items):
    return dmc.Stack(
        [
            dmc.Group(
                [
                    DashIconify(
                        icon="tabler:point-filled",
                        width=12,
                        color="var(--mantine-color-blue-6)",
                    ),
                    dmc.Text(item, size="sm"),
                ],
                gap="xs",
                align="start",
            )
            for item in items or []
        ],
        gap=6,
    )


def source_code_accordion(
    title,
    *,
    code=None,
    code_component=None,
    description=None,
    value="source-code",
    initially_open=False,
):
    """Render an accordion that keeps long code examples out of the main flow."""

    panel_children = []

    if description:
        panel_children.append(dmc.Text(description, size="sm", c="dimmed"))

    panel_children.append(
        code_component
        if code_component is not None
        else dmc.Code(block=True, children=code)
    )

    return dmc.Accordion(
        [
            dmc.AccordionItem(
                [
                    dmc.AccordionControl(
                        title,
                        icon=DashIconify(icon="tabler:code", width=18),
                    ),
                    dmc.AccordionPanel(
                        dmc.Stack(panel_children, gap="sm"),
                    ),
                ],
                value=value,
            )
        ],
        multiple=True,
        value=[value] if initially_open else [],
        variant="separated",
        radius="md",
        chevronPosition="left",
    )


def docs_control_panel(title, description, controls):
    """Render a consistent bordered wrapper for interactive documentation controls."""

    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Text(title, fw=600, size="sm"),
                dmc.Text(description, c="dimmed", size="sm"),
                controls,
            ],
            gap="sm",
        ),
        withBorder=True,
        radius="md",
        p="md",
    )


def demo_section(
    title,
    description,
    child,
    footer=None,
    section_id=None,
    methods=None,
    highlights=None,
):
    """Compose a full documentation section with intro copy, live demo, and notes."""

    intro_children = [
        dmc.Title(title, order=2),
        dmc.Text(description, c="dimmed", size="sm"),
    ]

    if methods:
        intro_children.extend(
            [
                dmc.Text("Dash API", size="xs", tt="uppercase", fw=700, c="dimmed"),
                method_badges(methods),
            ]
        )

    if highlights:
        intro_children.extend(
            [
                dmc.Text(
                    "What this example highlights",
                    size="xs",
                    tt="uppercase",
                    fw=700,
                    c="dimmed",
                ),
                highlight_points(highlights),
            ]
        )

    intro_children.append(child)

    children = [dmc.Stack(intro_children, gap="md")]
    if footer is not None:
        children.append(footer)

    return html.Div(
        dmc.Paper(
            children,
            withBorder=True,
            radius="lg",
            p="lg",
            shadow="xs",
        ),
        id=section_id,
        style={"scrollMarginTop": "1rem"},
    )


def category_divider(title, description, *, category_id=None):
    """Render a broad category heading between clusters of examples."""

    return html.Div(
        dmc.Stack(
            [
                html.Div(
                    [
                        html.Div(
                            style={
                                "flex": 1,
                                "height": "1px",
                                "background": "var(--mantine-color-blue-3)",
                            }
                        ),
                        dmc.Badge(
                            title,
                            variant="light",
                            color="blue",
                            radius="sm",
                            size="md",
                        ),
                        html.Div(
                            style={
                                "flex": 1,
                                "height": "1px",
                                "background": "var(--mantine-color-blue-3)",
                            }
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "0.75rem",
                    },
                ),
                dmc.Text(description, c="dimmed", size="sm", maw=760),
            ],
            gap="xs",
        ),
        id=category_id,
        style={"scrollMarginTop": "1rem"},
    )


app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "DashMantineDatatable Demo"

navigation_panel = dmc.Paper(
    dmc.Stack(
        [
            dmc.Text("Examples", fw=700, tt="uppercase", c="dimmed", size="xs"),
            dmc.Text(
                "Jump to a broader category or a specific example section.",
                size="sm",
                c="dimmed",
            ),
            html.Div(
                [
                    dmc.Paper(
                        dmc.Stack(
                            [
                                dmc.Text(
                                    category_title,
                                    fw=700,
                                    size="xs",
                                    tt="uppercase",
                                    c="blue",
                                ),
                                dmc.Text(
                                    category_description,
                                    size="xs",
                                    c="dimmed",
                                ),
                                dmc.Stack(
                                    [
                                        html.A(
                                            label,
                                            href=f"#{section_id}",
                                            style={
                                                "color": "var(--mantine-color-text)",
                                                "fontSize": "0.875rem",
                                                "textDecoration": "none",
                                            },
                                        )
                                        for section_id, label in category_sections
                                    ],
                                    gap="xs",
                                ),
                            ],
                            gap="xs",
                        ),
                        withBorder=True,
                        radius="md",
                        p="sm",
                    )
                    for category_title, category_description, category_sections in CATEGORY_LINK_GROUPS
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                    "gap": "0.75rem",
                },
            ),
        ],
        gap="md",
    ),
    withBorder=True,
    radius="lg",
    p="md",
    shadow="xs",
)

app.layout = dmc.MantineProvider(
    dmc.Container(
        dmc.Stack(
            [
                dmc.Stack(
                    [
                        dmc.Badge("Data Display", variant="light", size="lg"),
                        dmc.Title("DashMantineDatatable", order=1),
                        dmc.Text(
                            "This usage page is organized like a Dash Mantine Components "
                            "docs entry: the examples are grouped into broad categories, "
                            "each example leads with a live demo, and the source lives in "
                            "accordions so the page stays easy to scan.",
                            c="dimmed",
                            maw=720,
                        ),
                        html.Div(
                            [
                                dmc.Paper(
                                    dmc.Stack(
                                        [
                                            dmc.Text("Fluent methods", fw=600, size="sm"),
                                            dmc.Text(
                                                "Examples call out when to reach for "
                                                "`update_layout()`, `update_columns()`, "
                                                "`update_rows()`, and grouped helpers.",
                                                size="sm",
                                                c="dimmed",
                                            ),
                                        ],
                                        gap="xs",
                                    ),
                                    withBorder=True,
                                    radius="md",
                                    p="md",
                                ),
                                dmc.Paper(
                                    dmc.Stack(
                                        [
                                            dmc.Text("Interactive demos", fw=600, size="sm"),
                                            dmc.Text(
                                                "Several sections now include inputs so you can "
                                                "change direction, height, and persisted column "
                                                "state in real time like the DMC docs.",
                                                size="sm",
                                                c="dimmed",
                                            ),
                                        ],
                                        gap="xs",
                                    ),
                                    withBorder=True,
                                    radius="md",
                                    p="md",
                                ),
                                dmc.Paper(
                                    dmc.Stack(
                                        [
                                            dmc.Text("Dash payloads", fw=600, size="sm"),
                                            dmc.Text(
                                                "Callback outputs stay visible next to the "
                                                "tables, which makes it easier to understand "
                                                "what each prop emits and how to wire it up.",
                                                size="sm",
                                                c="dimmed",
                                            ),
                                        ],
                                        gap="xs",
                                    ),
                                    withBorder=True,
                                    radius="md",
                                    p="md",
                                ),
                            ],
                            style={
                                "display": "grid",
                                "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                                "gap": "1rem",
                            },
                        ),
                        navigation_panel,
                    ],
                    gap="md",
                ),
                category_divider(
                    "Core workflows",
                    "Start here for the examples most people will want first: basic formatting, selection, nested content, and server-driven table state.",
                    category_id="category-core-workflows",
                ),
                demo_section(
                    "1. Basic formatting",
                    "Start with a small set of strongly typed columns, then layer on Mantine styling props and presentation helpers to make cells feel native inside a DMC layout.",
                    dmc.Stack(
                        [
                            dmdt.DataTable(
                                id="overview-table",
                                data=EMPLOYEES[:6],
                                columns=OVERVIEW_COLUMNS,
                                sortStatus={"columnAccessor": "name", "direction": "asc"},
                                striped=True,
                                withTableBorder=True,
                                withColumnBorders=True,
                                paginationMode="none",
                                radius="md",
                                bg="var(--mantine-color-body)",
                            ),
                            source_code_accordion(
                                "Show Python for the formatting example",
                                code=build_basic_formatting_code(),
                                description=(
                                    "This example keeps everything declarative: column "
                                    "definitions handle currency, progress, badges, and "
                                    "links without custom React code."
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    section_id="section-basic",
                    methods=["DataTable()", "presentation", "style props"],
                    highlights=[
                        "Use `presentation` in column definitions to render badges, progress bars, links, and formatted currency from plain records.",
                        "Table-level props such as `striped`, `withTableBorder`, and `withColumnBorders` are often enough for a polished first example.",
                        "Mantine style props like `radius` and `bg` let the table inherit the same visual language as the rest of the page.",
                    ],
                ),
                demo_section(
                    "2. Client-side selection",
                    "Selection is fully Dash-native: enable a trigger, seed selected IDs if you want defaults, and read the resulting state from `selectedRecordIds`.",
                    dmc.Stack(
                        [
                            dmdt.DataTable(
                                id="selection-table",
                                data=EMPLOYEES,
                                columns=OVERVIEW_COLUMNS[:5],
                                striped=True,
                                recordsPerPageOptions=[5, 10],
                                selectionTrigger="checkbox",
                                selectedRecordIds=[1, 3],
                                paginationMode="client",
                                page=1,
                                recordsPerPage=5,
                                pageSize=5,
                                sortStatus={
                                    "columnAccessor": "team",
                                    "direction": "asc",
                                },
                                radius="md",
                            ),
                            dmc.Code(
                                id="selection-output",
                                block=True,
                                children="Selected record ids: [1, 3]",
                            ),
                            source_code_accordion(
                                "Show Python for selection callbacks",
                                code=build_selection_code(),
                                description=(
                                    "The callback stays tiny because the table writes the "
                                    "current selection directly to a regular Dash prop."
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    section_id="section-selection",
                    methods=["selectionTrigger", "selectedRecordIds", "@callback"],
                    highlights=[
                        "Checkbox selection is a good default when you want bulk actions or downstream filtering based on selected rows.",
                        "The selected IDs prop is easy to serialize, store, or pass into another callback without translating Mantine internals.",
                        "Because the example uses client pagination, the selection UX stays responsive even while the data remains fully declarative.",
                    ],
                ),
                demo_section(
                    "3. Row expansion and nested tables",
                    "Row expansion is where the component starts to feel app-like: you can attach inline detail panels, mount nested tables, or progressively hydrate child content from callbacks.",
                    dmc.Stack(
                        [
                            dmc.Stack(
                                [
                                    dmc.Text("Expanding rows", fw=600, size="sm"),
                                    make_expanding_rows_demo_table(),
                                    dmc.Code(
                                        id="expanding-rows-output",
                                        block=True,
                                        children="Expand a row to inspect expansion state.",
                                    ),
                                    source_code_accordion(
                                        "Show Python for expanding rows",
                                        code=build_expanding_rows_code(),
                                    ),
                                ],
                                gap="sm",
                            ),
                            dmc.Stack(
                                [
                                    dmc.Text(
                                        "Nested tables with group_by",
                                        fw=600,
                                        size="sm",
                                    ),
                                    make_nested_tables_demo_table(),
                                    source_code_accordion(
                                        "Show Python for nested tables",
                                        code=build_nested_tables_code(),
                                    ),
                                ],
                                gap="sm",
                            ),
                            dmc.Stack(
                                [
                                    dcc.Store(
                                        id="async-nested-pending-company-ids",
                                        data=[],
                                    ),
                                    dcc.Interval(
                                        id="async-nested-loader",
                                        interval=450,
                                        disabled=True,
                                        n_intervals=0,
                                    ),
                                    dmc.Text(
                                        "Nested tables with async data loading",
                                        fw=600,
                                        size="sm",
                                    ),
                                    make_async_nested_tables_demo_table(),
                                    source_code_accordion(
                                        "Show Python for async nested tables",
                                        code=build_async_nested_tables_code(),
                                    ),
                                ],
                                gap="sm",
                            ),
                        ],
                        gap="xl",
                    ),
                    dmc.Text(
                        "The first nested example uses `group_by` plus `group_aggregations` to build pivot-style parent rows from flat records, while the async example uses `child_rows_accessor` to hydrate a real record tree into the same inline hierarchy.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-expansion",
                    methods=["group_by", "group_aggregations", "child_rows_accessor", "expandedRecordIds", "@callback"],
                    highlights=[
                        "Use `group_by` when your source data is flat and you want pivot-style nested tables grouped by one or more keys.",
                        "Use `group_aggregations` to populate parent rows with built-in summaries like `sum`, `mean`, `median`, `min`, `max`, `count`, or a custom client-side lambda.",
                        "Use `child_rows_accessor` when your data is already hierarchical or arrives asynchronously and should still render as one seamless nested table.",
                        "The `expandedRecordIds` and `lastExpansionChange` props are enough to track which rows opened, closed, or still need data.",
                    ],
                ),
                demo_section(
                    "4. Server-style pagination and sorting",
                    "This pattern mirrors a real backend-backed table: text input drives the query, the table emits page and sort state, and the callback slices data before sending only the current page back.",
                    dmc.Stack(
                        [
                            dmc.TextInput(
                                id="server-search",
                                placeholder="Filter by name, team, role, or location",
                            ),
                            dmdt.DataTable(
                                id="server-table",
                                columns=OVERVIEW_COLUMNS[:6],
                                data=[],
                                paginationMode="server",
                                sortMode="server",
                                searchMode="server",
                                page=1,
                                recordsPerPage=4,
                                recordsPerPageOptions=[4, 6, 8],
                                sortStatus={
                                    "columnAccessor": "name",
                                    "direction": "asc",
                                },
                                withTableBorder=True,
                                striped=True,
                                radius="md",
                            ),
                            source_code_accordion(
                                "Show Python for server pagination",
                                code=build_server_pagination_code(),
                                description=(
                                    "The callback reads the table state the same way it would "
                                    "if the rows were coming from a database or API."
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    section_id="section-server",
                    methods=["paginationMode='server'", "sortMode='server'", "searchMode='server'"],
                    highlights=[
                        "Keep paging, sorting, and search in one callback so the user always sees a consistent subset of data.",
                        "The table still renders declaratively even when the records come from server logic instead of client-side transforms.",
                        "This is the pattern to copy when your datasets outgrow what you want to ship to the browser up front.",
                    ],
                ),
                category_divider(
                    "States and layout",
                    "These examples focus on how the table behaves inside real layouts: loading, empty states, constrained heights, infinite scroll, and RTL direction.",
                    category_id="category-states-and-layout",
                ),
                demo_section(
                    "5. Empty and loading states",
                    "Switch the same table between loaded, loading, and empty states to compare the behavior side by side, then tweak the Mantine loader and custom empty-state copy live.",
                    dmc.Stack(
                        [
                            html.Div(
                                [
                                    docs_control_panel(
                                        "Choose the table state",
                                        "Loading keeps rows visible under an overlay. Empty removes the rows and shows the custom emptyState component.",
                                        dmc.SegmentedControl(
                                            id="states-view-mode",
                                            value=STATES_DEMO_DEFAULTS["state_mode"],
                                            fullWidth=True,
                                            data=STATES_VIEW_OPTIONS,
                                        ),
                                    ),
                                    docs_control_panel(
                                        "Loader controls",
                                        "Pick a Mantine loader type and color, then adjust the size and backdrop blur for loading mode.",
                                        dmc.Stack(
                                            [
                                                dmc.RadioGroup(
                                                    id="states-loader-type",
                                                    label="Loader type",
                                                    value=STATES_DEMO_DEFAULTS["loader_type"],
                                                    children=dmc.Stack(
                                                        [
                                                            dmc.Radio(
                                                                label=option["label"],
                                                                value=option["value"],
                                                            )
                                                            for option in STATES_LOADER_TYPES
                                                        ],
                                                        gap=6,
                                                    ),
                                                ),
                                                dmc.RadioGroup(
                                                    id="states-loader-color",
                                                    label="Loader color",
                                                    value=STATES_DEMO_DEFAULTS["loader_color"],
                                                    children=dmc.Stack(
                                                        [
                                                            dmc.Radio(
                                                                label=option["label"],
                                                                value=option["value"],
                                                            )
                                                            for option in STATES_COLOR_OPTIONS
                                                        ],
                                                        gap=6,
                                                    ),
                                                ),
                                                dmc.Group(
                                                    [
                                                        dmc.Select(
                                                            id="states-loader-size",
                                                            label="Loader size",
                                                            data=TABLE_SIZE_OPTIONS,
                                                            value=STATES_DEMO_DEFAULTS["loader_size"],
                                                        ),
                                                        dmc.NumberInput(
                                                            id="states-loader-blur",
                                                            label="Background blur",
                                                            min=0,
                                                            max=6,
                                                            step=1,
                                                            value=STATES_DEMO_DEFAULTS["loader_blur"],
                                                        ),
                                                    ],
                                                    grow=True,
                                                    align="end",
                                                ),
                                            ],
                                            gap="sm",
                                        ),
                                    ),
                                    docs_control_panel(
                                        "Empty state content",
                                        "Switch to Empty to preview the built-in no-records state, then edit the message and table height live.",
                                        dmc.Stack(
                                            [
                                                dmc.TextInput(
                                                    id="states-empty-text",
                                                    label="Empty state text",
                                                    value=STATES_DEMO_DEFAULTS["empty_text"],
                                                ),
                                                dmc.Group(
                                                    [
                                                        dmc.NumberInput(
                                                            id="states-table-min-height",
                                                            label="Table min height",
                                                            min=160,
                                                            max=320,
                                                            step=20,
                                                            value=STATES_DEMO_DEFAULTS[
                                                                "table_min_height"
                                                            ],
                                                        ),
                                                    ],
                                                    grow=True,
                                                    align="end",
                                                ),
                                            ],
                                            gap="sm",
                                        ),
                                    ),
                                ],
                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
                                    "gap": "1rem",
                                },
                            ),
                            dmc.Text(
                                id="states-demo-copy",
                                size="sm",
                                c="dimmed",
                                children=(
                                    "Loading mode is active, so the current rows stay visible "
                                    "while a Mantine loader overlays the table."
                                ),
                            ),
                            html.Div(
                                id="states-demo-container",
                                children=make_states_demo_table(
                                    "states-live-table",
                                    **STATES_DEMO_DEFAULTS,
                                ),
                            ),
                            source_code_accordion(
                                "Show Python for empty and loading states",
                                description=(
                                    "The same callback can swap the data, fetching flag, "
                                    "loader props, and built-in no-records copy."
                                ),
                                code_component=dmc.Code(
                                    id="states-code-output",
                                    block=True,
                                    children=build_states_code(**STATES_DEMO_DEFAULTS),
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    section_id="section-states",
                    methods=[
                        "emptyState",
                        "fetching",
                        "loaderType",
                        "loaderColor",
                        "loaderSize",
                        "loaderBackgroundBlur",
                    ],
                    highlights=[
                        "A single state toggle makes it easier to understand the visual difference between keeping rows while fetching and rendering a true empty table.",
                        "Loader controls mirror the Mantine DataTable API, so users can explore type, color, size, and blur without reading the docs first.",
                        "Custom emptyState content shows how far you can push the blank-slate experience while staying inside the Dash wrapper.",
                    ],
                ),
                demo_section(
                    "6. Fixed-height scrolling",
                    "Tables expand to fit their rows by default. Add a `height` only when you want the header and pagination to stay put while the body scrolls inside a constrained viewport.",
                    dmc.Stack(
                        [
                            docs_control_panel(
                                "Try different viewport sizes",
                                "Switch between natural height and fixed-height scrolling to see how the same dataset behaves in each layout.",
                                dmc.SegmentedControl(
                                    id="scrolling-height-mode",
                                    value="300",
                                    fullWidth=True,
                                    data=[
                                        {"label": "Auto", "value": "auto"},
                                        {"label": "240 px", "value": "240"},
                                        {"label": "300 px", "value": "300"},
                                        {"label": "380 px", "value": "380"},
                                    ],
                                ),
                            ),
                            html.Div(
                                id="scrolling-demo-container",
                                children=make_scrolling_demo_table(
                                    "scrolling-live-table",
                                    height=300,
                                ),
                            ),
                            dmc.Text(
                                id="scrolling-demo-copy",
                                size="sm",
                                c="dimmed",
                                children=(
                                    "The table is currently using a 300 pixel viewport, so the "
                                    "body scrolls while the header stays anchored."
                                ),
                            ),
                            source_code_accordion(
                                "Show Python for scrollable tables",
                                code_component=dmc.Code(
                                    id="scrolling-code-output",
                                    block=True,
                                    children=build_scrolling_code(height=300),
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "This matches the DMC docs style of letting you change the prop that matters and immediately see the layout update.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-scrolling",
                    methods=["update_layout(height=...)", "scrollAreaProps"],
                    highlights=[
                        "Leave `height` unset when the table should size itself based on content.",
                        "Set `height` when the table needs to live inside dashboards, tabs, or cards with a predictable footprint.",
                        "The same column and pagination setup works in both modes, which makes this a clean progressive enhancement.",
                    ],
                ),
                demo_section(
                    "7. Infinite scrolling",
                    "Use the existing scrollEdge prop with a fixed height to append more records as the user reaches the bottom.",
                    dmc.Stack(
                        [
                            make_infinite_scroll_demo_table(),
                            dmc.Group(
                                [
                                    dmc.Code(
                                        id="infinite-scroll-status",
                                        block=True,
                                        children=format_infinite_scroll_status(
                                            INFINITE_SCROLL_RECORDS[
                                                :INFINITE_SCROLL_BATCH_SIZE
                                            ]
                                        ),
                                    ),
                                    dmc.Button(
                                        "Reset records",
                                        id="infinite-scroll-reset",
                                        n_clicks=0,
                                        variant="light",
                                    ),
                                ],
                                align="start",
                                justify="space-between",
                            ),
                            source_code_accordion(
                                "Show Python for infinite scrolling",
                                code=build_infinite_scrolling_code(),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "This keeps infinite loading fully in Dash callbacks: listen for scrollEdge == bottom, append a batch, and leave the table itself declarative.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-infinite-scroll",
                    methods=["scrollEdge", "@callback", "height"],
                    highlights=[
                        "Infinite loading depends on a fixed-height scroll container so the component can detect when the user reaches the bottom edge.",
                        "The callback only appends more rows; it does not need to rebuild the table or change column definitions.",
                        "A reset button is helpful in documentation because it lets users replay the interaction without refreshing the whole page.",
                    ],
                ),
                demo_section(
                    "8. Table properties",
                    "This playground is closest to the DMC docs experience: flip switches, opt into optional values, and watch the generated Dash code update alongside the live table.",
                    dmc.Stack(
                        [
                            dmc.Paper(
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                boolean_table_control(
                                                    "table-props-row-borders",
                                                    "Row borders",
                                                    TABLE_PROPERTIES_DEFAULTS[
                                                        "withRowBorders"
                                                    ],
                                                ),
                                                boolean_table_control(
                                                    "table-props-column-borders",
                                                    "Column borders",
                                                    TABLE_PROPERTIES_DEFAULTS[
                                                        "withColumnBorders"
                                                    ],
                                                ),
                                                boolean_table_control(
                                                    "table-props-striped",
                                                    "Striped",
                                                    TABLE_PROPERTIES_DEFAULTS[
                                                        "striped"
                                                    ],
                                                ),
                                                boolean_table_control(
                                                    "table-props-highlight",
                                                    "Highlight on hover",
                                                    TABLE_PROPERTIES_DEFAULTS[
                                                        "highlightOnHover"
                                                    ],
                                                ),
                                                boolean_table_control(
                                                    "table-props-table-border",
                                                    "Table border",
                                                    TABLE_PROPERTIES_DEFAULTS[
                                                        "withTableBorder"
                                                    ],
                                                ),
                                                boolean_table_control(
                                                    "table-props-no-header",
                                                    "No header",
                                                    TABLE_PROPERTIES_DEFAULTS[
                                                        "noHeader"
                                                    ],
                                                ),
                                            ],
                                            style={
                                                "display": "grid",
                                                "gap": "1rem",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                option_table_control(
                                                    "Shadow",
                                                    "table-props-shadow-enabled",
                                                    "table-props-shadow-value",
                                                    TABLE_SIZE_OPTIONS,
                                                ),
                                                option_table_control(
                                                    "Horizontal spacing",
                                                    "table-props-horizontal-enabled",
                                                    "table-props-horizontal-value",
                                                    TABLE_SIZE_OPTIONS,
                                                    checked=True,
                                                    value="lg",
                                                ),
                                                option_table_control(
                                                    "Vertical spacing",
                                                    "table-props-vertical-enabled",
                                                    "table-props-vertical-value",
                                                    TABLE_SIZE_OPTIONS,
                                                ),
                                                option_table_control(
                                                    "Font size",
                                                    "table-props-font-enabled",
                                                    "table-props-font-value",
                                                    TABLE_SIZE_OPTIONS,
                                                ),
                                                option_table_control(
                                                    "Border radius",
                                                    "table-props-radius-enabled",
                                                    "table-props-radius-value",
                                                    TABLE_SIZE_OPTIONS,
                                                ),
                                                option_table_control(
                                                    "Vertical alignment",
                                                    "table-props-align-enabled",
                                                    "table-props-align-value",
                                                    TABLE_ALIGN_OPTIONS,
                                                ),
                                            ],
                                            style={
                                                "display": "grid",
                                                "gap": "1rem",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "grid",
                                        "gridTemplateColumns": (
                                            "repeat(auto-fit, minmax(280px, 1fr))"
                                        ),
                                        "gap": "1.5rem",
                                    },
                                ),
                                withBorder=True,
                                radius="md",
                                p="lg",
                            ),
                            dmdt.DataTable(
                                id="table-properties-table",
                                data=EMPLOYEES[:5],
                                columns=TABLE_PROPERTIES_COLUMNS,
                                paginationMode="none",
                                radius="lg",
                                style=TABLE_PROPERTIES_VISUAL_STYLE,
                                withRowBorders=TABLE_PROPERTIES_DEFAULTS[
                                    "withRowBorders"
                                ],
                                withColumnBorders=TABLE_PROPERTIES_DEFAULTS[
                                    "withColumnBorders"
                                ],
                                striped=TABLE_PROPERTIES_DEFAULTS["striped"],
                                highlightOnHover=TABLE_PROPERTIES_DEFAULTS[
                                    "highlightOnHover"
                                ],
                                withTableBorder=TABLE_PROPERTIES_DEFAULTS[
                                    "withTableBorder"
                                ],
                                noHeader=TABLE_PROPERTIES_DEFAULTS["noHeader"],
                                horizontalSpacing=TABLE_PROPERTIES_DEFAULTS[
                                    "horizontalSpacing"
                                ],
                            ),
                            source_code_accordion(
                                "Show generated Python for these table props",
                                code_component=dmc.Code(
                                    id="table-properties-generated-code",
                                    block=True,
                                    children=build_table_properties_code(
                                        TABLE_PROPERTIES_DEFAULTS
                                    ),
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "The code sample mirrors the fluent Dash API instead of the original React example, so users can copy it directly.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-table-props",
                    methods=["update_layout()", "withRowBorders", "horizontalSpacing"],
                    highlights=[
                        "Use the boolean switches for high-impact visual changes such as borders, striping, and hover styling.",
                        "Optional Mantine size props are easier to explain when the input that enables them sits next to the value selector.",
                        "Generating copy-pasteable Python from the active state is especially helpful when you want docs users to leave with working Dash code.",
                    ],
                ),
                category_divider(
                    "Columns and structure",
                    "This group covers the shape of the table itself: columns, filters, grouped headers, resizing, persistence, and structural affordances.",
                    category_id="category-columns-and-structure",
                ),
                demo_section(
                    "9. Column properties and styling",
                    "Column width, alignment, responsive visibility, ellipsis, footers, sparklines, and DMC component renders can all be layered on with update_columns().",
                    dmc.Stack(
                        [
                            make_column_properties_demo_table(),
                            dmc.Code(
                                id="column-action-output",
                                block=True,
                                children="Click an action icon to show the action and row ID.",
                            ),
                            source_code_accordion(
                                "Show Python for column customization",
                                code=build_column_properties_code(),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "This mirrors the upstream Mantine DataTable column-properties examples and extends them with Dash component templates such as Sparklines and ActionIconGroup cell actions.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-column-props",
                    methods=["update_columns()", "template", "presentation"],
                    highlights=[
                        "Column definitions can mix standard text cells with currency, badges, progress bars, links, and small chart components.",
                        "This is a good section to explain how far you can get before you need any bespoke cell renderer logic.",
                        "The action column also shows how clickable Dash components can still emit clear table payloads.",
                    ],
                ),
                demo_section(
                    "10. Column searching and filtering",
                    "Build column-level search and filter UIs with Dash Mantine Components, then feed the filtered records back through Dash callbacks.",
                    dmc.Stack(
                        [
                            make_column_filtering_demo_table(),
                            source_code_accordion(
                                "Show Python for column filters",
                                code=build_column_filtering_code(),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "Mantine popovers nested inside a column filter popover should disable portals, so the MultiSelect and DatePickerInput examples set `withinPortal=False` via `comboboxProps` and `popoverProps`.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-column-filtering",
                    methods=["filter", "filtering", "filterPopoverProps"],
                    highlights=[
                        "Each column can own a purpose-built DMC control instead of forcing all filtering through a global toolbar.",
                        "The callback rebuilds both `data` and `columns`, which lets the filter UI reflect active state visually.",
                        "The popover note is important when you embed Mantine inputs inside other overlays and want the stacking to stay predictable.",
                    ],
                ),
                demo_section(
                    "11. Column dragging and toggling",
                    "Draggable and toggleable columns become much easier to document when users can also reset the saved state. This example keeps the interaction realistic by persisting preferences in local storage, then offers a one-click reset.",
                    dmc.Stack(
                        [
                            docs_control_panel(
                                "Reset persisted column state",
                                "Drag headers or hide columns, then reset the browser-saved preferences by rotating to a fresh storage key.",
                                dmc.Group(
                                    [
                                        dmc.Button(
                                            "Reset saved columns",
                                            id="column-dragging-reset",
                                            n_clicks=0,
                                            variant="light",
                                        ),
                                        dmc.Code(
                                            id="column-dragging-store-key-output",
                                            children="storeColumnsKey: demo-column-dragging-0",
                                        ),
                                    ],
                                    justify="space-between",
                                    align="center",
                                ),
                            ),
                            html.Div(
                                id="column-dragging-demo-container",
                                children=make_column_dragging_demo_table(
                                    "demo-column-dragging-0"
                                ),
                            ),
                            source_code_accordion(
                                "Show Python for draggable and toggleable columns",
                                code_component=dmc.Code(
                                    id="column-dragging-code-output",
                                    block=True,
                                    children=build_column_dragging_code(
                                        "demo-column-dragging-0"
                                    ),
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "Preferences persist in the browser's local storage. Change the key or clear local storage to reset the saved order and visibility state.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-column-dragging",
                    methods=["storeColumnsKey", "draggable", "toggleable"],
                    highlights=[
                        "Persisted column preferences make demos feel real because a reload preserves the choices users just made.",
                        "A reset affordance is worth documenting up front so users understand how to recover the original layout after experimentation.",
                        "Changing the storage key is a clean Dash-friendly way to demonstrate a reset without touching browser APIs directly.",
                    ],
                ),
                demo_section(
                    "12. Column resizing",
                    "Resizable columns use the same fluent API: a table-level `storeColumnsKey` plus per-column `resizable=True` updates.",
                    dmc.Stack(
                        [
                            make_column_resizing_demo_table(),
                            source_code_accordion(
                                "Show Python for resizable columns",
                                code=build_column_resizing_code(),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "Drag a header edge to resize a column. Double-clicking the resize handle restores the original width defined in the column config.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-column-resizing",
                    methods=["resizable", "storeColumnsKey"],
                    highlights=[
                        "Resizing shares the same persistence model as dragging and toggling, so the mental model stays consistent.",
                        "Documenting the double-click reset gesture is helpful because users do not always discover it on their own.",
                        "This is a small API surface area with a big usability payoff for dense operational tables.",
                    ],
                ),
                demo_section(
                    "13. Column grouping",
                    "Group related columns under shared headers, including nested group trees built with ColumnGroup().",
                    dmc.Stack(
                        [
                            make_group_columns_demo_table(),
                            source_code_accordion(
                                "Show Python for grouped columns",
                                code=build_group_columns_code(),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "The helper can now express nested group hierarchies as well as flat grouped headers, which makes wide operational tables easier to structure.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-grouping",
                    methods=["group_columns()", "ColumnGroup()", "groups"],
                    highlights=[
                        "Grouped headers help users parse wide tables by communicating which columns belong together conceptually.",
                        "Nested groups are useful when one top-level section still contains smaller conceptual clusters such as identity, organization, or financial metrics.",
                        "You can style groups independently, which is useful when one section of the table deserves stronger visual emphasis.",
                        "Because the groups stay declarative, the feature remains easy to combine with sorting, pinning, and responsive visibility.",
                    ],
                ),
                category_divider(
                    "Rows and interaction",
                    "The next examples shift from structure to behavior: row styling, row identity, drag-and-drop, click payloads, and inline editing.",
                    category_id="category-rows-and-interaction",
                ),
                demo_section(
                    "14. Row properties",
                    "Style rows with Dash-safe rules for color, background, class names, inline styles, and semantic attributes.",
                    dmc.Stack(
                        [
                            make_row_properties_demo_table(),
                            source_code_accordion(
                                "Show Python for row styling",
                                code=build_row_properties_code(),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "This mirrors Mantine DataTable row styling, but replaces React callbacks with JSON-serializable selector rules for Dash. Hover the Needs Review rows to see the row-level title attribute in action.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-row-props",
                    methods=["update_rows()", "rowBackgroundColor", "rowStyle", "rowAttributes"],
                    highlights=[
                        "Dash-safe selector rules are the key difference from the React API and deserve explicit documentation here.",
                        "You can mix broad rules, such as team-based highlighting, with narrower conditions like score thresholds.",
                        "Row attributes are helpful for QA hooks, accessibility affordances, and browser-native hints such as `title` tooltips.",
                        "Row styling is especially useful for review queues, exception lists, and operational dashboards that need quick visual scanning.",
                    ],
                ),
                demo_section(
                    "15. Row dragging",
                    "Enable Dash-native row reordering with update_rows(draggable=True); the reordered records are written back to the table data prop.",
                    dmc.Stack(
                        [
                            make_row_dragging_demo_table(),
                            html.Pre(
                                id="row-dragging-output",
                                style={"margin": 0},
                            ),
                            source_code_accordion(
                                "Show Python for row dragging",
                                code=build_row_dragging_code(),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "This is the Dash-friendly counterpart to the upstream row-dragging example: no custom React wrappers needed, just enable it through update_rows().",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-row-dragging",
                    methods=["update_rows(draggable=True)", "lastRowDragChange"],
                    highlights=[
                        "The table writes the reordered records back to `data`, so you can persist the new order without another translation layer.",
                        "The payload is useful for analytics, audit logs, or syncing the new position to a backend.",
                        "This is a strong example of the wrapper exposing advanced upstream behavior in a way that still feels normal in Dash.",
                    ],
                ),
                demo_section(
                    "16. Row IDs",
                    "Use non-standard or composite record IDs through update_rows(idAccessor=...).",
                    dmc.Stack(
                        [
                            make_row_ids_demo_table(),
                            dmc.Code(
                                id="row-ids-output",
                                block=True,
                                children='Selected record ids: ["Platform:Avery Stone"]',
                            ),
                            source_code_accordion(
                                "Show Python for custom row IDs",
                                code=build_row_ids_code(),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "String accessors still work, including dot notation, and template-based IDs cover the composite-ID use case from the upstream examples.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-row-ids",
                    methods=["idAccessor", "selectedRecordIds"],
                    highlights=[
                        "Custom IDs are essential when your dataset does not expose a simple integer primary key.",
                        "Dot notation and templated values let you keep the data shape you already have instead of reshaping every row just for selection.",
                        "This is worth documenting because row IDs influence selection, expansion, and drag payloads throughout the component.",
                    ],
                ),
                demo_section(
                    "17. Interactivity",
                    "Handle row and cell clicks through standard Dash callback props, with add_interactivity() applying the hover and pointer affordances.",
                    dmc.Stack(
                        [
                            html.Div(
                                [
                                    dmc.Stack(
                                        [
                                            dmc.Text(
                                                "Handling row clicks",
                                                fw=600,
                                                size="sm",
                                            ),
                                            make_row_click_demo_table(),
                                            html.Pre(
                                                id="interactive-row-click-output",
                                                style={"margin": 0},
                                            ),
                                            source_code_accordion(
                                                "Show Python for row clicks",
                                                code=build_row_click_code(),
                                            ),
                                        ],
                                        gap="md",
                                    ),
                                    dmc.Stack(
                                        [
                                            dmc.Text(
                                                "Handling cell clicks",
                                                fw=600,
                                                size="sm",
                                            ),
                                            make_cell_click_demo_table(),
                                            html.Pre(
                                                id="interactive-cell-click-output",
                                                style={"margin": 0},
                                            ),
                                            source_code_accordion(
                                                "Show Python for cell clicks",
                                                code=build_cell_click_code(),
                                            ),
                                        ],
                                        gap="md",
                                    ),
                                ],
                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                                    "gap": "1rem",
                                },
                            ),
                            dmc.Stack(
                                [
                                    dmc.Text(
                                        "Editable cells on double click",
                                        fw=600,
                                        size="sm",
                                    ),
                                    dmc.Alert(
                                        "Double-click an editable cell to open its configured DMC editor directly under the cell. "
                                        "This example mixes TextInput, RadioGroup, MultiSelect, DateInput, and NumberInput.",
                                        color="blue",
                                        variant="light",
                                    ),
                                    make_inline_edit_demo_table(),
                                    dmc.Code(
                                        id="inline-edit-active-cell-output",
                                        block=True,
                                        children="Double-click an editable cell to inspect the payload.",
                                    ),
                                    dmc.Code(
                                        id="inline-edit-records-output",
                                        block=True,
                                        children=json.dumps(INLINE_EDIT_RECORDS, indent=2),
                                    ),
                                    source_code_accordion(
                                        "Show Python for inline editing",
                                        code=build_inline_edit_code(),
                                    ),
                                ],
                                gap="md",
                            ),
                        ],
                        gap="lg",
                    ),
                    dmc.Text(
                        "The editing overlay now lives inside the table itself, so column props control both the display renderer and the in-place DMC editor.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-interactivity",
                    methods=["rowClick", "cellClick", "cellDoubleClick"],
                    highlights=[
                        "Click payloads are intentionally visible so users can understand exactly what the component sends back to Dash.",
                        "The inline editing example now shows the editor defined right on the column instead of coordinating a separate panel.",
                        "Row, cell, and double-click interactions all compose cleanly with the rest of the wrapper features.",
                    ],
                ),
                demo_section(
                    "18. RTL support",
                    "Right-to-left support is easiest to trust when you can toggle it live. This version lets you switch direction on one table so the changes to pinning, alignment, striping, and pagination are obvious.",
                    dmc.Stack(
                        [
                            docs_control_panel(
                                "Switch layout direction",
                                "Use the segmented control to compare left-to-right and right-to-left rendering with pinned edge columns and pagination.",
                                dmc.SegmentedControl(
                                    id="rtl-direction-control",
                                    value="rtl",
                                    fullWidth=True,
                                    data=[
                                        {"label": "LTR", "value": "ltr"},
                                        {"label": "RTL", "value": "rtl"},
                                    ],
                                ),
                            ),
                            html.Div(
                                id="rtl-demo-container",
                                children=make_rtl_support_demo_table(
                                    "rtl-live-table",
                                    direction="rtl",
                                    height=260,
                                ),
                            ),
                            dmc.Text(
                                id="rtl-demo-copy",
                                size="sm",
                                c="dimmed",
                                children=(
                                    "RTL mode is active, so the table is rendered inside a "
                                    "right-to-left Mantine direction context."
                                ),
                            ),
                            source_code_accordion(
                                "Show Python for RTL tables",
                                code_component=dmc.Code(
                                    id="rtl-code-output",
                                    block=True,
                                    children=build_rtl_support_code(
                                        direction="rtl",
                                        height=260,
                                    ),
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "The Dash wrapper applies Mantine direction context internally, so the fluent API only needs update_layout(direction='rtl') for the table to switch into right-to-left mode.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-rtl",
                    methods=["direction", "pinFirstColumn", "pinLastColumn"],
                    highlights=[
                        "Direction is a table-level concern, so you can verify the behavior without rebuilding your column definitions.",
                        "Pinned edge columns are especially useful to test here because they quickly reveal whether the layout has mirrored correctly.",
                        "A live direction toggle makes this easier to understand than a pair of static screenshots or separate examples.",
                    ],
                ),
                category_divider(
                    "Advanced patterns",
                    "These examples highlight the newer helper APIs and more customized presentation options that go beyond the common starter patterns.",
                    category_id="category-advanced-patterns",
                ),
                demo_section(
                    "19. Advanced selection and pagination",
                    "This example focuses on the newer fluent helpers and config builders: selection rules, colored pagination, custom sort icons, and a helper-driven setup that stays readable from Python.",
                    dmc.Stack(
                        [
                            dmc.Alert(
                                "Rows in Needs Review are intentionally not selectable, the checkboxes are color-coded by status, and the pagination controls use custom active colors.",
                                color="blue",
                                variant="light",
                            ),
                            make_advanced_controls_demo_table(),
                            source_code_accordion(
                                "Show Python for advanced selection, sorting, and pagination",
                                code=build_advanced_controls_code(),
                                description=(
                                    "This is the best copy-paste example for the new helper "
                                    "classes: SelectionConfig, PaginationConfig, update_selection(), "
                                    "update_pagination(), update_sorting(), and update_search()."
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "The table stays fully declarative even with custom sort icons, disabled selection rules, and pagination styling layered on top.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-advanced-controls",
                    methods=[
                        "SelectionConfig()",
                        "PaginationConfig()",
                        "update_selection()",
                        "update_pagination()",
                        "update_sorting()",
                        "update_search()",
                    ],
                    highlights=[
                        "Helper config objects keep larger demos readable when a table has a lot of related selection or pagination props.",
                        "Rule-based selection is the Dash-safe replacement for callback-style row selectability in the React API.",
                        "Custom sort icons and pagination colors make it easier to align the table with an established design system.",
                    ],
                ),
                demo_section(
                    "20. Custom loaders and empty icons",
                    "Component-based states are useful when the table needs to feel more branded than the built-in defaults. These examples show both a custom loading overlay and the lightweight noRecordsIcon path.",
                    dmc.Stack(
                        [
                            html.Div(
                                [
                                    dmc.Stack(
                                        [
                                            dmc.Text("Custom loader", fw=600, size="sm"),
                                            make_custom_loader_demo_table(),
                                        ],
                                        gap="sm",
                                    ),
                                    dmc.Stack(
                                        [
                                            dmc.Text("No-records icon", fw=600, size="sm"),
                                            make_no_records_icon_demo_table(),
                                        ],
                                        gap="sm",
                                    ),
                                ],
                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                                    "gap": "1rem",
                                },
                            ),
                            source_code_accordion(
                                "Show Python for custom loaders and empty-state icons",
                                code=build_custom_components_code(),
                                description=(
                                    "The layout also demonstrates the newer root style props "
                                    "such as bd and bdrs, which are useful for visually framing "
                                    "table states inside dashboards and docs pages."
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "Use customLoader when the loading surface should carry text or branding, and prefer noRecordsIcon when the built-in empty-state layout is already close to what you need.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-custom-components",
                    methods=["customLoader", "noRecordsIcon", "bd", "bdrs"],
                    highlights=[
                        "Component-based states let the wrapper stay expressive without dropping into custom React.",
                        "The icon-only empty state is lighter weight than a full custom emptyState component, which makes it a good default for many admin screens.",
                        "These examples also show how table container style props can help stateful tables feel intentionally designed instead of purely utilitarian.",
                    ],
                ),
            ],
            gap="xl",
        ),
        size="xl",
        py="xl",
    )
)


@callback(Output("selection-output", "children"), Input("selection-table", "selectedRecordIds"))
def show_selected_rows(selected_ids):
    return f"Selected record ids: {selected_ids or []}"


@callback(
    Output("expanding-rows-output", "children"),
    Input("expanding-rows-table", "expandedRecordIds"),
    Input("expanding-rows-table", "lastExpansionChange"),
)
def show_expanding_rows_state(expanded_ids, last_change):
    payload = None
    if expanded_ids or last_change:
        payload = {
            "expandedRecordIds": expanded_ids or [],
            "lastExpansionChange": last_change,
        }
    return format_payload(payload)


@callback(
    Output("async-nested-tables-table", "data"),
    Output("async-nested-pending-company-ids", "data"),
    Output("async-nested-loader", "disabled"),
    Output("async-nested-loader", "n_intervals"),
    Input("async-nested-tables-table", "expandedRecordIds"),
    State("async-nested-tables-table", "data"),
)
def queue_async_company_load(expanded_ids, current_rows):
    rows = deepcopy(current_rows or build_async_nested_company_records())
    pending_ids = []
    expanded_set = set(expanded_ids or [])

    for row in iter_async_nested_rows(rows):
        if (
            row["id"] in expanded_set
            and "childrenData" in row
            and not row.get("childrenLoaded")
            and not row.get("childrenLoading")
        ):
            row["childrenLoading"] = True
            pending_ids.append(row["id"])

    if not pending_ids:
        return no_update, no_update, no_update, no_update

    return rows, pending_ids, False, 0


@callback(
    Output("async-nested-tables-table", "data", allow_duplicate=True),
    Output("async-nested-pending-company-ids", "data", allow_duplicate=True),
    Output("async-nested-loader", "disabled", allow_duplicate=True),
    Input("async-nested-loader", "n_intervals"),
    State("async-nested-pending-company-ids", "data"),
    State("async-nested-tables-table", "data"),
    prevent_initial_call=True,
)
def hydrate_async_company_load(n_intervals, pending_ids, current_rows):
    if n_intervals < 1 or not pending_ids:
        return no_update, no_update, no_update

    rows = deepcopy(current_rows or build_async_nested_company_records())
    pending_set = set(pending_ids)

    for row in iter_async_nested_rows(rows):
        if row["id"] in pending_set:
            if row.get("nodeType") == "company":
                row["childrenData"] = [
                    build_async_department_record(department)
                    for department in DEPARTMENTS_BY_COMPANY.get(row["id"], [])
                ]
            elif row.get("nodeType") == "department":
                row["childrenData"] = [
                    build_async_employee_record(employee)
                    for employee in EMPLOYEES_BY_DEPARTMENT.get(row["id"], [])
                ]

            row["childrenLoaded"] = True
            row["childrenLoading"] = False

    return rows, [], True


@callback(
    Output("interactive-row-click-output", "children"),
    Input("interactive-row-click-table", "rowClick"),
)
def show_interactive_row_click(payload):
    if not payload:
        return "Click a row to inspect the payload."
    return format_payload(payload)


@callback(
    Output("interactive-cell-click-output", "children"),
    Input("interactive-cell-click-table", "cellClick"),
)
def show_interactive_cell_click(payload):
    if not payload:
        return "Click a Name or Status cell to inspect the payload."
    return format_payload(payload)


@callback(
    Output("inline-edit-active-cell-output", "children"),
    Input("inline-edit-table", "cellDoubleClick"),
)
def activate_inline_edit_cell(cell_double_click):
    if not cell_double_click:
        return "Double-click an editable cell to inspect the payload."

    accessor = cell_double_click.get("columnAccessor")
    if accessor not in INLINE_EDITABLE_ACCESSORS:
        return "Double-click one of the editable columns to open its inline editor."

    return format_payload(cell_double_click)


@callback(
    Output("inline-edit-records-output", "children"),
    Input("inline-edit-table", "data"),
)
def show_inline_edit_records(current_rows):
    return json.dumps(current_rows or [], indent=2)


@callback(
    Output("infinite-scroll-table", "data"),
    Output("infinite-scroll-status", "children"),
    Input("infinite-scroll-table", "scrollEdge"),
    Input("infinite-scroll-reset", "n_clicks"),
    State("infinite-scroll-table", "data"),
)
def update_infinite_scroll_demo(scroll_edge, reset_clicks, current_rows):
    del reset_clicks

    rows = current_rows or INFINITE_SCROLL_RECORDS[:INFINITE_SCROLL_BATCH_SIZE]
    triggered_id = callback_context.triggered_id

    if triggered_id == "infinite-scroll-reset":
        rows = INFINITE_SCROLL_RECORDS[:INFINITE_SCROLL_BATCH_SIZE]
    elif (
        triggered_id == "infinite-scroll-table"
        and scroll_edge
        and scroll_edge.get("edge") == "bottom"
    ):
        next_size = min(
            len(rows) + INFINITE_SCROLL_BATCH_SIZE,
            len(INFINITE_SCROLL_RECORDS),
        )
        rows = INFINITE_SCROLL_RECORDS[:next_size]

    return rows, format_infinite_scroll_status(rows)


@callback(
    Output("states-demo-container", "children"),
    Output("states-demo-copy", "children"),
    Output("states-code-output", "children"),
    Input("states-view-mode", "value"),
    Input("states-loader-type", "value"),
    Input("states-loader-color", "value"),
    Input("states-loader-size", "value"),
    Input("states-loader-blur", "value"),
    Input("states-empty-text", "value"),
    Input("states-table-min-height", "value"),
    prevent_initial_call=True,
)
def update_states_demo(
    state_mode,
    loader_type,
    loader_color,
    loader_size,
    loader_blur,
    empty_text,
    table_min_height,
):
    config = resolve_states_demo_config(
        state_mode=state_mode,
        loader_type=loader_type,
        loader_color=loader_color,
        loader_size=loader_size,
        loader_blur=loader_blur,
        empty_text=empty_text,
        table_min_height=table_min_height,
    )

    if config["state_mode"] == "loading":
        description = (
            f'Loading mode keeps the current rows on screen and overlays the '
            f'{config["loader_type"]} loader in {config["loader_color"]}.'
        )
    elif config["state_mode"] == "empty":
        description = (
            f'Empty mode removes the rows and shows the built-in no-records '
            f'state with the "{config["empty_text"]}" message.'
        )
    else:
        description = (
            "Loaded mode shows the baseline table with records and no overlay, "
            "so you can compare it directly against the loading and empty variants."
        )

    return (
        make_states_demo_table("states-live-table", **config),
        description,
        build_states_code(**config),
    )


@callback(
    Output("scrolling-demo-container", "children"),
    Output("scrolling-demo-copy", "children"),
    Output("scrolling-code-output", "children"),
    Input("scrolling-height-mode", "value"),
    prevent_initial_call=True,
)
def update_scrolling_demo(height_mode):
    if height_mode == "auto":
        return (
            make_scrolling_demo_table("scrolling-live-table"),
            "Auto height is active, so the table expands to fit all rendered rows without introducing an internal scroll area.",
            build_scrolling_code(),
        )

    height = int(height_mode or 300)
    return (
        make_scrolling_demo_table("scrolling-live-table", height=height),
        (
            f"The table is currently using a {height} pixel viewport, so the body "
            "scrolls while the header stays anchored."
        ),
        build_scrolling_code(height=height),
    )


@callback(
    Output("column-dragging-demo-container", "children"),
    Output("column-dragging-store-key-output", "children"),
    Output("column-dragging-code-output", "children"),
    Input("column-dragging-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_column_dragging_demo(n_clicks):
    store_key = f"demo-column-dragging-{n_clicks or 0}"
    return (
        make_column_dragging_demo_table(store_key),
        f"storeColumnsKey: {store_key}",
        build_column_dragging_code(store_key),
    )


@callback(
    Output("rtl-demo-container", "children"),
    Output("rtl-demo-copy", "children"),
    Output("rtl-code-output", "children"),
    Input("rtl-direction-control", "value"),
    prevent_initial_call=True,
)
def update_rtl_demo(direction):
    direction = direction or "rtl"
    description = (
        "RTL mode is active, so the table is rendered inside a right-to-left "
        "Mantine direction context."
        if direction == "rtl"
        else "LTR mode is active, so the table uses the default left-to-right Mantine direction context."
    )
    return (
        make_rtl_support_demo_table(
            "rtl-live-table",
            direction=direction,
            height=260,
        ),
        description,
        build_rtl_support_code(direction=direction, height=260),
    )


@callback(
    Output("row-dragging-output", "children"),
    Input("row-dragging-table", "lastRowDragChange"),
)
def show_row_dragging_payload(payload):
    if not payload:
        return "Drag a row to reorder the dataset and inspect the payload."
    return format_payload(payload)


@callback(Output("column-action-output", "children"), Input("column-properties-table", "cellClick"))
def show_column_action(payload):
    if not payload or payload.get("columnAccessor") != "actions":
        return "Click an action icon to show the action and row ID."

    action = payload.get("action")
    row_id = payload.get("recordId")

    if not action:
        return format_payload(payload)

    return f"Action: {action.title()}, Row ID: {row_id}"


@callback(Output("row-ids-output", "children"), Input("row-ids-table", "selectedRecordIds"))
def show_selected_composite_row_ids(selected_ids):
    return f"Selected record ids: {selected_ids or []}"


@callback(
    Output("column-filtering-table", "data"),
    Output("column-filtering-table", "columns"),
    Input("column-name-filter", "value"),
    Input("column-team-filter", "value"),
    Input("column-start-date-from-filter", "value"),
    Input("column-start-date-to-filter", "value"),
    Input("column-score-filter", "value"),
    Input("column-status-filter", "value"),
    prevent_initial_call=True,
)
def update_column_filtering_table(
    name_query,
    selected_teams,
    start_date_from,
    start_date_to,
    score_range,
    selected_status,
):
    table = make_column_filtering_demo_table(
        name_query=name_query,
        selected_teams=selected_teams,
        start_date_range=[start_date_from, start_date_to],
        score_range=score_range,
        selected_status=selected_status,
    )
    return table.data, table.columns


@callback(
    Output("table-properties-table", "withRowBorders"),
    Output("table-properties-table", "withColumnBorders"),
    Output("table-properties-table", "striped"),
    Output("table-properties-table", "highlightOnHover"),
    Output("table-properties-table", "withTableBorder"),
    Output("table-properties-table", "noHeader"),
    Output("table-properties-table", "shadow"),
    Output("table-properties-table", "horizontalSpacing"),
    Output("table-properties-table", "verticalSpacing"),
    Output("table-properties-table", "fz"),
    Output("table-properties-table", "borderRadius"),
    Output("table-properties-table", "verticalAlign"),
    Output("table-props-shadow-value", "disabled"),
    Output("table-props-horizontal-value", "disabled"),
    Output("table-props-vertical-value", "disabled"),
    Output("table-props-font-value", "disabled"),
    Output("table-props-radius-value", "disabled"),
    Output("table-props-align-value", "disabled"),
    Output("table-properties-generated-code", "children"),
    Input("table-props-row-borders", "checked"),
    Input("table-props-column-borders", "checked"),
    Input("table-props-striped", "checked"),
    Input("table-props-highlight", "checked"),
    Input("table-props-table-border", "checked"),
    Input("table-props-no-header", "checked"),
    Input("table-props-shadow-enabled", "checked"),
    Input("table-props-shadow-value", "value"),
    Input("table-props-horizontal-enabled", "checked"),
    Input("table-props-horizontal-value", "value"),
    Input("table-props-vertical-enabled", "checked"),
    Input("table-props-vertical-value", "value"),
    Input("table-props-font-enabled", "checked"),
    Input("table-props-font-value", "value"),
    Input("table-props-radius-enabled", "checked"),
    Input("table-props-radius-value", "value"),
    Input("table-props-align-enabled", "checked"),
    Input("table-props-align-value", "value"),
)
def update_table_properties_demo(
    with_row_borders,
    with_column_borders,
    striped,
    highlight_on_hover,
    with_table_border,
    no_header,
    shadow_enabled,
    shadow_value,
    horizontal_enabled,
    horizontal_value,
    vertical_enabled,
    vertical_value,
    font_enabled,
    font_value,
    radius_enabled,
    radius_value,
    align_enabled,
    align_value,
):
    config = {
        "withRowBorders": bool(with_row_borders),
        "withColumnBorders": bool(with_column_borders),
        "striped": bool(striped),
        "highlightOnHover": bool(highlight_on_hover),
        "withTableBorder": bool(with_table_border),
        "noHeader": bool(no_header),
        "shadow": resolve_optional_value(shadow_enabled, shadow_value),
        "horizontalSpacing": resolve_optional_value(
            horizontal_enabled, horizontal_value
        ),
        "verticalSpacing": resolve_optional_value(vertical_enabled, vertical_value),
        "fontSize": resolve_optional_value(font_enabled, font_value),
        "borderRadius": resolve_optional_value(radius_enabled, radius_value),
        "verticalAlign": resolve_optional_value(align_enabled, align_value),
    }

    return (
        config["withRowBorders"],
        config["withColumnBorders"],
        config["striped"],
        config["highlightOnHover"],
        config["withTableBorder"],
        config["noHeader"],
        config["shadow"],
        config["horizontalSpacing"],
        config["verticalSpacing"],
        config["fontSize"],
        config["borderRadius"],
        config["verticalAlign"],
        not shadow_enabled,
        not horizontal_enabled,
        not vertical_enabled,
        not font_enabled,
        not radius_enabled,
        not align_enabled,
        build_table_properties_code(config),
    )


@callback(
    Output("server-table", "data"),
    Output("server-table", "totalRecords"),
    Output("server-table", "page"),
    Input("server-search", "value"),
    Input("server-table", "page"),
    Input("server-table", "recordsPerPage"),
    Input("server-table", "sortStatus"),
)
def update_server_table(search_value, page, records_per_page, sort_status):
    page = page or 1
    records_per_page = records_per_page or 4
    filtered = filter_and_sort(EMPLOYEES, search_value, sort_status)
    max_page = max(1, (len(filtered) + records_per_page - 1) // records_per_page)
    page = min(page, max_page)
    start = (page - 1) * records_per_page
    end = start + records_per_page
    return filtered[start:end], len(filtered), page


if __name__ == "__main__":
    app.run(debug=False)
