"""
IF.witness PDF Compliance Report Generator
Creates professional compliance reports with chain validation results and witness entries.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class ComplianceReportGenerator:
    """
    Generates professional compliance reports for IF.witness audit trails.

    Philosophy: IF.ground Principle 8 - Observability without fragility.
    Create clean, professional reports that demonstrate compliance with audit requirements
    while maintaining the integrity of the hash chain.
    """

    def __init__(self):
        """Initialize the report generator."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a3a52'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=10,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

    def _generate_report_hash(self, content: str) -> str:
        """Generate SHA-256 hash of entire report content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def _parse_date_range(self, entries: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Extract date range from entries."""
        if not entries:
            return "N/A", "N/A"

        timestamps = [datetime.fromisoformat(e['timestamp']) for e in entries]
        start_date = min(timestamps)
        end_date = max(timestamps)

        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

    def generate_pdf(
        self,
        entries: List[Dict[str, Any]],
        output_path: str,
        verification_results: Optional[Tuple[bool, str, int]] = None,
        cost_summary: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a professional compliance PDF report.

        Args:
            entries: List of witness entries to include in report
            output_path: Path to save PDF file
            verification_results: Tuple of (is_valid, error_msg, entry_count)
            cost_summary: Dictionary with cost breakdown by component

        Returns:
            Path to generated PDF file
        """
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Create document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        # Build story (list of elements to add to PDF)
        story = []

        # Title
        title = Paragraph(
            "IF.witness Compliance Report",
            self.styles['ReportTitle']
        )
        story.append(title)

        # Metadata
        start_date, end_date = self._parse_date_range(entries)
        generation_ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

        metadata_text = f"""
        <b>Date Range:</b> {start_date} to {end_date}<br/>
        <b>Generated:</b> {generation_ts}<br/>
        <b>Total Entries:</b> {len(entries)}
        """
        story.append(Paragraph(metadata_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Section 1: Chain Validation Results
        story.append(Paragraph("Section 1: Chain Validation Results", self.styles['SectionHeading']))

        if verification_results:
            is_valid, error_msg, count = verification_results
            status = "VALID" if is_valid else "INVALID"
            status_color = '#2d7f2d' if is_valid else '#b32b27'

            validation_text = f"""
            <b>Chain Integrity:</b> <font color="{status_color}"><b>{status}</b></font><br/>
            <b>Message:</b> {error_msg}<br/>
            <b>Total Entries Verified:</b> {count}
            """
            story.append(Paragraph(validation_text, self.styles['Normal']))
        else:
            story.append(Paragraph("Verification status not available", self.styles['Normal']))

        story.append(Spacer(1, 0.2 * inch))

        # Section 2: Witness Entries Table
        story.append(Paragraph("Section 2: All Witness Entries", self.styles['SectionHeading']))

        if entries:
            # Build table data
            table_data = [[
                'ID', 'Timestamp', 'Event', 'Component', 'Trace ID',
                'Content Hash (first 16)', 'Signature (first 16)'
            ]]

            for entry in entries:
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                content_hash = entry.get('content_hash', 'N/A')[:16]
                signature = entry.get('signature', 'N/A')[:16]
                entry_id = entry.get('id', 'N/A')[:8]

                table_data.append([
                    entry_id,
                    timestamp,
                    entry.get('event', 'N/A')[:15],
                    entry.get('component', 'N/A')[:12],
                    entry.get('trace_id', 'N/A')[:12],
                    content_hash,
                    signature
                ])

            # Create table with styling
            table = Table(table_data, colWidths=[0.8*inch, 1.0*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.0*inch, 1.0*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ]))

            story.append(table)
        else:
            story.append(Paragraph("No entries to display", self.styles['Normal']))

        story.append(Spacer(1, 0.2 * inch))

        # Section 3: Cost Summary
        story.append(Paragraph("Section 3: Cost Summary", self.styles['SectionHeading']))

        if cost_summary:
            total_cost = cost_summary.get('total_cost_usd', 0.0)
            total_tokens = cost_summary.get('total_tokens', 0)

            cost_text = f"""
            <b>Total Cost:</b> ${total_cost:.6f}<br/>
            <b>Total Tokens:</b> {total_tokens}
            """
            story.append(Paragraph(cost_text, self.styles['Normal']))

            # Cost breakdown by component
            components = cost_summary.get('by_component', [])
            if components:
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph("Cost Breakdown by Component:", self.styles['Normal']))

                breakdown_data = [['Component', 'Operations', 'Tokens', 'Cost (USD)']]
                for comp in components:
                    breakdown_data.append([
                        comp.get('component', 'N/A'),
                        str(comp.get('operations', 0)),
                        str(comp.get('total_tokens', 0)),
                        f"${comp.get('total_cost', 0.0):.6f}"
                    ])

                breakdown_table = Table(breakdown_data, colWidths=[2.0*inch, 1.2*inch, 1.2*inch, 1.3*inch])
                breakdown_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('TOPPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ]))
                story.append(breakdown_table)
        else:
            story.append(Paragraph("No cost data available", self.styles['Normal']))

        story.append(Spacer(1, 0.2 * inch))

        # Section 4: IF.ground Principles
        story.append(Paragraph("Section 4: IF.ground Principles", self.styles['SectionHeading']))

        principles_text = """
        <b>Principle 8 - Observability without Fragility</b><br/>
        This report demonstrates observability through comprehensive audit trails.
        All entries are cryptographically signed and chained, ensuring tamper detection.<br/>
        <br/>
        <b>Mapped Entries:</b> All {0} entries in this report are logged under Principle 8
        (Observability) as they provide complete provenance tracking for all operations.<br/>
        <br/>
        <b>IF.guard Integration:</b> IF.guard approval logs integration pending
        """.format(len(entries))

        story.append(Paragraph(principles_text, self.styles['Normal']))

        story.append(Spacer(1, 0.3 * inch))

        # Footer with report hash
        report_content = (
            f"IF.witness Compliance Report\n"
            f"Date Range: {start_date} to {end_date}\n"
            f"Generated: {generation_ts}\n"
            f"Total Entries: {len(entries)}\n"
        )

        report_hash = self._generate_report_hash(report_content)
        footer_text = f"""
        <b>Report Integrity Hash (SHA-256):</b><br/>
        <font face="Courier" size="7">{report_hash}</font><br/>
        <br/>
        <i>This report was generated by IF.witness compliance export tool.</i>
        """

        story.append(Paragraph(footer_text, self.styles['Normal']))

        # Build PDF
        doc.build(story)

        return str(output_path)
