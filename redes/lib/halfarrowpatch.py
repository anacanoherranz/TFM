"""
HalfArrowPatch module for drawing curved arrows with half-arrowheads.
This module provides custom matplotlib patches for creating arrows
with half arrowheads, used in network visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, PathPatch
from matplotlib.path import Path
import matplotlib.transforms as transforms

class HalfArrowPatch(FancyArrowPatch):
    """
    A custom arrow patch that draws arrows with half arrowheads.
    Useful for drawing multiple parallel edges between nodes.
    """
    
    def __init__(self, posA, posB, marker='-|>', width=1, height=1, 
                 color='black', linewidth=1, curvature=0.3, 
                 arrow_linewidth=2, **kwargs):
        """
        Initialize a HalfArrowPatch.
        
        Parameters:
        -----------
        posA, posB : tuples
            Starting and ending positions (x, y)
        marker : str
            Arrow style ('-|>' for right half, '|\\' for left half, etc.)
        width, height : float
            Width and height of the arrowhead
        color : str or tuple
            Arrow color
        linewidth : float
            Width of the arrow shaft
        curvature : float
            Curvature of the arrow (0 = straight, >0 = curved)
        arrow_linewidth : float
            Width of the arrowhead lines
        **kwargs : additional arguments for FancyArrowPatch
        """
        # Store parameters
        self.marker = marker
        self.arrow_width = width
        self.arrow_height = height
        self.arrow_linewidth = arrow_linewidth
        self.curvature = curvature
        
        # Initialize the parent class
        super().__init__(posA, posB, 
                        connectionstyle=f"arc3,rad={curvature}",
                        arrowstyle='-',  # Start with no arrowhead, we'll draw it manually
                        color=color,
                        linewidth=linewidth,
                        **kwargs)
        
        self._color = color
        self._posA = np.array(posA)
        self._posB = np.array(posB)
        
    def draw(self, renderer):
        """Override draw method to add custom half arrowhead."""
        # Draw the curved line first
        super().draw(renderer)
        
        # Get the transformed points
        trans = self.get_transform()
        posA_trans = trans.transform(self._posA)
        posB_trans = trans.transform(self._posB)
        
        # Calculate the direction at the end of the curve
        # For curved arrows, we need the tangent at the endpoint
        if self.curvature != 0:
            # For curved arrows, calculate tangent at endpoint
            C, R = self._get_circle_center()
            if C is not None:
                # Vector from center to endpoint
                v = posB_trans - C
                # Tangent is perpendicular to radius
                tangent = np.array([-v[1], v[0]])
                tangent = tangent / np.linalg.norm(tangent)
            else:
                # Fallback to straight line direction
                tangent = posB_trans - posA_trans
                tangent = tangent / np.linalg.norm(tangent)
        else:
            # Straight line - direction is from start to end
            tangent = posB_trans - posA_trans
            tangent = tangent / np.linalg.norm(tangent)
        
        # Perpendicular vector (90 degrees rotation)
        perp = np.array([-tangent[1], tangent[0]])
        
        # Calculate arrowhead points based on marker style
        arrowhead_center = posB_trans
        
        if self.marker == '-|>' or self.marker == '|>':
            # Right half arrowhead (pointing to the right of the direction)
            points = [
                arrowhead_center,
                arrowhead_center - tangent * self.arrow_height + perp * self.arrow_width/2,
                arrowhead_center - tangent * self.arrow_height
            ]
        elif self.marker == '|\\' or self.marker == '<|':
            # Left half arrowhead (pointing to the left of the direction)
            points = [
                arrowhead_center,
                arrowhead_center - tangent * self.arrow_height - perp * self.arrow_width/2,
                arrowhead_center - tangent * self.arrow_height
            ]
        elif self.marker == '|<':
            # Half arrowhead on the other side (for bidirectional)
            points = [
                arrowhead_center,
                arrowhead_center - tangent * self.arrow_height + perp * self.arrow_width/2,
                arrowhead_center - tangent * self.arrow_height
            ]
        else:
            # Default full arrowhead
            points = [
                arrowhead_center,
                arrowhead_center - tangent * self.arrow_height + perp * self.arrow_width/2,
                arrowhead_center - tangent * self.arrow_height - perp * self.arrow_width/2,
                arrowhead_center
            ]
        
        # Create the arrowhead patch
        if len(points) >= 3:
            # Create path for the filled arrowhead
            verts = points
            codes = [Path.MOVETO] + [Path.LINETO] * (len(points)-2) + [Path.CLOSEPOLY]
            
            path = Path(verts, codes)
            patch = PathPatch(path, facecolor=self._color, 
                            edgecolor=self._color, 
                            linewidth=self.arrow_linewidth,
                            transform=transforms.IdentityTransform(),
                            zorder=self.zorder+1)
            
            # Draw the arrowhead
            patch.draw(renderer)
    
    def _get_circle_center(self):
        """Calculate the center of the circle for curved arrows."""
        try:
            A = self._posA
            B = self._posB
            rad = self.curvature
            
            # Calculate the center of the arc
            M = (A + B) / 2
            d = B - A
            L = np.linalg.norm(d)
            
            if L == 0:
                return None, None
                
            n = np.array([-d[1], d[0]]) / L
            h = rad * L / 2
            R = (L**2 / 4 + h**2) / (2 * h)
            C = M + n * (R - L**2 / (8 * h))
            
            return C, R
        except:
            return None, None


def test_half_arrow():
    """Test function to demonstrate HalfArrowPatch usage."""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Create some test positions
    pos = {
        'A': np.array([0, 0]),
        'B': np.array([1, 0.5]),
        'C': np.array([0.5, 1]),
        'D': np.array([-0.5, 0.5])
    }
    
    # Draw nodes
    for node, p in pos.items():
        circle = plt.Circle(p, 0.1, color='lightblue', ec='black', lw=2)
        ax.add_patch(circle)
        ax.text(p[0], p[1]+0.15, node, ha='center', fontsize=12)
    
    # Test different arrow styles
    # Right half arrow
    arrow1 = HalfArrowPatch(
        pos['A'], pos['B'],
        marker='-|>',
        width=0.2, height=0.3,
        color='blue',
        linewidth=2,
        curvature=0.2,
        arrow_linewidth=2
    )
    ax.add_patch(arrow1)
    
    # Left half arrow
    arrow2 = HalfArrowPatch(
        pos['A'], pos['C'],
        marker='|\\',
        width=0.2, height=0.3,
        color='red',
        linewidth=2,
        curvature=0.2,
        arrow_linewidth=2
    )
    ax.add_patch(arrow2)
    
    # Double arrows (parallel)
    arrow3 = HalfArrowPatch(
        pos['A'], pos['D'],
        marker='-|>',
        width=0.2, height=0.3,
        color='green',
        linewidth=2,
        curvature=0.15,
        arrow_linewidth=2
    )
    ax.add_patch(arrow3)
    
    arrow4 = HalfArrowPatch(
        pos['A'], pos['D'],
        marker='|\\',
        width=0.2, height=0.3,
        color='orange',
        linewidth=2,
        curvature=0.15,
        arrow_linewidth=2
    )
    # Adjust offset manually
    arrow4._posA = arrow4._posA + np.array([0.05, 0.05])
    arrow4._posB = arrow4._posB + np.array([0.05, 0.05])
    ax.add_patch(arrow4)
    
    ax.set_xlim(-1, 2)
    ax.set_ylim(-1, 2)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('HalfArrowPatch Test')
    
    plt.show()


if __name__ == "__main__":
    test_half_arrow()
    