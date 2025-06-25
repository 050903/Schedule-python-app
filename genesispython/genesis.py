import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
import seaborn as sns

# Set up the style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create figure and subplots
fig = plt.figure(figsize=(20, 16))
fig.suptitle('PROJECT GENESIS - Comprehensive Technical Architecture', 
             fontsize=24, fontweight='bold', y=0.95)

# Define colors
colors = {
    'input': '#FF6B6B',
    'analysis': '#4ECDC4', 
    'generation': '#45B7D1',
    'deployment': '#96CEB4',
    'aws': '#FF9500',
    'ai': '#9B59B6',
    'ui': '#3498DB'
}

# Main workflow diagram
ax1 = plt.subplot(2, 2, (1, 2))
ax1.set_title('End-to-End Workflow', fontsize=18, fontweight='bold', pad=20)

# Workflow steps
steps = [
    ("User Input\n(Natural Language)", colors['input'], (1, 4)),
    ("Requirement Analysis\n& Clarification", colors['analysis'], (3, 4)),
    ("Detailed Specification\nGeneration (JSON)", colors['generation'], (5, 4)),
    ("Code Generation\n(HTML/CSS/JS)", colors['ai'], (7, 4)),
    ("Packaging &\nDeployment", colors['deployment'], (9, 4))
]

# Draw workflow steps
for i, (step_name, color, pos) in enumerate(steps):
    # Create fancy box
    box = FancyBboxPatch((pos[0]-0.8, pos[1]-0.8), 1.6, 1.6,
                        boxstyle="round,pad=0.1", 
                        facecolor=color, edgecolor='black', linewidth=2,
                        alpha=0.8)
    ax1.add_patch(box)
    
    # Add text
    ax1.text(pos[0], pos[1], step_name, ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')
    
    # Add step number
    circle = plt.Circle((pos[0]-0.6, pos[1]+0.6), 0.2, 
                       color='white', zorder=10)
    ax1.add_patch(circle)
    ax1.text(pos[0]-0.6, pos[1]+0.6, str(i+1), ha='center', va='center',
            fontsize=12, fontweight='bold', color='black')
    
    # Add arrows between steps
    if i < len(steps) - 1:
        arrow = patches.FancyArrowPatch((pos[0]+0.8, pos[1]), 
                                       (steps[i+1][2][0]-0.8, steps[i+1][2][1]),
                                       arrowstyle='->', mutation_scale=20,
                                       color='black', linewidth=2)
        ax1.add_patch(arrow)

ax1.set_xlim(0, 10)
ax1.set_ylim(2, 6)
ax1.axis('off')

# AWS Architecture Components
ax2 = plt.subplot(2, 2, 3)
ax2.set_title('AWS Cloud Infrastructure', fontsize=16, fontweight='bold', pad=20)

# AWS components with positions
aws_components = [
    ("API Gateway", (2, 8), colors['aws']),
    ("Cognito/IAM", (1, 6.5), colors['aws']),
    ("SQS/Kafka", (3, 6.5), colors['aws']),
    ("Lambda", (1, 5), colors['aws']),
    ("EKS/EC2", (3, 5), colors['aws']),
    ("S3", (0.5, 3.5), colors['aws']),
    ("DynamoDB", (2, 3.5), colors['aws']),
    ("RDS", (3.5, 3.5), colors['aws']),
    ("SageMaker", (1, 2), colors['ai']),
    ("Bedrock", (3, 2), colors['ai']),
    ("CloudWatch", (2, 0.5), colors['aws'])
]

# Draw AWS components
for component, pos, color in aws_components:
    box = FancyBboxPatch((pos[0]-0.4, pos[1]-0.3), 0.8, 0.6,
                        boxstyle="round,pad=0.05", 
                        facecolor=color, edgecolor='black', 
                        alpha=0.7)
    ax2.add_patch(box)
    ax2.text(pos[0], pos[1], component, ha='center', va='center',
            fontsize=8, fontweight='bold', color='white')

# Add connections between components
connections = [
    ((2, 8), (1, 6.5)),  # API Gateway to Cognito
    ((2, 8), (3, 6.5)),  # API Gateway to SQS
    ((3, 6.5), (1, 5)),  # SQS to Lambda
    ((3, 6.5), (3, 5)),  # SQS to EKS
    ((1, 5), (2, 3.5)),  # Lambda to DynamoDB
    ((3, 5), (0.5, 3.5)), # EKS to S3
    ((3, 5), (1, 2)),    # EKS to SageMaker
    ((1, 5), (3, 2)),    # Lambda to Bedrock
]

for start, end in connections:
    ax2.plot([start[0], end[0]], [start[1], end[1]], 
            'k--', alpha=0.5, linewidth=1)

ax2.set_xlim(0, 4)
ax2.set_ylim(0, 9)
ax2.axis('off')

# AI Models and Technologies
ax3 = plt.subplot(2, 2, 4)
ax3.set_title('AI Models & Technologies', fontsize=16, fontweight='bold', pad=20)

# Create a hierarchical view of AI models
models = {
    'NLP Models': ['GPT-4', 'Gemini', 'Claude'],
    'Code Generation': ['Code Llama', 'StarCoder', 'Codey APIs'],
    'Specification': ['GPT-4', 'Gemini 1.5 Pro', 'Claude 3 Opus'],
    'Image/Assets': ['Stable Diffusion', 'Midjourney']
}

y_pos = 4
colors_list = ['#E74C3C', '#9B59B6', '#3498DB', '#2ECC71']

for i, (category, model_list) in enumerate(models.items()):
    # Category header
    rect = FancyBboxPatch((0.5, y_pos-0.2), 3, 0.4,
                         boxstyle="round,pad=0.05",
                         facecolor=colors_list[i], alpha=0.8)
    ax3.add_patch(rect)
    ax3.text(2, y_pos, category, ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')
    
    # Models under category
    y_pos -= 0.7
    for j, model in enumerate(model_list):
        model_rect = FancyBboxPatch((0.7 + j*0.8, y_pos-0.15), 0.7, 0.3,
                                   boxstyle="round,pad=0.02",
                                   facecolor=colors_list[i], alpha=0.4)
        ax3.add_patch(model_rect)
        ax3.text(1.05 + j*0.8, y_pos, model, ha='center', va='center',
                fontsize=8, fontweight='bold')
    
    y_pos -= 0.8

ax3.set_xlim(0, 4)
ax3.set_ylim(-1, 5)
ax3.axis('off')

# Add technology stack information
fig.text(0.02, 0.35, 
         'Technology Stack:\n'
         '• Frontend: React/Next.js\n'
         '• Styling: Tailwind CSS\n'
         '• Backend: AWS Lambda/EKS\n'
         '• Database: DynamoDB/RDS\n'
         '• Storage: Amazon S3\n'
         '• AI/ML: SageMaker/Bedrock\n'
         '• Deployment: Vercel/AWS Amplify',
         fontsize=11, fontweight='bold',
         bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.7))

# Add key features
fig.text(0.02, 0.02,
         'Key Features:\n'
         '• Natural Language to Website\n'
         '• Real-time Preview & Iteration\n'
         '• Interactive Specification Editor\n'
         '• Multi-platform Deployment\n'
         '• Version Control & Project Management\n'
         '• Scalable Cloud-Native Architecture',
         fontsize=11, fontweight='bold',
         bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen', alpha=0.7))

plt.tight_layout()
plt.show()

# Create a separate detailed workflow diagram
fig2, ax = plt.subplots(figsize=(16, 10))
ax.set_title('Project Genesis - Detailed System Flow', fontsize=20, fontweight='bold', pad=30)

# Detailed workflow with more components
detailed_steps = [
    ("User Input", "Natural Language\nDescription", (1, 8), colors['input']),
    ("NLP Processing", "Entity Recognition\n& Intent Classification", (3, 8), colors['analysis']),
    ("Clarification", "Interactive Q&A\nChatbot", (5, 8), colors['analysis']),
    ("JSON Generation", "Structured Spec\nCreation", (7, 8), colors['generation']),
    ("Code Generation", "HTML/CSS/JS\nCreation", (9, 8), colors['ai']),
    ("Preview", "Real-time\nRendering", (11, 8), colors['ui']),
    ("Refinement", "User Feedback\n& Iteration", (9, 6), colors['ui']),
    ("Deployment", "Platform\nDeployment", (7, 4), colors['deployment']),
    ("Monitoring", "Performance\n& Analytics", (5, 4), colors['aws']),
    ("Version Control", "Git Integration\n& Versioning", (3, 4), colors['aws'])
]

# Draw detailed workflow
for step_name, description, pos, color in detailed_steps:
    # Main box
    box = FancyBboxPatch((pos[0]-0.6, pos[1]-0.6), 1.2, 1.2,
                        boxstyle="round,pad=0.1", 
                        facecolor=color, edgecolor='black', linewidth=2,
                        alpha=0.8)
    ax.add_patch(box)
    
    # Step name
    ax.text(pos[0], pos[1]+0.2, step_name, ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    
    # Description
    ax.text(pos[0], pos[1]-0.2, description, ha='center', va='center',
            fontsize=9, color='white')

# Add flow arrows for detailed workflow
detailed_connections = [
    ((1, 8), (3, 8)),    # Input to NLP
    ((3, 8), (5, 8)),    # NLP to Clarification
    ((5, 8), (7, 8)),    # Clarification to JSON
    ((7, 8), (9, 8)),    # JSON to Code Generation
    ((9, 8), (11, 8)),   # Code to Preview
    ((11, 8), (9, 6)),   # Preview to Refinement
    ((9, 6), (7, 8)),    # Refinement back to JSON (feedback loop)
    ((9, 8), (7, 4)),    # Code to Deployment
    ((7, 4), (5, 4)),    # Deployment to Monitoring
    ((5, 4), (3, 4)),    # Monitoring to Version Control
]

for start, end in detailed_connections:
    if start[1] == end[1]:  # Horizontal arrow
        arrow = patches.FancyArrowPatch(start, end,
                                       arrowstyle='->', mutation_scale=15,
                                       color='black', linewidth=2)
    else:  # Curved arrow for feedback loops
        arrow = patches.FancyArrowPatch(start, end,
                                       arrowstyle='->', mutation_scale=15,
                                       color='red', linewidth=2,
                                       connectionstyle="arc3,rad=0.3")
    ax.add_patch(arrow)

ax.set_xlim(0, 12)
ax.set_ylim(3, 9)
ax.axis('off')

# Add legend
legend_elements = [
    patches.Patch(color=colors['input'], label='User Interface'),
    patches.Patch(color=colors['analysis'], label='Analysis & Processing'),
    patches.Patch(color=colors['generation'], label='Content Generation'),
    patches.Patch(color=colors['ai'], label='AI/ML Services'),
    patches.Patch(color=colors['deployment'], label='Deployment'),
    patches.Patch(color=colors['aws'], label='Infrastructure')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=12)

plt.tight_layout()
plt.show()

print("✅ Project Genesis Architecture Visualization Complete!")
print("\nKey Components Visualized:")
print("1. End-to-End Workflow (4 main steps)")
print("2. AWS Cloud Infrastructure (11 services)")
print("3. AI Models & Technologies (4 categories)")
print("4. Detailed System Flow (10 components)")
print("\nThis architecture supports:")
print("• Natural language to website generation")
print("• Cloud-native scalable infrastructure") 
print("• Real-time preview and iteration")
print("• Multi-platform deployment")
print("• Comprehensive project management")