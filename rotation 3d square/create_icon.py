import matplotlib.pyplot as plt
import numpy as np

# Create figure
fig, ax = plt.subplots(figsize=(2, 2))
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal')
ax.axis('off')

# Draw 3D-looking square with perspective
square1 = np.array([[-0.8, -0.8], [0.8, -0.8], [0.8, 0.8], [-0.8, 0.8], [-0.8, -0.8]])
square2 = np.array([[-0.5, -0.5], [1.1, -0.5], [1.1, 1.1], [-0.5, 1.1], [-0.5, -0.5]])

# Draw back square (lighter)
ax.plot(square2[:, 0], square2[:, 1], 'b-', linewidth=3, alpha=0.6)
ax.fill(square2[:, 0], square2[:, 1], 'lightblue', alpha=0.3)

# Draw front square (darker)
ax.plot(square1[:, 0], square1[:, 1], 'b-', linewidth=4)
ax.fill(square1[:, 0], square1[:, 1], 'cyan', alpha=0.7)

# Connect corners for 3D effect
for i in range(4):
    ax.plot([square1[i, 0], square2[i, 0]], [square1[i, 1], square2[i, 1]], 'b-', linewidth=2, alpha=0.8)

# Add rotation arrow
theta = np.linspace(0, 1.5*np.pi, 50)
r = 1.2
x_arrow = r * np.cos(theta)
y_arrow = r * np.sin(theta)
ax.plot(x_arrow, y_arrow, 'red', linewidth=3, alpha=0.8)

# Add arrowhead
ax.annotate('', xy=(x_arrow[-1], y_arrow[-1]), xytext=(x_arrow[-5], y_arrow[-5]),
            arrowprops=dict(arrowstyle='->', color='red', lw=3))

plt.tight_layout()
plt.savefig('icon.png', dpi=300, bbox_inches='tight', pad_inches=0, facecolor='white')
plt.close()

print("Icon created: icon.png")