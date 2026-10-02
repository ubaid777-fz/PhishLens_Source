"""Generate test cases and sample QR code images for PhishLens demonstrations.

Generates:
1. Sample A: Clean authentic merchant UPI payment QR (Safe).
2. Sample B: Suspicious mule/burner UPI payment QR (> 6 digits, unverified PSP).
3. Sample C: Deceptive redirect URL leading to an executable package (.apk).
4. Sample D: Simulated physical tamper sticker pasted over a merchant stand.
"""

from pathlib import Path
import cv2
import numpy as np


def generate_qr_bgr(payload: str, module_size: int = 10, quiet_zone: int = 4) -> np.ndarray:
    """Encode payload into a clean standard QR code image."""
    encoder = cv2.QRCodeEncoder.create()
    matrix = encoder.encode(payload)
    if matrix is None:
        raise ValueError(f"Failed to encode QR payload: {payload}")

    h, w = matrix.shape
    # Add quiet zone modules
    padded_matrix = cv2.copyMakeBorder(
        matrix,
        quiet_zone,
        quiet_zone,
        quiet_zone,
        quiet_zone,
        cv2.BORDER_CONSTANT,
        value=255
    )

    # Scale up with nearest-neighbor to keep sharp QR edges
    ph, pw = padded_matrix.shape
    qr_img = cv2.resize(
        padded_matrix,
        (pw * module_size, ph * module_size),
        interpolation=cv2.INTER_NEAREST
    )

    return cv2.cvtColor(qr_img, cv2.COLOR_GRAY2BGR)


def generate_merchant_stand(
    qr_bgr: np.ndarray,
    merchant_name: str = "OFFICIAL MERCHANT STAND"
) -> np.ndarray:
    """Mount QR code on a uniform acrylic merchant stand with top banner and footer."""
    qr_h, qr_w = qr_bgr.shape[:2]
    stand_w = qr_w + 180
    stand_h = qr_h + 200

    # Clean solid stand background
    stand = np.ones((stand_h, stand_w, 3), dtype=np.uint8) * 255

    # Top brand bar
    cv2.rectangle(stand, (0, 0), (stand_w, 55), (30, 24, 18), -1)
    cv2.putText(
        stand,
        merchant_name,
        (24, 36),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    # Place QR seamlessly on the stand with generous quiet zone
    y_pos = 100
    x_pos = (stand_w - qr_w) // 2
    stand[y_pos:y_pos + qr_h, x_pos:x_pos + qr_w] = qr_bgr

    # Footer note
    cv2.putText(
        stand,
        "SCAN WITH ANY UPI APP",
        (x_pos + 18, stand_h - 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (120, 120, 120),
        1,
        cv2.LINE_AA
    )

    return stand


def generate_tampered_sticker_stand(
    base_payload: str,
    sticker_payload: str
) -> np.ndarray:
    """Create a simulated physical sticker pasted over an authentic merchant stand."""
    base_qr = generate_qr_bgr(base_payload, module_size=10, quiet_zone=4)
    stand = generate_merchant_stand(base_qr, "CAMPUS COFFEE SHOP")
    stand_h, stand_w = stand.shape[:2]

    # Generate sticker QR
    encoder = cv2.QRCodeEncoder.create()
    matrix = encoder.encode(sticker_payload)
    qr_raw = cv2.resize(matrix, (matrix.shape[1] * 8, matrix.shape[0] * 8), interpolation=cv2.INTER_NEAREST)
    qr_raw_bgr = cv2.cvtColor(qr_raw, cv2.COLOR_GRAY2BGR)
    st_h, st_w = qr_raw_bgr.shape[:2]

    # Create paper sticker patch with a distinct border margin and cut seam edge
    margin = 18
    patch_w = st_w + (2 * margin)
    patch_h = st_h + (2 * margin)
    paper_patch = np.ones((patch_h, patch_w, 3), dtype=np.uint8) * 255

    # Place sticker QR inside paper patch
    paper_patch[margin:margin + st_h, margin:margin + st_w] = qr_raw_bgr

    # Physical paper border seam (raised edge and shadow line)
    cv2.rectangle(paper_patch, (0, 0), (patch_w - 1, patch_h - 1), (30, 30, 30), 2)
    cv2.rectangle(paper_patch, (1, 1), (patch_w - 2, patch_h - 2), (180, 180, 180), 1)

    # Paste paper sticker over center QR area
    paste_y = 110
    paste_x = (stand_w - patch_w) // 2

    stand[paste_y:paste_y + patch_h, paste_x:paste_x + patch_w] = paper_patch

    return stand


def main():
    output_dir = Path(__file__).resolve().parent / "test_samples"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating PhishLens demo test cases in:", output_dir)

    # --- Sample A: Clean Authentic UPI ---
    payload_a = "upi://pay?pa=merchant@okaxis&pn=CampusStore&am=50"
    stand_a = generate_merchant_stand(
        generate_qr_bgr(payload_a, module_size=10),
        "CAMPUS STORE - VERIFIED STAND"
    )
    path_a = output_dir / "sample_a_clean_upi.png"
    cv2.imwrite(str(path_a), stand_a)
    print(f"[+] Saved -> {path_a.name} (Authentic UPI payment stand)")

    # --- Sample B: Suspicious Mule UPI ---
    payload_b = "upi://pay?pa=mule9847192837@custompsp&pn=QuickPay"
    stand_b = generate_merchant_stand(
        generate_qr_bgr(payload_b, module_size=10),
        "SPECIAL DISCOUNT PAYMENT"
    )
    path_b = output_dir / "sample_b_mule_upi.png"
    cv2.imwrite(str(path_b), stand_b)
    print(f"[+] Saved -> {path_b.name} (Suspicious mule UPI handle)")

    # --- Sample C: Redirect URL leading to APK ---
    payload_c = "https://httpbin.org/redirect-to?url=https%3A%2F%2Fbank-secure-update.example%2Fpatch.apk"
    stand_c = generate_merchant_stand(
        generate_qr_bgr(payload_c, module_size=10),
        "WIFI & APP UPDATE PORTAL"
    )
    path_c = output_dir / "sample_c_redirect_url.png"
    cv2.imwrite(str(path_c), stand_c)
    print(f"[+] Saved -> {path_c.name} (Redirect URL to malicious .apk)")

    # --- Sample D: Simulated Physical Sticker Tamper ---
    stand_d = generate_tampered_sticker_stand(payload_a, payload_b + "#tamper")
    path_d = output_dir / "sample_d_tampered_physical_sticker.png"
    cv2.imwrite(str(path_d), stand_d)
    print(f"[+] Saved -> {path_d.name} (Physical paper sticker pasted over stand)")

    print("
Test sample generation complete!")


if __name__ == "__main__":
    main()
