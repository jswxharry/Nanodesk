"""Create a simple icon for Nanodesk Desktop."""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont

    def create_icon():
        """Create a simple turtle icon."""
        sizes = [16, 32, 48, 64, 128, 256]
        images = []

        for size in sizes:
            # Create image with transparent background
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Draw a simple turtle shell (green circle)
            margin = size // 8
            draw.ellipse(
                [margin, margin, size - margin, size - margin],
                fill=(76, 175, 80, 255),  # Green
                outline=(56, 142, 60, 255),
                width=max(1, size // 32),
            )

            # Draw head (smaller circle on top)
            head_size = size // 4
            head_y = margin // 2
            draw.ellipse(
                [
                    size // 2 - head_size // 2,
                    head_y,
                    size // 2 + head_size // 2,
                    head_y + head_size,
                ],
                fill=(129, 199, 132, 255),
                outline=(56, 142, 60, 255),
                width=max(1, size // 32),
            )

            # Draw legs (4 small circles)
            leg_size = size // 6
            leg_positions = [
                (margin, size // 2 - leg_size // 2),  # left
                (size - margin - leg_size, size // 2 - leg_size // 2),  # right
                (size // 2 - leg_size // 2, margin),  # top
                (size // 2 - leg_size // 2, size - margin - leg_size),  # bottom
            ]
            for x, y in leg_positions:
                draw.ellipse(
                    [x, y, x + leg_size, y + leg_size],
                    fill=(129, 199, 132, 255),
                    outline=(56, 142, 60, 255),
                    width=max(1, size // 32),
                )

            images.append(img)

        # Save as ICO
        icon_path = Path(__file__).parent / "icons" / "logo.ico"
        icon_path.parent.mkdir(parents=True, exist_ok=True)

        images[0].save(
            icon_path, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:]
        )

        print(f"Icon created: {icon_path}")
        return icon_path

    if __name__ == "__main__":
        create_icon()

except ImportError:
    print("PIL not installed. Run: pip install Pillow")
    print("Or manually place an icon at: nanodesk/desktop/resources/icons/logo.ico")
