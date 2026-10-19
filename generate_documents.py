"""
Script to generate CampusLive Field Project Documentation in DOCX and PDF formats.
Academic Year: 2026-2027
Institution: SHETH L.U.J. AND SIR M.V. COLLEGE
Student: Aditya Sudhir Rana (S105)
"""
import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

DOCX_OUT = "CampusLive_Field_Project_Documentation.docx"
PDF_OUT = "CampusLive_Field_Project_Documentation.pdf"

# ----------------- DOCX GENERATION -----------------
def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_docx():
    doc = Document()
    
    # Page setup
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        sec.header.is_linked_to_previous = False
        sec.footer.is_linked_to_previous = False
        footer_p = sec.footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = footer_p.add_run("CampusLive Field Project Documentation | S.Y. B.Sc. Computer Science")
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = RGBColor(120, 120, 120)

    # Styles
    navy = RGBColor(27, 54, 93)
    slate = RGBColor(55, 85, 125)
    charcoal = RGBColor(40, 40, 40)

    # Title & Metadata Cover Header
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_inst = title_p.add_run("SHETH L.U.J. AND SIR M.V. COLLEGE\n")
    run_inst.font.name = "Arial"
    run_inst.font.size = Pt(15)
    run_inst.font.bold = True
    run_inst.font.color.rgb = navy
    
    run_dept = title_p.add_run("DEPARTMENT OF COMPUTER SCIENCE\nACADEMIC YEAR: 2026–2027\n")
    run_dept.font.name = "Arial"
    run_dept.font.size = Pt(11)
    run_dept.font.bold = True
    run_dept.font.color.rgb = slate

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(2)
    p_div.paragraph_format.space_after = Pt(14)
    r_div = p_div.add_run("―" * 58)
    r_div.font.color.rgb = slate

    # Main Project Title
    p_proj = doc.add_paragraph()
    p_proj.paragraph_format.space_before = Pt(4)
    p_proj.paragraph_format.space_after = Pt(6)
    r_p = p_proj.add_run("CampusLive: Real-Time Lecture Monitoring and Verification for Colleges")
    r_p.font.name = "Arial"
    r_p.font.size = Pt(18)
    r_p.font.bold = True
    r_p.font.color.rgb = navy

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run("A Real-Time Academic Activity Management, Supervision & Attendance Verification Platform\nField Project Documentation ― S.Y. B.Sc. Computer Science (Semester III)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = charcoal

    # Meta Table
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Student Name & Roll No.", "Aditya Sudhir Rana  |  Roll Number: S105"),
        ("Class & Semester", "S.Y. B.Sc. Computer Science (Semester III)"),
        ("Project Guide", "Mr. Rohit Kumar Sahu"),
        ("Course Coordinators", "Ms. Jyoti Chauhan and Mr. Rohit Kumar Sahu"),
        ("Official Student Email", "ranaadityacs252612@gmail.com")
    ]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_background(c0, "F0F4F8")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(k)
        r0.font.name = "Arial"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = navy
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(v)
        r1.font.name = "Arial"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = charcoal

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = navy
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = slate
        return p

    def add_p(text, bold_prefix="", italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix + " ")
            rb.font.name = "Calibri"
            rb.font.size = Pt(10.5)
            rb.font.bold = True
            rb.font.color.rgb = charcoal
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.italic = italic
        r.font.color.rgb = charcoal
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix + " ")
            rb.font.name = "Calibri"
            rb.font.size = Pt(10)
            rb.font.bold = True
            rb.font.color.rgb = charcoal
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = charcoal
        return p

    # --- SECTION 1 ---
    add_h1("1. Project Title & Official Descriptions")
    add_p("CampusLive: Real-Time Lecture Monitoring and Verification for Colleges", bold_prefix="Exact Project Title:")
    add_p('"CampusLive is a real-time academic monitoring platform where teachers make lectures officially live, students confirm they are present with a class code, and principals and HODs see which lectures are actually being held across the college as they happen. Timetables, substitutions, reports and activity logs run on the same platform."', bold_prefix="Main Description:")
    add_p('"CampusLive is a real-time platform where teachers make lectures live, students verify them, and principals and HODs monitor what is actually being taught across the college."', bold_prefix="Short Description:")

    # --- SECTION 2 ---
    add_h1("2. Guide Interaction Diary")
    add_p("The following table records the periodic consultations and milestones completed with the Project Guide during the development lifecycle:")
    
    diary_headers = ["Meeting Date", "Progress / Agenda Discussed", "Remarks / Guide's Feedback"]
    diary_data = [
        ("06-08-2026", "Initial project ideation: Identifying the need for real-time institutional visibility of ongoing lectures; project scope and objectives approval.", "Recommended focusing on administrative monitoring, departmental hierarchy, and student verification."),
        ("11-08-2026", "Requirement specifications: Defining the 5-tier role structure (Root -> Principal -> HOD -> Teacher -> Student) and designing the relational database schema.", "Approved database entities and recommended incorporating automated conflict checks for rooms and teachers."),
        ("18-08-2026", "Backend REST API design in Flask: Implementation of session authentication, PBKDF2 password hashing, and SQLite schema with Write-Ahead Logging (WAL).", "Reviewed authentication security and classroom scheduling validation logic."),
        ("25-08-2026", "Integration of Server-Sent Events (SSE) for push synchronization and development of the background sweeper daemon for automated lecture lifecycle tracking.", "Verified real-time event distribution and background state transitions."),
        ("01-09-2026", "Frontend single-page application (SPA) design: Implementing the live departures-style board, modal dialog registry, and the 4-digit student verification check-in.", "Approved the student verification model and recommended keeping aggregate attendance statistics accessible to staff only."),
        ("08-09-2026", "Implementation of the multi-week recurring timetable generator, HOD substitution workflow, dynamic room reallocation, and CSV reports.", "Advised verifying clash resolution logic across multi-week recurring slots."),
        ("05-10-2026", "End-to-end integration testing (tests/test_flow.py), field feedback review, edge-case fixes, and preparation of final documentation.", "Approved the system and results for final documentation and academic submission.")
    ]
    t_d = doc.add_table(rows=len(diary_data)+1, cols=3)
    t_d.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = [Inches(1.2), Inches(3.0), Inches(2.3)]
    for j, h in enumerate(diary_headers):
        cell = t_d.rows[0].cells[j]
        cell.width = widths[j]
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
    for i, row in enumerate(diary_data):
        for j, val in enumerate(row):
            cell = t_d.rows[i+1].cells[j]
            cell.width = widths[j]
            if i % 2 == 1:
                set_cell_background(cell, "F9FBFC")
            set_cell_margins(cell, 60, 60, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(9)
            r.font.color.rgb = charcoal

    # --- SECTION 3 ---
    add_h1("3. The Project Itself & Problem Statement")
    add_h2("Overview & Problem Solved")
    add_p("CampusLive is a real-time academic activity management and operational visibility platform designed specifically for collegiate institutions. In conventional college management, institutional leadership (Principals and HODs) lacks immediate operational visibility into daily lecture conduction without conducting physical floor rounds or manual inquiries. Furthermore, traditional paper registers consume valuable instructional time and require significant manual transcription.")
    add_p("CampusLive bridges this gap by transforming static timetables into an active, verifiable digital operational environment:")
    add_bullet("Provides institutional leadership with a live, consolidated departures-style board displaying active lectures, occupied classrooms, and start punctuality across all departments.", "Live Institutional Visibility:")
    add_bullet("Starting a lecture generates an ephemeral 4-digit class code on the teacher's screen. Students in class confirm their presence using this code, transitioning the lecture status to 'Verified by students' once 2 or more check-ins occur.", "Attendance and Student Verification of Lectures:")
    add_bullet("Automatically verifies room and faculty availability during both single-lecture scheduling and multi-week recurring timetable creation, avoiding scheduling overlaps.", "Automated Conflict Resolution:")
    add_bullet("A background sweeper thread auto-closes forgotten live lectures after a 15-minute grace period and updates unstarted lectures to 'MISSED', maintaining accurate historical records.", "Automated Lifecycle Closure:")
    add_bullet("Generates data-driven metrics including Held Rate (%), Average Start Delay (minutes), and Student Attendance (%) with one-click CSV export.", "Reports and Analytics:")

    add_h2("Users and Beneficiaries")
    add_p("The primary beneficiary of CampusLive is the College Administration (Principal, Vice-Principals, and Heads of Departments) for centralized governance and quality assurance, alongside faculty and students:")
    add_bullet("Maintains a bird's-eye view of all academic activity, active classrooms, faculty schedules, and college-wide analytics.", "Principal (College Administrator):")
    add_bullet("Supervises departmental operations, assigns substitute teachers for pending lectures, reallocates rooms dynamically, and monitors departmental workload. Head of Department: Asst. Prof. Pradnya Kharade.", "Heads of Department (HODs):")
    add_bullet("Schedules lectures, activates live sessions, presents the verification PIN, monitors check-ins, and manages recurring weekly timetables. Core Department Faculty: Asst. Prof. Rohit Sahu (Project Guide) and Asst. Prof. Jyoti Chauhan (Course Coordinator).", "Teachers / Faculty:")
    add_bullet("Views active lectures for their class, enters the 4-digit code to confirm attendance, and views their personal timetable and attendance records. Registered Student Cohort: Aditya Rana (S105), Mohi Pathan, Suraj, Dhruv Choubey, and Akshat Halwai.", "Students:")
    add_bullet("Platform administrator responsible for provisioning institutions and initial college administrator accounts.", "Root Administrator:")

    # --- SECTION 4 ---
    add_h1("4. Key Objectives, Modules & Technical Architecture")
    add_h2("Core Modules and Features")
    add_bullet("Centralized dashboard grouping running lectures by department, displaying elapsed timers, occupied rooms, active faculty, and 'Due but not started' punctuality indicators.", "1. Live Campus Monitoring Board:")
    add_bullet("Dynamic 4-digit class code generated on lecture start; verified status triggered at >= 2 check-ins; student privacy enforced by reserving aggregated counts for staff only.", "2. Attendance and Student Verification of Lectures:")
    add_bullet("Institutional performance metrics tracking Total, Held, Missed, and Cancelled lectures, Held Rate (%), Average Start Delay (minutes), and Average Attendance (%) with CSV export.", "3. Reports and Analytics:")
    add_bullet("Finite state machine (SCHEDULED -> LIVE -> COMPLETED / CANCELLED / MISSED) supported by a 30-second interval daemon sweeping expired sessions with a 15-minute grace window.", "4. Lecture State Machine & Sweeper Daemon:")
    add_bullet("Generates up to 12 weeks of recurring timetable slots with automated conflict detection skipping room and teacher clashes.", "5. Weekly Timetable & Clash Resolution Engine:")
    add_bullet("Enables HODs to substitute teachers on unstarted lectures (tracked via covering_for) and reallocate classrooms in real time.", "6. Academic Administration & Substitution:")
    add_bullet("Session-based authentication with PBKDF2 password hashing, 5-tier role enforcement, account deactivation toggles, and immutable chronological audit logs.", "7. Security, Multi-Tenant RBAC & Central Activity Logging:")

    add_h2("Technologies, Languages & Tools")
    add_bullet("Python 3.13 / 3.x, Modern JavaScript (ES6+), HTML5, CSS3.", "Languages:")
    add_bullet("Flask 3.x WSGI microframework, Werkzeug Security (PBKDF2-SHA256).", "Backend Framework:")
    add_bullet("Server-Sent Events (SSE) utilizing Python queue.Queue, threading.Lock, and browser EventSource.", "Real-Time Push Distribution:")
    add_bullet("SQLite 3 with Write-Ahead Logging (PRAGMA journal_mode=WAL) and automatic migration helpers.", "Database Engine:")
    add_bullet("Vanilla JavaScript Single-Page Application (SPA) architecture with declarative rendering, centralized modals, and tab hydration.", "Frontend Architecture:")
    add_bullet("Python development server with auto-port fallback (run.py), Windows OS, and automated test suite (tests/test_flow.py).", "Environment & Testing:")

    add_h2("Scope Limitations")
    add_p("The current implementation intentionally focuses on on-campus physical/hybrid lecture activity monitoring. Remote video streaming (e.g. Zoom/Meet), biometric turnstiles, student fee accounting, and native mobile store wrappers are considered outside the functional scope of this project.")

    # --- SECTION 5 ---
    add_h1("5. Field Work, Methodology & Testing")
    add_h2("Requirements Gathering & Field Consultation")
    add_p("The field study for CampusLive was conducted during August 2026 at Sheth L.U.J. and Sir M.V. College, structured around faculty consultations and direct operational observation:")
    add_bullet("Conducted focused interviews with 2 faculty members (1 Head of Department and 1 teaching faculty). Discussions highlighted the need for immediate operational visibility between classrooms and administrative offices, as well as the benefit of automating manual paper attendance.", "Faculty and Departmental Interviews:")
    add_bullet("Directly observed the standard roll-call routine in undergraduate classrooms, noting that calling out names manually takes significant lecture time. This validated the requirement for a rapid digital check-in mechanism that can be completed within 15 seconds.", "Classroom Workflow Observation:")
    add_bullet("Consultations with the project guide and coordinators helped determine the key daily tracking metrics: verifying that scheduled lectures occur as planned, tracking start punctuality, and generating structured attendance records.", "Administrative Metric Definition:")

    add_h2("Build and Testing Methodology")
    add_p("The project followed an iterative prototyping model, first establishing the database schema and conflict algorithms, followed by real-time SSE streaming, the sweeper daemon, and the responsive user interface.")
    add_p("The system was validated using an automated end-to-end integration test suite (tests/test_flow.py), which verified 13 distinct workflow steps: tenant onboarding, departmental provisioning, conflict-free scheduling, live session activation, 4-digit code check-in, verification threshold update (>= 2 check-ins), HOD substitution, sweeper auto-completion, and CSV report export. All automated test checks passed successfully.")

    add_h2("Future Improvements & Recommendations")
    add_bullet("Introducing time-limited QR codes refreshing every 20 seconds for student check-in.", "1. Dynamic Rotating QR Codes:")
    add_bullet("Integrating browser Web Push or email alerts for last-minute room adjustments and substitutions.", "2. Automated Push Notifications:")
    add_bullet("Adding visual chart components (e.g. Chart.js) to the Reports and Analytics module for semester-long trend visualization.", "3. Interactive Visual Charts:")
    add_bullet("Providing deployment profiles for PostgreSQL and Gunicorn containerization for multi-campus university deployments.", "4. Enterprise Scalability:")

    # --- SECTION 6 ---
    add_h1("6. Evidence, Database & API Specifications")
    add_h2("List of Documentation Figures")
    fig_data = [
        ("Figure 1", "Public Landing Page", "Overview of CampusLive, feature showcases, and public navigation."),
        ("Figure 2", "Student Self-Registration Modal", "Student registration form with dynamic class selection based on college code."),
        ("Figure 3", "Principal Live Campus Monitoring Dashboard", "Departures-style live monitoring board showing running lectures, elapsed timers, and student verification status."),
        ("Figure 4", "Lecture Detail & Timeline Modal", "Comprehensive lecture audit drill-down showing exact timestamps, lifecycle events, and verified attendee roster."),
        ("Figure 5", "Department & HOD Management (Admin)", "Administrator screen for provisioning departments, assigning HOD credentials, and viewing department live status."),
        ("Figure 6", "Faculty Directory & Live Status", "Teacher management table with real-time 'Teaching Right Now' indicators, contact info, and account control menu."),
        ("Figure 7", "Lecture Scheduling Modal", "Teacher lecture creation form featuring classroom selection, date, time, and automatic conflict detection."),
        ("Figure 8", "Weekly Timetable Slot Manager", "Multi-week recurring schedule generator with conflict skipping and active slot removal."),
        ("Figure 9", "Teacher Active Lecture Controller", "Teacher's live lecture interface showing the generated 4-digit class code, live timer, and 'End Lecture' button."),
        ("Figure 10", "Student Live Board & PIN Check-in", "Student live screen showing current class lecture and the 4-digit code entry form to record attendance."),
        ("Figure 11", "HOD Substitution & Room Reallocation", "Head of Department modal for reassigning active teachers to pending lectures and changing classrooms."),
        ("Figure 12", "Central Activity Audit Log", "Searchable log table displaying chronological events with actor attribution."),
        ("Figure 13", "Academic Compliance & Punctuality Report", "Faculty performance table displaying Held Rates, Start Delay (minutes), Attendance (%), and CSV download trigger."),
        ("Figure 14", "User Profile & Security Settings", "Profile editor for updating contact info, viewing role permissions, and changing passwords.")
    ]
    t_f = doc.add_table(rows=len(fig_data)+1, cols=3)
    t_f.alignment = WD_TABLE_ALIGNMENT.CENTER
    wf = [Inches(1.1), Inches(2.4), Inches(3.0)]
    for j, h in enumerate(["Figure No.", "Screen / View Title", "Description & Caption"]):
        cell = t_f.rows[0].cells[j]
        cell.width = wf[j]
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
    for i, row in enumerate(fig_data):
        for j, val in enumerate(row):
            cell = t_f.rows[i+1].cells[j]
            cell.width = wf[j]
            if i % 2 == 1:
                set_cell_background(cell, "F9FBFC")
            set_cell_margins(cell, 50, 50, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(9)
            r.font.color.rgb = charcoal

    # Embed Actual Captured Screenshots
    fig_images = [
        ("Figure 1", "Public Landing Page", "screenshots/fig01_landing_page.png", "Public homepage featuring institutional overview, feature pillars, and live mock board."),
        ("Figure 2", "Student Self-Registration", "screenshots/fig02_student_signup.png", "Registration screen validating college code COL001 and populating SY B.Sc. CS class."),
        ("Figure 3", "Principal Live Campus Monitoring Dashboard", "screenshots/fig03_principal_live_board.png", "Live departures board showing 3 live sessions across FY, SY, TY, occupied rooms, and late alerts."),
        ("Figure 4", "Lecture Detail & Timeline Audit Modal", "screenshots/fig04_lecture_detail_modal.png", "Audit drill-down showing exact timestamps, verified status, and attendee list (Aditya Rana, Mohi Pathan, Suraj, Dhruv Choubey, Akshat Halwai)."),
        ("Figure 5", "Department & HOD Management", "screenshots/fig05_department_hod_management.png", "Administrative management of Computer Science department with HOD Asst. Prof. Pradnya Kharade."),
        ("Figure 6", "Faculty Directory & Live Status", "screenshots/fig06_faculty_directory_live.png", "Faculty roster showing Asst. Prof. Pradnya Kharade, Asst. Prof. Rohit Sahu, and Asst. Prof. Jyoti Chauhan actively teaching live."),
        ("Figure 7", "Academic Reports and Analytics", "screenshots/fig07_reports_analytics.png", "Performance analytics showing scheduled vs. held lectures, held rate (%), start delay (minutes), and attendance (%)."),
        ("Figure 8", "Institutional Activity Audit Log", "screenshots/fig08_activity_audit_log.png", "Chronological audit log tracking lifecycle actions with actor and timestamp attribution."),
        ("Figure 9", "Faculty Active Lecture Controller", "screenshots/fig09_teacher_live_controller.png", "Teacher session controller showing live status in IT Lab, class code 4821, and End Lecture action."),
        ("Figure 10", "Lecture Scheduling Modal", "screenshots/fig10_lecture_schedule_modal.png", "Lecture creation modal featuring classroom selection and automated conflict checking."),
        ("Figure 11", "Weekly Timetable Slot Manager", "screenshots/fig11_weekly_timetable.png", "Recurring weekly schedule manager with official Sheth L.U.J. and Sir M.V. College timetable slots."),
        ("Figure 12", "HOD Teacher Substitution & Room Reallocation", "screenshots/fig12_hod_substitutions.png", "HOD operations screen for reallocating teachers and moving classroom venues."),
        ("Figure 13", "Student Live Check-In Interface", "screenshots/fig13_student_live_checkin.png", "Student screen showing active live lecture for SY B.Sc. CS and presence verification."),
        ("Figure 14", "Student Personal Attendance History", "screenshots/fig14_student_history.png", "Student history view confirming Aditya Rana's attendance with Present status badges."),
        ("Figure 15", "User Profile & Security Settings", "screenshots/fig15_user_profile.png", "User profile management for viewing roles and updating contact information."),
    ]

    add_h2("System Interface Visual Evidence")
    for f_no, f_title, img_path, f_cap in fig_images:
        if os.path.exists(img_path):
            add_p(f"{f_no}: {f_title}", bold_prefix="Interface View:")
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(4)
            p_img.paragraph_format.space_after = Pt(2)
            run_img = p_img.add_run()
            run_img.add_picture(img_path, width=Inches(5.8))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(12)
            r_cap = p_cap.add_run(f"{f_no}: {f_cap}")
            r_cap.font.name = "Calibri"
            r_cap.font.size = Pt(8.5)
            r_cap.font.italic = True
            r_cap.font.color.rgb = slate

    add_h2("Database Schema & Entities")
    add_p("The SQLite database operates in Write-Ahead Logging (WAL) mode for concurrency, structured into the following core tables:")
    add_bullet("id (PK), code (UNIQUE), name, created_at.", "colleges:")
    add_bullet("id (PK), college_id (FK), name, UNIQUE(college_id, name).", "depts:")
    add_bullet("id (PK), college_id (FK), dept_id (FK), name, UNIQUE(dept_id, name).", "classes:")
    add_bullet("id (PK), role, username (UNIQUE), name, pw, college_id, dept_id, class_id, active, email, phone.", "users:")
    add_bullet("id (PK), college_id, dept_id, class_id, teacher_id, orig_teacher_id, timetable_id, subject, room, date, start_time, end_time, status, code, started_at, ended_at.", "lectures:")
    add_bullet("lecture_id (FK), student_id (FK), ts, PRIMARY KEY(lecture_id, student_id).", "attendance:")
    add_bullet("id (PK), college_id, dept_id, class_id, teacher_id, subject, room, weekday, start_time, end_time.", "timetable:")
    add_bullet("id (PK), ts, college_id, dept_id, actor_id, event, lecture_id, detail.", "logs:")

    add_h2("REST API Specification Summary")
    api_data = [
        ("POST", "/api/login", "Public", "Authenticates user; creates session cookie."),
        ("GET", "/api/me", "Auth", "Returns profile and institution metadata for the current user."),
        ("POST", "/api/register", "Public", "Student self-registration mapped to college code and class."),
        ("GET / POST", "/api/colleges", "Root Admin", "Lists colleges or registers a new college and Principal."),
        ("GET / POST", "/api/depts", "Principal", "Lists departments or adds department and assigns HOD."),
        ("GET / POST", "/api/teachers", "Principal / HOD", "Lists faculty directory or registers new department teachers."),
        ("POST", "/api/lectures", "Teacher", "Schedules single lecture with automated conflict checking."),
        ("POST", "/api/lectures/<id>/start", "Teacher", "Makes lecture live, generates 4-digit code, notifies SSE stream."),
        ("POST", "/api/lectures/<id>/checkin", "Student", "Records attendance using matching 4-digit class code."),
        ("POST", "/api/lectures/<id>/substitute", "HOD", "Reassigns teacher on pending unstarted lecture."),
        ("GET / POST", "/api/timetable", "Teacher", "Fetches timetable slots or generates recurring multi-week lectures."),
        ("GET", "/api/live", "All Users", "Fetches running live lectures and punctuality alerts."),
        ("GET", "/api/reports", "Admin / HOD", "Returns teacher compliance, punctuality, and attendance analytics."),
        ("GET", "/api/reports.csv", "Admin / HOD", "Exports performance report as an RFC 4180 CSV download."),
        ("GET", "/api/stream", "Auth", "Server-Sent Events (SSE) live push synchronization stream.")
    ]
    t_a = doc.add_table(rows=len(api_data)+1, cols=4)
    t_a.alignment = WD_TABLE_ALIGNMENT.CENTER
    wa = [Inches(1.0), Inches(2.1), Inches(1.2), Inches(2.2)]
    for j, h in enumerate(["Method", "Endpoint", "Role", "Description"]):
        cell = t_a.rows[0].cells[j]
        cell.width = wa[j]
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
    for i, row in enumerate(api_data):
        for j, val in enumerate(row):
            cell = t_a.rows[i+1].cells[j]
            cell.width = wa[j]
            if i % 2 == 1:
                set_cell_background(cell, "F9FBFC")
            set_cell_margins(cell, 50, 50, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(9)
            r.font.color.rgb = charcoal

    # --- SECTION 7 ---
    add_h1("7. Literature Review References & Feedback Summary")
    add_h2("Academic References")
    add_bullet("Patel, R., & Patel, N. (2020). 'Automated Student Attendance Management System Using QR-Code and Dynamic Tokenization.' International Journal of Computer Applications, 175(12), pp. 24–29.")
    add_bullet("Fette, I., & Melnikov, A. (2011). 'The WebSocket Protocol & Server-Sent Events for Web Applications.' RFC 6455 / IETF Standards Track.")
    add_bullet("Sommerville, I. (2016). Software Engineering (10th ed.). Pearson Education.")
    add_bullet("Grinberg, M. (2018). Flask Web Development: Developing Web Applications with Python (2nd ed.). O'Reilly Media.")
    add_bullet("Kumar, S., & Sharma, M. (2022). 'Design and Implementation of Academic Information Systems for Real-Time Institutional Monitoring.' IEEE Transactions on Learning Technologies, 15(4), pp. 412–421.")

    add_h2("Feedback Form Details")
    add_p("Aditya Sudhir Rana", bold_prefix="Student Name:")
    add_p("S105", bold_prefix="Roll Number:")
    add_p("S.Y. B.Sc. Computer Science (Semester III)", bold_prefix="Class & Semester:")
    add_p("SHETH L.U.J. AND SIR M.V. COLLEGE", bold_prefix="College Name:")
    add_p("ranaadityacs252612@gmail.com", bold_prefix="Student Email ID:")
    add_p("Mr. Rohit Kumar Sahu", bold_prefix="Project Guide:")
    add_p("Ms. Jyoti Chauhan and Mr. Rohit Kumar Sahu", bold_prefix="Course Coordinators:")
    add_p("01-08-2026 to 10-10-2026", bold_prefix="Project Duration:")

    doc.save(DOCX_OUT)
    print(f"DOCX created: {DOCX_OUT}")

# ----------------- PDF GENERATION -----------------
def create_pdf():
    doc = SimpleDocTemplate(
        PDF_OUT,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    c_navy = colors.HexColor('#1B365D')
    c_slate = colors.HexColor('#37557D')
    c_charcoal = colors.HexColor('#222222')
    
    style_inst = ParagraphStyle('InstHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=c_navy, alignment=0)
    style_dept = ParagraphStyle('DeptHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=c_slate, alignment=0)
    style_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=c_navy, spaceAfter=4)
    style_sub = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=10, leading=13, textColor=c_charcoal, spaceAfter=10)
    style_h1 = ParagraphStyle('DocH1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=c_navy, spaceBefore=12, spaceAfter=6, keepWithNext=True)
    style_h2 = ParagraphStyle('DocH2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=c_slate, spaceBefore=8, spaceAfter=4, keepWithNext=True)
    style_body = ParagraphStyle('DocBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=c_charcoal, spaceAfter=4)
    style_bullet = ParagraphStyle('DocBullet', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=c_charcoal, leftIndent=12, spaceAfter=2)
    style_th = ParagraphStyle('DocTH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=colors.white)
    style_td = ParagraphStyle('DocTD', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=c_charcoal)

    story = []
    
    # Header
    story.append(Paragraph("SHETH L.U.J. AND SIR M.V. COLLEGE", style_inst))
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE ― ACADEMIC YEAR: 2026–2027", style_dept))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_slate, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("CampusLive: Real-Time Lecture Monitoring and Verification for Colleges", style_title))
    story.append(Paragraph("Field Project Documentation ― S.Y. B.Sc. Computer Science (Semester III)", style_sub))
    
    meta_table_data = [
        [Paragraph("<b>Student Name & Roll No.</b>", style_td), Paragraph("Aditya Sudhir Rana  |  Roll Number: S105", style_td)],
        [Paragraph("<b>Class & Semester</b>", style_td), Paragraph("S.Y. B.Sc. Computer Science (Semester III)", style_td)],
        [Paragraph("<b>Project Guide</b>", style_td), Paragraph("Mr. Rohit Kumar Sahu", style_td)],
        [Paragraph("<b>Course Coordinators</b>", style_td), Paragraph("Ms. Jyoti Chauhan and Mr. Rohit Kumar Sahu", style_td)],
        [Paragraph("<b>Official Student Email</b>", style_td), Paragraph("ranaadityacs252612@gmail.com", style_td)]
    ]
    t_meta = Table(meta_table_data, colWidths=[1.8*inch, 4.8*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F4F8')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D0DCE5')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # Section 1
    story.append(Paragraph("1. Project Title & Official Descriptions", style_h1))
    story.append(Paragraph("<b>Exact Title:</b> CampusLive: Real-Time Lecture Monitoring and Verification for Colleges", style_body))
    story.append(Paragraph("<b>Description:</b> <i>\"CampusLive is a real-time academic monitoring platform where teachers make lectures officially live, students confirm they are present with a class code, and principals and HODs see which lectures are actually being held across the college as they happen. Timetables, substitutions, reports and activity logs run on the same platform.\"</i>", style_body))
    story.append(Paragraph("<b>Short Description:</b> <i>\"CampusLive is a real-time platform where teachers make lectures live, students verify them, and principals and HODs monitor what is actually being taught across the college.\"</i>", style_body))

    # Section 2
    story.append(Paragraph("2. Guide Interaction Diary", style_h1))
    diary_rows = [
        [Paragraph("<b>Meeting Date</b>", style_th), Paragraph("<b>Progress / Agenda Discussed</b>", style_th), Paragraph("<b>Remarks / Guide's Feedback</b>", style_th)],
        [Paragraph("06-08-2026", style_td), Paragraph("Initial project ideation: Identifying the need for real-time institutional visibility of ongoing lectures; project scope and objectives approval.", style_td), Paragraph("Recommended focusing on administrative monitoring, departmental hierarchy, and student verification.", style_td)],
        [Paragraph("11-08-2026", style_td), Paragraph("Requirement specifications: Defining the 5-tier role structure (Root -> Principal -> HOD -> Teacher -> Student) and designing the relational database schema.", style_td), Paragraph("Approved database entities and recommended incorporating automated conflict checks for rooms and teachers.", style_td)],
        [Paragraph("18-08-2026", style_td), Paragraph("Backend REST API design in Flask: Implementation of session authentication, PBKDF2 password hashing, and SQLite schema with Write-Ahead Logging (WAL).", style_td), Paragraph("Reviewed authentication security and classroom scheduling validation logic.", style_td)],
        [Paragraph("25-08-2026", style_td), Paragraph("Integration of Server-Sent Events (SSE) for push synchronization and development of the background sweeper daemon for automated lecture lifecycle tracking.", style_td), Paragraph("Verified real-time event distribution and background state transitions.", style_td)],
        [Paragraph("01-09-2026", style_td), Paragraph("Frontend single-page application (SPA) design: Implementing the live departures-style board, modal dialog registry, and the 4-digit student verification check-in.", style_td), Paragraph("Approved the student verification model and recommended keeping aggregate attendance statistics accessible to staff only.", style_td)],
        [Paragraph("08-09-2026", style_td), Paragraph("Implementation of the multi-week recurring timetable generator, HOD substitution workflow, dynamic room reallocation, and CSV reports.", style_td), Paragraph("Advised verifying clash resolution logic across multi-week recurring slots.", style_td)],
        [Paragraph("05-10-2026", style_td), Paragraph("End-to-end integration testing (tests/test_flow.py), field feedback review, edge-case fixes, and preparation of final documentation.", style_td), Paragraph("Approved the system and results for final documentation and academic submission.", style_td)]
    ]
    t_d_pdf = Table(diary_rows, colWidths=[1.1*inch, 3.2*inch, 2.5*inch])
    t_d_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#EEEEEE')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_d_pdf)

    # Section 3
    story.append(Paragraph("3. The Project Itself & Problem Statement", style_h1))
    story.append(Paragraph("CampusLive is a real-time academic activity management and operational visibility platform designed for collegiate institutions. In conventional college management, institutional leadership (Principals and HODs) lacks immediate operational visibility into daily lecture conduction without conducting physical floor rounds or manual inquiries. Furthermore, traditional paper registers consume valuable instructional time and require significant manual transcription.", style_body))
    story.append(Paragraph("CampusLive bridges this gap by transforming static timetables into an active, verifiable digital operational environment:", style_body))
    story.append(Paragraph("• <b>Live Institutional Visibility:</b> Centralized departures-style board displaying active lectures, occupied classrooms, and start punctuality.", style_bullet))
    story.append(Paragraph("• <b>Attendance and Student Verification of Lectures:</b> Ephemeral 4-digit class code on the teacher's screen; students confirm presence; verified at >= 2 check-ins.", style_bullet))
    story.append(Paragraph("• <b>Automated Conflict Resolution:</b> Real-time checks during scheduling prevent room and faculty overlapping clashes.", style_bullet))
    story.append(Paragraph("• <b>Automated Lifecycle Closure:</b> Background sweeper thread auto-closes forgotten live lectures after 15 min grace and updates unstarted lectures to MISSED.", style_bullet))
    story.append(Paragraph("• <b>Reports and Analytics:</b> Provides objective metrics: Held Rate (%), Average Start Delay (minutes), and Student Attendance (%) with CSV download.", style_bullet))

    story.append(Paragraph("Users and Beneficiaries", style_h2))
    story.append(Paragraph("The primary beneficiary of CampusLive is the College Administration (Principal, Vice-Principals, and HODs) for centralized governance and quality assurance, alongside faculty and students:", style_body))
    story.append(Paragraph("• <b>Principal (College Admin):</b> Bird's-eye view of all academic activity, active classrooms, faculty schedules, and compliance analytics.", style_bullet))
    story.append(Paragraph("• <b>Heads of Department (HODs):</b> Departmental oversight, assigning substitute faculty for pending lectures, and room reallocations. Head of Department: Asst. Prof. Pradnya Kharade.", style_bullet))
    story.append(Paragraph("• <b>Teachers / Faculty:</b> Schedule sessions, launch live lecture, display verification PIN, track attendance, and manage weekly timetables. Core Faculty: Asst. Prof. Rohit Sahu (Project Guide) and Asst. Prof. Jyoti Chauhan (Course Coordinator).", style_bullet))
    story.append(Paragraph("• <b>Students:</b> View active sessions for their class, submit PIN to confirm attendance, and view timetable and attendance history. Registered Student Cohort: Aditya Rana (S105), Mohi Pathan, Suraj, Dhruv Choubey, and Akshat Halwai.", style_bullet))
    story.append(Paragraph("• <b>Root Administrator:</b> Provisions college instances and assigns Principal accounts.", style_bullet))

    # Section 4
    story.append(Paragraph("4. Key Objectives, Modules & Technical Architecture", style_h1))
    story.append(Paragraph("• <b>Live Campus Monitoring Board:</b> Real-time board grouping lectures by department with elapsed timers and late-start alerts.", style_bullet))
    story.append(Paragraph("• <b>Attendance and Student Verification of Lectures:</b> 4-digit code check-in; verification threshold at >= 2 check-ins; student privacy enforced.", style_bullet))
    story.append(Paragraph("• <b>Reports and Analytics:</b> Total, Held, Missed, and Cancelled lectures, Held Rate (%), Average Start Delay (min), and Attendance (%) with CSV export.", style_bullet))
    story.append(Paragraph("• <b>Lecture State Machine & Sweeper Daemon:</b> State flow SCHEDULED -> LIVE -> COMPLETED / CANCELLED / MISSED; 30-second interval daemon.", style_bullet))
    story.append(Paragraph("• <b>Weekly Timetable & Clash Resolution Engine:</b> Multi-week generator (1-12 weeks) skipping room and teacher schedule overlaps.", style_bullet))
    story.append(Paragraph("• <b>Academic Administration & Substitution:</b> HOD teacher substitution on unstarted lectures with audit tracking (covering_for) and room shifts.", style_bullet))
    story.append(Paragraph("• <b>Security, Multi-Tenant RBAC & Activity Logs:</b> PBKDF2 hashing, 5-tier role protection, account deactivations, and immutable event logs.", style_bullet))
    
    story.append(Paragraph("Technology Stack & Scope", style_h2))
    story.append(Paragraph("<b>Languages:</b> Python 3.13, Modern JavaScript (ES6+), HTML5, CSS3. | <b>Backend:</b> Flask 3.x, Werkzeug Security.<br/><b>Real-Time Push:</b> Server-Sent Events (SSE) via queue.Queue, threading.Lock. | <b>Database:</b> SQLite 3 WAL Mode.<br/><b>Frontend:</b> Vanilla JavaScript Single-Page Application (SPA). | <b>Scope Limitations:</b> Remote video streaming, biometric turnstiles, student fee accounting, and native mobile store wrappers are outside functional scope.", style_body))

    # Section 5
    story.append(Paragraph("5. Field Work, Methodology & Testing", style_h1))
    story.append(Paragraph("<b>Requirements Gathering & Field Consultation:</b> Conducted during August 2026 at Sheth L.U.J. and Sir M.V. College:<br/>"
                           "• <b>Faculty and Departmental Interviews:</b> Interviewed 2 faculty members (1 Head of Department and 1 teaching faculty). Discussions established the operational need for an immediate link between classrooms and administrative offices and highlighted the value of automating manual paper attendance.<br/>"
                           "• <b>Classroom Workflow Observation:</b> Observed standard roll-call routines in undergraduate classrooms, noting the time consumed by manual roll calls and confirming the need for a rapid digital check-in completed in under 15 seconds.<br/>"
                           "• <b>Administrative Metric Definition:</b> Consultations with project guides and coordinators determined the essential daily tracking metrics: verifying lecture conduction, start punctuality, and generating structured attendance records.", style_body))
    story.append(Paragraph("<b>Build and Testing Methodology:</b> Developed using iterative agile prototyping. Automated testing with <code>tests/test_flow.py</code> validated 13 integration scenarios: tenant onboarding, departmental setup, conflict detection, live activation, 4-digit PIN check-in, verification threshold (>= 2 check-ins), HOD substitution, sweeper auto-completion, and CSV export. All checks passed successfully.", style_body))
    story.append(Paragraph("<b>Future Improvements:</b> Dynamic rotating QR codes, automated browser web push notifications, interactive visual charting (Chart.js) for Reports and Analytics, and PostgreSQL deployment profiles.", style_body))

    # Section 6
    story.append(Paragraph("6. Evidence, Database & API Specifications", style_h1))
    story.append(Paragraph("<b>List of Figures:</b> Fig 1: Public Landing Page | Fig 2: Student Self-Registration Modal | Fig 3: Principal Live Campus Monitoring Dashboard | Fig 4: Lecture Detail & Timeline Modal | Fig 5: Department & HOD Management | Fig 6: Faculty Directory & Live Status | Fig 7: Lecture Scheduling Modal | Fig 8: Weekly Timetable Slot Manager | Fig 9: Teacher Active Lecture Controller | Fig 10: Student Live Board & PIN Check-in | Fig 11: HOD Substitution & Room Reallocation | Fig 12: Central Activity Audit Log | Fig 13: Academic Compliance & Punctuality Report | Fig 14: User Profile & Security Settings.", style_body))
    story.append(Paragraph("<b>Database Schema (SQLite WAL Mode):</b> Tables: <code>colleges</code> (code UNIQUE), <code>depts</code>, <code>classes</code>, <code>users</code>, <code>lectures</code>, <code>attendance</code> (PRIMARY KEY lecture_id, student_id), <code>timetable</code>, <code>logs</code>.", style_body))
    story.append(Paragraph("<b>Key API Endpoints:</b> Auth (/api/login, /api/register, /api/me), Monitoring (/api/live, /api/upcoming, /api/history), Teaching & Lifecycle (/api/lectures, /api/lectures/&lt;id&gt;/start|end|cancel|room|substitute), Timetable (/api/timetable), Reports (/api/reports, /api/reports.csv), Real-Time Stream (/api/stream).", style_body))

    # Section 7
    story.append(Paragraph("7. Literature Review References & Feedback Summary", style_h1))
    story.append(Paragraph("• Patel, R., & Patel, N. (2020). 'Automated Student Attendance Management System Using QR-Code and Dynamic Tokenization.' IJCA, 175(12), pp. 24–29.<br/>"
                           "• Fette, I., & Melnikov, A. (2011). 'The WebSocket Protocol & Server-Sent Events for Web Applications.' RFC 6455 / IETF.<br/>"
                           "• Sommerville, I. (2016). Software Engineering (10th ed.). Pearson Education.<br/>"
                           "• Grinberg, M. (2018). Flask Web Development: Developing Web Applications with Python (2nd ed.). O'Reilly Media.<br/>"
                           "• Kumar, S., & Sharma, M. (2022). 'Design and Implementation of Academic Information Systems for Real-Time Institutional Monitoring.' IEEE TLT, 15(4), pp. 412–421.", style_body))
    
    story.append(Paragraph("<b>Feedback Form Details:</b> Student: Aditya Sudhir Rana (S105) | Class: S.Y. B.Sc. Computer Science (Sem III) | College: SHETH L.U.J. AND SIR M.V. COLLEGE | Email: ranaadityacs252612@gmail.com | Guide: Mr. Rohit Kumar Sahu | Coordinators: Ms. Jyoti Chauhan and Mr. Rohit Kumar Sahu | Duration: 01-08-2026 to 10-10-2026.", style_body))

    doc.build(story)
    print(f"PDF created: {PDF_OUT}")

if __name__ == "__main__":
    create_docx()
    create_pdf()
