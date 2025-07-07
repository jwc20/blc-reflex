import reflex as rx
from typing import List
from blc import Blc

# Plate color configurations
PLATE_COLORS = {
    25: "#FF0000",  # Red
    20: "#0000FF",  # Blue
    15: "#FFFF00",  # Yellow
    10: "#00FF00",  # Green
    5: "#FFFFFF",  # White
    2.5: "#FF0000",  # Red
    2: "#0000FF",  # Blue
    1.5: "#FFFF00",  # Yellow
    1: "#00FF00",  # Green
    0.5: "#FFFFFF"  # White
}

PLATE_CONFIGS = {
    25: {"width": 64, "height": 450, "weight": 25, "xi": 546, "yi": 45, "color": "#FF0000"},
    20: {"width": 54, "height": 450, "weight": 20, "xi": 610, "yi": 45, "color": "#0000FF"},
    15: {"width": 42, "height": 450, "weight": 15, "xi": 664, "yi": 45, "color": "#FFFF00"},
    10: {"width": 34, "height": 450, "weight": 10, "xi": 706, "yi": 45, "color": "#00FF00"},
    5: {"width": 26.5, "height": 230, "weight": 5, "xi": 740, "yi": 156, "color": "#FFFFFF"},
    2.5: {"width": 19, "height": 190, "weight": 2.5, "xi": 767, "yi": 165, "color": "#FF0000"},
    2: {"width": 19, "height": 190, "weight": 2, "xi": 786, "yi": 176, "color": "#0000FF"},
    1.5: {"width": 18, "height": 175, "weight": 1.5, "xi": 805, "yi": 183, "color": "#FFFF00"},
    1: {"width": 15, "height": 160, "weight": 1, "xi": 823, "yi": 190, "color": "#00FF00"},
    0.5: {"width": 13, "height": 135, "weight": 0.5, "xi": 838, "yi": 204, "color": "#FFFFFF"}
}

COLLAR_CONFIG = {"width": 77, "height": 101, "weight": 2.5, "xi": 851, "yi": 220, "color": "#808080"}
BARBELL_CONFIG = {"bar_weight": 20, "sleeve_length": 415, "xi": 66, "yi": 171}


class State(rx.State):
    target_weight: str = "20"
    plates_needed: List[float] = []
    barbell_type: str = "men"
    use_collar: bool = False
    error_message: str = ""

    @rx.var
    def barbell_weight(self) -> int:
        return 15 if self.barbell_type == "women" else 20

    @rx.var
    def total_plates_needed(self) -> int:
        return len(self.plates_needed) * 2

    @rx.var
    def plates_display(self) -> str:
        if not self.plates_needed:
            return "No plates needed"
        return ", ".join([f"{weight}kg" for weight in self.plates_needed])

    @rx.var
    def complete_svg(self) -> str:
        """Generate complete SVG as a string"""
        svg_parts = []

        # SVG opening tag
        svg_parts.append(
            '<svg viewBox="0 0 1024 768" width="1024px" height="768px" style="background: #f5f5f5; border-radius: 8px; display: block; margin: 0 auto;">')

        # shaft
        svg_parts.append('<rect x="0" y="384" width="36" height="25" fill="#666" stroke="#333" stroke-width="2"/>')
        # collar
        svg_parts.append('<rect x="35" y="346" width="32" height="101" fill="#555" stroke="#333" stroke-width="2"/>')
        # sleeve
        svg_parts.append('<rect x="66" y="371" width="415" height="51" fill="#666" stroke="#333" stroke-width="2"/>')

        # Add plates if any
        if self.plates_needed:
            # side plates
            x_left = 66
            for weight in self.plates_needed:
                color = PLATE_COLORS.get(weight, "#999")

                width, height = PLATE_CONFIGS[weight]["width"], PLATE_CONFIGS[weight]["height"]

                y_pos = 394 - height // 2

                # Plate rectangle
                svg_parts.append(
                    f'<rect x="{x_left}" y="{y_pos}" width="{width}" height="{height}" fill="{color}" stroke="#000" stroke-width="2" rx="2"/>')

                # Weight text
                text_x = x_left + width // 2
                text_y = y_pos + height // 2 + 3
                svg_parts.append(
                    f'<text x="{text_x}" y="{text_y}" text-anchor="middle" font-size="10" font-weight="bold" fill="black">{weight}</text>')

                x_left += width + 2

            # Add collars if enabled
            if self.use_collar:
                collar_x_left = x_left
                svg_parts.append(
                    f'<rect x="{collar_x_left}" y="346" width="52" height="101" fill="#404040" stroke="#000" stroke-width="2"/>')
                # svg_parts.append(
                #     f'<text x="{collar_x_left + 7}" y="346" text-anchor="middle" font-size="8" fill="black" font-weight="bold">2.5</text>')

        # Close SVG
        svg_parts.append('</svg>')

        return ''.join(svg_parts)

    def calculate_plates(self):
        try:
            weight = float(self.target_weight)
            if weight <= 0:
                self.error_message = "Please enter a positive weight"
                self.plates_needed = []
                return

            from blc import Plates, Barbell
            plates = Plates()
            barbell = Barbell(weight=20 if self.barbell_type == "men" else 15)
            blc = Blc(plates=plates, barbell=barbell)

            if blc is not None:
                try:
                    plates_result = blc.calculate_plates(weight, self.use_collar)
                    plates = []
                    for plate_weight in plates_result:
                        plates.append(plate_weight)
                    self.plates_needed = plates
                    self.error_message = ""
                    return
                except Exception as e:
                    pass

            if plates:
                self.plates_needed = plates
                self.error_message = ""
            else:
                self.error_message = "Cannot achieve exact weight with available plates"
                self.plates_needed = []

        except ValueError:
            self.error_message = "Please enter a valid number"
            self.plates_needed = []

    def set_target_weight(self, value: str):
        self.target_weight = value
        self.calculate_plates()

    def set_barbell_type(self, value: str):
        self.barbell_type = value
        self.calculate_plates()

    def toggle_collar(self):
        self.use_collar = not self.use_collar
        self.calculate_plates()


def create_plates_display() -> rx.Component:
    """Create visual display of plates using boxes"""
    return rx.cond(
        State.plates_needed.length() > 0,
        rx.vstack(
            rx.text("Plates per side:", font_weight="bold", font_size="18px"),
            rx.hstack(
                rx.foreach(
                    State.plates_needed,
                    lambda plate: rx.box(
                        rx.text(
                            f"{plate}kg",
                            color="black",
                            font_weight="bold",
                            font_size="14px"
                        ),
                        width="60px",
                        height="80px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        margin="3px",
                        border_radius="6px",
                        border="3px solid #000",
                        background_color=rx.match(
                            plate,
                            (25, PLATE_COLORS[25]),
                            (20, PLATE_COLORS[20]),
                            (15, PLATE_COLORS[15]),
                            (10, PLATE_COLORS[10]),
                            (5, PLATE_COLORS[5]),
                            (2.5, PLATE_COLORS[2.5]),
                            (2, PLATE_COLORS[2]),
                            (1.5, PLATE_COLORS[1.5]),
                            (1, PLATE_COLORS[1]),
                            PLATE_COLORS[0.5]
                        ),
                        box_shadow="2px 2px 4px rgba(0,0,0,0.3)"
                    )
                ),
                spacing="1",
                justify="center",
                wrap="wrap"
            ),
            spacing="3",
            align="center"
        ),
        rx.box(
            rx.text("Enter a weight to see plate configuration",
                    font_style="italic",
                    color="gray"),
            text_align="center"
        )
    )


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Barbell Loading Calculator", size="7", text_align="center"),

            # Input controls
            rx.card(
                rx.hstack(
                    rx.vstack(
                        rx.text("Target Weight (kg):", font_weight="bold"),
                        rx.input(
                            placeholder="Enter weight...",
                            value=State.target_weight,
                            on_change=State.set_target_weight,
                            width="150px",
                            type="number"
                        ),
                        spacing="1",
                        align="start"
                    ),
                    rx.vstack(
                        rx.text("Barbell Type:", font_weight="bold"),
                        rx.select(
                            ["men", "women"],
                            value=State.barbell_type,
                            on_change=State.set_barbell_type,
                            width="150px"
                        ),
                        spacing="1",
                        align="start"
                    ),
                    rx.vstack(
                        rx.text("Use Collar (+2.5kg):", font_weight="bold"),
                        rx.checkbox(
                            checked=State.use_collar,
                            on_change=State.toggle_collar,
                            size="3"
                        ),
                        spacing="1",
                        align="start"
                    ),
                    spacing="6",
                    align="start",
                    justify="center"
                ),
                padding="2rem"
            ),

            # Error message
            rx.cond(
                State.error_message != "",
                rx.callout(
                    State.error_message,
                    icon="triangle_alert",
                    color_scheme="red",
                    size="2"
                ),
                rx.box()
            ),

            rx.card(
                rx.vstack(
                    rx.text("Barbell Visualization", font_weight="bold", font_size="20px"),
                    rx.html(State.complete_svg),
                    spacing="2",
                    align="center",
                ),
                # padding="1.5rem"
            ),

            # Plates display
            create_plates_display(),

            spacing="4",
            align="center",
            # width="100%"
        ),
        max_width="1000px",
        margin="0 auto",
        padding="2rem"
    )


app = rx.App(
    style={
        # "font_family": "Inter, system-ui, sans-serif",
        "background": "#201f24",
        "min_height": "100vh"
    }
)
app.add_page(index)
