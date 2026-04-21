"""Interactive documentation app for Dash Mantine DataTable.

This module doubles as a local sandbox and a curated example gallery. Each
section is designed to be copy-paste friendly for Dash users while still
showing how the wrapper extends Mantine DataTable with Dash-native patterns
such as callback payloads, selector rules, chainable update helpers, and
component-based templates.
"""

import ast
import json
import os
import re
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

import dash_mantine_components as dmc
import dash_mantine_datatable as dmdt
from dash import ALL, Dash, Input, Output, State, callback, callback_context, dcc, html, no_update
from dash_iconify import DashIconify as _DashIconifyComponent

try:
    import yfinance as yf
except ImportError:  # pragma: no cover - optional demo dependency
    yf = None


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
STOCK_PORTFOLIO_DEFAULT_TICKERS = ["GME", "SHEL", "AAPL", "MARA", "KO", "JPM"]
STOCK_PORTFOLIO_HISTORY_PERIOD = "3mo"


def normalize_stock_ticker(value):
    return str(value or "").strip().upper()


def coerce_numeric(value):
    try:
        if value in (None, "", "nan"):
            return None
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def build_stock_portfolio_placeholder_record(ticker_symbol, row_id):
    symbol = normalize_stock_ticker(ticker_symbol)
    return {
        "id": row_id,
        "ticker": symbol,
        "_queryTicker": symbol,
        "Exchange": "",
        "sector": "",
        "lastValue": None,
        "marketCap": None,
        "priceTargetLow": None,
        "priceTargetMedian": None,
        "priceTargetHigh": None,
        "sparkline": [],
        "sparklineLabel": [],
        "sparklineColor": "blue",
        "_loadError": None,
    }


def build_stock_portfolio_placeholder_records(tickers=None):
    return [
        build_stock_portfolio_placeholder_record(ticker_symbol, row_id)
        for row_id, ticker_symbol in enumerate(
            tickers or STOCK_PORTFOLIO_DEFAULT_TICKERS,
            start=1,
        )
    ]


def load_stock_portfolio_record(ticker_symbol, row_id):
    placeholder = build_stock_portfolio_placeholder_record(ticker_symbol, row_id)
    symbol = placeholder["_queryTicker"]

    if not symbol:
        placeholder["_loadError"] = "Missing ticker symbol."
        return placeholder

    if yf is None:
        placeholder["_loadError"] = "Install yfinance to load live market data."
        return placeholder

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        fast_info = dict(getattr(ticker, "fast_info", {}) or {})
        analyst_targets = dict(getattr(ticker, "analyst_price_targets", {}) or {})
        history = ticker.history(period=STOCK_PORTFOLIO_HISTORY_PERIOD)

        close_values = []
        if history is not None and not history.empty and "Close" in history:
            close_values = [
                round(float(value), 2)
                for value in history["Close"].dropna().tolist()
            ]

        return {
            "id": row_id,
            "ticker": info.get("displayName") or info.get("shortName") or symbol,
            "_queryTicker": symbol,
            "Exchange": fast_info.get("exchange") or info.get("exchange") or "",
            "sector": info.get("sector") or info.get("industry") or "",
            "lastValue": coerce_numeric(analyst_targets.get("current")),
            "marketCap": coerce_numeric(fast_info.get("marketCap")),
            "priceTargetLow": coerce_numeric(analyst_targets.get("low")),
            "priceTargetMedian": coerce_numeric(analyst_targets.get("median")),
            "priceTargetHigh": coerce_numeric(analyst_targets.get("high")),
            "sparkline": close_values,
            "sparklineLabel": close_values,
            "sparklineColor": "blue",
            "_loadError": None,
        }
    except Exception as exc:  # pragma: no cover - network/runtime dependent
        placeholder["_loadError"] = f"{type(exc).__name__}: {exc}"
        return placeholder


def load_stock_portfolio_records(tickers=None):
    symbols = list(tickers or STOCK_PORTFOLIO_DEFAULT_TICKERS)
    records = [
        load_stock_portfolio_record(ticker_symbol, row_id)
        for row_id, ticker_symbol in enumerate(symbols, start=1)
    ]

    failures = [
        record["_queryTicker"]
        for record in records
        if record.get("_loadError")
    ]
    if yf is None:
        status = "Install `yfinance` to enable the live stock portfolio demo."
    elif failures:
        status = (
            "Live yfinance data loaded with gaps for: "
            + ", ".join(failures)
        )
    else:
        status = (
            "Loaded live yfinance data for "
            + ", ".join(record["_queryTicker"] for record in records)
            + "."
        )

    return records, status


STOCK_PORTFOLIO_RECORDS = build_stock_portfolio_placeholder_records()
STOCK_PORTFOLIO_STATUS = "Loading live yfinance data..."
STOCK_PORTFOLIO_COLUMNS = [
    {"accessor": "ticker", "editable": True, "editor": dmc.TextInput(label="ticker")},
    {"accessor": "Exchange"},
    {"accessor": "sector"},
    {"accessor": "lastValue"},
    {"accessor": "marketCap"},
    {"accessor": "priceTargetLow"},
    {"accessor": "priceTargetMedian"},
    {"accessor": "priceTargetHigh"},
    {"accessor": "sparkline"},
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
    ("section-api", "0. API reference"),
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
    ("section-stock-portfolio", "20. Stock portfolio"),
    ("section-custom-components", "21. Custom loaders and empty icons"),
]

CATEGORY_LINK_GROUPS = [
    (
        "API reference",
        "Curated definitions, fluent methods, and commonly used keyword arguments for the public Python API.",
        [
            ("section-api", "0. API overview"),
            ("api-datatable", "DataTable"),
            ("api-column", "Column"),
            ("api-column-group", "ColumnGroup"),
            ("api-selection-config", "SelectionConfig"),
            ("api-pagination-config", "PaginationConfig"),
            ("api-row-expansion-config", "RowExpansionConfig"),
        ],
    ),
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
            ("section-stock-portfolio", "20. Stock portfolio"),
            ("section-custom-components", "21. Custom loaders and empty icons"),
        ],
    ),
]

API_REFERENCE_TABLE_COLUMNS = [
    dmdt.Column(
        "name",
        title="Name",
        width=320,
        cellsStyle={
            "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            "fontSize": "0.85rem",
            "whiteSpace": "normal",
        },
    ),
    dmdt.Column(
        "description",
        title="Description",
        width=760,
        cellsStyle={
            "whiteSpace": "normal",
            "lineHeight": 1.45,
        },
    ),
    dmdt.Column(
        "type",
        title="Type",
        width=260,
        cellsStyle={
            "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            "fontSize": "0.85rem",
            "whiteSpace": "normal",
        },
    ),
]

API_REFERENCE_SURFACE_COLUMNS = [
    dmdt.Column(
        "name",
        title="Name",
        width=240,
        cellsStyle={
            "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            "fontSize": "0.84rem",
            "whiteSpace": "normal",
        },
    ),
    dmdt.Column(
        "kind",
        title="Kind",
        width=140,
        cellsStyle={"whiteSpace": "normal"},
    ),
    dmdt.Column(
        "type",
        title="Type",
        width=230,
        cellsStyle={
            "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            "fontSize": "0.84rem",
            "whiteSpace": "normal",
        },
    ),
    dmdt.Column(
        "default",
        title="Default",
        width=160,
        cellsStyle={
            "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            "fontSize": "0.84rem",
            "whiteSpace": "normal",
        },
    ),
    dmdt.Column(
        "description",
        title="Description",
        width=720,
        cellsStyle={
            "whiteSpace": "normal",
            "lineHeight": 1.45,
        },
    ),
]

API_REFERENCE_PARAMETER_COLUMNS = [
    dmdt.Column(
        "name",
        title="Name",
        width=260,
        cellsStyle={
            "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            "fontSize": "0.84rem",
            "whiteSpace": "normal",
        },
    ),
    dmdt.Column(
        "type",
        title="Type",
        width=180,
        cellsStyle={
            "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            "fontSize": "0.84rem",
            "whiteSpace": "normal",
        },
    ),
    dmdt.Column(
        "default",
        title="Default",
        width=160,
        cellsStyle={
            "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            "fontSize": "0.84rem",
            "whiteSpace": "normal",
        },
    ),
    dmdt.Column(
        "description",
        title="Description",
        width=760,
        cellsStyle={
            "whiteSpace": "normal",
            "lineHeight": 1.45,
        },
    ),
]

API_REFERENCE_ITEMS = [
    {
        "id": "api-datatable",
        "name": "DataTable",
        "kind": "component",
        "signature": "dmdt.DataTable(*args, **kwargs)",
        "description": (
            "The main Dash component. Use it to render records, define columns, "
            "control selection and pagination, and read callback payloads back "
            "from the browser."
        ),
        "returns": "Returns a Dash component instance with chainable Python helpers.",
        "methods": [
            {
                "name": "update_layout(**kwargs)",
                "description": "Merge layout, sizing, direction, className, style, and other table-level presentation props.",
                "type": "method -> DataTable",
            },
            {
                "name": "update_table_properties(**kwargs)",
                "description": "Readable alias for `update_layout()` when you are tuning borders, spacing, striped rows, or other table props.",
                "type": "method -> DataTable",
            },
            {
                "name": "update_columns(*columns, selector=None, overwrite=False, **kwargs)",
                "description": "Add new columns or merge updates into existing columns by accessor.",
                "type": "method -> DataTable",
            },
            {
                "name": "group_columns(*groups, selector=None, **kwargs)",
                "description": "Create or update grouped headers, including nested group trees.",
                "type": "method -> DataTable",
            },
            {
                "name": "update_rows(selector=None, **kwargs)",
                "description": "Apply row-level colors, styles, class names, attributes, dragging, IDs, or expansion state.",
                "type": "method -> DataTable",
            },
            {
                "name": "add_interactivity(...)",
                "description": "Enable row or cell pointer-cursor affordances for click, double-click, or context-menu patterns.",
                "type": "method -> DataTable",
            },
            {
                "name": "update_selection(**kwargs)",
                "description": "Update controlled selection props and selection rule settings.",
                "type": "method -> DataTable",
            },
            {
                "name": "update_pagination(**kwargs)",
                "description": "Update page, page size, total records, and pagination appearance props.",
                "type": "method -> DataTable",
            },
            {
                "name": "update_sorting(**kwargs)",
                "description": "Update sort mode, sort status, or sort icon props.",
                "type": "method -> DataTable",
            },
            {
                "name": "update_search(**kwargs)",
                "description": "Update search mode, query text, and searchable accessor props.",
                "type": "method -> DataTable",
            },
            {
                "name": "clear_selection()",
                "description": "Reset `selectedRecordIds` and `selectedRecords` to empty lists.",
                "type": "method -> DataTable",
            },
            {
                "name": "clear_expansion()",
                "description": "Reset `expandedRecordIds` to an empty list.",
                "type": "method -> DataTable",
            },
        ],
        "keyword_arguments": [
            {
                "name": "id",
                "description": "Unique Dash callback identifier for the component.",
                "type": "str | dict",
            },
            {
                "name": "data",
                "description": "Primary row data for the table. This is the preferred Dash-facing records prop.",
                "type": "list[dict]",
            },
            {
                "name": "columns",
                "description": "Column-definition dictionaries that control accessors, formatting, editing, filtering, and rendering.",
                "type": "list[dict]",
            },
            {
                "name": "groups",
                "description": "Grouped-header definitions for multi-column header layouts.",
                "type": "list[dict]",
            },
            {
                "name": "groupBy",
                "description": "Accessor or accessors used to build inline grouped parent rows.",
                "type": "str | list[str]",
            },
            {
                "name": "childRowsAccessor",
                "description": "Accessor for already nested child-row arrays.",
                "type": "str",
            },
            {
                "name": "idAccessor",
                "description": "Record identifier accessor used by selection, expansion, and row updates.",
                "type": "str | dict | list[str]",
            },
            {
                "name": "selectionTrigger",
                "description": "Turns selection on and chooses whether rows are selected by a cell click or checkbox click.",
                "type": "'cell' | 'checkbox'",
            },
            {
                "name": "selectedRecordIds",
                "description": "Controlled selection state. Useful when the rest of the app owns selected rows.",
                "type": "list",
            },
            {
                "name": "rowExpansion",
                "description": "Expansion configuration, usually built with `RowExpansionConfig()`.",
                "type": "dict",
            },
            {
                "name": "rowDragging",
                "description": "Enables drag-and-drop row reordering and emits `lastRowDragChange` payloads.",
                "type": "bool | dict",
            },
            {
                "name": "sortStatus",
                "description": "Controlled sorting descriptor containing the active accessor and direction.",
                "type": "dict",
            },
            {
                "name": "searchQuery",
                "description": "Controlled search text for client or server search flows.",
                "type": "str",
            },
            {
                "name": "page / pageSize / recordsPerPage / totalRecords",
                "description": "Core controlled pagination props for server-backed tables and explicit pagination UIs.",
                "type": "number",
            },
            {
                "name": "paginationMode / sortMode / searchMode",
                "description": "Switch each behavior between client and server control, or disable pagination entirely.",
                "type": "enum",
            },
            {
                "name": "striped / withTableBorder / withColumnBorders / stickyHeader",
                "description": "High-value presentation props that make a first table look polished quickly.",
                "type": "bool",
            },
            {
                "name": "height / minHeight / maxHeight",
                "description": "Sizing props commonly used for fixed-height scrolling layouts.",
                "type": "str | number",
            },
            {
                "name": "emptyState / customLoader / noRecordsIcon",
                "description": "Built-in empty and loading customization points for more branded table states.",
                "type": "component | str",
            },
            {
                "name": "storeColumnsKey",
                "description": "Persists draggable, toggleable, and resizable column state in local storage.",
                "type": "str",
            },
        ],
        "attributes": [
            {
                "name": "data",
                "description": "The current records attached to the table component.",
                "type": "list[dict]",
            },
            {
                "name": "columns",
                "description": "The active column configuration after any fluent updates.",
                "type": "list[dict]",
            },
            {
                "name": "groups",
                "description": "Current grouped-header definitions.",
                "type": "list[dict] | None",
            },
            {
                "name": "selectedRecordIds",
                "description": "Currently selected record identifiers.",
                "type": "list",
            },
            {
                "name": "selectedRecords",
                "description": "Selected record payloads mirrored from the front end.",
                "type": "list",
            },
            {
                "name": "expandedRecordIds",
                "description": "Identifiers for rows that are currently expanded.",
                "type": "list",
            },
            {
                "name": "sortStatus",
                "description": "Current sort descriptor used for client or server sorting.",
                "type": "dict | None",
            },
            {
                "name": "searchQuery",
                "description": "Current search text.",
                "type": "str | None",
            },
            {
                "name": "lastSelectionChange",
                "description": "Latest selection callback payload emitted by the component.",
                "type": "dict | None",
            },
            {
                "name": "lastSortChange",
                "description": "Latest sort callback payload emitted by the component.",
                "type": "dict | None",
            },
            {
                "name": "lastExpansionChange",
                "description": "Latest row-expansion callback payload emitted by the component.",
                "type": "dict | None",
            },
            {
                "name": "lastRowDragChange",
                "description": "Latest row-drag callback payload emitted by the component.",
                "type": "dict | None",
            },
        ],
    },
    {
        "id": "api-column",
        "name": "Column",
        "kind": "helper",
        "signature": "dmdt.Column(accessor=None, /, **kwargs)",
        "description": (
            "Convenience builder for a column-definition dictionary. It keeps "
            "demo code compact and makes default-column props easier to read."
        ),
        "returns": "Returns a plain `dict` that can be used in `columns` or `defaultColumnProps`.",
        "keyword_arguments": [
            {
                "name": "accessor",
                "description": "Record key rendered by the column.",
                "type": "str",
            },
            {
                "name": "title",
                "description": "Human-friendly header label. Defaults to a title-cased accessor when omitted by the front end.",
                "type": "str",
            },
            {
                "name": "presentation",
                "description": "Built-in display mode such as `text`, `number`, `currency`, `date`, `datetime`, `badge`, `link`, `code`, `json`, or `progress`.",
                "type": "str",
            },
            {
                "name": "sortable",
                "description": "Marks the column as sortable.",
                "type": "bool",
            },
            {
                "name": "textAlign",
                "description": "Horizontal alignment for header and cell content.",
                "type": "'left' | 'center' | 'right'",
            },
            {
                "name": "width",
                "description": "Preferred column width, especially useful with dragging or resizing enabled.",
                "type": "number",
            },
            {
                "name": "render",
                "description": "Custom cell renderer template or component.",
                "type": "component | any",
            },
            {
                "name": "editable / editor",
                "description": "Enable inline editing and optionally provide a custom Dash input component.",
                "type": "bool / component",
            },
            {
                "name": "filter",
                "description": "Dash component rendered inside the column filter popover.",
                "type": "component",
            },
            {
                "name": "cellsStyle / titleStyle",
                "description": "Inline style mappings for body cells and header cells.",
                "type": "dict",
            },
            {
                "name": "draggable / toggleable / resizable",
                "description": "Enable column dragging, visibility toggling, or resizing for the column.",
                "type": "bool",
            },
            {
                "name": "defaultToggle",
                "description": "Initial toggle state for optional columns when column toggling is enabled.",
                "type": "bool",
            },
        ],
    },
    {
        "id": "api-column-group",
        "name": "ColumnGroup",
        "kind": "helper",
        "signature": "dmdt.ColumnGroup(group_id=None, /, *, columns=None, groups=None, **kwargs)",
        "description": (
            "Builder for grouped-header dictionaries. Use it for shared "
            "header labels and nested header trees."
        ),
        "returns": "Returns a plain `dict` for use in `groups` or `group_columns()`.",
        "keyword_arguments": [
            {
                "name": "group_id",
                "description": "Stable identifier used when updating existing groups with `group_columns(selector=...)`.",
                "type": "str",
            },
            {
                "name": "title",
                "description": "Visible group label shown above the grouped columns.",
                "type": "str",
            },
            {
                "name": "columns",
                "description": "Column accessors or column dictionaries included in the group.",
                "type": "list[str | dict]",
            },
            {
                "name": "groups",
                "description": "Nested child groups for multi-row header structures.",
                "type": "list[dict]",
            },
            {
                "name": "style",
                "description": "Inline styles applied to the grouped-header cell.",
                "type": "dict",
            },
        ],
    },
    {
        "id": "api-selection-config",
        "name": "SelectionConfig",
        "kind": "helper",
        "signature": "dmdt.SelectionConfig(**kwargs)",
        "description": (
            "Compact builder for selection-related props. It removes `None` "
            "values so larger table declarations stay readable."
        ),
        "returns": "Returns a plain `dict` with `None` values removed.",
        "keyword_arguments": [
            {
                "name": "selectionTrigger",
                "description": "Turns selection on and chooses cell-based or checkbox-based selection.",
                "type": "'cell' | 'checkbox'",
            },
            {
                "name": "selectedRecordIds",
                "description": "Controlled selection IDs.",
                "type": "list",
            },
            {
                "name": "selectedRecords",
                "description": "Controlled selection payloads.",
                "type": "list[dict]",
            },
            {
                "name": "selectableRowRules",
                "description": "Rule objects that determine which rows are selectable.",
                "type": "bool | dict | list",
            },
            {
                "name": "disabledSelectionRowRules",
                "description": "Rules that explicitly disable selection for matching rows.",
                "type": "bool | dict | list",
            },
            {
                "name": "selectionCheckboxRules",
                "description": "Rules that customize checkbox appearance or behavior per row.",
                "type": "dict | list",
            },
            {
                "name": "selectionCheckboxProps / allRecordsSelectionCheckboxProps",
                "description": "Props forwarded to row checkboxes or the header checkbox.",
                "type": "dict",
            },
            {
                "name": "selectionColumnClassName / selectionColumnStyle",
                "description": "Styling hooks for the selection column.",
                "type": "str / dict",
            },
        ],
    },
    {
        "id": "api-pagination-config",
        "name": "PaginationConfig",
        "kind": "helper",
        "signature": "dmdt.PaginationConfig(**kwargs)",
        "description": (
            "Compact builder for pagination-related props. It is especially "
            "useful when a table has several pagination styling and state props."
        ),
        "returns": "Returns a plain `dict` with `None` values removed.",
        "keyword_arguments": [
            {
                "name": "page",
                "description": "Current page number.",
                "type": "number",
            },
            {
                "name": "pageSize / recordsPerPage",
                "description": "Current page size. Both names appear in the API, so demos often set both for clarity.",
                "type": "number",
            },
            {
                "name": "totalRecords",
                "description": "Total row count used for server pagination.",
                "type": "number",
            },
            {
                "name": "recordsPerPageOptions / pageSizeOptions",
                "description": "Available page-size choices shown in the pagination UI.",
                "type": "list[number]",
            },
            {
                "name": "recordsPerPageLabel",
                "description": "Label shown next to the page-size selector.",
                "type": "str",
            },
            {
                "name": "paginationSize",
                "description": "Mantine size token for the pagination controls.",
                "type": "str | number",
            },
            {
                "name": "paginationActiveTextColor / paginationActiveBackgroundColor",
                "description": "Overrides the active page colors so the paginator can match the rest of the app.",
                "type": "str | dict",
            },
            {
                "name": "paginationWithEdges / paginationWithControls",
                "description": "Toggle first/last buttons and previous/next controls.",
                "type": "bool",
            },
        ],
    },
    {
        "id": "api-row-expansion-config",
        "name": "RowExpansionConfig",
        "kind": "helper",
        "signature": "dmdt.RowExpansionConfig(content=None, /, **kwargs)",
        "description": (
            "Builder for row-expansion dictionaries. Use it when expanded rows "
            "should render detail content, nested tables, or callback-driven child views."
        ),
        "returns": "Returns a plain `dict` with `None` values removed.",
        "keyword_arguments": [
            {
                "name": "content",
                "description": "Expansion content rendered when a row opens.",
                "type": "component | any",
            },
            {
                "name": "allowMultiple",
                "description": "Allows more than one row to remain expanded at the same time.",
                "type": "bool",
            },
            {
                "name": "trigger",
                "description": "Controls how expansion is triggered, such as click-driven row expansion.",
                "type": "str",
            },
        ],
    },
]

DATA_TABLE_METADATA_PATH = Path(dmdt.__file__).with_name("metadata.json")
DATA_TABLE_PY_PATH = Path(dmdt.__file__).with_name("DataTable.py")
DATA_TABLE_METADATA = json.loads(DATA_TABLE_METADATA_PATH.read_text(encoding="utf-8"))[
    "src/lib/components/DataTable.react.js"
]["props"]

DATA_TABLE_PROP_DESCRIPTION_OVERRIDES = {
    "paginationMode": "Controls whether pagination is handled on the client, delegated to the server, or disabled entirely.",
    "sortMode": "Controls whether sorting is handled on the client or delegated to the server.",
    "searchMode": "Controls whether search filtering is handled on the client or delegated to the server.",
    "searchQuery": "Controlled search query used for client-side filtering or server-side search callbacks.",
    "searchableAccessors": "Limits client-side search to the listed column accessors.",
    "page": "Controlled current page number.",
    "recordsPerPage": "Controlled rows-per-page value used by the pagination UI.",
    "pageSize": "Controlled page size used by the component's page calculations.",
    "totalRecords": "Total available record count, typically required for server pagination.",
    "sortStatus": "Controlled sorting descriptor containing the active accessor and sort direction.",
    "selectedRecordIds": "Controlled list of selected record identifiers.",
    "selectedRecords": "Selected record payloads mirrored from the current front-end state.",
    "expandedRecordIds": "Controlled list of expanded row identifiers.",
    "selectionTrigger": "Enables row selection and chooses whether it is triggered by cell clicks or checkboxes.",
    "selectionColumnClassName": "Custom class name applied to the selection column.",
    "selectionColumnStyle": "Inline style mapping applied to the selection column.",
    "selectionCheckboxProps": "Props forwarded to each row selection checkbox.",
    "allRecordsSelectionCheckboxProps": "Props forwarded to the header checkbox that selects all rows.",
    "selectableRowRules": "Dash-safe rule objects that determine which rows can be selected.",
    "disabledSelectionRowRules": "Dash-safe rule objects that explicitly disable selection for matching rows.",
    "selectionCheckboxRules": "Dash-safe rule objects that customize checkbox appearance or behavior per row.",
    "rowAttributes": "Static attributes or selector-based rule objects applied to rendered row elements.",
    "rowExpansion": "Configuration for expanded row content, trigger behavior, and multi-row expansion.",
    "rowClick": "Callback payload emitted when a row click occurs.",
    "rowDoubleClick": "Callback payload emitted when a row double-click occurs.",
    "rowContextMenu": "Callback payload emitted when a row context-menu interaction occurs.",
    "cellClick": "Callback payload emitted when a cell click occurs.",
    "cellDoubleClick": "Callback payload emitted when a cell double-click occurs.",
    "cellContextMenu": "Callback payload emitted when a cell context-menu interaction occurs.",
    "pagination": "Callback payload describing the current pagination interaction.",
    "scrollPosition": "Callback payload containing the current scroll offsets.",
    "scrollEdge": "Callback payload emitted when the table reaches a scroll edge.",
    "lastRowDragChange": "Latest row-drag payload, including moved IDs and reordered records.",
    "lastSortChange": "Latest sorting payload emitted by the component.",
    "lastSelectionChange": "Latest selection payload emitted by the component.",
    "lastExpansionChange": "Latest expansion payload emitted by the component.",
    "emptyState": "Custom component or string rendered when the table has no records.",
    "noRecordsIcon": "Custom icon or component shown above the no-records text.",
    "noRecordsText": "Text shown when the table has no records to display.",
    "recordsPerPageOptions": "List of rows-per-page options shown by the pagination control.",
    "pageSizeOptions": "Alternate page-size option list accepted by the component.",
    "recordsPerPageLabel": "Label displayed next to the rows-per-page selector.",
    "paginationSize": "Mantine size token used for the pagination controls.",
    "paginationActiveTextColor": "Active page text color override for the pagination controls.",
    "paginationActiveBackgroundColor": "Active page background color override for the pagination controls.",
    "loadingText": "Text shown inside the built-in loading overlay.",
    "tableProps": "Additional props forwarded to the underlying Mantine table element.",
    "scrollAreaProps": "Additional props forwarded to the Mantine scroll area wrapper.",
    "className": "Custom class name applied to the root table wrapper.",
    "tableClassName": "Custom class name applied to the inner table element.",
    "classNames": "Mantine classNames mapping for internal table parts.",
    "style": "Inline styles applied to the root table wrapper.",
    "styles": "Mantine styles mapping for internal table parts.",
    "radius": "Mantine radius token or explicit value used by the outer table container.",
    "height": "Explicit table height, commonly used to enable internal scrolling.",
    "minHeight": "Minimum table height.",
    "maxHeight": "Maximum table height.",
    "shadow": "Mantine shadow token applied to the outer table container.",
    "bg": "Mantine background style prop applied to the root container.",
    "c": "Mantine text-color style prop applied to the root container.",
    "rowBorderColor": "Border color used between body rows.",
    "stripedColor": "Background color used for striped rows.",
    "highlightOnHoverColor": "Background color used when rows are hovered.",
    "withRowBorders": "Controls whether horizontal borders are shown between rows.",
    "withTableBorder": "Controls whether the table wrapper shows an outer border.",
    "withColumnBorders": "Controls whether vertical borders are shown between columns.",
    "horizontalSpacing": "Horizontal cell padding.",
    "verticalSpacing": "Vertical cell padding.",
    "borderRadius": "Alias-style table border radius setting used by the underlying Mantine table.",
    "striped": "Turns zebra-striping on or off.",
    "highlightOnHover": "Highlights rows on hover.",
    "textSelectionDisabled": "Disables text selection inside the table, useful for interactive rows and cells.",
    "fetching": "Shows the loading overlay while data is being fetched or hydrated.",
    "loaderBackgroundBlur": "Backdrop blur strength used by the built-in loading overlay.",
    "loaderSize": "Size of the built-in loader.",
    "loaderType": "Visual variant of the built-in loader.",
    "loaderColor": "Color used by the built-in loader.",
    "customLoader": "Custom component rendered instead of the built-in loading indicator.",
    "noHeader": "Hides the table header row.",
    "pinFirstColumn": "Pins the first visible data column to the left edge while horizontally scrolling.",
    "pinLastColumn": "Pins the last visible data column to the right edge while horizontally scrolling.",
    "stickyHeader": "Makes the header sticky while the body scrolls vertically.",
    "stickyHeaderOffset": "Offset applied to the sticky header position.",
    "verticalAlign": "Vertical alignment for body cells.",
    "paginationWithEdges": "Shows first-page and last-page controls in the paginator.",
    "paginationWithControls": "Shows previous and next controls in the paginator.",
    "defaultColumnProps": "Default column props merged into every column definition.",
    "defaultColumnRender": "Default Dash render template used when a column does not provide its own renderer.",
    "sortIcons": "Custom sorted and unsorted icons used by sortable columns.",
    "bodyRef": "Ref-like prop exposed for the table body container.",
    "tableRef": "Ref-like prop exposed for the root table container.",
    "setProps": "Dash-managed internal callback used to push property updates back to Python.",
}

DATA_TABLE_METHOD_DETAILS = [
    {
        "name": "update_layout",
        "signature": "update_layout(**kwargs)",
        "description": "Merge layout, sizing, direction, style, and other table-level presentation props into the current table instance.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "radius",
                "description": "Rounded-corner setting for the outer table container.",
                "type": "str | number",
                "default": "",
            },
            {
                "name": "withTableBorder",
                "description": "Shows an outer border around the table wrapper.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "withColumnBorders",
                "description": "Shows vertical borders between columns.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "striped",
                "description": "Turns zebra striping on for alternating rows.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "direction",
                "description": "Switches the table into left-to-right or right-to-left layout mode.",
                "type": "'ltr' | 'rtl'",
                "default": "",
            },
            {
                "name": "height / minHeight / maxHeight",
                "description": "Common sizing props used for fixed-height scrolling and constrained layouts.",
                "type": "str | number",
                "default": "",
            },
            {
                "name": "bg",
                "description": "Mantine background style prop applied to the root container.",
                "type": "str | dict",
                "default": "",
            },
            {
                "name": "textSelectionDisabled",
                "description": "Disables text selection, useful for interactive rows and cells.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "pinFirstColumn / pinLastColumn",
                "description": "Pins the first or last visible column while horizontally scrolling.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "loadingText / loaderType / loaderColor",
                "description": "Common loading-overlay customization props used by the examples.",
                "type": "str",
                "default": "",
            },
            {
                "name": "**kwargs",
                "description": "Any other layout-oriented props such as `style`, `className`, `tableProps`, `scrollAreaProps`, or Mantine style props.",
                "type": "component props",
                "default": "",
            }
        ],
        "notes": [
            "Mapping props such as `style`, `styles`, `classNames`, `tableProps`, and `scrollAreaProps` are merged recursively.",
            "Python aliases such as `dir` and `group_by` are normalized before the update is applied.",
        ],
    },
    {
        "name": "update_table_properties",
        "signature": "update_table_properties(**kwargs)",
        "description": "Readable alias for `update_layout()` when you are adjusting table behavior, borders, spacing, striped rows, or default-column settings.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "withRowBorders / withTableBorder / withColumnBorders",
                "description": "Controls the row, outer, and vertical border treatment.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "horizontalSpacing / verticalSpacing",
                "description": "Cell padding controls used heavily in the table-properties demo.",
                "type": "str | number",
                "default": "",
            },
            {
                "name": "verticalAlign",
                "description": "Vertical alignment for body cells.",
                "type": "'top' | 'center' | 'bottom'",
                "default": "",
            },
            {
                "name": "striped / highlightOnHover / stickyHeader",
                "description": "High-value behavior and presentation toggles for body rendering and header behavior.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "defaultColumnProps",
                "description": "Default props merged into every column definition.",
                "type": "dict",
                "default": "",
            },
            {
                "name": "**kwargs",
                "description": "Any other table-level props that read more clearly when grouped under a table-properties call.",
                "type": "component props",
                "default": "",
            }
        ],
        "notes": [
            "This method exists for readability in fluent chains; behavior matches `update_layout()`.",
        ],
    },
    {
        "name": "update_columns",
        "signature": "update_columns(*columns, selector=None, overwrite=False, **kwargs)",
        "description": "Add new columns or merge updates into existing columns by accessor.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "*columns",
                "description": "Accessor strings or column dictionaries to add or update.",
                "type": "str | dict",
                "default": "",
            },
            {
                "name": "selector",
                "description": "Accessor or collection of accessors identifying the columns to update. When omitted, incoming columns target their own accessor values.",
                "type": "Any",
                "default": "None",
            },
            {
                "name": "overwrite",
                "description": "Replace matching column definitions instead of merging into them.",
                "type": "bool",
                "default": "False",
            },
            {
                "name": "title / width / presentation / textAlign",
                "description": "Most common display and formatting props used to shape a column quickly.",
                "type": "column props",
                "default": "",
            },
            {
                "name": "sortable / ellipsis",
                "description": "Frequently used boolean props for sorting and truncation behavior.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "cellsStyle / titleStyle",
                "description": "Inline style mappings for body cells and header cells.",
                "type": "dict",
                "default": "",
            },
            {
                "name": "render",
                "description": "Custom render template or Dash component for cell content.",
                "type": "component | any",
                "default": "",
            },
            {
                "name": "editable / editor",
                "description": "Turns on inline editing and optionally supplies a custom editor component.",
                "type": "bool / component",
                "default": "",
            },
            {
                "name": "filter / filtering / filterPopoverProps",
                "description": "Column filter UI and related behavior.",
                "type": "component / bool / dict",
                "default": "",
            },
            {
                "name": "draggable / toggleable / resizable / defaultToggle",
                "description": "Column persistence and layout controls used in the dragging, toggling, and resizing demos.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "**kwargs",
                "description": "Any other column props accepted by the component.",
                "type": "column props",
                "default": "",
            },
        ],
        "notes": [
            "Nested mapping props like `style`, `cellsStyle`, `titleStyle`, `headerStyle`, and `filterPopoverProps` are merged recursively.",
            "If no matching column exists and the update includes an accessor, the column is appended.",
        ],
    },
    {
        "name": "group_columns",
        "signature": "group_columns(*groups, selector=None, **kwargs)",
        "description": "Create or update grouped headers, including nested group trees.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "*groups",
                "description": "Group dictionaries to append or apply.",
                "type": "dict",
                "default": "",
            },
            {
                "name": "selector",
                "description": "Group ID or collection of IDs used to target existing groups.",
                "type": "Any",
                "default": "None",
            },
            {
                "name": "title",
                "description": "Visible grouped-header label.",
                "type": "str",
                "default": "",
            },
            {
                "name": "columns / groups",
                "description": "Direct child columns or nested child groups.",
                "type": "list",
                "default": "",
            },
            {
                "name": "style / textAlign",
                "description": "Common presentation props for grouped-header cells.",
                "type": "dict / str",
                "default": "",
            },
            {
                "name": "**kwargs",
                "description": "Any other grouped-header props accepted by the component.",
                "type": "group props",
                "default": "",
            },
        ],
        "notes": [
            "Column accessors inside `columns` are resolved against the current column definitions.",
            "Nested `groups` trees are normalized before being stored on the component.",
        ],
    },
    {
        "name": "update_rows",
        "signature": "update_rows(selector=None, **kwargs)",
        "description": "Apply row-level colors, styles, class names, attributes, dragging, IDs, or expansion state.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "selector",
                "description": "Dash-safe row selector, commonly a mapping of field names to expected values.",
                "type": "Any",
                "default": "None",
            },
            {
                "name": "rowColor / color",
                "description": "Static or selector-based row text color.",
                "type": "str | dict | list",
                "default": "",
            },
            {
                "name": "rowBackgroundColor / backgroundColor",
                "description": "Static or selector-based row background color.",
                "type": "str | dict | list",
                "default": "",
            },
            {
                "name": "rowClassName / className",
                "description": "Static or selector-based row class names.",
                "type": "str | dict | list",
                "default": "",
            },
            {
                "name": "rowStyle / style",
                "description": "Static or selector-based row inline styles.",
                "type": "dict | list",
                "default": "",
            },
            {
                "name": "rowAttributes / attributes",
                "description": "Static or selector-based DOM attributes for rows.",
                "type": "dict | list",
                "default": "",
            },
            {
                "name": "rowDragging / draggable",
                "description": "Turns on row dragging. This is table-level and cannot be combined with a selector.",
                "type": "bool | dict",
                "default": "",
            },
            {
                "name": "idAccessor",
                "description": "Record ID accessor, including tuple/list shorthand for composite IDs.",
                "type": "str | list[str]",
                "default": "",
            },
            {
                "name": "expandedRecordIds / rowExpansion",
                "description": "Controlled expansion state and expansion configuration.",
                "type": "list / dict",
                "default": "",
            },
            {
                "name": "**kwargs",
                "description": "Any other row props accepted by the component.",
                "type": "row props",
                "default": "",
            },
        ],
        "notes": [
            "Supported aliases are `color`, `backgroundColor`, `className`, `style`, `attributes`, and `draggable`.",
            "Selector-based row styling is stored as Dash-safe rule objects of the form `{'selector': ..., 'value': ...}`.",
            "Table-level props such as `rowDragging` and `rowExpansion` cannot be combined with a selector.",
        ],
    },
    {
        "name": "add_interactivity",
        "signature": "add_interactivity(*, rowClick=False, rowDoubleClick=False, rowContextMenu=False, cellClick=False, cellDoubleClick=False, cellContextMenu=False, cellSelector=None)",
        "description": "Enable row or cell pointer-cursor affordances for click, double-click, or context-menu patterns.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "rowClick / rowDoubleClick / rowContextMenu",
                "description": "Turn on interactive row styling for the selected row interaction types.",
                "type": "bool",
                "default": "False",
            },
            {
                "name": "cellClick / cellDoubleClick / cellContextMenu",
                "description": "Turn on interactive cell styling for the selected cell interaction types.",
                "type": "bool",
                "default": "False",
            },
            {
                "name": "cellSelector",
                "description": "Optional accessor or accessor list limiting which columns receive interactive cell styling.",
                "type": "Any",
                "default": "None",
            },
        ],
        "notes": [
            "This helper adjusts presentation only. It does not register Dash callbacks by itself.",
            "When row interactivity is enabled, the helper turns on pointer cursors and disables text selection.",
        ],
    },
    {
        "name": "update_selection",
        "signature": "update_selection(**kwargs)",
        "description": "Update controlled selection props and selection rule settings.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "selectionTrigger",
                "description": "Turns selection on and chooses between cell-based and checkbox-based selection.",
                "type": "'cell' | 'checkbox'",
                "default": "",
            },
            {
                "name": "selectedRecordIds / selectedRecords",
                "description": "Controlled selection state written into the component.",
                "type": "list",
                "default": "",
            },
            {
                "name": "selectableRowRules / disabledSelectionRowRules",
                "description": "Rule objects that allow or block selection for matching rows.",
                "type": "bool | dict | list",
                "default": "",
            },
            {
                "name": "selectionCheckboxRules",
                "description": "Per-row checkbox customization rules.",
                "type": "dict | list",
                "default": "",
            },
            {
                "name": "selectionCheckboxProps / allRecordsSelectionCheckboxProps",
                "description": "Props forwarded to row checkboxes and the header checkbox.",
                "type": "dict",
                "default": "",
            },
            {
                "name": "selectionColumnClassName / selectionColumnStyle",
                "description": "Styling hooks for the selection column.",
                "type": "str / dict",
                "default": "",
            },
            {
                "name": "**kwargs",
                "description": "Any other selection-related props accepted by the component.",
                "type": "selection props",
                "default": "",
            }
        ],
        "notes": [
            "Useful when selection-related props are easier to keep grouped in a fluent chain.",
        ],
    },
    {
        "name": "update_pagination",
        "signature": "update_pagination(**kwargs)",
        "description": "Update page, page size, total records, and pagination appearance props.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "page",
                "description": "Current page number.",
                "type": "number",
                "default": "",
            },
            {
                "name": "pageSize / recordsPerPage",
                "description": "Current page-size values used by the component and UI.",
                "type": "number",
                "default": "",
            },
            {
                "name": "totalRecords",
                "description": "Total result size for server-driven pagination.",
                "type": "number",
                "default": "",
            },
            {
                "name": "recordsPerPageOptions / pageSizeOptions",
                "description": "Available page-size choices shown in the pagination controls.",
                "type": "list[number]",
                "default": "",
            },
            {
                "name": "recordsPerPageLabel / paginationSize",
                "description": "Common paginator labeling and sizing props.",
                "type": "str | number",
                "default": "",
            },
            {
                "name": "paginationActiveTextColor / paginationActiveBackgroundColor",
                "description": "Active-page color overrides.",
                "type": "str | dict",
                "default": "",
            },
            {
                "name": "paginationWithEdges / paginationWithControls",
                "description": "Toggles first/last and previous/next pagination controls.",
                "type": "bool",
                "default": "",
            },
            {
                "name": "**kwargs",
                "description": "Any other pagination-related props accepted by the component.",
                "type": "pagination props",
                "default": "",
            }
        ],
        "notes": [
            "Especially useful in server-driven tables where pagination props are updated together.",
        ],
    },
    {
        "name": "update_sorting",
        "signature": "update_sorting(**kwargs)",
        "description": "Update sort mode, sort status, or sort icon props.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "sortStatus",
                "description": "Controlled sort descriptor containing the active accessor and direction.",
                "type": "dict",
                "default": "",
            },
            {
                "name": "sortMode",
                "description": "Chooses client-side or server-side sorting.",
                "type": "'client' | 'server'",
                "default": "",
            },
            {
                "name": "sortIcons",
                "description": "Custom sorted and unsorted icons for sortable headers.",
                "type": "dict",
                "default": "",
            },
            {
                "name": "**kwargs",
                "description": "Any other sorting-related props accepted by the component.",
                "type": "sorting props",
                "default": "",
            }
        ],
        "notes": [
            "Useful when sort state is controlled by the rest of the Dash app.",
        ],
    },
    {
        "name": "update_search",
        "signature": "update_search(**kwargs)",
        "description": "Update search mode, query text, and searchable accessor props.",
        "returns": "DataTable",
        "parameters": [
            {
                "name": "searchQuery",
                "description": "Controlled search query text.",
                "type": "str",
                "default": "",
            },
            {
                "name": "searchMode",
                "description": "Chooses client-side or server-side search behavior.",
                "type": "'client' | 'server'",
                "default": "",
            },
            {
                "name": "searchableAccessors",
                "description": "Limits client-side search to the listed columns.",
                "type": "list[str]",
                "default": "",
            },
            {
                "name": "**kwargs",
                "description": "Any other search-related props accepted by the component.",
                "type": "search props",
                "default": "",
            }
        ],
        "notes": [
            "Useful when search state is controlled outside the table or synchronized with external inputs.",
        ],
    },
    {
        "name": "clear_selection",
        "signature": "clear_selection()",
        "description": "Reset `selectedRecordIds` and `selectedRecords` to empty lists.",
        "returns": "DataTable",
        "parameters": [],
        "notes": [
            "A small convenience helper for reset flows and example callbacks.",
        ],
    },
    {
        "name": "clear_expansion",
        "signature": "clear_expansion()",
        "description": "Reset `expandedRecordIds` to an empty list.",
        "returns": "DataTable",
        "parameters": [],
        "notes": [
            "Useful when expansion state should be cleared after a filter, refresh, or navigation event.",
        ],
    },
]

DATA_TABLE_STYLE_PROP_NAMES = {
    "m", "mx", "my", "mt", "mb", "ms", "me", "ml", "mr",
    "p", "px", "py", "pt", "pb", "ps", "pe", "pl", "pr",
    "w", "miw", "maw", "h", "mih", "mah", "opacity", "ff",
    "fz", "fw", "lts", "ta", "lh", "fs", "tt", "display",
    "flex", "bd", "bdrs", "td", "bgsz", "bgp", "bgr", "bga",
    "pos", "top", "left", "bottom", "right", "inset", "hiddenFrom", "visibleFrom",
}

DATA_TABLE_STYLE_DRIVEN_NAMES = DATA_TABLE_STYLE_PROP_NAMES | {
    "backgroundColor",
    "borderColor",
    "borderRadius",
    "c",
    "className",
    "classNames",
    "fz",
    "height",
    "highlightOnHover",
    "highlightOnHoverColor",
    "horizontalSpacing",
    "maxHeight",
    "minHeight",
    "noHeader",
    "paginationActiveBackgroundColor",
    "paginationActiveTextColor",
    "paginationSize",
    "radius",
    "rowBorderColor",
    "shadow",
    "stickyHeader",
    "stickyHeaderOffset",
    "striped",
    "stripedColor",
    "style",
    "styles",
    "tableClassName",
    "textSelectionDisabled",
    "verticalAlign",
    "verticalSpacing",
    "withColumnBorders",
    "withRowBorders",
    "withTableBorder",
}


def read_generated_datatable_parameter_names():
    """Read the canonical generated parameter names from `DataTable.py`."""

    source = DATA_TABLE_PY_PATH.read_text(encoding="utf-8")
    match = re.search(r"self\.available_properties = (\[[^\]]*\])", source, re.DOTALL)
    if not match:
        raise ValueError("Could not locate available_properties in generated DataTable.py")
    return ast.literal_eval(match.group(1))


def format_metadata_type(type_def):
    """Convert react-docgen type metadata into a readable string."""

    if not isinstance(type_def, dict):
        return str(type_def or "")

    type_name = type_def.get("name")
    if type_name == "union":
        return " | ".join(format_metadata_type(value) for value in type_def.get("value", []))
    if type_name == "arrayOf":
        return f"list[{format_metadata_type(type_def.get('value'))}]"
    if type_name == "enum":
        values = []
        for value in type_def.get("value", []):
            rendered = value.get("value", "")
            if rendered.startswith("'") and rendered.endswith("'"):
                rendered = rendered[1:-1]
            values.append(rendered)
        return " | ".join(values)
    return {
        "string": "str",
        "number": "number",
        "bool": "bool",
        "object": "dict",
        "array": "list",
        "func": "callable",
        "any": "any",
    }.get(type_name, type_name or "")


def format_metadata_default(prop_meta):
    """Render a human-readable default value from react-docgen metadata."""

    default = prop_meta.get("defaultValue")
    if not default:
        return ""

    value = str(default.get("value", "")).strip()
    if value in {"undefined", "None", ""}:
        return ""
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def normalize_doc_text(text):
    """Collapse doc text so it fits better inside a table cell."""

    return " ".join(str(text or "").split())


def describe_datatable_prop(name, prop_meta):
    """Return a useful description for a DataTable property."""

    description = normalize_doc_text(prop_meta.get("description"))
    if description:
        return description

    if name in DATA_TABLE_PROP_DESCRIPTION_OVERRIDES:
        return DATA_TABLE_PROP_DESCRIPTION_OVERRIDES[name]

    if name.startswith("last") and name.endswith("Change"):
        label = name[4:-6]
        return f"Latest {label[:1].lower() + label[1:]} payload emitted by the component."

    if name in {"rowClick", "rowDoubleClick", "rowContextMenu", "cellClick", "cellDoubleClick", "cellContextMenu"}:
        return f"Callback payload emitted when `{name}` fires."

    if name in DATA_TABLE_STYLE_PROP_NAMES:
        return "Mantine style prop forwarded to the root table container."

    if name in {"backgroundColor", "borderColor"}:
        return "Color override applied to the table container."

    if name in {"bodyRef", "tableRef"}:
        return "Ref-like prop exposed by the component for advanced integrations."

    return "Public DataTable property available as both a constructor keyword argument and an instance attribute."


def is_style_driven_datatable_name(name, *, canonical_name=None):
    """Return whether a DataTable prop or alias is primarily style-driven."""

    target = canonical_name or name
    return target in DATA_TABLE_STYLE_DRIVEN_NAMES


def split_rows_by_style(rows, *, canonical_key=None):
    """Split rows into functionality-driven and style-driven groups."""

    functionality_rows = []
    style_rows = []

    for row in rows:
        canonical_name = row.get(canonical_key) if canonical_key else row.get("name")
        if is_style_driven_datatable_name(row.get("name"), canonical_name=canonical_name):
            style_rows.append(row)
        else:
            functionality_rows.append(row)

    return functionality_rows, style_rows


def build_datatable_surface_rows():
    """Build a combined keyword-argument and attribute table for DataTable."""

    rows = []
    for name, prop_meta in DATA_TABLE_METADATA.items():
        kind = "internal" if name == "setProps" else "prop / attribute"
        rows.append(
            {
                "rowId": f"prop::{name}",
                "name": name,
                "kind": kind,
                "canonicalName": name,
                "type": format_metadata_type(prop_meta.get("type")),
                "default": format_metadata_default(prop_meta),
                "description": describe_datatable_prop(name, prop_meta),
            }
        )

    for alias, canonical in sorted(dmdt._PROP_ALIASES.items()):
        canonical_meta = DATA_TABLE_METADATA.get(canonical, {})
        rows.append(
            {
                "rowId": f"alias::{alias}",
                "name": alias,
                "kind": "python alias",
                "canonicalName": canonical,
                "type": format_metadata_type(canonical_meta.get("type")),
                "default": "",
                "description": f"Python-friendly alias for `{canonical}` accepted by `DataTable(...)` and fluent prop-update helpers.",
            }
        )

    return rows


def build_generated_datatable_parameter_rows():
    """Build the canonical generated DataTable parameter table from `DataTable.py`."""

    rows = []
    for name in read_generated_datatable_parameter_names():
        prop_meta = DATA_TABLE_METADATA.get(name, {})
        rows.append(
            {
                "rowId": f"generated::{name}",
                "name": name,
                "kind": "generated prop",
                "canonicalName": name,
                "type": format_metadata_type(prop_meta.get("type")),
                "default": format_metadata_default(prop_meta),
                "description": describe_datatable_prop(name, prop_meta),
            }
        )
    return rows


def build_datatable_api_item():
    """Return the enriched API-reference entry for DataTable."""

    method_summary_rows = [
        {
            "name": f"{method['signature']}",
            "description": method["description"],
            "type": f"method -> {method['returns']}",
        }
        for method in DATA_TABLE_METHOD_DETAILS
    ]

    return {
        "id": "api-datatable",
        "name": "DataTable",
        "kind": "component",
        "signature": "dmdt.DataTable(*args, **kwargs)",
        "description": (
            "The main Dash component. Use it to render records, define columns, "
            "control selection, search, sorting, pagination, row expansion, "
            "and callback payloads from a single Python API."
        ),
        "returns": "Returns a Dash component instance with chainable Python helpers.",
        "methods": method_summary_rows,
        "method_details": DATA_TABLE_METHOD_DETAILS,
        "surface_rows": build_datatable_surface_rows(),
        "all_parameters_rows": build_generated_datatable_parameter_rows(),
    }


API_REFERENCE_ITEMS = [
    build_datatable_api_item(),
    *API_REFERENCE_ITEMS[1:],
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


def build_stock_portfolio_code():
    return "\n".join(
        [
            "def load_stock_portfolio_record(symbol, row_id):",
            "    ticker = yf.Ticker(symbol)",
            '    history = ticker.history(period="3mo")["Close"].dropna().tolist()',
            "    return {",
            '        "id": row_id,',
            '        "ticker": ticker.info["displayName"],',
            '        "_queryTicker": symbol,',
            '        "Exchange": ticker.fast_info["exchange"],',
            '        "sector": ticker.info["sector"],',
            '        "lastValue": ticker.analyst_price_targets["current"],',
            '        "marketCap": ticker.fast_info["marketCap"],',
            '        "priceTargetLow": ticker.analyst_price_targets["low"],',
            '        "priceTargetMedian": ticker.analyst_price_targets["median"],',
            '        "priceTargetHigh": ticker.analyst_price_targets["high"],',
            '        "sparkline": history,',
            '        "sparklineLabel": history,',
            '        "sparklineColor": "blue",',
            "    }",
            "",
            "stock_records = [",
            "    load_stock_portfolio_record(symbol, row_id)",
            "    for row_id, symbol in enumerate(STOCK_PORTFOLIO_DEFAULT_TICKERS, start=1)",
            "]",
            "",
            "portfolio_table = (",
            "    dmdt.DataTable(",
            '        id="stock-portfolio-table",',
            "        data=stock_records,",
            "        columns=STOCK_PORTFOLIO_COLUMNS,",
            '        idAccessor="id",',
            '        paginationMode="none",',
            "    )",
            "    .update_layout(",
            '        radius="lg",',
            "        withTableBorder=True,",
            "        withColumnBorders=True,",
            "        striped=True,",
            "        pinFirstColumn=True,",
            "        textSelectionDisabled=True,",
            "    )",
            "    .update_columns(",
            '        selector="ticker",',
            '        title="Stock ticker",',
            "        width=140,",
            "        editable=True,",
            '        editor=dmc.TextInput(label="Stock ticker", placeholder="e.g. NVDA"),',
            '        cellsStyle={"fontWeight": 700, "letterSpacing": "0.04em", "textTransform": "uppercase"},',
            "    )",
            "    .update_columns(selector=\"Exchange\", title=\"Exchange\", width=120)",
            "    .update_columns(selector=\"sector\", title=\"Sector\", width=190)",
            "    .update_columns(",
            '        selector="lastValue",',
            '        title="Last value",',
            '        presentation="currency",',
            '        currency="USD",',
            '        textAlign="right",',
            "        width=130,",
            '        cellsStyle={"fontVariantNumeric": "tabular-nums"},',
            "    )",
            "    .update_columns(",
            '        selector="marketCap",',
            '        title="Market cap",',
            '        presentation="currency",',
            '        currency="USD",',
            '        textAlign="right",',
            "        width=150,",
            '        cellsStyle={"fontVariantNumeric": "tabular-nums"},',
            "    )",
            "    .update_columns(",
            '        selector=["priceTargetLow", "priceTargetMedian", "priceTargetHigh"],',
            '        presentation="currency",',
            '        currency="USD",',
            '        textAlign="right",',
            "        width=120,",
            '        cellsStyle={"fontVariantNumeric": "tabular-nums"},',
            "    )",
            "    .update_columns(selector=\"priceTargetLow\", title=\"Low\")",
            "    .update_columns(selector=\"priceTargetMedian\", title=\"Median\", cellsStyle={\"fontWeight\": 700})",
            "    .update_columns(selector=\"priceTargetHigh\", title=\"High\")",
            "    .update_columns(",
            '        selector="sparkline",',
            '        title="3M history",',
            "        width=160,",
            '        render=dmc.Sparkline(data="{sparkline}", color="{sparklineColor}", w=140, h=34),',
            "    )",
            "    .group_columns(",
            '        dmdt.ColumnGroup(',
            '            "snapshot",',
            '            title="Snapshot",',
            '            columns=["ticker", "Exchange", "sector", "lastValue", "marketCap"],',
            "        ),",
            '        dmdt.ColumnGroup(',
            '            "price-target",',
            '            title="Price target",',
            '            textAlign="center",',
            '            columns=["priceTargetLow", "priceTargetMedian", "priceTargetHigh"],',
            "        ),",
            '        dmdt.ColumnGroup(',
            '            "history",',
            '            title="History",',
            '            columns=["sparkline"],',
            "        )",
            "    )",
            "    .group_columns(",
            '        selector="snapshot",',
            '        style={"backgroundColor": "var(--mantine-color-gray-0)"},',
            "    )",
            "    .group_columns(",
            '        selector="price-target",',
            '        style={"backgroundColor": "var(--mantine-color-blue-0)"},',
            "    )",
            "    .group_columns(",
            '        selector="history",',
            '        style={"backgroundColor": "var(--mantine-color-green-0)"},',
            "    )",
            ")",
            "",
            "# In the docs app, a callback reloads the live rows on page load and",
            "# re-hydrates the table after ticker edits.",
        ]
    )


def make_stock_portfolio_demo_table(data=None, *, fetching=False):
    columns = deepcopy(STOCK_PORTFOLIO_COLUMNS)

    table_data = deepcopy(STOCK_PORTFOLIO_RECORDS if data is None else data)

    table = (
        dmdt.DataTable(
            id="stock-portfolio-table",
            data=table_data,
            columns=columns,
            idAccessor="id",
            paginationMode="none",
            fetching=fetching,
        )
        .update_layout(
            radius="lg",
            withTableBorder=True,
            withColumnBorders=True,
            striped=True,
            pinFirstColumn=True,
            textSelectionDisabled=True,
            minHeight=260,
            loadingText="Loading live yfinance data...",
            loaderType="dots",
            loaderColor="blue",
        )
        .update_columns(
            selector="ticker",
            title="Stock ticker",
            width=140,
            cellsStyle={
                "fontWeight": 700,
                "letterSpacing": "0.04em",
                "textTransform": "uppercase",
            },
        )
        .update_columns(
            selector="Exchange",
            title="Exchange",
            width=120,
        )
        .update_columns(
            selector="sector",
            title="Sector",
            width=190,
            ellipsis=True,
        )
        .update_columns(
            selector="lastValue",
            title="Last value",
            presentation="currency",
            currency="USD",
            textAlign="right",
            width=130,
            cellsStyle={"fontVariantNumeric": "tabular-nums"},
        )
        .update_columns(
            selector="marketCap",
            title="Market cap",
            presentation="currency",
            currency="USD",
            textAlign="right",
            width=150,
            cellsStyle={"fontVariantNumeric": "tabular-nums"},
        )
        .update_columns(
            selector=["priceTargetLow", "priceTargetMedian", "priceTargetHigh"],
            presentation="currency",
            currency="USD",
            textAlign="right",
            width=120,
            cellsStyle={"fontVariantNumeric": "tabular-nums"},
        )
        .update_columns(selector="priceTargetLow", title="Low")
        .update_columns(
            selector="priceTargetMedian",
            title="Median",
            cellsStyle={
                "fontVariantNumeric": "tabular-nums",
                "fontWeight": 700,
            },
        )
        .update_columns(selector="priceTargetHigh", title="High")
        .group_columns(
            dmdt.ColumnGroup(
                "snapshot",
                title="Snapshot",
                columns=["ticker", "Exchange", "sector", "lastValue", "marketCap"],
            ),
            dmdt.ColumnGroup(
                "price-target",
                title="Price target",
                textAlign="center",
                columns=["priceTargetLow", "priceTargetMedian", "priceTargetHigh"],
            ),
            dmdt.ColumnGroup(
                "history",
                title="History",
                columns=["sparkline"],
            )
        )
        .group_columns(
            selector="snapshot",
            style={"backgroundColor": "var(--mantine-color-gray-0)"},
        )
        .group_columns(
            selector="price-target",
            style={"backgroundColor": "var(--mantine-color-blue-0)"},
        )
        .group_columns(
            selector="history",
            style={"backgroundColor": "var(--mantine-color-green-0)"},
        )
    )

    if USE_FULL_RUNTIME_DEMOS:
        table = table.update_columns(
            selector="ticker",
            editable=True,
            editor=dmc.TextInput(
                label="Stock ticker",
                placeholder="e.g. NVDA",
                size="xs",
            ),
        )

    return table.update_columns(
        selector="sparkline",
        title="3M history",
        width=160,
        render=dmc.Sparkline(
            data="{sparkline}",
            color="{sparklineColor}",
            w=140,
            h=34,
        ),
    )


def resolve_stock_portfolio_symbols(edited_rows, current_rows):
    current_by_id = {
        str(row.get("id")): row
        for row in current_rows or []
    }
    next_symbols = []
    ticker_changed = False

    for index, row in enumerate(edited_rows or [], start=1):
        row_id = str(row.get("id") or index)
        current_row = current_by_id.get(row_id, {})
        edited_value = str(row.get("ticker") or "").strip()
        current_value = str(current_row.get("ticker") or "").strip()

        if edited_value and edited_value != current_value:
            ticker_changed = True
            next_symbols.append(edited_value)
        else:
            next_symbols.append(
                current_row.get("_queryTicker")
                or normalize_stock_ticker(edited_value)
                or STOCK_PORTFOLIO_DEFAULT_TICKERS[index - 1]
            )

    return next_symbols, ticker_changed


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


def make_api_reference_table(rows, *, columns=None, id_accessor="name"):
    """Render an API reference table using the provided column configuration."""

    return dmdt.DataTable(
        data=rows,
        columns=columns or API_REFERENCE_TABLE_COLUMNS,
        idAccessor=id_accessor,
        defaultColumnProps=dmdt.Column(ellipsis=False),
        paginationMode="none",
        withTableBorder=True,
        withColumnBorders=True,
        striped=True,
        highlightOnHover=False,
        verticalAlign="top",
        tableProps={"style": {"tableLayout": "fixed"}},
        radius="md",
        noRecordsText="No documented entries.",
    )


def make_api_method_card(method):
    """Render a deeper documentation block for one fluent method."""

    children = [
        dmc.Title(method["name"], order=5),
        dmc.Code(method["signature"], block=True),
        dmc.Text(method["description"], size="sm", c="dimmed"),
        dmc.Alert(f"Returns `{method['returns']}`.", color="gray", variant="light"),
    ]

    if method.get("parameters"):
        children.extend(
            [
                dmc.Text("Parameters", fw=700, size="sm"),
                make_api_reference_table(
                    method["parameters"],
                    columns=API_REFERENCE_PARAMETER_COLUMNS,
                ),
            ]
        )

    if method.get("notes"):
        children.extend(
            [
                dmc.Text("Notes", fw=700, size="sm"),
                highlight_points(method["notes"]),
            ]
        )

    return dmc.Paper(
        dmc.Stack(children, gap="md"),
        withBorder=True,
        radius="md",
        p="md",
    )


def make_api_reference_item(item):
    """Render one public API item with deep method and API-surface tables."""

    children = [
        dmc.Group(
            [
                dmc.Title(item["name"], order=3),
                dmc.Badge(item["kind"], variant="light", color="blue"),
            ],
            justify="space-between",
            align="center",
        ),
        dmc.Text(item["description"], size="sm", c="dimmed"),
        dmc.Code(item["signature"], block=True),
        dmc.Alert(item["returns"], color="gray", variant="light"),
    ]

    functionality_surface_rows, style_surface_rows = split_rows_by_style(
        item.get("surface_rows", []),
        canonical_key="canonicalName",
    )
    functionality_parameter_rows, style_parameter_rows = split_rows_by_style(
        item.get("all_parameters_rows", []),
        canonical_key="canonicalName",
    )

    if item.get("methods"):
        children.extend(
            [
                dmc.Title("Fluent Methods", order=4),
                make_api_reference_table(item["methods"]),
            ]
        )

    if item.get("method_details"):
        children.extend(
            [
                dmc.Title("Method Details", order=4),
                dmc.Stack(
                    [make_api_method_card(method) for method in item["method_details"]],
                    gap="md",
                ),
            ]
        )

    if item.get("surface_rows"):
        children.extend(
            [
                dmc.Title("Functionality-Driven Keyword Arguments and Attributes", order=4),
                dmc.Text(
                    "These entries control data flow, interaction, callbacks, selection, sorting, pagination, expansion, loading state, and other table behavior.",
                    size="sm",
                    c="dimmed",
                ),
                make_api_reference_table(
                    functionality_surface_rows,
                    columns=API_REFERENCE_SURFACE_COLUMNS,
                    id_accessor="rowId",
                ),
                dmc.Title("Style-Driven Keyword Arguments and Attributes", order=4),
                dmc.Text(
                    "These entries primarily affect layout, spacing, borders, colors, sizing, and other visual presentation concerns.",
                    size="sm",
                    c="dimmed",
                ),
                make_api_reference_table(
                    style_surface_rows,
                    columns=API_REFERENCE_SURFACE_COLUMNS,
                    id_accessor="rowId",
                ),
            ]
        )
    if item.get("all_parameters_rows"):
        children.extend(
            [
                dmc.Title("All Functionality Parameters from DataTable.py", order=4),
                dmc.Text(
                    "This exhaustive table is sourced from the generated component in `dash_mantine_datatable/DataTable.py` and lists the canonical functionality-oriented constructor parameters exposed by the component.",
                    size="sm",
                    c="dimmed",
                ),
                make_api_reference_table(
                    functionality_parameter_rows,
                    columns=API_REFERENCE_SURFACE_COLUMNS,
                    id_accessor="rowId",
                ),
                dmc.Title("All Style Parameters from DataTable.py", order=4),
                dmc.Text(
                    "This exhaustive table lists the canonical style- and layout-oriented constructor parameters exposed by the generated component.",
                    size="sm",
                    c="dimmed",
                ),
                make_api_reference_table(
                    style_parameter_rows,
                    columns=API_REFERENCE_SURFACE_COLUMNS,
                    id_accessor="rowId",
                ),
            ]
        )
    elif item.get("keyword_arguments"):
        children.extend(
            [
                dmc.Title("Keyword Arguments", order=4),
                make_api_reference_table(item["keyword_arguments"]),
            ]
        )

    return html.Div(
        dmc.Paper(
            dmc.Stack(children, gap="md"),
            withBorder=True,
            radius="lg",
            p="lg",
            shadow="xs",
        ),
        id=item["id"],
        style={"scrollMarginTop": "1rem"},
    )


def make_api_reference_section():
    """Render the curated public Python API reference for the usage page."""

    overview_cards = html.Div(
        [
            html.A(
                dmc.Paper(
                    dmc.Stack(
                        [
                            dmc.Text(item["name"], fw=700, size="sm"),
                            dmc.Text(item["signature"], size="xs", c="dimmed"),
                            dmc.Text(item["description"], size="sm", c="dimmed"),
                        ],
                        gap="xs",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                href=f"#{item['id']}",
                style={"textDecoration": "none", "color": "inherit"},
            )
            for item in API_REFERENCE_ITEMS
        ],
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
            "gap": "1rem",
        },
    )

    return dmc.Stack(
        [
            dmc.Alert(
                "This reference is intentionally curated around the props and attributes people reach for most often first, so the page stays approachable.",
                color="blue",
                variant="light",
            ),
            overview_cards,
            *[make_api_reference_item(item) for item in API_REFERENCE_ITEMS],
        ],
        gap="xl",
    )


app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "DashMantineDatatable Demo"

navigation_panel = dmc.Paper(
    dmc.Stack(
        [
            dmc.Text("Docs", fw=700, tt="uppercase", c="dimmed", size="xs"),
            dmc.Text(
                "Jump to a reference block or a specific example section.",
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
                            "docs entry: it opens with a curated API reference, then moves "
                            "through grouped live examples, and keeps longer source in "
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
                    "API reference",
                    "Start here when you want definitions, fluent methods, and the most commonly used keyword arguments for the public Python API.",
                    category_id="category-api-reference",
                ),
                demo_section(
                    "0. Python API reference",
                    "This section documents each public item exported by the package, with special emphasis on the attributes and keyword arguments people tend to use first.",
                    make_api_reference_section(),
                    section_id="section-api",
                    methods=[
                        "DataTable",
                        "Column",
                        "ColumnGroup",
                        "SelectionConfig",
                        "PaginationConfig",
                        "RowExpansionConfig",
                    ],
                    highlights=[
                        "DataTable lists fluent methods, common keyword arguments, and the instance attributes most likely to appear in callbacks.",
                        "Helper builders are documented as plain dictionary factories so it is clear what each one returns and when to reach for it.",
                        "The reference tables are curated instead of exhaustive, which keeps the page readable while still making the component easy to pick up.",
                    ],
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
                    "20. Stock portfolio",
                    "This portfolio demo combines a pinned ticker editor, exchange and market-cap snapshot fields, grouped analyst targets, and a compact 3-month history column. It loads live rows from yfinance on page load and re-hydrates the table after ticker edits.",
                    dmc.Stack(
                        [
                            dmc.Alert(
                                "The demo loads live rows from yfinance on page load. Edit the first column with a ticker symbol to re-hydrate that row with exchange, sector, targets, market cap, and recent close history.",
                                color="blue",
                                variant="light",
                            ),
                            dcc.Store(
                                id="stock-portfolio-data-store",
                                data=[],
                            ),
                            dcc.Store(
                                id="stock-portfolio-pending-symbols",
                                data=[],
                            ),
                            dcc.Interval(
                                id="stock-portfolio-loader",
                                interval=250,
                                n_intervals=0,
                                max_intervals=1,
                            ),
                            dmc.Text(
                                id="stock-portfolio-status",
                                size="sm",
                                c="dimmed",
                                children=STOCK_PORTFOLIO_STATUS,
                            ),
                            make_stock_portfolio_demo_table([], fetching=True),
                            source_code_accordion(
                                "Show Python for the stock portfolio example",
                                code=build_stock_portfolio_code(),
                                description=(
                                    "This demo now uses a live `yfinance` loader. Keep the "
                                    "row ID stable, treat the edited ticker cell as the lookup "
                                    "key, and rewrite the rest of the record from the remote "
                                    "payload."
                                ),
                            ),
                        ],
                        gap="md",
                    ),
                    dmc.Text(
                        "Pinned symbols make the table easier to scan horizontally, while the snapshot fields and grouped target columns keep the yfinance payload readable inside one wide grid.",
                        c="dimmed",
                        size="sm",
                    ),
                    section_id="section-stock-portfolio",
                    methods=[
                        "editable",
                        "editor",
                        "pinFirstColumn",
                        "group_columns()",
                        "ColumnGroup()",
                        "render",
                    ],
                    highlights=[
                        "A pinned editable ticker column doubles as the live lookup key for yfinance reloads.",
                        "Exchange, sector, last value, and market cap mirror the fast-info and profile fields you will hydrate from yfinance.",
                        "Grouped low, median, and high targets make the analyst data easier to compare without widening the table too much.",
                        "A sparkline render keeps recent close-history compact enough to live directly inside the grid.",
                    ],
                ),
                demo_section(
                    "21. Custom loaders and empty icons",
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
    Output("stock-portfolio-status", "children"),
    Output("stock-portfolio-pending-symbols", "data"),
    Output("stock-portfolio-table", "fetching"),
    Input("stock-portfolio-loader", "n_intervals"),
    Input("stock-portfolio-table", "data"),
    State("stock-portfolio-data-store", "data"),
    prevent_initial_call=True,
)
def queue_stock_portfolio_load(n_intervals, edited_rows, current_rows):
    del n_intervals

    triggered_id = callback_context.triggered_id
    if triggered_id == "stock-portfolio-loader":
        return (
            "Loading live yfinance data...",
            STOCK_PORTFOLIO_DEFAULT_TICKERS,
            True,
        )

    if triggered_id != "stock-portfolio-table":
        return no_update, no_update, no_update

    if not edited_rows or edited_rows == current_rows:
        return no_update, no_update, no_update

    next_symbols, ticker_changed = resolve_stock_portfolio_symbols(
        edited_rows,
        current_rows,
    )
    if not ticker_changed:
        return no_update, no_update, no_update

    return (
        f"Loading live yfinance data for {', '.join(next_symbols)}...",
        next_symbols,
        True,
    )


@callback(
    Output("stock-portfolio-data-store", "data"),
    Output("stock-portfolio-table", "data"),
    Output("stock-portfolio-status", "children", allow_duplicate=True),
    Output("stock-portfolio-pending-symbols", "data", allow_duplicate=True),
    Output("stock-portfolio-table", "fetching", allow_duplicate=True),
    Input("stock-portfolio-pending-symbols", "data"),
    prevent_initial_call=True,
)
def hydrate_stock_portfolio_load(symbols):
    if not symbols:
        return no_update, no_update, no_update, no_update, no_update

    records, status = load_stock_portfolio_records(symbols)
    return records, records, status, [], False


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
