"""
Joint Angle Calculator Module

Handles geometric calculations for joint angles and movements:
- Calculate angle between two or three joints
- Calculate velocity and acceleration
- Determine peak positions and ranges
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Point2D:
    """2D point for pose landmarks."""
    x: float
    y: float
    
    def distance_to(self, other: 'Point2D') -> float:
        """Calculate Euclidean distance to another point."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class JointAngleCalculator:
    """Calculate angles between joints from pose data."""
    
    @staticmethod
    def calculate_angle_between_points(
        point_a: Dict[str, float],
        point_b: Dict[str, float],
        point_c: Dict[str, float]
    ) -> float:
        """
        Calculate angle at point_b formed by points a-b-c.
        
        Args:
            point_a: {'x': float, 'y': float} - Start point
            point_b: {'x': float, 'y': float} - Vertex (angle measured here)
            point_c: {'x': float, 'y': float} - End point
            
        Returns:
            Angle in degrees (0-180)
        """
        try:
            # Convert to Point2D objects
            a = Point2D(point_a['x'], point_a['y'])
            b = Point2D(point_b['x'], point_b['y'])
            c = Point2D(point_c['x'], point_c['y'])
            
            # Calculate vectors
            ba = Point2D(a.x - b.x, a.y - b.y)
            bc = Point2D(c.x - b.x, c.y - b.y)
            
            # Calculate magnitudes
            mag_ba = math.sqrt(ba.x ** 2 + ba.y ** 2)
            mag_bc = math.sqrt(bc.x ** 2 + bc.y ** 2)
            
            # Avoid division by zero
            if mag_ba == 0 or mag_bc == 0:
                return 0.0
            
            # Calculate dot product
            dot_product = ba.x * bc.x + ba.y * bc.y
            
            # Calculate cosine of angle
            cos_angle = dot_product / (mag_ba * mag_bc)
            
            # Clamp to [-1, 1] to handle floating point errors
            cos_angle = max(-1.0, min(1.0, cos_angle))
            
            # Calculate angle in radians and convert to degrees
            angle_radians = math.acos(cos_angle)
            angle_degrees = math.degrees(angle_radians)
            
            return round(angle_degrees, 1)
            
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Invalid point data: {e}")
    
    @staticmethod
    def calculate_angle_from_landmarks(
        landmarks: Dict[str, Dict[str, float]],
        joint_a: str,
        joint_b: str,
        joint_c: str
    ) -> Optional[float]:
        """
        Calculate angle using named joints from landmarks.
        
        Args:
            landmarks: Dict of joint names to coordinates
            joint_a: Name of start joint
            joint_b: Name of vertex joint (where angle is measured)
            joint_c: Name of end joint
            
        Returns:
            Angle in degrees or None if joints not found
        """
        if joint_a not in landmarks or joint_b not in landmarks or joint_c not in landmarks:
            return None
        
        return JointAngleCalculator.calculate_angle_between_points(
            landmarks[joint_a],
            landmarks[joint_b],
            landmarks[joint_c]
        )
    
    @staticmethod
    def calculate_joint_displacement(
        current_position: Dict[str, float],
        previous_position: Dict[str, float]
    ) -> float:
        """
        Calculate distance moved by a joint between frames.
        
        Args:
            current_position: {'x': float, 'y': float}
            previous_position: {'x': float, 'y': float}
            
        Returns:
            Displacement in pixels
        """
        current = Point2D(current_position['x'], current_position['y'])
        previous = Point2D(previous_position['x'], previous_position['y'])
        return round(current.distance_to(previous), 2)
    
    @staticmethod
    def calculate_velocity(
        displacement: float,
        time_delta_seconds: float
    ) -> float:
        """
        Calculate velocity of joint movement.
        
        Args:
            displacement: Distance moved (pixels)
            time_delta_seconds: Time elapsed
            
        Returns:
            Velocity in pixels/second
        """
        if time_delta_seconds == 0:
            return 0.0
        return round(displacement / time_delta_seconds, 2)
    
    @staticmethod
    def calculate_acceleration(
        current_velocity: float,
        previous_velocity: float,
        time_delta_seconds: float
    ) -> float:
        """
        Calculate acceleration of joint movement.
        
        Args:
            current_velocity: Current velocity (pixels/second)
            previous_velocity: Previous velocity (pixels/second)
            time_delta_seconds: Time elapsed
            
        Returns:
            Acceleration in pixels/second²
        """
        if time_delta_seconds == 0:
            return 0.0
        return round((current_velocity - previous_velocity) / time_delta_seconds, 2)
    
    @staticmethod
    def calculate_angle_velocity(
        current_angle: float,
        previous_angle: float,
        time_delta_seconds: float
    ) -> float:
        """
        Calculate how fast angle is changing.
        
        Args:
            current_angle: Current angle in degrees
            previous_angle: Previous angle in degrees
            time_delta_seconds: Time elapsed
            
        Returns:
            Angular velocity in degrees/second
        """
        if time_delta_seconds == 0:
            return 0.0
        
        angle_diff = current_angle - previous_angle
        
        # Handle angle wrap-around
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360
        
        return round(angle_diff / time_delta_seconds, 2)
    
    @staticmethod
    def is_angle_stable(
        angles: List[float],
        stability_threshold: float = 5.0
    ) -> Tuple[bool, float]:
        """
        Determine if angle is stable (consistent) over time.
        
        Args:
            angles: List of angle measurements over time
            stability_threshold: Max variance allowed (degrees)
            
        Returns:
            (is_stable, variance) - Tuple of stability flag and variance
        """
        if len(angles) < 2:
            return True, 0.0
        
        mean_angle = sum(angles) / len(angles)
        variance = sum((angle - mean_angle) ** 2 for angle in angles) / len(angles)
        std_dev = math.sqrt(variance)
        
        is_stable = std_dev <= stability_threshold
        return is_stable, round(std_dev, 2)
    
    @staticmethod
    def get_angle_range(angles: List[float]) -> Tuple[float, float, float]:
        """
        Get min, max, and range of angles.
        
        Args:
            angles: List of angle measurements
            
        Returns:
            (min_angle, max_angle, range)
        """
        if not angles:
            return 0.0, 0.0, 0.0
        
        min_angle = min(angles)
        max_angle = max(angles)
        angle_range = max_angle - min_angle
        
        return round(min_angle, 1), round(max_angle, 1), round(angle_range, 1)
    
    @staticmethod
    def smooth_angle_series(angles: List[float], window_size: int = 3) -> List[float]:
        """
        Apply moving average smoothing to angle series to reduce noise.
        
        Args:
            angles: List of angle measurements
            window_size: Size of smoothing window
            
        Returns:
            Smoothed angle list
        """
        if len(angles) < window_size:
            return angles
        
        smoothed = []
        for i in range(len(angles)):
            start = max(0, i - window_size // 2)
            end = min(len(angles), i + window_size // 2 + 1)
            window = angles[start:end]
            smoothed.append(round(sum(window) / len(window), 1))
        
        return smoothed


class JointKinematics:
    """Analyze joint movement patterns and kinematics."""
    
    @staticmethod
    def classify_movement_phase(
        angle_velocity: float,
        acceleration: float
    ) -> str:
        """
        Classify movement phase based on velocity and acceleration.
        
        Args:
            angle_velocity: Rate of angle change (degrees/second)
            acceleration: Acceleration (degrees/second²)
            
        Returns:
            Phase name: 'acceleration', 'deceleration', 'constant', 'stop'
        """
        velocity_threshold = 2.0  # degrees/second
        
        if abs(angle_velocity) < velocity_threshold:
            return "stop"
        
        if acceleration > 1.0:
            return "acceleration"
        elif acceleration < -1.0:
            return "deceleration"
        else:
            return "constant"
    
    @staticmethod
    def detect_peak_position(
        angles: List[float],
        position_type: str = "max"
    ) -> Tuple[int, float]:
        """
        Find peak angle position (maximum or minimum).
        
        Args:
            angles: List of angle measurements over time
            position_type: 'max' for maximum or 'min' for minimum
            
        Returns:
            (frame_index, angle_value)
        """
        if not angles:
            return -1, 0.0
        
        if position_type == "max":
            frame_index = angles.index(max(angles))
            return frame_index, angles[frame_index]
        else:
            frame_index = angles.index(min(angles))
            return frame_index, angles[frame_index]
    
    @staticmethod
    def calculate_range_of_motion(
        angles: List[float],
        ideal_min: float,
        ideal_max: float
    ) -> float:
        """
        Calculate achieved range of motion as percentage of ideal range.
        
        Args:
            angles: List of angles achieved
            ideal_min: Ideal minimum angle
            ideal_max: Ideal maximum angle
            
        Returns:
            Percentage of ideal range achieved (0-100)
        """
        if not angles:
            return 0.0
        
        achieved_min = min(angles)
        achieved_max = max(angles)
        achieved_range = achieved_max - achieved_min
        
        ideal_range = ideal_max - ideal_min
        
        if ideal_range == 0:
            return 0.0
        
        rom_percentage = (achieved_range / ideal_range) * 100
        return round(min(100, rom_percentage), 1)
