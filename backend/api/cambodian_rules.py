"""
Cambodian Traffic Law Enforcement Engine
Tailored to the Road Traffic Law of the Kingdom of Cambodia (ច្បាប់ស្តីពីចរាចរណ៍ផ្លូវគោក).

Implements Computer Vision rule-based post-processing:
1. Helmet Violations (មាត្រាពាក់មួកសុវត្ថិភាព): Drivers & all passengers must wear helmets.
2. Motorcycle Overloading (ការឌុបលើសចំណុះ): Max 1 driver + 1 adult passenger (+ 1 child < 14).
3. Cambodian Vehicle Classification: motorcycle, car, auto_rickshaw (PassApp/Bajaj), remorque, truck.
4. Red Light Running (បើកបរល្មើសភ្លើងស្តុប): Stop-line polygon intrusion when light is RED.
5. Wrong-Way Driving (បើកបរបញ្ច្រាសទិស): Trajectory angle vs lane direction vector.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DetectionBox:
    """Represents a single bounding box detection."""
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    track_id: Optional[int] = None
    trajectory: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def x1(self) -> int:
        return self.bbox[0]

    @property
    def y1(self) -> int:
        return self.bbox[1]

    @property
    def x2(self) -> int:
        return self.bbox[2]

    @property
    def y2(self) -> int:
        return self.bbox[3]

    @property
    def width(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def height(self) -> int:
        return max(0, self.y2 - self.y1)

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def center(self) -> Tuple[int, int]:
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    @property
    def bottom_center(self) -> Tuple[int, int]:
        """Vehicle tire/ground contact reference point."""
        return ((self.x1 + self.x2) // 2, self.y2)


@dataclass
class MotorcycleSafetyAssessment:
    """Safety evaluation results for a single motorcycle."""
    motorcycle_id: Optional[int]
    motorcycle_box: DetectionBox
    rider_count: int
    riders: List[DetectionBox]
    is_overloaded: bool
    has_helmet_violation: bool
    violating_riders: List[DetectionBox]
    violations: List[str]


class CambodianTrafficRuleEngine:
    """
    Automated traffic law enforcement logic for Cambodia road conditions.
    Associates riders with motorcycles, checks overloading, detects helmet violations,
    evaluates red-light stop-line crossing, and flags wrong-way driving.
    """

    MAX_LEGAL_MOTO_RIDERS: int = 2

    @classmethod
    def is_auto_rickshaw(
        cls,
        crop: Optional[any],
        bbox: Tuple[int, int, int, int],
        img_shape: Tuple[int, ...],
        original_class: str = "truck",
    ) -> bool:
        """
        Disambiguates Cambodian PassApp, Bajaj RE, and Tuk-Tuks from Cars and Trucks.
        Recognizes:
        1. Official Cambodian PassApp (White body + Black curved canopy roof)
        2. Yellow / Orange / Green Bajaj 3-wheelers (PassApp / Grab)
        3. Preserves standard Cars and Delivery Vans as 'car'.
        """
        import cv2
        import numpy as np

        if crop is None or getattr(crop, "size", 0) == 0:
            return False

        img_h, img_w = img_shape[:2]
        x1, y1, x2, y2 = bbox
        bw = x2 - x1
        bh = y2 - y1
        if bw <= 0 or bh <= 0:
            return False

        aspect_ratio = bh / bw

        # PassApp / 3-wheelers are compact (square or taller than wide)
        if not (0.75 <= aspect_ratio <= 1.70):
            return False

        try:
            hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
            ch, cw = crop.shape[:2]

            # --- Pattern 1: Yellow / Green Bajaj PassApp ---
            yellow_mask = cv2.inRange(hsv, (14, 30, 30), (38, 255, 255))
            green_mask = cv2.inRange(hsv, (35, 25, 25), (88, 255, 255))
            total_pixels = ch * cw
            yg_ratio = (np.sum(yellow_mask > 0) + np.sum(green_mask > 0)) / total_pixels

            if yg_ratio >= 0.18:
                return True

            # --- Pattern 2: Official Cambodian White PassApp (Black Canopy + White Lower Body) ---
            # Top 38% has black/charcoal curved canopy roof
            top_h = max(1, int(ch * 0.38))
            top_canopy = crop[:top_h, :]
            bottom_body = crop[top_h:, :]

            hsv_top = cv2.cvtColor(top_canopy, cv2.COLOR_BGR2HSV)
            dark_top_ratio = np.sum(hsv_top[:, :, 2] < 120) / (top_canopy.shape[0] * top_canopy.shape[1])

            hsv_bottom = cv2.cvtColor(bottom_body, cv2.COLOR_BGR2HSV)
            white_bottom_ratio = np.sum((hsv_bottom[:, :, 1] < 55) & (hsv_bottom[:, :, 2] > 105)) / (bottom_body.shape[0] * bottom_body.shape[1])

            # True PassApp: dark hood on top + white lower body + compact 3-wheel footprint
            if dark_top_ratio >= 0.30 and white_bottom_ratio >= 0.25:
                return True

        except Exception:
            pass

        return False

    # Canonical mapping for Cambodian vehicle types
    LOCAL_VEHICLE_MAP = {
        "passapp": "auto_rickshaw",
        "bajaj": "auto_rickshaw",
        "rickshaw": "auto_rickshaw",
        "auto_rickshaw": "auto_rickshaw",
        "tuktuk": "auto_rickshaw",
        "remorque": "remorque",
        "moto_trailer": "remorque",
        "motorcycle": "motorcycle",
        "moto": "motorcycle",
        "motorbike": "motorcycle",
        "car": "car",
        "truck": "truck",
        "heavy_truck": "truck",
        "bus": "bus",
    }

    @classmethod
    def detect_remorques(
        cls,
        motorcycles: List[DetectionBox],
        trailers_or_trucks: List[DetectionBox],
        img: Optional[any] = None,
    ) -> Tuple[List[DetectionBox], List[DetectionBox], List[DetectionBox]]:
        """
        Disambiguates Traditional Khmer Remorques (រ៉ឺម៉កកង់បី).
        A Remorque consists of a motorcycle attached to an open passenger carriage with a flat roof.
        Standard COCO models predict the motorcycle as 'motorcycle' and the canopy trailer as 'truck'.
        This method detects spatial coupling and fuses them into a single 'remorque' vehicle,
        while ensuring solid enclosed automotive vans and cars are not falsely paired.
        """
        import cv2
        import numpy as np

        remorques: List[DetectionBox] = []
        matched_motos = set()
        matched_trailers = set()

        for m_idx, moto in enumerate(motorcycles):
            for t_idx, trailer in enumerate(trailers_or_trucks):
                if t_idx in matched_trailers:
                    continue

                # Ensure candidate trailer is not an enclosed white automotive van or car
                if img is not None:
                    try:
                        tx1, ty1, tx2, ty2 = trailer.bbox
                        t_crop = img[ty1:ty2, tx1:tx2]
                        if t_crop.size > 0:
                            hsv = cv2.cvtColor(t_crop, cv2.COLOR_BGR2HSV)
                            white_mask = (hsv[:, :, 1] < 45) & (hsv[:, :, 2] > 130)
                            white_ratio = np.sum(white_mask > 0) / (t_crop.shape[0] * t_crop.shape[1])
                            if white_ratio > 0.32:
                                continue  # Enclosed white car/van, not an open Remorque trailer
                    except Exception:
                        pass

                # Calculate spatial overlap
                x_left = max(moto.x1, trailer.x1)
                x_right = min(moto.x2, trailer.x2)
                min_w = min(moto.width, trailer.width)
                h_overlap = (max(0, x_right - x_left) / min_w) if min_w > 0 else 0.0

                y_top = max(moto.y1, trailer.y1)
                y_bottom = min(moto.y2, trailer.y2)
                min_h = min(moto.height, trailer.height)
                v_overlap = (max(0, y_bottom - y_top) / min_h) if min_h > 0 else 0.0

                # Coupling check
                if h_overlap > 0.40 and v_overlap > 0.30:
                    matched_motos.add(m_idx)
                    matched_trailers.add(t_idx)

                    fx1 = min(moto.x1, trailer.x1)
                    fy1 = min(moto.y1, trailer.y1)
                    fx2 = max(moto.x2, trailer.x2)
                    fy2 = max(moto.y2, trailer.y2)
                    avg_conf = (moto.confidence + trailer.confidence) / 2.0

                    remorques.append(
                        DetectionBox(
                            class_name="remorque",
                            confidence=avg_conf,
                            bbox=(fx1, fy1, fx2, fy2),
                            track_id=moto.track_id or trailer.track_id,
                        )
                    )
                    break

        remaining_motos = [m for i, m in enumerate(motorcycles) if i not in matched_motos]
        remaining_trucks = [t for i, t in enumerate(trailers_or_trucks) if i not in matched_trailers]

        return remorques, remaining_motos, remaining_trucks

    @staticmethod
    def calculate_horizontal_overlap(box1: DetectionBox, box2: DetectionBox) -> float:
        """Calculate horizontal (X-axis) overlap ratio relative to the narrower box."""
        x_left = max(box1.x1, box2.x1)
        x_right = min(box1.x2, box2.x2)
        if x_right <= x_left:
            return 0.0
        overlap_width = x_right - x_left
        min_width = min(box1.width, box2.width)
        return overlap_width / min_width if min_width > 0 else 0.0

    @classmethod
    def is_rider_on_motorcycle(
        cls,
        rider: DetectionBox,
        moto: DetectionBox,
        min_horizontal_overlap: float = 0.35,
    ) -> bool:
        """
        Determines if a rider (person or helmet box) is positioned on a motorcycle.
        In Cambodia traffic, riders sit vertically directly on or above the motorcycle chassis.
        """
        # Horizontal alignment check
        h_overlap = cls.calculate_horizontal_overlap(rider, moto)
        if h_overlap < min_horizontal_overlap:
            return False

        # Vertical sanity check: Rider's bottom should be inside or slightly above the motorcycle
        # Rider's top should NOT be below the motorcycle's bottom
        if rider.y2 < moto.y1 - (moto.height * 0.8):
            return False  # Too high up
        if rider.y1 > moto.y2:
            return False  # Below the motorcycle

        return True

    @classmethod
    def evaluate_motorcycle_safety(
        cls,
        motorcycles: List[DetectionBox],
        riders_or_helmets: List[DetectionBox],
    ) -> List[MotorcycleSafetyAssessment]:
        """
        Matches riders to their respective motorcycles and evaluates:
        1. Overloading (ឌុបលើសចំណុះ): count > 2
        2. Helmet law violation (អត់ពាក់មួកសុវត្ថិភាព): any rider without helmet
        Uses center-alignment matching to prevent riders in adjacent lanes from being falsely grouped.
        """
        assessments: List[MotorcycleSafetyAssessment] = []
        if not motorcycles:
            return assessments

        # Separate heads/helmets and person bodies
        head_boxes: List[DetectionBox] = []
        body_boxes: List[DetectionBox] = []
        for box in riders_or_helmets:
            c_name = box.class_name.lower()
            if any(tag in c_name for tag in ("helmet", "head")):
                head_boxes.append(box)
            else:
                body_boxes.append(box)

        # Map each motorcycle index to its matched heads and bodies
        moto_heads: Dict[int, List[DetectionBox]] = {i: [] for i in range(len(motorcycles))}
        moto_violating: Dict[int, List[DetectionBox]] = {i: [] for i in range(len(motorcycles))}
        moto_bodies: Dict[int, List[DetectionBox]] = {i: [] for i in range(len(motorcycles))}

        # 1. Assign each head to the motorcycle with the closest center
        for h_box in head_boxes:
            hcx = (h_box.x1 + h_box.x2) / 2
            best_idx = None
            min_dist = float('inf')

            for m_idx, moto in enumerate(motorcycles):
                # Must be horizontally aligned with the motorcycle's lane
                if (moto.x1 - 12 <= hcx <= moto.x2 + 12) and (h_box.y2 <= moto.y2) and (h_box.y1 >= moto.y1 - moto.height * 0.95):
                    mcx = (moto.x1 + moto.x2) / 2
                    dist = abs(hcx - mcx)
                    if dist < min_dist:
                        min_dist = dist
                        best_idx = m_idx

            if best_idx is not None:
                moto_heads[best_idx].append(h_box)
                is_no_helmet = any(
                    tag in h_box.class_name.lower()
                    for tag in ("no_helmet", "without_helmet", "head", "person_no_helmet")
                )
                if is_no_helmet:
                    moto_violating[best_idx].append(h_box)

        # 2. Assign bodies that don't already have an assigned head on that motorcycle
        for b_box in body_boxes:
            bcx = (b_box.x1 + b_box.x2) / 2
            best_idx = None
            min_dist = float('inf')

            for m_idx, moto in enumerate(motorcycles):
                if (moto.x1 - 12 <= bcx <= moto.x2 + 12) and (b_box.y2 <= moto.y2) and (b_box.y1 >= moto.y1 - moto.height * 0.95):
                    mcx = (moto.x1 + moto.x2) / 2
                    dist = abs(bcx - mcx)
                    if dist < min_dist:
                        min_dist = dist
                        best_idx = m_idx

            if best_idx is not None:
                # Check if this body already matches an assigned head on this motorcycle
                has_assigned_head = any(
                    abs((h.x1 + h.x2)/2 - bcx) < 28 and h.y1 <= b_box.y1 + (b_box.height * 0.55)
                    for h in moto_heads[best_idx]
                )
                if not has_assigned_head:
                    moto_bodies[best_idx].append(b_box)

        # 3. Build assessments for each motorcycle
        for m_idx, moto in enumerate(motorcycles):
            matched_heads = moto_heads[m_idx]
            matched_bodies = moto_bodies[m_idx]
            violating_riders = moto_violating[m_idx]
            all_riders = matched_heads + matched_bodies
            rider_count = max(len(matched_heads) + len(matched_bodies), 1 if matched_heads or matched_bodies else 0)

            is_overloaded = rider_count > cls.MAX_LEGAL_MOTO_RIDERS
            has_helmet_violation = len(violating_riders) > 0
            violations = []

            if is_overloaded:
                violations.append(
                    f"OVERLOADING: {rider_count} persons on motorcycle (legal limit: {cls.MAX_LEGAL_MOTO_RIDERS})"
                )
            if has_helmet_violation:
                violations.append(
                    f"NO_HELMET: {len(violating_riders)} rider(s) without helmet detected"
                )

            assessments.append(
                MotorcycleSafetyAssessment(
                    motorcycle_id=moto.track_id,
                    motorcycle_box=moto,
                    rider_count=rider_count,
                    riders=all_riders if all_riders else [moto],
                    is_overloaded=is_overloaded,
                    has_helmet_violation=has_helmet_violation,
                    violating_riders=violating_riders,
                    violations=violations,
                )
            )

        return assessments

    @staticmethod
    def point_inside_polygon(point: Tuple[int, int], polygon: List[Tuple[int, int]]) -> bool:
        """Ray-casting algorithm to test if a point is inside a polygon."""
        x, y = point
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    @classmethod
    def check_red_light_running(
        cls,
        vehicle: DetectionBox,
        traffic_light_state: str,
        stop_line_roi: List[Tuple[int, int]],
    ) -> bool:
        """
        Flag vehicle crossing the stop line when the light is RED.
        traffic_light_state: 'red', 'yellow', or 'green'
        stop_line_roi: list of (x, y) vertices defining the violation zone behind the stop line.
        """
        if traffic_light_state.lower() != "red":
            return False

        contact_point = vehicle.bottom_center
        return cls.point_inside_polygon(contact_point, stop_line_roi)

    @classmethod
    def check_wrong_way(
        cls,
        trajectory: List[Tuple[int, int]],
        allowed_vector: Tuple[float, float],
        min_distance_px: float = 30.0,
    ) -> bool:
        """
        Detects if vehicle moves opposite to allowed lane direction.
        trajectory: historical (x, y) centers from ByteTrack
        allowed_vector: normalized (dx, dy) direction of traffic flow
        """
        if len(trajectory) < 4:
            return False

        start_pt = trajectory[0]
        end_pt = trajectory[-1]
        dx = end_pt[0] - start_pt[0]
        dy = end_pt[1] - start_pt[1]
        dist = math.hypot(dx, dy)

        if dist < min_distance_px:
            return False  # Stationary or minimal jitter

        # Normalized movement vector
        move_x = dx / dist
        move_y = dy / dist

        # Dot product: cos(theta)
        dot_product = (move_x * allowed_vector[0]) + (move_y * allowed_vector[1])

        # If dot product is strongly negative (cos > 120 degrees opposite), vehicle is going wrong way
        return dot_product < -0.5

