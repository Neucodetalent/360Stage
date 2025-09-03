# Core Libraries
import os
import io
import sys
import time
import shutil
import tempfile
from datetime import datetime
import subprocess

# Data Handling
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import plotly.graph_objs as go

# Dash for Web Applications
from dash import Dash, dcc, html, Input, Output
from dash.dash_table import DataTable

# Text Handling
import textwrap
from textwrap import wrap

# ReportLab for PDF Generation
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
)

# PyPDF2 for PDF Merging
from PyPDF2 import PdfMerger

# PIL for Image Handling
from PIL import Image as PILImage
from reportlab.platypus import Image

# Azure Storage (Optional)
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.identity import ClientSecretCredential

# Django (Optional)
from django.http import JsonResponse
from io import BytesIO

import zipfile
from io import BytesIO

 
# Configuration
AZURE_STORAGE_ACCOUNT_NAME = 'neucodestoragedev'  # Replace with your storage account name
AZURE_CONTAINER_NAME = 'neucode-container'      # Replace with your container name
AZURE_STORAGE_ACCOUNT_URL = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
 
# Azure Blob Service Client Initialization
#credential = DefaultAzureCredential()
credential = ClientSecretCredential(
    tenant_id="b2aa0d4b-c7bf-49f4-9539-6ff110ea720d",
    client_id="4c676a8b-1afa-471f-b199-d643ba8e6fa4",
    client_secret="VsC8Q~kiRAD4iFnPHzffrpkhYIe32n_8SPlhyajV"
)
blob_service_client = BlobServiceClient(account_url=AZURE_STORAGE_ACCOUNT_URL, credential=credential)

full_rating_path = sys.argv[1]
open_question_path = sys.argv[2]
p_assessment_number_path = sys.argv[3]

# full_rating_path = 'D:/Projects/Neucode/Neucode Talent/360 Rating Data_For Testing.pkl'
# open_question_path = 'D:/Projects/Neucode/Neucode Talent/360 Open Question_For Testing.pkl'
# Load DataFrames
# full_rating_df = pd.read_pickle(full_rating_path)
# open_question_df = pd.read_pickle(open_question_path)

# Load DataFrames
full_rating_df = pd.read_excel(full_rating_path)
open_question_df = pd.read_excel(open_question_path)
assement_number_df = pd.read_excel(p_assessment_number_path)

full_rating_df.rename(columns= {'seeker_name':'Seeker Name','seeker_email': 'Seeker Email', 'relationship':'Relationship'
                                , 'provider_email': 'Provider Email', 'question_text': 'Statements', 'competency': 'Competency mapped to Statement'
                                , 'feedback_value': 'Rating'}, inplace = True)
open_question_df.rename(columns= {'seeker_name':'Seeker Name','seeker_email': 'Seeker Email', 'relationship':'Relationship'
                                , 'provider_email': 'Provider Email', 'question_text': 'Statements'
                                , 'feedback_value': 'Rating', 'feedback_text': 'Response'}, inplace = True)

# full_rating_df.rename(columns= {'SeekerName':'Seeker Name','SeekerEmail': 'Seeker Email', 'relationship':'Relationship'
#                                 , 'ProviderEmail': 'Provider Email', 'QuestionText': 'Statements', 'Competency': 'Competency mapped to Statement'
#                                 , 'FeedbackValue': 'Rating'}, inplace = True)
# open_question_df.rename(columns= {'SeekerName':'Seeker Name','SeekerEmail': 'Seeker Email', 'relationship':'Relationship'
#                                 , 'ProviderEmail': 'Provider Email', 'QuestionText': 'Statements'
#                                 , 'FeedbackValue': 'Rating', 'FeedbackText': 'Response'}, inplace = True)

ODB_360=open_question_df
FRD=full_rating_df
assessment = assement_number_df

print(f'FRD::::::::>>>>>>> {FRD.head()}')  # Check FRD data
print(f'ODB::::::::>>>>>>> {ODB_360.head()}')  # Check ODB_360 data
print(f'Assement::::::::>>>>>>> {assessment.head()}') 

rd=FRD[['Seeker Name','Seeker Email','Relationship','Statements','Competency mapped to Statement','Rating']].copy()
print(f'RD::::::::>>>>>>> {rd.head()}')

def assessment_number(df):
    try:
        # Check if DataFrame is empty
        if df.empty:
            return "00"
        
        # Extract the value from the column and row
        value = df.loc[0, "assessment_type"]
        value1 = df.loc[0, "project_name"]
        value2 = df.loc[0, "client_name"]   
        
        # Check if the value is missing, None, or empty string
        if pd.isna(value) or value == "":
            return "00", '00', '00'
        
        return value, value1, value2
    except Exception as e:
        # Handle any unexpected errors
        return "00"

assessment_number, project1, client1=assessment_number(assessment)
print(f"11.....Assessment number is ----------->>>>> {assessment_number} ")
print(f"11.....Project is ----------->>>>> {project1} ")
print(f"11.....Client is ----------->>>>> {client1} ")

def Create_RD(db):
    # Separate 'Self' ratings
    self_ratings = db[db['Relationship'] == 'Self']

    # Calculate SelfAvg
    self_avg = self_ratings[['Seeker Name', 'Seeker Email', 'Statements', 'Competency mapped to Statement', 'Rating']]
    self_avg = self_avg.rename(columns={'Rating': 'SelfAvg'})

    # Calculate OtherAvg (excluding 'Self')
    other_ratings = db[db['Relationship'] != 'Self']
    other_avg = (
        other_ratings
        .groupby(['Seeker Name', 'Seeker Email', 'Statements', 'Competency mapped to Statement'])['Rating']
        .mean()
        .reset_index()
        .rename(columns={'Rating': 'OtherAvg'})
    )

    # Merge SelfAvg and OtherAvg
    result = pd.merge(self_avg, other_avg, 
                      on=['Seeker Name', 'Seeker Email', 'Statements', 'Competency mapped to Statement'],
                      how='left')

    return result

RD = Create_RD(rd)
RD=RD[(~RD['SelfAvg'].isna())&(~RD['OtherAvg'].isna())]
RD['cStrength']=np.where((RD['OtherAvg'] > 3.5) & (RD['SelfAvg'] > 3.5),"Yes","No")
RD['cImprovArea'] = np.where((RD['OtherAvg'] < 3.5) & (RD['SelfAvg'] < 3.5),"Yes","No")
RD['cBlindSpot'] = np.where((RD['OtherAvg'] < 3.5) & (RD['SelfAvg'] >= 3.5),'Yes','No')
RD['cHiddenStrength'] = np.where((RD['OtherAvg'] > 3.5) & (RD['SelfAvg'] < 3.5),'Yes','No')

def Strength(db,email):
    sorted_db = db[(db['Seeker Email']==email)&(db['cStrength']=="Yes")].sort_values(by=['OtherAvg', 'SelfAvg', 'Statements'],ascending=[False, False, True])
    return sorted_db[['Statements','Competency mapped to Statement','OtherAvg']].rename(columns={'Competency mapped to Statement':'Competency','OtherAvg':'Average Rating'}).head(5)

def improvement(db,email):
    sorted_db = db[(db['Seeker Email']==email)&(db['cImprovArea']=="Yes")].sort_values(by=['OtherAvg', 'SelfAvg', 'Statements'],ascending=[True, True, True])
    return sorted_db[['Statements','OtherAvg']].rename(columns={'OtherAvg':"Rating"}).head(5)

def blind_spots(db,email):
    sorted_db = db[(db['Seeker Email']==email)&(db['cBlindSpot']=="Yes")].sort_values(by=['OtherAvg', 'SelfAvg', 'Statements'],ascending=[True, False, True])
    return sorted_db[['Statements','SelfAvg','OtherAvg']].rename(columns={'SelfAvg':'Self','OtherAvg':"Other"}).head(5)

def hidden_strength(db, email):
    sorted_db = db[(db['Seeker Email']==email)&(db['cHiddenStrength']=="Yes")].sort_values(by=['OtherAvg', 'SelfAvg', 'Statements'],ascending=[False, True, True])
    return sorted_db[['Statements','SelfAvg','OtherAvg']].rename(columns={'SelfAvg':'Self','OtherAvg':"Other"}).head(5)

#Adding Others column in FRD
FRD['Others'] = FRD['Relationship'].apply(lambda x: 'Self' if x == 'Self' else 'Others')

#Calculating the average rating, grouped by 'Competency mapped to Statement' for a particular seeker
def uAllRatingAvg(db,email,competency):
    uAllRatingAvg = db[(db['Seeker Email']==email)&(db['Competency mapped to Statement']==competency)].groupby('Competency mapped to Statement')['Rating'].mean().to_dict()[competency]
    return uAllRatingAvg

#Calculating the average rating, grouped by 'Competency mapped to Statement' for Others
def Accountability(db,competency):
    Accountability = db[(db['Competency mapped to Statement']==competency)].groupby('Competency mapped to Statement')['Rating'].mean().to_dict()[competency]
    return Accountability

def create_first_page(pdf_path, image_path, logo_path, assessment_number, candidate_name):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Add logo - Centered with blank space above
    logo_width = 275 / 72  # Convert px to inches
    logo_height = 57 / 72  # Convert px to inches
    logo_y_position = height - 120  # Positioned lower to create blank space above

    c.drawImage(logo_path, (width - logo_width * inch) / 2, logo_y_position, width=logo_width * inch, height=logo_height * inch)

    # Title and Candidate Name - Centered and closer to the image
    c.setFont("Helvetica-Bold", 28)
    title_text = f"{assessment_number} - Degree Assessment Report"
    c.drawCentredString(width / 2, height - 220, title_text)  # Positioned closer to the image

    c.setFont("Helvetica-Bold", 26)
    c.setFillColorRGB(13 / 255, 106 / 255, 291 / 255)
    c.drawCentredString(width / 2, height - 270, candidate_name)  # Positioned closer to the image

    # Add image - Stretched to the full width with padding, centered, and increased height
    img_width = width - 80  # Set width to almost the full page with padding
    img_height = 4 * inch  # Increased height to make the image more prominent
    c.drawImage(image_path, 40, (height - img_height) / 2 - 30, width=img_width, height=img_height)

    # Get the current date (only the date, not the time)
    current_date = datetime.now().strftime('%B %d, %Y')  # Format: Month Day, Year

    # Print the current date below the image
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    date_y_position = (height - img_height) / 2 - 50  # Adjusting the Y position below the image
    c.drawCentredString(width / 2, date_y_position, current_date)  # Centered date text

    # Add footer text - Split into two lines for better fit
    c.setFont("Helvetica",9)
    c.setFillColor(colors.grey)
    
    # First part of footer text
    footer_text_1 = "This report is confidential and for personal development purposes only.Unauthorized distribution or use of this document is strictly prohibited." 
    c.drawCentredString(width / 2, 50, footer_text_1)  # Positioned closer to the bottom

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.grey)

    # Third part of footer text 
    footer_text_3 = "©Copyright 2025 NeuCode Talent Academy LLP"
    c.drawCentredString(width / 2, 30, footer_text_3)  # Positioned further down for new line

    # Save PDF
    c.showPage()
    c.save()

    print("First page generated successfully")

def create_second_page(pdf_path, logo_path):
    # Create PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Second Page: Table of Contents
    # Adjust the size of the logo for the second page
    logo_width_second_page = 1.8 * inch  # Smaller width for the logo on the second page
    logo_height_second_page = 0.41 * inch  # Smaller height for the logo on the second page
    c.drawImage(logo_path, width - logo_width_second_page - 30, height - logo_height_second_page - 30, 
                width=logo_width_second_page, height=logo_height_second_page)

    # Add "Table of Contents" heading
    heading_y_position = height - logo_height_second_page - 10 - 60  # 10 for the margin from top, 40 for the gap
    c.setFont("Helvetica-Bold", 24)

    # Set x position for left alignment
    heading_x_position = 50
    c.drawString(heading_x_position, heading_y_position, "Table of Contents")

    # Draw underline for the heading across the full width of the page
    underline_y_position = heading_y_position - 20  # 5 px space between the text and the underline
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.line(40, underline_y_position, width - 40, underline_y_position)  # Stretch to the full width of the page

    # Draw blue rectangle marker next to the heading
    marker_width = 9
    marker_height = 40
    c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
    c.rect(heading_x_position - 15, heading_y_position - 12, marker_width, marker_height, fill=1, stroke=0)

    # Add some space before the list
    c.setFont("Helvetica", 16)  # Using Helvetica font with size 16
    line_height = 40  # Set line height for spacing (adjusted for more space)
    toc_items = [
        "1.  Introduction",
        "2.  Competency Summary",
        "3.  Evaluation Summary By Competency",
        "    3.1  Strengths",
        "    3.2  Areas of Improvement",
        "    3.3  Hidden Strengths",
        "    3.4  Blind Spots",
        "4.  Detailed Feedback",
        "5.  Open-Ended Feedback"
    ]

    # Starting position for the list
    y_position = height - 180

    # Set font color back to black for TOC items
    c.setFillColor(colors.black)

    for item in toc_items:
        c.drawString(50, y_position, item)
        y_position -= line_height  # Decrease y position for next item with increased spacing

    # Save PDF
    c.showPage()
    c.save()

    print("Second page generated successfully")

def create_third_page(pdf_path, logo_path, assessment_number):

    # Create PRD
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Third Page: Introduction
    # Adjust the size of the logo for the third page
    logo_width_third_page = 1.8 * inch  # Smaller width for the logo on the second page
    logo_height_third_page = 0.41 * inch  # Smaller height for the logo on the second page
    c.drawImage(logo_path, width - logo_width_third_page - 30, height - logo_height_third_page - 30, 
                width=logo_width_third_page, height=logo_height_third_page)

    # Add "Introduction" heading
    heading_y_position = height - logo_height_third_page - 10 - 40
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, heading_y_position, "Introduction")

    # Draw underline for the heading
    underline_y_position = heading_y_position - 20
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.line(40, underline_y_position, width - 40, underline_y_position)

    # Draw blue rectangle marker
    marker_width = 9
    marker_height = 40
    c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
    c.rect(50 - 15, heading_y_position - 12, marker_width, marker_height, fill=1, stroke=0)

    # Add content text
    c.setFont("Helvetica", 12)
    text_start_y = height - 550  # Initial content start position

    # Define content with bold phrases wrapped in <b> HTML tags
    content = f"""
    {assessment_number} assessment is a valuable tool designed to support your personal and professional growth, uncover blind spots, promote collaboration, and drive individual and organizational success.<br/><br/>
    The purpose of {assessment_number} degree feedback:<br/><br/>
    <b>Increase self-awareness:</b> The {assessment_number} assessment aims to provide you with a comprehensive understanding of your strengths, and areas for development. It offers a unique opportunity to gain insights into how others perceive your performance, behavior, and impact on others.<br/><br/>
    <b>Identify blind spots:</b> By gathering feedback from multiple perspectives, the assessment helps you identify blind spots or areas where you may be unaware of your strengths or weaknesses. It uncovers valuable insights that can be used to enhance your effectiveness and make targeted improvements.<br/><br/>
    <b>Support personal growth and development:</b> The primary goal of the assessment is to facilitate personal and professional growth. The feedback received can serve as a catalyst for individual development plans, helping you refine your skills, address developmental gaps, and maximize your potential.<br/><br/>
    <b>Promote teamwork and collaboration:</b> The {assessment_number} assessment promotes a culture of feedback and collaboration within the organization. By including input from peers, subordinates, and supervisors, it encourages you to recognize and value the perspectives of others. This, in turn, fosters better teamwork and collaboration within teams and across departments.
    """

    # Use ReportLab's `Paragraph` for styled text
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Helvetica"
    style.fontSize = 13
    style.leading = 15
    style.alignment = TA_LEFT

    # Create a `Paragraph` object with the styled content
    story = Paragraph(content, style)
    story.wrapOn(c, width - 100, height)  # Adjust text wrapping to page width
    story.drawOn(c, 50, text_start_y)

    # Save PRD
    c.showPage()
    c.save()

    print("Third page generated successfully")

def wrap_labels(labels, width):
    wrapped_labels = []
    for label in labels:
        wrapped_label = '\n'.join(textwrap.wrap(label, width=width))
        wrapped_labels.append(wrapped_label)
    return wrapped_labels

def create_radar_chart(db, email, title="Other Vs Self Competency", chart_path="radar_chart.png"):
    # Group by 'Competency mapped to Statement' and calculate mean of 'SelfAvg' and 'OtherAvg'
    grouped_db = db[db['Seeker Email'] == email].groupby('Competency mapped to Statement')[['SelfAvg', 'OtherAvg']].mean()
    
    # Extract categories (Competency mapped to Statement) from the grouped data
    categories = grouped_db.index.tolist()
    grouped_db = grouped_db.reindex(categories)

    # Extract the data values for each category
    self_values = grouped_db['SelfAvg'].tolist()
    other_values = grouped_db['OtherAvg'].tolist()
    
    # Number of variables (categories)
    num_vars = len(categories)
    
    # Calculate the angle for each axis, rotated by 180 degrees (π radians)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles = [(angle + np.pi) % (2 * np.pi) for angle in angles]  # Apply 180-degree rotation

    # Complete the loop for data
    self_values += self_values[:1]
    other_values += other_values[:1]
    angles += angles[:1]

    # Initialize the radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Style grid and background
    ax.spines['polar'].set_visible(False)
    ax.grid(color='lightblue', linestyle='solid', linewidth=0.5)
    ax.set_facecolor('white')
    
    # Plot data
    ax.plot(angles, self_values, linewidth=1.5, linestyle='solid', color='blue', marker='o', markersize=6, label='Self')
    ax.plot(angles, other_values, linewidth=1.5, linestyle='solid', color='deepskyblue', marker='o', markersize=6, label='Other')
    ax.fill(angles, self_values, color='blue', alpha=0.1)
    ax.fill(angles, other_values, color='deepskyblue', alpha=0.1)

    # Hide angular ticks and labels
    ax.set_xticklabels([])  # Hide angular tick labels
    ax.set_yticklabels([])  # Hide radial axis labels

    # Wrap category labels and position them consistently
    wrapped_categories = wrap_labels(categories, width=15)
    label_radius_offset = 1.35  # Labels positioned outside data points

    for i, label in enumerate(wrapped_categories):
        ax.text(angles[i], label_radius_offset * max(max(self_values), max(other_values)), 
                label, horizontalalignment='center', verticalalignment='center', 
                fontsize=14, color='navy')

    # Rotate the chart
    ax.set_theta_offset(np.radians(55))
    ax.set_theta_direction(-1)

    # Title and legend
    ax.legend(loc='lower left', bbox_to_anchor=(-0.35, -0.35), ncol=2, fontsize=14, frameon=False, title="Legend")
    
    # Save chart
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close(fig)

def create_fourth_page(pdf_path, logo_path, db, assessment_number, email):
    # Create PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Logo
    logo_width = 1.8 * inch
    logo_height = 0.41 * inch
    c.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30, 
                width=logo_width, height=logo_height)

    # Title
    heading_y_position = height - logo_height - 50
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, heading_y_position, "Summary")
    underline_y_position = heading_y_position - 20
    c.setLineWidth(1.5)
    c.line(40, underline_y_position, width - 40, underline_y_position)
    c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
    c.rect(35, heading_y_position - 12, 9, 40, fill=1, stroke=0)

    # Add description
    description_y = heading_y_position - 60
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 14)
    c.drawString(50, description_y, "This section shows overall scores on competencies provided by others and self,")
    description_y -= 24
    c.drawString(50, description_y, "in the form of a Spider graph.")

    # Radar chart
    radar_chart_path = "radar_chart.png"
    create_radar_chart(db=db, email=email, title="Other and Self by Competency", chart_path=radar_chart_path)
    c.drawImage(radar_chart_path, width / 2 - 200, height - 600, width=400, height=400)

    # Delete the temporary radar chart image
    os.remove(radar_chart_path)

    # Summary Table
    content_start_y_position = height - 750
    summary_table = db[db['Seeker Email'] == email].groupby('Competency mapped to Statement')[['OtherAvg', 'SelfAvg']].mean().round(2)
    table_data = [['Competency', 'Other', 'Self']] + [[row[0]] + [f"{value:.2f}" for value in row[1:]] for row in summary_table.reset_index().values.tolist()]
    col_widths = [260, 70, 70]
    table_x_position = (width - sum(col_widths)) / 2
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([ 
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#007FFF")),  # Header background
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),                # White header text
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),                       # Center-align all headers horizontally
    ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),                      # Center-align all headers vertically
    ('TOPPADDING', (0, 0), (-1, 0), 7),
    ('ALIGN', (0, 1), (0, -1), 'LEFT'),                         # Left-align first column values
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),                      # Center-align remaining column values
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),            # Bold font for headers
    ('FONTSIZE', (0, 0), (-1, -1), 12),                         # Font size for all text
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),                     # Padding for headers
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#E4E4E4")]),  # Alternate row colors
    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),               # Table grid
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, table_x_position, content_start_y_position)

    # Save PDF
    c.showPage()
    c.save()

    print("Fourth page generated successfully")

#Creating Viz table as per competency and email
def viz_table(data, email, competency):
    # Filter data based on email and competency
    filtered_data = data[(data['Seeker Email'] == email) & (data['Competency mapped to Statement'] == competency)]
    
    # Calculate aggregate statistics for each main category (Others)
    main_category_stats = filtered_data.groupby('Others')['Rating'].agg(['mean', 'max', 'min']).rename(columns={'mean': 'Avg', 'max': 'Max', 'min': 'Min'}).round(2)
    
    # Calculate aggregate statistics for each subcategory (Others + Relationship)
    subcategory_stats = filtered_data.groupby(['Others', 'Relationship'])['Rating'].agg(['mean', 'max', 'min']).rename(columns={'mean': 'Avg', 'max': 'Max', 'min': 'Min'}).round(2)
    
    # Prepare the rows for the final DataFrame
    rows = []
    
    # Ensure 'Self' appears first by sorting the main categories explicitly
    main_categories = ['Self', 'Others']  # Hardcoding the order you want for main categories
    
    # Add main category stats to rows, starting with 'Self' then 'Others'
    for category in main_categories:
        if category in main_category_stats.index:
            main_stats = main_category_stats.loc[category]
            # Add the main category row with '− ' to show hierarchy
            rows.append(('− ' + category, main_stats['Avg'], main_stats['Max'], main_stats['Min']))
            
            # Add each subcategory under the main category, replacing 'Others' with 'Relationship' and adding indentation
            subcategories = subcategory_stats.loc[category]
            for relationship, sub_stats in subcategories.iterrows():
                # Add two spaces for child rows (subcategories) to make hierarchy clear
                rows.append(('  ' + relationship, sub_stats['Avg'], sub_stats['Max'], sub_stats['Min']))  # Indentation for child rows

    # Convert rows to DataFrame
    final_df = pd.DataFrame(rows, columns=['Others', 'Avg', 'Max', 'Min'])
    
    # Set 'Others' column as index
    final_df.set_index('Others', inplace=True)
    
    # Return the final DataFrame
    return final_df

def create_speedometer_chart(db, competency, email, is_second_chart=False):
    # Get the actual and target values
    target_value = Accountability(db, competency)
    actual_value = uAllRatingAvg(db, email, competency)

    # Define the range for the gauge
    min_value, max_value = 0, 5

    # Calculate angles
    actual_angle = (actual_value - min_value) / (max_value - min_value) * 180
    target_angle = (target_value - min_value) / (max_value - min_value) * 180

    # Create the figure with a fixed aspect ratio of 2.5:1
    fig_width = 36  # Inches
    fig_height = 20  # Inches
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), subplot_kw={'projection': 'polar'})
    ax.set_theta_offset(np.pi)  # Start from 180 degrees
    ax.set_theta_direction(-1)  # Clockwise

    # Title wrapping logic
    max_title_length = 30
    if len(competency) > max_title_length:
        # Break the title into lines for wrapping
        title_lines = []
        words = competency.split()
        line = ""
        for word in words:
            if len(line + " " + word) <= max_title_length:
                line += " " + word if line else word
            else:
                title_lines.append(line)
                line = word
        title_lines.append(line)
        wrapped_title = "\n".join(title_lines)
    else:
        wrapped_title = competency

    # Adjust title position for the second chart
    title_y_position = 1.1  # Default position
    if is_second_chart:
        title_y_position = 1.2  # Move the title upward slightly for the second chart

    # Add wrapped title
    plt.title(wrapped_title, fontsize=75, fontweight="bold", color="black", y=title_y_position)

    # Clean the plot and add arcs
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.spines['polar'].set_visible(False)
    ax.grid(False)
    ax.barh(1, np.deg2rad(180), color="#EEEEEE", height=0.3)
    ax.barh(1, np.deg2rad(actual_angle), color="#3399FF", height=0.3)
    target_rad = np.deg2rad(target_angle)
    ax.plot([target_rad, target_rad], [0.85, 1.15], color="darkblue", lw=4)

    # Add labels
    ax.text(target_rad, 1.30, f"{target_value:.2f}", ha="center", color="green", fontsize=62)
    ax.text(target_rad - 0.1, 0.0, f"{actual_value:.2f}", ha="center", color="gray", fontsize=180)

    # Save the chart with tighter bounding box and adjusted padding
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        chart_path = temp_file.name
        fig.tight_layout(pad=0.1 if is_second_chart else 0.5)
        fig.savefig(chart_path, bbox_inches="tight", dpi=300)
        plt.close(fig)

    return chart_path

def create_competency_pages(pdf_path, logo_path, db, email):
    # Page settings
    chart_width = 2.9 * inch
    chart_height = 3.0 * inch
    table_x_offset = 200

    # Define the render_speedometer_chart function
    def render_speedometer_chart(c, competency, x, y):
        # Generate the speedometer chart using the create_speedometer_chart function
        chart_path = create_speedometer_chart(db, competency, email)

        # Open the chart and determine its size
        with PILImage.open(chart_path) as img:
            img_width, img_height = img.size

            # Apply uniform scaling logic: Scale up all speedometers by 10%
            scale_factor = min((chart_width * 1.12) / img_width, (chart_height * 1.12) / img_height)  # 10% upscale

            # New width and height to maintain the aspect ratio
            scaled_width = img_width * scale_factor
            scaled_height = img_height * scale_factor

            # Draw the chart on the canvas, ensuring it is scaled correctly
            c.drawImage(chart_path, x, y, width=scaled_width, height=scaled_height)

        # Clean up by deleting the temporary file with a delay
        try:
            time.sleep(0.1)  # Delay to ensure the file is released
            os.remove(chart_path)
        except PermissionError:
            print(f"PermissionError: Unable to delete file {chart_path}")

    # Define a helper function to render a single competency
    def render_competency(c, competency, x, chart_y, table_y, is_first_table=True):
        # Call the speedometer chart rendering function
        render_speedometer_chart(c, competency, x, chart_y)

        # Render the table
        table_data = viz_table(db, email, competency).reset_index()
        render_table(c, table_data, x + table_x_offset + 40, table_y, is_first_table)

    # Define the render_table function (unchanged)
    def render_table(c, table_data, x, y, is_first_table=True):
        row_height = 25
        col_x_offsets = [0, 150, 190, 230, 270]  # Column start positions
        light_gray = colors.HexColor("#E4E4E4")
        table_width = col_x_offsets[-1]  # Restrict shading to last column's position
        indent_spaces = 4  # Indentation for subcategories

        # Set column header color
        header_color = colors.black
        c.setStrokeColor(header_color)
        c.setFillColor(header_color)
        c.setFont("Helvetica-Bold", 15)
        headers = ["Others", "Avg", "Max", "Min"]
        for i, header in enumerate(headers):
            header_x = x + (col_x_offsets[i] + (col_x_offsets[i + 1] - col_x_offsets[i]) / 2) - (
                c.stringWidth(header, "Helvetica-Bold", 15) / 2
            )
            c.drawString(header_x, y, header)

        # Add the thin blue line underneath the headers
        c.setStrokeColor(colors.HexColor("#4682B4"))  # Blue color for the line
        c.setLineWidth(0.5)
        c.line(x, y - 5, x + table_width, y - 5)

        # Add extra space between headers and the first row
        y -= 9

        # Draw rows with alternate row coloring
        for idx, row in enumerate(table_data.itertuples(index=False), start=1):
            row_y = y - (idx * row_height)

            # Alternate row colors, restricted to table width
            c.setFillColor(light_gray if idx % 2 == 0 else colors.white)
            c.rect(x, row_y, table_width, row_height, fill=1, stroke=0)

            # Set font style based on the value
            others_value = str(row[0])
            if "−" in others_value:
                c.setFont("Helvetica-Bold", 13)
            else:
                c.setFont("Helvetica", 13)

            # Draw row values
            for i, value in enumerate(row):
                value_str = str(value)

                if i == 0:  # First column (Others column)
                    # Left-align text and apply indentation for subcategories
                    if value_str.startswith("  "):  # Detect subcategory (indicated with spaces)
                        value_x = x + col_x_offsets[i] + (indent_spaces * 6)  # Indentation for subcategory
                    else:
                        value_x = x + col_x_offsets[i] + 2  # Small offset for left alignment
                else:
                    # Center align for other columns
                    col_width = col_x_offsets[i + 1] - col_x_offsets[i] if i < len(col_x_offsets) - 1 else 60
                    value_x = x + col_x_offsets[i] + (col_width - c.stringWidth(value_str, "Helvetica", 13)) / 2

                    # For columns 2, 3, and 4, format the values to 2 decimal places
                    if i in [1, 2, 3]:  # Column 2, 3, and 4
                        try:
                            value_str = f"{float(value):.2f}"
                        except ValueError:
                            pass

                c.setFillColor(colors.black)
                c.drawString(value_x, row_y + 8, value_str)

        # Add vertical blue line separating "Others" from other columns
        c.setStrokeColor(colors.HexColor("#4682B4"))  # Blue color
        c.setLineWidth(0.5)
        c.line(x + col_x_offsets[1], y, x + col_x_offsets[1], y - (len(table_data) * row_height))

    # Initialize PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Fetch all unique competencies
    unique_competencies = db['Competency mapped to Statement'].unique()
    total_competencies = len(unique_competencies)

    # Divide competencies into pages (2 per page)
    competencies_per_page = 2
    total_pages = (total_competencies + competencies_per_page - 1) // competencies_per_page

    for page_num in range(total_pages):
        # Add logo
        logo_width = 1.8 * inch
        logo_height = 0.41 * inch
        c.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30, 
                width=logo_width, height=logo_height)

        # Add "Competency Summary" heading
        heading_y = height - logo_height - 50
        c.setFont("Helvetica-Bold", 20)
        if page_num == 0:
            c.drawString(50, heading_y, "Competency Summary")
            # Add description text on the first page
            description_y = heading_y - 40
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 14)
            c.drawString(50, description_y, "Below is a summary of your feedback ratings for each competency along with the")
            description_y -= 24
            c.drawString(50, description_y, "average ratings from different rater groups. You can also refer to the benchmark")
            description_y -= 24
            c.drawString(50, description_y, "rating indicated in")
            c.setFillColor(colors.green)
            c.drawString(163, description_y, "green.")
        else:
            c.drawString(50, heading_y, "Competency Summary (Continued)")

        # Add underline
        underline_y = heading_y - 10
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.5)
        c.line(50, underline_y, width - 50, underline_y)

        # Draw blue rectangle marker next to the heading
        marker_width = 9
        marker_height = 40
        c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
        c.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)

        # Define positions for charts and tables
        first_chart_x = 30
        first_chart_y = underline_y - 80 - chart_height - 20 -10 -20
        second_chart_y = first_chart_y - chart_height - 80 -20

        # Get competencies for this page
        start_idx = page_num * competencies_per_page
        end_idx = min(start_idx + competencies_per_page, total_competencies)
        competencies = unique_competencies[start_idx:end_idx]

        # Render competencies for this page
        if len(competencies) > 0:
            render_competency(c, competencies[0], first_chart_x, first_chart_y, first_chart_y + chart_height +10 , is_first_table=True)
        if len(competencies) > 1:
            render_competency(c, competencies[1], first_chart_x, second_chart_y, second_chart_y + chart_height +20, is_first_table=False)

        # Add a new page if not the last page
        if page_num < total_pages - 1:
            c.showPage()

    # Save the PDF
    c.save()
    print("Competency Page Generated Successfully")

# def create_strength_page(pdf_path, logo_path, db, email):
#     # Create PDF canvas
#     c = canvas.Canvas(pdf_path, pagesize=A4)
#     width, height = A4

#     # Add logo
#     logo_width = 1.8 * inch
#     logo_height = 0.41 * inch
#     c.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30, 
#             width=logo_width, height=logo_height)

#     # Add "Strengths" heading
#     heading_y = height - logo_height - 50
#     c.setFont("Helvetica-Bold", 20)
#     c.drawString(50, heading_y, "Strengths")

#     # Add underline
#     underline_y = heading_y - 10
#     c.setStrokeColor(colors.black)
#     c.setLineWidth(1.5)
#     c.line(50, underline_y, width - 50, underline_y)

#     # Draw blue rectangle marker next to the heading
#     marker_width = 9
#     marker_height = 40
#     c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
#     c.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)

#     # Add description text
#     description_y = underline_y - 40
#     c.setFont("Helvetica", 14)
#     c.setFillColor(colors.black)
#     c.drawString(50, description_y, "Below is a summary of your strengths, highlighting the statements where both")
#     description_y -= 24
#     c.drawString(50, description_y, "you and others have consistently given high ratings.")
#     description_y -= 24
#     c.setFillColor(colors.black)

#     # Define column widths based on percentages
#     total_table_width = width - 100
#     col_widths = [0.5 * total_table_width, 0.3 * total_table_width, 0.2 * total_table_width]

#     # Getting the table data using the strength function
#     table_data_df = Strength(db, email)

#     # Adjust table position based on whether data exists
#     if table_data_df.empty:  # If the DataFrame is empty
#         content_start_y_position = description_y - 70
#         c.setFont("Helvetica", 14)
#         c.drawString(50, content_start_y_position, "No data available")
#     else:
#         # Format 'Average Rating' column to two decimals
#         table_data_df['Average Rating'] = table_data_df['Average Rating'].apply(lambda x: f"{x:.2f}")

#         # Convert DataFrame to list of lists for the table
#         table_data = [table_data_df.columns.tolist()] + table_data_df.values.tolist()

#         # Wrap text in 'Statements' and 'Competency' columns, including headers
#         def wrap_text(cell, col_width):
#             wrapped_lines = wrap(cell, width=int(col_width * 0.14))  # Adjust the wrap width scaling factor
#             return "\n".join(wrapped_lines)

#         # Apply wrapping to all cells (including headers)
#         for i in range(len(table_data)):
#             table_data[i][0] = wrap_text(table_data[i][0], col_widths[0])  # Wrap 'Statements'
#             table_data[i][1] = wrap_text(table_data[i][1], col_widths[1])  # Wrap 'Competency'

#         # Create the Table and add style
#         table = Table(table_data, colWidths=col_widths)

#         table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#007FFF")),  # Blue header background
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # White text for headers
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Default center align for all cells
#             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center-align all headers horizontally
#             ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
#             ('ALIGN', (0, 1), (1, -1), 'LEFT'),  # Left-align first two columns (Statements and Competency)
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Middle align vertically for all cells
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for headers
#             ('FONTSIZE', (0, 0), (-1, -1), 12),  # Font size 12 for all text
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Padding for headers
#             ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#E4E4E4")]),  # Alternating row colors
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.gray)  # Gray grid lines
#         ]))

#         # Adjust the position for the table when data is available
#         content_start_y_position = description_y - 270
#         table.wrapOn(c, width, height)
#         table.drawOn(c, 50, content_start_y_position)

#     # Save PDF
#     c.showPage()
#     c.save()
#     print("Strength page generated successfully")

def create_strength_page(pdf_path, logo_path, db, email):
    # Create PDF canvas
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
 
    # Add logo
    logo_width = 1.8 * inch
    logo_height = 0.41 * inch
    c.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30,
                width=logo_width, height=logo_height)
 
    # Add "Strengths" heading
    heading_y = height - logo_height - 50
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, heading_y, "Strengths")
 
    # Add underline
    underline_y = heading_y - 10
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.line(50, underline_y, width - 50, underline_y)
 
    # Draw blue rectangle marker next to the heading
    marker_width = 9
    marker_height = 40
    c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
    c.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)
 
    # Add description text
    description_y = underline_y - 40
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawString(50, description_y, "Below is a summary of your strengths, highlighting the statements where both")
    description_y -= 24
    c.drawString(50, description_y, "you and others have consistently given high ratings.")
    description_y -= 24
    c.setFillColor(colors.black)
 
    # Define column widths based on percentages
    total_table_width = width - 100
    col_widths = [0.5 * total_table_width, 0.3 * total_table_width, 0.2 * total_table_width]
 
    # Getting the table data using the strength function
    table_data_df = Strength(db, email)
 
    # Adjust table position based on whether data exists
    if table_data_df.empty:  # If the DataFrame is empty
        content_start_y_position = description_y - 70
        c.setFont("Helvetica", 14)
        c.drawString(50, content_start_y_position, "No data available")
    else:
        # Format 'Average Rating' column to two decimals
        table_data_df['Average Rating'] = table_data_df['Average Rating'].apply(lambda x: f"{x:.2f}")
 
        # Convert DataFrame to list of lists for the table
        table_data = [table_data_df.columns.tolist()] + table_data_df.values.tolist()
 
        # Wrap text in 'Statements' and 'Competency' columns, including headers
        def wrap_text(cell, col_width):
            wrapped_lines = wrap(cell, width=int(col_width * 0.14))  # Adjust the wrap width scaling factor
            return "\n".join(wrapped_lines)
 
        # Apply wrapping to all cells (including headers)
        for i in range(len(table_data)):
            table_data[i][0] = wrap_text(table_data[i][0], col_widths[0])  # Wrap 'Statements'
            table_data[i][1] = wrap_text(table_data[i][1], col_widths[1])  # Wrap 'Competency'
 
        # Create the Table and add style
        table = Table(table_data, colWidths=col_widths)
 
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#007FFF")),  # Blue header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # White text for headers
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Default center align for all cells
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center-align all headers horizontally
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),  # Left-align first two columns (Statements and Competency)
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Middle align vertically for all cells
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for headers
            ('FONTSIZE', (0, 0), (-1, -1), 12),  # Font size 12 for all text
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Padding for headers
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#E4E4E4")]),  # Alternating row colors
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray)  # Gray grid lines
        ]))
 
        # Adjust the position for the table when data is available
        content_start_y_position = description_y - 270
 
        # Calculate the number of rows in the table (including the header)
        num_rows = len(table_data)
 
        # Adjust the y-position if the number of rows is less than or equal to 3
        if num_rows <= 4:
            content_start_y_position += 80
       
        # Ensure that content fits within the page margins and avoids tight layout
        available_space = content_start_y_position - 40  # Leave some buffer
        if available_space < 0:
            content_start_y_position = description_y - 200  # Adjust position to fit
 
        table.wrapOn(c, width, height)
        table.drawOn(c, 50, content_start_y_position)
 
    # Save PDF
    c.showPage()
    c.save()
    print("Strength page generated successfully")

def generate_visualization(db, email, filename="visualization.png"):
    # Call the improvement function to get the DataFrame
    data = improvement(db, email)
    
    # Check if data is a DataFrame and contains the necessary columns
    if not isinstance(data, pd.DataFrame) or 'Statements' not in data.columns or 'Rating' not in data.columns:
        raise ValueError("improvement() must return a DataFrame with 'Statements' and 'Rating' columns.")
    
    # Ensure there are at most 5 rows (as per the requirement)
    data = data.head(5)

    # Dynamically calculate the figure height based on the number of rows
    fig_height = len(data) * 1.2  # Each line-statement combination needs 3 units of space
    fig, ax = plt.subplots(figsize=(8, fig_height))
    ax.axis('off')  # Turn off axis

    # Calculate y-positions for lines and statements
    y_positions = [fig_height - (i * 0.7) for i in range(len(data))]  # 3.0 units between lines

    bar_length = 0.8  # Length of black bars (relative to plot width)

    for i, (statement, rating) in enumerate(zip(data['Statements'], data['Rating'])):
        y = y_positions[i]  # Determine y-coordinate for the current line and text

        # Add the black horizontal line
        ax.hlines(y=y, xmin=0.1, xmax=bar_length, colors='black', linewidth=3)

        # Add the statement text 1 unit below the black line
        ax.text(0.1, y - 0.08, statement, fontsize=10, ha='left', va='top', wrap=True)

        # Add the rating in an orange box, aligned with the statement
        ax.text(bar_length+0.05, y - 0.01, f"{rating:.2f}", fontsize=12, color='white',
                bbox=dict(boxstyle="round", facecolor=(1, 0.522, 0), edgecolor="none"),
                va='center', ha='center')

        # Add the small vertical black line at the end of the horizontal line
        vertical_line_height = 0.1  # Length of the vertical line
        ax.vlines(x=bar_length + 0.001, ymin=y - vertical_line_height / 2, ymax=y + vertical_line_height / 2, colors='black', linewidth=3)

    # Save the visualization as an image
    plt.tight_layout()  # Ensure no content is clipped
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close(fig)

def create_improvement_page(pdf_path, logo_path, db, email):
    # Create PDF canvas
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Add logo
    logo_width = 1.8 * inch
    logo_height = 0.41 * inch
    c.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30, 
            width=logo_width, height=logo_height)

    # Add "Improvements" heading
    heading_y = height - logo_height - 50
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, heading_y, "Improvements")

    # Add underline
    underline_y = heading_y - 10
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.line(50, underline_y, width - 50, underline_y)

    # Draw blue rectangle marker next to the heading
    marker_width = 9
    marker_height = 40
    c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
    c.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)

    # Add description text
    description_y = underline_y - 40
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawString(50, description_y, "Below is a summary of areas for improvement, highlighting the statements where")
    description_y -= 24
    c.drawString(50, description_y, "both you and others have consistently identified opportunities for growth.")
    description_y -= 40

    # Generate visualization and add to the PDF
    visualization_path = "temp_visualization.png"
    try:
        # Generate the visualization only if the improvement function returns valid data
        data = improvement(db, email)  # This is a new check before generating visualization

        # Proceed only if there are rows (improvement data is non-empty)
        if isinstance(data, pd.DataFrame) and not data.empty:
            generate_visualization(db, email, filename=visualization_path)

            # Determine the visualization height dynamically
            num_statements = len(data)
            visualization_height = max(120, num_statements * 100)  # Minimum height of 100, scaled by number of statements

            # Visualization width remains consistent
            visualization_width = width - 100  # Fit within margins (adjust to preferred size)

            # Embed visualization in the PDF
            c.drawImage(visualization_path, 50, description_y - visualization_height, width=visualization_width, height=visualization_height)
        else:
            # In case there is no data, you can add a message or leave the space empty
            c.setFont("Helvetica", 14)
            c.drawString(50, description_y, "No improvement data available.")
            description_y -= 24
    finally:
        # Ensure the temporary visualization file is removed if it exists
        if os.path.exists(visualization_path):
            try:
                os.remove(visualization_path)
            except PermissionError:
                print(f"Warning: Unable to delete temporary file {visualization_path}")

    # Save and finalize PDF
    c.save()
    print("Improvement page generated successfully")

def create_hidden_strength_page(pdf_path, logo_path, db, email):
    # Create PDF canvas
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Add logo
    logo_width = 1.8 * inch
    logo_height = 0.41 * inch
    c.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30, 
            width=logo_width, height=logo_height)

    # Add "Strengths" heading
    heading_y = height - logo_height - 50
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, heading_y, "Hidden Strengths")

    # Add underline
    underline_y = heading_y - 10
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.line(50, underline_y, width - 50, underline_y)

    # Draw blue rectangle marker next to the heading
    marker_width = 9
    marker_height = 40
    c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
    c.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)

    # Add description text
    description_y = underline_y - 40
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawString(50, description_y, "Below is a summary of your hidden strengths, highlighting the statements where")
    description_y -= 24
    c.drawString(50, description_y, "others have rated you higher than you rated yourself. Reflect on these areas to")
    description_y -= 24
    c.drawString(50, description_y, "recognize strengths you may undervalue and consider how to leverage them")
    description_y -= 24
    c.drawString(50, description_y, "more effectively.")
    description_y -= 24
    c.setFillColor(colors.black)

    # Define column widths based on percentages
    total_table_width = width - 100
    col_widths = [0.8 * total_table_width, 0.1 * total_table_width, 0.1 * total_table_width]

    # Getting the table data using the strength function
    table_data_df = hidden_strength(db, email)

    # Adjust table position based on whether data exists
    if table_data_df.empty:  # If the DataFrame is empty
        content_start_y_position = description_y - 20
        c.setFont("Helvetica", 14)
        c.drawString(50, content_start_y_position, "No data available")
    else:
        content_start_y_position = description_y - 170

    # Ensure the table starts at a proper position (avoid overlapping with bottom margin)
    if content_start_y_position < 100:  # Prevent overlap with bottom margin
        content_start_y_position = 100

    # Convert DataFrame to list of lists for the table
    if not table_data_df.empty:
        # Format 'Self' column to two decimals
        table_data_df['Self'] = table_data_df['Self'].apply(lambda x: f"{x:.2f}")
        table_data_df['Other'] = table_data_df['Other'].apply(lambda x: f"{x:.2f}")
        table_data = [table_data_df.columns.tolist()] + table_data_df.values.tolist()

        # Wrap text in 'Statements' and 'Competency' columns, including headers
        def wrap_text(cell, col_width):
            wrapped_lines = wrap(cell, width=int(col_width * 0.18))  # Adjust the wrap width scaling factor
            return "\n".join(wrapped_lines)

        # Apply wrapping to all cells (including headers)
        for i in range(len(table_data)):
            table_data[i][0] = wrap_text(table_data[i][0], col_widths[0])  # Wrap 'Statements'
            table_data[i][1] = wrap_text(table_data[i][1], col_widths[1])  # Wrap 'Competency'

        # Create the Table and add style
        table = Table(table_data, colWidths=col_widths)

        table.setStyle(TableStyle([
        # Header style
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#007FFF")),  # Blue header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # White text for headers
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center-align all headers horizontally
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),  # Middle-align headers vertically
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for headers

        # Alignment for specific columns (column values only)
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left-align column 1 values (excluding header)
        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),  # Center-align vertically for column 1 values

        # Other column styles
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Center-align columns 2 and 3 horizontally
        ('VALIGN', (1, 1), (-1, -1), 'MIDDLE'),  # Center-align columns 2 and 3 vertically

        # General styling
        ('FONTSIZE', (0, 0), (-1, -1), 12),  # Font size 12 for all text
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Padding for headers
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#E4E4E4")]),  # Alternating row colors
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray)  # Gray grid lines
    ]))


        # Draw the table on the PDF
        table.wrapOn(c, width, height)
        # Adjust table position if it has two or fewer rows
        if len(table_data) <= 2:  # Include header row in count
            content_start_y_position += 50
        table.drawOn(c, 50, content_start_y_position)

    # Save PDF
    c.showPage()
    c.save()
    print("Hidden Strength page generated successfully")


# # Function to generate bar images
# def generate_bar_image(value, color, is_reverse=False, text_color='black'):
#     fig, ax = plt.subplots(figsize=(5, 1))
 
#     if is_reverse:
#         ax.barh([0], [value], color=color, height=0.2, left=5 - value)
#         # Label positioning for reverse bars
#         x_pos = 5 - value / 2
#     else:
#         ax.barh([0], [value], color=color, height=0.2)
#         # Label positioning for normal bars
#         x_pos = value / 2
 
#     ax.set_xlim(0, 5)
#     ax.axis('off')
 
#     # Add text with font size 18 and two decimal places
#     ax.text(x_pos, 0, f"{value:.2f}", va='center', ha='center', color=text_color, fontsize=18, weight='bold')
 
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0)
#     plt.close(fig)
#     buf.seek(0)
#     return buf
 
 
# # Function to create the table with bar charts
# def create_bar_chart_table(db, email):
#     df = blind_spots(db, email)  # Fetch data dynamically
 
#     if df.empty:
#         # Return None if there is no data
#         return None
 
#     # Proceed with generating the table if data exists
#     table_data = []
 
#     # Prepare the header
#     styles = getSampleStyleSheet()
#     header_style = styles["Heading4"]
#     header_style.alignment = 0  # Left-aligned
#     header_style.textColor = colors.white
#     header_style.fontSize = 13
#     header_style.fontName = "Helvetica-Bold"
#     header = [Paragraph(col, header_style) for col in df.columns]
#     table_data.append(header)
 
#     # Customize body text style
#     body_text_style = styles["BodyText"]
#     body_text_style.fontSize = 12
 
#     for _, row in df.iterrows():
#         statement = Paragraph(row['Statements'], body_text_style)  # Wrap text
#         self_value = row['Self']
#         others_value = row['Other']
 
#         # Generate bar images
#         self_bar_buf = generate_bar_image(self_value, "#44d65f", is_reverse=True, text_color='white')
#         others_bar_buf = generate_bar_image(others_value, "#e66c37", is_reverse=False, text_color='white')
 
#         # Convert bar images to Image objects
#         self_bar_img = Image(self_bar_buf, width=120, height=20)  # This uses reportlab.platypus.Image
#         others_bar_img = Image(others_bar_buf, width=120, height=20)  # Same here
 
#         # Add row to table data
#         table_data.append([statement, self_bar_img, others_bar_img])
 
#     # Table styles
#     table_style = TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007FFF")),  # Header background
#         ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
#         ("ALIGN", (0, 1), (-1, -1), "CENTER"),
#         ("ALIGN", (0, 0), (-1, 0), "LEFT"),
#         ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#         # Apply alternating row background to the first column only
#         ("ROWBACKGROUNDS", (0, 1), (0, -1), [colors.white, colors.lightgrey]),
#         ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
#     ])
 
#     # Create the table
#     table = Table(table_data, colWidths=[280, 120, 120], rowHeights=[30] + [50] * (len(table_data) - 1))
#     table.setStyle(table_style)
#     return table
 
# # Function to create the full PDF with canvas and table
# def create_blind_spots(db, email, pdf_path, logo_path):
#     c = canvas.Canvas(pdf_path, pagesize=A4)
#     width, height = A4
 
#     # Add logo
#     logo_width = 1.8 * inch
#     logo_height = 0.41 * inch
#     c.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30,
#                 width=logo_width, height=logo_height)
 
#     # Add "Blind Spot" heading
#     heading_y = height - logo_height - 50
#     c.setFont("Helvetica-Bold", 20)
#     c.drawString(50, heading_y, "Blind Spots")
 
#     # Add underline
#     underline_y = heading_y - 10
#     c.setStrokeColor(colors.black)
#     c.setLineWidth(1.5)
#     c.line(50, underline_y, width - 50, underline_y)
 
#     # Draw blue rectangle marker
#     marker_width = 9
#     marker_height = 40
#     c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
#     c.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)
 
#     # Add description text
#     description_y = underline_y - 40
#     c.setFont("Helvetica", 14)
#     c.setFillColor(colors.black)
#     c.drawString(50, description_y, "Below is a summary of your blind spots, where your self-ratings are higher than")
#     description_y -= 24
#     c.drawString(50, description_y, "those of others. Reflect on these areas to explore potential gaps in self-perception")
#     description_y -= 24
#     c.drawString(50, description_y, "and identify opportunities to align your actions with others' expectations.")
#     description_y -= 40  # Add extra spacing below the description text
 
#     # Fetch and create the table
#     table = create_bar_chart_table(db, email)
 
#     if table is None:
#         # Draw "No Blind Spots Data Available" message
#         c.setFont("Helvetica", 14)
#         c.setFillColor(colors.black)
#         c.drawString(50, description_y, "No Blind Spots Data Available")
#     else:
#         # Add the table below the description
#         table.wrapOn(c, width, height)
#         table.drawOn(c, 35, description_y - 350)  # Adjust table position
        
#         row_count = len(table._argW)  # Calculate the number of rows in the table
#         table_y_position = description_y - 350  # Default position
 
#         if row_count <= 2:
#             table_y_position += 250  # Move table upwards if rows are 2 or fewer
 
#         table.drawOn(c, 35, table_y_position)  # Adjusted table position

#     # Save the canvas with the content
#     c.save()
 
# # Function to merge content and table into final PDF
# def create_blind_spots_page(pdf_path, logo_path, db, email):
#     create_blind_spots(db, email, pdf_path, logo_path)
#     print("BlindSpot PDF generated successfully")

def generate_bar_image(value, color, is_reverse=False, text_color='black'):
    fig, ax = plt.subplots(figsize=(5, 1))
 
    if is_reverse:
        ax.barh([0], [value], color=color, height=0.2, left=5 - value)
        # Label positioning for reverse bars
        x_pos = 5 - value / 2
    else:
        ax.barh([0], [value], color=color, height=0.2)
        # Label positioning for normal bars
        x_pos = value / 2
 
    ax.set_xlim(0, 5)
    ax.axis('off')
 
    # Add text with font size 18 and two decimal places
    ax.text(x_pos, 0, f"{value:.2f}", va='center', ha='center', color=text_color, fontsize=18, weight='bold')
 
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf
 
 
# Function to create the table with bar charts
def create_bar_chart_table(db, email):
    df = blind_spots(db, email)  # Fetch data dynamically
 
    if df.empty:
        # Return None if there is no data
        return None
 
    # Proceed with generating the table if data exists
    table_data = []
 
    # Prepare the header
    styles = getSampleStyleSheet()
    header_style = styles["Heading4"]
    header_style.alignment = 0  # Left-aligned
    header_style.textColor = colors.white
    header_style.fontSize = 13
    header_style.fontName = "Helvetica-Bold"
    header = [Paragraph(col, header_style) for col in df.columns]
    table_data.append(header)
 
    # Customize body text style
    body_text_style = styles["BodyText"]
    body_text_style.fontSize = 12
 
    for _, row in df.iterrows():
        statement = Paragraph(row['Statements'], body_text_style)  # Wrap text
        self_value = row['Self']
        others_value = row['Other']
 
        # Generate bar images
        self_bar_buf = generate_bar_image(self_value, "#44d65f", is_reverse=True, text_color='white')
        others_bar_buf = generate_bar_image(others_value, "#e66c37", is_reverse=False, text_color='white')
 
        # Convert bar images to Image objects
        self_bar_img = Image(self_bar_buf, width=120, height=20)  # This uses reportlab.platypus.Image
        others_bar_img = Image(others_bar_buf, width=120, height=20)  # Same here
 
        # Add row to table data
        table_data.append([statement, self_bar_img, others_bar_img])
 
    # Table styles
    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007FFF")),  # Header background
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        # Apply alternating row background to the first column only
        ("ROWBACKGROUNDS", (0, 1), (0, -1), [colors.white, colors.lightgrey]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ])
 
    # Create the table
    table = Table(table_data, colWidths=[280, 120, 120], rowHeights=[30] + [50] * (len(table_data) - 1))
    table.setStyle(table_style)
    return table
 
# Function to create the full PDF with canvas and table
def create_blind_spots(db, email, pdf_path, logo_path):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
 
    # Add logo
    logo_width = 1.8 * inch
    logo_height = 0.41 * inch
    c.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30,
                width=logo_width, height=logo_height)
 
    # Add "Blind Spot" heading
    heading_y = height - logo_height - 50
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, heading_y, "Blind Spots")
 
    # Add underline
    underline_y = heading_y - 10
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.line(50, underline_y, width - 50, underline_y)
 
    # Draw blue rectangle marker
    marker_width = 9
    marker_height = 40
    c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
    c.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)
 
    # Add description text
    description_y = underline_y - 40
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawString(50, description_y, "Below is a summary of your blind spots, where your self-ratings are higher than")
    description_y -= 24
    c.drawString(50, description_y, "those of others. Reflect on these areas to explore potential gaps in self-perception")
    description_y -= 24
    c.drawString(50, description_y, "and identify opportunities to align your actions with others' expectations.")
    description_y -= 40  # Add extra spacing below the description text
 
    # Fetch and create the table
    table = create_bar_chart_table(db, email)
 
    if table is None:
    # Draw "No Blind Spots Data Available" message
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.black)
        c.drawString(50, description_y, "No Blind Spots Data Available")
    else:
        # Determine the number of rows in the table (including header)
        num_rows = len(table._cellvalues)  # `table._argW` stores the column widths, rows are tied to table height
   
        # Adjust table position
        table_y_position = description_y - 560
        if num_rows <= 3:
            table_y_position += 380  # Move table upward if rows <= 4
        elif num_rows <= 4:
            table_y_position += 350
        else:
            table_y_position = description_y - 300  # Default position
           
        # Add the table below the description
        table.wrapOn(c, width, height)
        table.drawOn(c, 35, table_y_position)  # Adjusted table position
 
    # Save the canvas with the content
    c.save()
 
# Function to merge content and table into final PDF
def create_blind_spots_page(pdf_path, logo_path, db, email):
    create_blind_spots(db, email, pdf_path, logo_path)
    print("BlindSpot PDF generated successfully")
 





# # Helper functions for dynamic data
# def detailed_statements(db, email):
#     db = db[db['Seeker Email'] == email]
#     return (
#         db[['Statements', 'Competency mapped to Statement', 'Others', 'Relationship', 'Rating']]
#         .sort_values(by=['Competency mapped to Statement', 'Statements'])
#         .rename(columns={'Competency mapped to Statement': 'Competency'})
#     )

# def all_competency_average(db, email):
#     db = db[db['Seeker Email'] == email]
#     return (
#         pd.DataFrame(db.groupby('Competency mapped to Statement')['Rating'].mean())
#         .reset_index()
#         .rename(columns={'Competency mapped to Statement': 'Statements'})
#     )

# # Functions for drawing headers and logos
# def draw_header(canvas, logo_path):
#     width, height = letter

#     # Add logo
#     logo_width = 1.8 * inch
#     logo_height = 0.41 * inch
#     canvas.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30, 
#                      width=logo_width, height=logo_height)

#     # Add "Detailed Feedback" heading
#     heading_y = height - logo_height - 50
#     canvas.setFont("Helvetica-Bold", 20)
#     canvas.drawString(50, heading_y, "Detailed Feedback")

#     # Add underline
#     underline_y = heading_y - 10
#     canvas.setStrokeColor(colors.black)
#     canvas.setLineWidth(1.5)
#     canvas.line(50, underline_y, width - 50, underline_y)

#     # Draw blue rectangle marker next to the heading
#     marker_width = 9
#     marker_height = 40
#     canvas.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)  # Light blue
#     canvas.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)

#     # Add description text
#     description_y = underline_y - 40
#     canvas.setFont("Helvetica", 14)
#     canvas.setFillColor(colors.black)
#     canvas.drawString(50, description_y, "The detailed statement-wise rating provides your complete group-wise breakdown")
#     description_y -= 24
#     canvas.drawString(50, description_y, "of your feedback on each statement.")

# def draw_logo(canvas, logo_path):
#     width, height = letter

#     # Add logo on subsequent pages
#     logo_width = 1.8 * inch
#     logo_height = 0.41 * inch
#     canvas.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30, 
#                      width=logo_width, height=logo_height)

# def detailed_statement_page(logo_path, db, email, pdf_path):
#     # Create a canvas for the header and other content
#     def header(canvas, doc):
#         draw_header(canvas, logo_path)

#     def subsequent_pages(canvas, doc):
#         draw_logo(canvas, logo_path)

#     # Initialize the document
#     doc = SimpleDocTemplate(pdf_path, pagesize=letter)
#     elements = []

#     # Add spacer to provide space below the description text
#     elements.append(Spacer(1, 1.8 * inch))

#     # Generate table data dynamically
#     competency_averages = all_competency_average(db, email)
#     statement_data = detailed_statements(db, email)

#     table_data = [["Statements", "Others", "Relationship", "Rating"]]
#     styles = getSampleStyleSheet()
#     style_left_top = ParagraphStyle(name="LeftTop", parent=styles["Normal"], alignment=0, fontSize=12)
#     style_bold_left_top = ParagraphStyle(name="BoldLeftTop", parent=styles["Normal"], alignment=0, fontName="Helvetica-Bold", fontSize=12)

#     row_index = 1  # To keep track of rows for merging
#     merging_rules = []  # To collect merging rules dynamically

#     # Iterate over each competency and dynamically build rows
#     for _, competency_row in competency_averages.iterrows():
#         competency_name = competency_row["Statements"]
#         avg_rating = f"{competency_row['Rating']:.2f}"
#         table_data.append([Paragraph(competency_name, style_bold_left_top), "", "", Paragraph(avg_rating, style_bold_left_top)])  # Bold rating
#         merging_rules.append(("SPAN", (0, row_index), (2, row_index)))  # Merge Columns 1-3
#         row_index += 1

#         # Filter statements for this competency
#         competency_statements = statement_data[statement_data["Competency"] == competency_name]

#         # Iterate through each unique statement
#         for statement in competency_statements["Statements"].unique():
#             # Filter rows for this statement
#             statement_rows = competency_statements[competency_statements["Statements"] == statement]

#             # Add the first row for "Self"
#             self_rows = statement_rows[statement_rows["Others"] == "Self"]
#             if not self_rows.empty:
#                 self_row = self_rows.iloc[0]
#                 table_data.append([Paragraph(statement, style_left_top), Paragraph("Self", style_bold_left_top), "", f"{self_row['Rating']:.2f}"])
#             else:
#                 table_data.append([Paragraph(statement, style_left_top), Paragraph("Self", style_bold_left_top), "", "-"])  # Hyphen for missing Self data

#             statement_start_row = row_index
#             row_index += 1

#             # Add "Others" row with average and individual roles
#             others_rows = statement_rows[statement_rows["Others"] == "Others"]
#             if not others_rows.empty:
#                 avg_others = f"{others_rows['Rating'].mean():.2f}"
#                 table_data.append(["", Paragraph("Others", style_bold_left_top), "", avg_others])  # Average row
#                 others_start_row = row_index
#                 row_index += 1

#                 # Group by "Relationship" and calculate the average rating
#                 grouped_relationships = others_rows.groupby("Relationship").mean(numeric_only=True).reset_index()

#                 # Add individual role rows for Others, showing the averaged rating for each relationship
#                 for _, group_row in grouped_relationships.iterrows():
#                     table_data.append(["", "", group_row["Relationship"], f"{group_row['Rating']:.2f}"])
#                     row_index += 1

#                 # Merging rules for Statements and Others
#                 merging_rules.append(("SPAN", (0, statement_start_row), (0, row_index - 1)))  # Merge Column 1 (Statements)
#                 merging_rules.append(("SPAN", (1, others_start_row), (1, row_index - 1)))  # Merge Column 2 (Others)
#             else:
#                 table_data.append(["", Paragraph("Others", style_bold_left_top), "", "-"])  # Hyphen for missing Others data

#     # Create the main table with data and merging rules
#     table = Table(table_data, colWidths=[230, 100, 120, 60])
#     table.setStyle(TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007FFF")),  
#         ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  
#         ("ALIGN", (0, 0), (-1, 0), "LEFT"),  
#         ("FONTSIZE", (0, 0), (-1, 0), 13),  
#         ("FONTSIZE", (0, 1), (-1, -1), 12),  
#         ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  
#         ("BOTTOMPADDING", (0, 0), (-1, 0), 12),  
#         ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),  
#         ("ALIGN", (0, 1), (-1, -1), "LEFT"),  
#         ("VALIGN", (0, 0), (-1, -1), "TOP"),  
#         ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
#     ]))

#     for merge_rule in merging_rules:
#         table.setStyle(TableStyle([merge_rule]))

#     # Add the table to the document
#     elements.append(table)

#     # Build the PDF with the header and subsequent pages
#     doc.build(elements, onFirstPage=header, onLaterPages=subsequent_pages)
#     print("Detailed Statement PDF generated successfully")

# Helper functions for dynamic data
def detailed_statements(db, email):
    db = db[db['Seeker Email'] == email]
    return (
        db[['Statements', 'Competency mapped to Statement', 'Others', 'Relationship', 'Rating']]
        .sort_values(by=['Competency mapped to Statement', 'Statements'])
        .rename(columns={'Competency mapped to Statement': 'Competency'})
    )
 
def all_competency_average(db, email):
    db = db[db['Seeker Email'] == email]
    return (
        pd.DataFrame(db.groupby('Competency mapped to Statement')['Rating'].mean())
        .reset_index()
        .rename(columns={'Competency mapped to Statement': 'Statements'})
    )
 
# Functions for drawing headers and logos
def draw_header(canvas, logo_path):
    width, height = letter
 
    # Add logo
    logo_width = 1.8 * inch
    logo_height = 0.41 * inch
    canvas.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30,
                     width=logo_width, height=logo_height)
 
    # Add "Detailed Feedback" heading
    heading_y = height - logo_height - 50
    canvas.setFont("Helvetica-Bold", 20)
    canvas.drawString(50, heading_y, "Detailed Feedback")
 
    # Add underline
    underline_y = heading_y - 10
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1.5)
    canvas.line(50, underline_y, width - 50, underline_y)
 
    # Draw blue rectangle marker next to the heading
    marker_width = 9
    marker_height = 40
    canvas.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)  # Light blue
    canvas.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)
 
    # Add description text
    description_y = underline_y - 40
    canvas.setFont("Helvetica", 14)
    canvas.setFillColor(colors.black)
    canvas.drawString(50, description_y, "The detailed statement-wise rating provides your complete group-wise breakdown")
    description_y -= 24
    canvas.drawString(50, description_y, "of your feedback on each statement.")
 
def draw_logo(canvas, logo_path):
    width, height = letter
 
    # Add logo on subsequent pages
    logo_width = 1.8 * inch
    logo_height = 0.41 * inch
    canvas.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30,
                     width=logo_width, height=logo_height)
 
def detailed_statement_page(logo_path, db, email, pdf_path):
    # Create a canvas for the header and other content
    def header(canvas, doc):
        draw_header(canvas, logo_path)
 
    def subsequent_pages(canvas, doc):
        draw_logo(canvas, logo_path)
 
    # Initialize the document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    elements = []
 
    # Add spacer to provide space below the description text
    elements.append(Spacer(1, 1.8 * inch))
 
    # Generate table data dynamically
    competency_averages = all_competency_average(db, email)
    statement_data = detailed_statements(db, email)
 
    table_data = [["Statements", "Others", "Relationship", "Rating"]]
    styles = getSampleStyleSheet()
    style_left_top = ParagraphStyle(name="LeftTop", parent=styles["Normal"], alignment=0, fontSize=12)
    style_bold_left_top = ParagraphStyle(name="BoldLeftTop", parent=styles["Normal"], alignment=0, fontName="Helvetica-Bold", fontSize=12)
 
    row_index = 1  # To keep track of rows for merging
    merging_rules = []  # To collect merging rules dynamically
 
    # Iterate over each competency and dynamically build rows
    for _, competency_row in competency_averages.iterrows():
        competency_name = competency_row["Statements"]
        avg_rating = f"{competency_row['Rating']:.2f}"
        table_data.append([Paragraph(competency_name, style_bold_left_top), "", "", Paragraph(avg_rating, style_bold_left_top)])  # Bold rating
        merging_rules.append(("SPAN", (0, row_index), (2, row_index)))  # Merge Columns 1-3
        row_index += 1
 
        # Filter statements for this competency
        competency_statements = statement_data[statement_data["Competency"] == competency_name]
 
        # Iterate through each unique statement
        for statement in competency_statements["Statements"].unique():
            # Filter rows for this statement
            statement_rows = competency_statements[competency_statements["Statements"] == statement]
 
            # Add the first row for "Self"
            self_rows = statement_rows[statement_rows["Others"] == "Self"]
            if not self_rows.empty:
                self_row = self_rows.iloc[0]
                table_data.append([Paragraph(statement, style_left_top), Paragraph("Self", style_bold_left_top), "", f"{self_row['Rating']:.2f}"])
            else:
                table_data.append([Paragraph(statement, style_left_top), Paragraph("Self", style_bold_left_top), "", "-"])  # Hyphen for missing Self data
 
            statement_start_row = row_index
            row_index += 1
 
            # Add "Others" row with average and individual roles
            others_rows = statement_rows[statement_rows["Others"] == "Others"]
            if not others_rows.empty:
                avg_others = f"{others_rows['Rating'].mean():.2f}"
                table_data.append(["", Paragraph("Others", style_bold_left_top), "", avg_others])  # Average row
                others_start_row = row_index
                row_index += 1
 
                # Group by "Relationship" and calculate the average rating
                grouped_relationships = others_rows.groupby("Relationship").mean(numeric_only=True).reset_index()
 
                # Add individual role rows for Others, showing the averaged rating for each relationship
                for _, group_row in grouped_relationships.iterrows():
                    table_data.append(["", "", group_row["Relationship"], f"{group_row['Rating']:.2f}"])
                    row_index += 1
 
                # Merging rules for Statements and Others
                merging_rules.append(("SPAN", (0, statement_start_row), (0, row_index - 1)))  # Merge Column 1 (Statements)
                merging_rules.append(("SPAN", (1, others_start_row), (1, row_index - 1)))  # Merge Column 2 (Others)
            else:
                # Handle "Others" with no relationships or ratings
                table_data.append(["", Paragraph("Others", style_bold_left_top), "", "-"])
                merging_rules.append(("SPAN", (0, statement_start_row), (0, row_index)))  # Merge Column 1 (Statements)
                merging_rules.append(("SPAN", (1, row_index), (1, row_index)))  # Merge Column 2 (Others)
                row_index += 1
 
    # Create the main table with data and merging rules
    table = Table(table_data, colWidths=[230, 100, 120, 60])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007FFF")),  
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),  
        ("FONTSIZE", (0, 0), (-1, 0), 13),  
        ("FONTSIZE", (0, 1), (-1, -1), 12),  
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),  
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),  
        ("ALIGN", (0, 1), (-1, -1), "LEFT"),  
        ("VALIGN", (0, 0), (-1, -1), "TOP"),  
        ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
 
    for merge_rule in merging_rules:
        table.setStyle(TableStyle([merge_rule]))
 
    # Add the table to the document
    elements.append(table)
 
    # Build the PDF with the header and subsequent pages
    doc.build(elements, onFirstPage=header, onLaterPages=subsequent_pages)
    print("Detailed Statement PDF generated successfully")

def OEF(db, email):
    return db[(db['Seeker Email']==email)
    #&(db['Relationship']!='Self')
    &(~db['Response'].isna())][['Statements','Response']].groupby('Statements').head(5).sort_values('Statements')

def create_open_ended_feedback_page(db, email, pdf_path, logo_path, icon_path):

    FOOTER_MARGIN = 20  # Define footer margin
    HEADER_MARGIN = 50  # Leave space at the top for the header

    # Create PDF canvas
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Function to start a new page with consistent margins
    def start_new_page():
        c.showPage()  # Finish the current page and start a new one
        return height - HEADER_MARGIN  # Reset the drawing position for the new page

    # Add logo
    logo_width = 1.8 * inch
    logo_height = 0.41 * inch
    c.drawImage(logo_path, width - logo_width - 30, height - logo_height - 30, 
                width=logo_width, height=logo_height)

    # Add "Open Ended Feedback" heading
    heading_y = height - logo_height - 50
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, heading_y, "Open Ended Feedback")

    # Add underline
    underline_y = heading_y - 10
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.line(50, underline_y, width - 50, underline_y)

    # Draw blue rectangle marker next to the heading
    marker_width = 9
    marker_height = 40
    c.setFillColorRGB(17 / 255, 141 / 255, 255 / 255)
    c.rect(35, heading_y - 12, marker_width, marker_height, fill=1, stroke=0)

    # Add description text
    description_y = underline_y - 40
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawString(50, description_y, "This section provides verbatim comments from all respondents. You will gain the")
    description_y -= 24
    c.drawString(50, description_y, "most value if you pay attention to the frequently occurring topics and suggestions.")
    description_y -= 24
    c.drawString(50, description_y, "Try to view the information objectively and reconcile it with the information in the")
    description_y -= 24
    c.drawString(50, description_y, "previous rating sections.")

    # Fetch dynamic statements and responses using the OEF function
    df = OEF(db, email)  # Assume OEF returns a DataFrame with 'Statements' and 'Response' columns
    
    # Group responses by statement and calculate their length
    statement_responses = (
        df.groupby('Statements')['Response']
        .apply(list)
        .reset_index()
    )

    # Sort statements by the number of responses
    statement_responses['ResponseCount'] = statement_responses['Response'].apply(len)
    statement_responses = statement_responses.sort_values(by='ResponseCount', ascending=False)
    statement_responses = statement_responses[['Statements', 'Response']].to_dict('records')

    block_y = description_y - 30
    block_margin = 50
    line_spacing = 24  # Adjusted line spacing for consistent layout

    # Define paragraph style for wrapping
    statement_style = ParagraphStyle(
        'Statement',
        parent=getSampleStyleSheet()['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.black,
        alignment=0  # Left-align text
    )

    response_style = ParagraphStyle(
        'Response',
        parent=getSampleStyleSheet()['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=line_spacing,
        textColor=colors.black,
        alignment=0  # Left-align text
    )

    # Iterate through statements and responses
    for item in statement_responses:
        statement = item['Statements']
        responses = item['Response']
        
        # Skip if no responses
        if not responses:
            continue
        
        # Create a Paragraph for the statement
        statement_paragraph = Paragraph(statement, statement_style)
        statement_width = width - 2 * block_margin - 20
        statement_p_width, statement_p_height = statement_paragraph.wrap(statement_width, 1000)

        # Adjust box height dynamically for centering and additional spacing
        box_height = statement_p_height + 20

        # Draw the statement box dynamically based on the wrapped height
        if block_y - box_height - FOOTER_MARGIN < 0:
            block_y = start_new_page()
        c.rect(block_margin, block_y - box_height, width - 2 * block_margin, box_height)

        # Adjust Y position for middle alignment within the box
        y_position = block_y - (box_height / 2) - (statement_p_height / 2)
        statement_paragraph.drawOn(c, block_margin + 10, y_position)

        # Draw responses
        response_y = block_y - box_height - 40
        for response in responses:
            # Create a Paragraph for wrapping the response text
            response_paragraph = Paragraph(response, response_style)

            # Calculate the width available for the response text
            available_width = width - 2 * block_margin - 55  # Adjust for margins and icon space
            p_width, p_height = response_paragraph.wrap(available_width, 1000)  # Wrap the text to fit within the available width

            # Ensure enough space for the paragraph and icon together
            required_space = p_height + 10  # Add padding for spacing
            if response_y - required_space - FOOTER_MARGIN < 0:
                response_y = start_new_page()

            # Draw the icon
            icon_width = 0.5 * inch
            icon_height = 0.5 * inch
            icon_x = block_margin + 10
            icon_y = response_y - icon_height
            c.drawImage(icon_path, icon_x, icon_y, width=icon_width, height=icon_height)

            # Draw the paragraph text
            response_paragraph.drawOn(c, block_margin + 55, response_y - p_height -12)

            # Add a line below the paragraph
            line_start_x = block_margin + 55
            line_end_x = width - block_margin
            line_y = response_y - p_height - 10  # Position slightly below the paragraph
            c.setStrokeColor(colors.grey)
            c.setLineWidth(0.5)
            c.line(line_start_x, line_y, line_end_x, line_y)

            # Update the Y position for the next response
            response_y -= max(p_height + line_spacing, line_spacing)

        block_y = response_y - 30  # Move to next block position

    # Save the PDF
    c.save()
    print("Open ended feedback page generated successfully")

# def upload_pdf_to_adls(pdf_content, blob_name):
#     try:
#         container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
#         container_client.upload_blob(name=blob_name, data=pdf_content.getvalue(), overwrite=True)
#         print(f"Uploaded PDF to container '{AZURE_CONTAINER_NAME}' as '{blob_name}'.")
#     except Exception as e:
#         print(f"Error uploading PDF: {e}")

# def generate_master_reports(rd, frd, odb_360, assessment_number,project1, client1, logo_path, logo_path_p, image_path, icon_path):
#     """
#     Generate PDF reports for each candidate and upload them directly to Azure Data Lake Storage.
#     """
#     # Extract unique candidates
#     candidates = rd[['Seeker Name', 'Seeker Email']].drop_duplicates()
#     print(" Iteration Started: @@@@@@@@@@@@>>>>>>> .")

#     for _, candidate in candidates.iterrows():
#         candidate_name = candidate['Seeker Name']
#         email = candidate['Seeker Email']

#         # Initialize in-memory buffers for each page
#         pdf_buffers = [BytesIO() for _ in range(11)]

#         print("Printing Page : >>>>>>> for PDF one by one.")
#         # Generate individual pages
#         create_first_page(pdf_buffers[0], image_path, logo_path_p, assessment_number, candidate_name)
#         create_second_page(pdf_buffers[1], logo_path)
#         create_third_page(pdf_buffers[2], logo_path, assessment_number)
#         create_fourth_page(pdf_buffers[3], logo_path, rd, assessment_number, email)
#         create_competency_pages(pdf_buffers[4], logo_path, frd, email)
#         create_strength_page(pdf_buffers[5], logo_path, rd, email)
#         create_improvement_page(pdf_buffers[6], logo_path, rd, email)
#         create_hidden_strength_page(pdf_buffers[7], logo_path, rd, email)
#         create_blind_spots_page(pdf_buffers[8], logo_path, rd, email)
#         detailed_statement_page(logo_path, frd, email, pdf_buffers[9])
#         create_open_ended_feedback_page(odb_360, email, pdf_buffers[10], logo_path, icon_path)

#         # Merge all pages into a single in-memory PDF
#         final_pdf_buffer = BytesIO()
#         merger = PdfMerger()
#         for pdf_buffer in pdf_buffers:
#             pdf_buffer.seek(0)
#             merger.append(pdf_buffer)
#         merger.write(final_pdf_buffer)
#         merger.close()

#         # Generate the blob name with the naming convention
#         blob_name = f"reports/{candidate_name.replace(' ', '_').lower()}_assessment_{assessment_number}_{client1}_{project1}_report.pdf"
#         blob_name = blob_name.lower()
#         print("Report generated succsfully : >>>>>>> Going for Upload PDF.")

#         # Upload the merged PDF to Azure Data Lake Storage
#         upload_pdf_to_adls(final_pdf_buffer, blob_name)

#         # Close all buffers
#         for pdf_buffer in pdf_buffers:
#             pdf_buffer.close()

#         final_pdf_buffer.close()

#         print(f"Generated and uploaded report for {candidate_name} ({email}) as '{blob_name}'.")


# # Fetch static files directly from the App_admin static folder
# app_admin_static_dir = os.path.join(os.path.dirname(__file__), 'static')
# icon_path = os.path.join(app_admin_static_dir, 'App_Admin/image/admin_text_icon.png')
# logo_path_p = os.path.join(app_admin_static_dir, 'App_Admin/image/admin_ForPage1.jpg')
# image_path = os.path.join(app_admin_static_dir, 'App_Admin/image/admin_img.png')
# logo_path = os.path.join(app_admin_static_dir, 'App_Admin/image/admin_For_All_pages.jpg')

# def main():
#     # Pass these dynamic paths to your function
#     print(f"In-process_______Reports generated!!!!!!!!!!! ")

#     # Path to your script
    
#     # assessment_number=assessment_number(assessment)
#     # print(f"Assessment number is ----------->>>>> {assessment_number}")
#     return generate_master_reports(
#         rd=RD,
#         frd=FRD,
#         odb_360=ODB_360,
#         assessment_number=assessment_number,
#         project1 = project1,
#         client1 = client1,
#         icon_path=icon_path,
#         logo_path_p=logo_path_p,
#         image_path=image_path,
#         logo_path=logo_path,
#     )
# # print(f"Reports generated successfully!!!!!!!!!!! at {generate_master_reports}")
        

# if __name__ == "__main__":
#     try:
#         # Step 1: Generate the PDF in memory
#         main()
#         print(f"Reports generated successfully!!!!!!!!!!!")
    
#     except Exception as e:
#         print(f"Error occurred: {e}")


 
def upload_to_adls(content, blob_name):
    """Upload content to ADLS"""
    try:
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        container_client.upload_blob(name=blob_name, data=content.getvalue(), overwrite=True)
        print(f"Uploaded to ADLS as '{blob_name}'.")
    except Exception as e:
        print(f"Error uploading: {e}")
 
def generate_master_reports(rd, frd, odb_360, assessment_number, project1, client1, logo_path, logo_path_p, image_path, icon_path):
    """
    Generate PDF reports for each candidate and add them to a ZIP archive, then upload the ZIP file to ADLS.
    """
    candidates = rd[['Seeker Name', 'Seeker Email']].drop_duplicates()
    print("Iteration started...")
 
    zip_buffer = BytesIO()
 
    # Create a ZIP archive in memory
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_archive:
       
        for _, candidate in candidates.iterrows():
            candidate_name = candidate['Seeker Name']
            email = candidate['Seeker Email']
 
            # Generate PDF pages
            pdf_buffers = [BytesIO() for _ in range(11)]
            create_first_page(pdf_buffers[0], image_path, logo_path_p, assessment_number, candidate_name)
            create_second_page(pdf_buffers[1], logo_path)
            create_third_page(pdf_buffers[2], logo_path, assessment_number)
            create_fourth_page(pdf_buffers[3], logo_path, rd, assessment_number, email)
            create_competency_pages(pdf_buffers[4], logo_path, frd, email)
            create_strength_page(pdf_buffers[5], logo_path, rd, email)
            create_improvement_page(pdf_buffers[6], logo_path, rd, email)
            create_hidden_strength_page(pdf_buffers[7], logo_path, rd, email)
            create_blind_spots_page(pdf_buffers[8], logo_path, rd, email)
            detailed_statement_page(logo_path, frd, email, pdf_buffers[9])
            create_open_ended_feedback_page(odb_360, email, pdf_buffers[10], logo_path, icon_path)
 
            # Merge all pages into a single in-memory PDF
            final_pdf_buffer = BytesIO()
            merger = PdfMerger()
           
            for pdf_buffer in pdf_buffers:
                pdf_buffer.seek(0)
                merger.append(pdf_buffer)
           
            merger.write(final_pdf_buffer)
            merger.close()
 
            # Create a unique PDF filename
            pdf_filename = f"{candidate_name.replace(' ', '_').lower()}_assessment_{assessment_number}_{client1}_{project1}_report.pdf"
           
            # Add the PDF to the ZIP archive
            zip_archive.writestr(pdf_filename, final_pdf_buffer.getvalue())
           
            # Close buffers
            for pdf_buffer in pdf_buffers:
                pdf_buffer.close()
            final_pdf_buffer.close()
 
            print(f"Added {pdf_filename} to ZIP archive.")
 
    # Upload the ZIP to ADLS
    zip_buffer.seek(0)
    zip_blob_name = f"reports/assessment_{assessment_number}_{client1}_{project1}.zip"
    upload_to_adls(zip_buffer, zip_blob_name)
 
    print(f"Uploaded ZIP file with all reports to ADLS as ---->>> '{zip_blob_name}'.")
 
# Update the `main()` function
def main():
    print("In-process... Generating reports!")
 
    # Fetch static files directly from the App_admin static folder
    app_admin_static_dir = os.path.join(os.path.dirname(__file__), 'static')
   
    # Define paths inside main()
    icon_path = os.path.join(app_admin_static_dir, 'App_Admin/image/admin_text_icon.png')
    logo_path_p = os.path.join(app_admin_static_dir, 'App_Admin/image/admin_ForPage1.jpg')
    image_path = os.path.join(app_admin_static_dir, 'App_Admin/image/admin_img.png')
    logo_path = os.path.join(app_admin_static_dir, 'App_Admin/image/admin_For_All_pages.jpg')
 
    # Pass paths to the function
    generate_master_reports(
        rd=RD,
        frd=FRD,
        odb_360=ODB_360,
        assessment_number=assessment_number,
        project1=project1,
        client1=client1,
        icon_path=icon_path,
        logo_path_p=logo_path_p,
        image_path=image_path,
        logo_path=logo_path,
    )
 
 
if __name__ == "__main__":
    try:
        main()
        print("Reports ZIP file generated and uploaded successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")
 
