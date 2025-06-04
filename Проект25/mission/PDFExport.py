'''
Created on May 24, 2025

@author: redbu
'''
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime

# 主関数

def export_mission_pdf(filename, ctx, carrier):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 50

    # --- Header ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, height - 50, "MISSION REPORT")

    c.setFont("Helvetica", 10)
    c.drawString(margin, height - 70, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(margin, height - 85, f"Mission Type: {ctx.mission_type}")
    c.drawString(margin, height - 100, f"Aircraft: F/A-18C")
    c.drawString(margin, height - 115, f"Carrier: {carrier.name} ({carrier.lat}, {carrier.lon})")

    # --- Segment Table ---
    data = [["Seg", "Phase", "Lat", "Lon", "Alt(ft)", "Spd(kt)", "Dist(NM)", "Fuel(lb)"]]

    for i, (wp, phase, fuel) in enumerate(zip(ctx.flightplan.waypoints[1:], ctx.segment_phases, ctx.segment_fuel), 1):
        data.append([
            i, phase,
            f"{wp.latitude:.2f}", f"{wp.longitude:.2f}",
            wp.altitude_ft, wp.speed_kt, round(wp.distance_nm, 1), round(fuel, 1)
        ])

    table = Table(data, colWidths=[40]*8)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, margin, height - 350)

    # --- Summary ---
    c.setFont("Helvetica", 11)
    y_summary = height - 380 - len(ctx.segment_fuel)*18
    c.drawString(margin, y_summary, f"Total Flight Time: {ctx.total_flight_time_min:.1f} min")
    c.drawString(margin, y_summary - 15, f"Landing Weight: {ctx.landing_weight:.1f} lb")
    c.drawString(margin, y_summary - 30, f"Total Fuel Used: {sum(ctx.segment_fuel):.1f} lb")

    c.showPage()
    c.save()

    print(f"PDF exported to {filename}")