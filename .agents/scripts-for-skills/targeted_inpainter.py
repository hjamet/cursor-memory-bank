#!/usr/bin/env python3
"""
targeted_inpainter.py — Outil Canonique d'In-Painting Ciblé avec Double Garde-Fou Mathématique
Conçu pour le skill image-retoucher d'Antigravity.

Workflow :
1. Extraction chirurgicale d'une sous-zone d'intérêt (crop contextuel) avec marge paramétrable en pixels ou en ratio.
2. In-painting génératif haute fidélité (generate_image avec prompt diff-only et sanctuarisation des bords).
3. Double Contrôle Qualité Bloquant lors du blend :
   a. Contrôle 1 : Sanctuarisation des bords périphériques (MAE <= 12.75 soit dérive <= 5.0% sur l'anneau extérieur).
   b. Contrôle 2 : Calculateur mathématique de style sans réseau de neurones (D_style <= 5.0% combinant
      Moments CIELAB, Analyse Texturale GLCM/Gradients et Analyse Fréquentielle 2D FFT).
4. Réintégration continue dans l'image originale avec masque de dégradé transparent périphérique (feathering cosinus 40-50 px)
   garantissant zéro raccord visible, continuité parfaite et préservation intégrale du reste de l'image.
"""

import argparse
import sys
from pathlib import Path
import cv2
import numpy as np

# Configuration de l'encodage console UTF-8 sur Windows
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass


def imread_unicode(path: Path | str, flags: int = cv2.IMREAD_COLOR) -> np.ndarray:
    """Lecture d'image compatible avec les chemins Unicode sur Windows."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Image introuvable : {p}")
    data = np.fromfile(str(p), dtype=np.uint8)
    img = cv2.imdecode(data, flags)
    if img is None:
        raise ValueError(f"Impossible de décoder l'image : {p}")
    return img


def imwrite_unicode(path: Path | str, img: np.ndarray, quality: int = 98) -> bool:
    """Écriture d'image compatible avec les chemins Unicode sur Windows."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ext = p.suffix.lower()
    if ext in [".jpg", ".jpeg"]:
        params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    elif ext == ".png":
        params = [int(cv2.IMWRITE_PNG_COMPRESSION), 3]
    else:
        params = []
    success, enc = cv2.imencode(ext if ext else ".jpg", img, params)
    if success:
        enc.tofile(str(p))
        return True
    return False


# =============================================================================
# CALCULATEUR MATHÉMATIQUE DE STYLE (SANS RÉSEAU DE NEURONES)
# =============================================================================

def compute_color_moments(img_bgr: np.ndarray) -> np.ndarray:
    """
    Calcule les 3 premiers moments statistiques (Moyenne, Écart-type, Skewness)
    pour chaque canal de l'espace colorimétrique CIELAB (L, a, b).
    Retourne un vecteur 1D de 9 descripteurs : [mu_L, sigma_L, skew_L, mu_a, sigma_a, skew_a, mu_b, sigma_b, skew_b].
    """
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float64)
    moments = []
    eps = 1e-7
    for c in range(3):
        channel = lab[:, :, c]
        mu = np.mean(channel)
        sigma = np.std(channel)
        m3 = np.mean((channel - mu) ** 3)
        skewness = m3 / ((sigma ** 3) + eps)
        moments.extend([mu, sigma, skewness])
    return np.array(moments, dtype=np.float64)


def compute_color_distance(moments_base: np.ndarray, moments_gen: np.ndarray) -> float:
    """
    Calcule la divergence de palette/couleur normalisée en pourcentage [0.0, 100.0].
    Pondération : Moyenne (50%), Écart-type (30%), Skewness (20%) sur L, a, b.
    """
    diffs = []
    w_mu, w_sig, w_sk = 0.50, 0.30, 0.20
    for c_idx in range(3):
        b_mu, b_sig, b_sk = moments_base[c_idx * 3 : c_idx * 3 + 3]
        g_mu, g_sig, g_sk = moments_gen[c_idx * 3 : c_idx * 3 + 3]

        d_mu = abs(b_mu - g_mu) / 255.0
        d_sig = abs(b_sig - g_sig) / 128.0
        d_sk = min(1.0, abs(b_sk - g_sk) / 6.0)

        d_channel = w_mu * d_mu + w_sig * d_sig + w_sk * d_sk
        diffs.append(d_channel)

    return float(np.mean(diffs)) * 100.0


def compute_glcm_features(gray: np.ndarray) -> tuple[float, float, float]:
    """
    Calcule la matrice de cooccurrence de niveaux de gris (GLCM) quantifiée à 16 niveaux
    sur 4 directions (horizontal, vertical, diagonales) et extrait :
    - Contraste : sum |i-j|^2 p(i, j)
    - Énergie : sum p(i, j)^2
    - Homogénéité : sum p(i, j) / (1 + |i-j|)
    """
    q = (gray // 16).clip(0, 15).astype(np.int32)
    pairs = [
        (q[:, :-1].ravel(), q[:, 1:].ravel()),
        (q[:-1, :].ravel(), q[1:, :].ravel()),
        (q[:-1, :-1].ravel(), q[1:, 1:].ravel()),
        (q[:-1, 1:].ravel(), q[1:, :-1].ravel()),
    ]
    p1 = np.concatenate([p[0] for p in pairs])
    p2 = np.concatenate([p[1] for p in pairs])
    indices = p1 * 16 + p2
    counts = np.bincount(indices, minlength=256).reshape((16, 16)).astype(np.float64)
    counts = counts + counts.T
    total = np.sum(counts)
    if total > 0:
        glcm = counts / total
    else:
        glcm = np.zeros((16, 16), dtype=np.float64)

    i_coords, j_coords = np.indices((16, 16))
    diff = np.abs(i_coords - j_coords)

    contrast = float(np.sum((diff ** 2) * glcm))
    energy = float(np.sum(glcm ** 2))
    homogeneity = float(np.sum(glcm / (1.0 + diff)))
    return contrast, energy, homogeneity


def compute_texture_features(img_bgr: np.ndarray) -> dict[str, float]:
    """
    Extrait les descripteurs de texture combinant GLCM et gradients locaux Sobel/Laplacien.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    contrast, energy, homogeneity = compute_glcm_features(gray)

    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    g_mag = np.sqrt(gx ** 2 + gy ** 2)
    grad_mean = float(np.mean(g_mag))
    grad_std = float(np.std(g_mag))

    lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=3)
    lap_var = float(np.var(lap))

    return {
        "contrast": contrast,
        "energy": energy,
        "homogeneity": homogeneity,
        "grad_mean": grad_mean,
        "grad_std": grad_std,
        "lap_var": lap_var,
    }


def compute_texture_distance(
    t_base: dict[str, float], t_gen: dict[str, float]
) -> float:
    """
    Calcule la divergence texturale et de grain en pourcentage [0.0, 100.0].
    """
    # 1. Différences GLCM (Contraste, Énergie, Homogénéité)
    d_cont = abs(t_base["contrast"] - t_gen["contrast"]) / max(
        t_base["contrast"] + t_gen["contrast"], 0.1
    )
    d_energy = abs(t_base["energy"] - t_gen["energy"]) / max(
        t_base["energy"] + t_gen["energy"], 0.001
    )
    d_homog = abs(t_base["homogeneity"] - t_gen["homogeneity"]) / max(
        t_base["homogeneity"] + t_gen["homogeneity"], 0.01
    )
    d_glcm = (d_cont + d_energy + d_homog) / 3.0

    # 2. Différences de gradients locaux et rugosité (Sobel & Laplacien)
    d_gmean = abs(t_base["grad_mean"] - t_gen["grad_mean"]) / max(
        t_base["grad_mean"] + t_gen["grad_mean"], 1.0
    )
    d_gstd = abs(t_base["grad_std"] - t_gen["grad_std"]) / max(
        t_base["grad_std"] + t_gen["grad_std"], 1.0
    )
    d_lap = abs(t_base["lap_var"] - t_gen["lap_var"]) / max(
        t_base["lap_var"] + t_gen["lap_var"], 100.0
    )
    d_grad = (d_gmean + d_gstd + d_lap) / 3.0

    d_tex = 0.5 * d_glcm + 0.5 * d_grad
    return min(100.0, max(0.0, float(d_tex * 100.0)))


def compute_fft_features(img_bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcule le spectre de magnitude 2D FFT logarithmique log(1 + |FFT2(I)|)
    et extrait la distribution d'énergie en 3 bandes radiales (Basses, Moyennes, Hautes fréquences)
    ainsi que le profil radial moyen.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    f = np.fft.fft2(gray.astype(np.float64))
    fshift = np.fft.fftshift(f)
    mag = np.log1p(np.abs(fshift))

    cy, cx = h / 2.0, w / 2.0
    y_idx, x_idx = np.ogrid[:h, :w]
    max_r = np.sqrt(cy ** 2 + cx ** 2)
    r = np.sqrt((y_idx - cy) ** 2 + (x_idx - cx) ** 2) / max_r

    band_low = r < 0.15
    band_mid = (r >= 0.15) & (r < 0.50)
    band_high = r >= 0.50

    sum_total = np.sum(mag) + 1e-7
    e_low = np.sum(mag[band_low]) / sum_total
    e_mid = np.sum(mag[band_mid]) / sum_total
    e_high = np.sum(mag[band_high]) / sum_total
    band_dist = np.array([e_low, e_mid, e_high], dtype=np.float64)

    num_bins = 20
    bin_edges = np.linspace(0.0, 1.0, num_bins + 1)
    radial_profile = np.zeros(num_bins, dtype=np.float64)
    for k in range(num_bins):
        mask = (r >= bin_edges[k]) & (r < bin_edges[k + 1])
        if np.any(mask):
            radial_profile[k] = np.mean(mag[mask])
    profile_norm = radial_profile / (np.sum(radial_profile) + 1e-7)
    return band_dist, profile_norm


def compute_fft_distance(
    fft_base: tuple[np.ndarray, np.ndarray], fft_gen: tuple[np.ndarray, np.ndarray]
) -> float:
    """
    Calcule la divergence fréquentielle (grain/finesse vs aplats lisses) en pourcentage [0.0, 100.0].
    """
    bands_b, prof_b = fft_base
    bands_g, prof_g = fft_gen

    d_bands = 0.5 * np.sum(np.abs(bands_b - bands_g))
    d_prof = 0.5 * np.sum(np.abs(prof_b - prof_g))

    d_fft = (0.5 * d_bands + 0.5 * d_prof) * 100.0
    return min(100.0, max(0.0, float(d_fft)))


def evaluate_style_divergence(
    img_base: np.ndarray, img_gen: np.ndarray
) -> tuple[float, float, float, float]:
    """
    Analyse stylistique mathématique sans réseau de neurones :
    - Moments de couleur CIELAB (35%)
    - Analyse texturale GLCM & Gradients locaux (35%)
    - Analyse fréquentielle 2D FFT (30%)
    Retourne (D_style, D_color, D_texture, D_fft) en pourcentages [0.0, 100.0].
    """
    # 1. Moments CIELAB
    mb = compute_color_moments(img_base)
    mg = compute_color_moments(img_gen)
    color_diff = compute_color_distance(mb, mg)

    # 2. Texture GLCM & Gradients
    tb = compute_texture_features(img_base)
    tg = compute_texture_features(img_gen)
    texture_diff = compute_texture_distance(tb, tg)

    # 3. FFT 2D
    fb = compute_fft_features(img_base)
    fg = compute_fft_features(img_gen)
    fft_diff = compute_fft_distance(fb, fg)

    # Score global pondéré
    style_diff_pct = 0.35 * color_diff + 0.35 * texture_diff + 0.30 * fft_diff
    return style_diff_pct, color_diff, texture_diff, fft_diff


# =============================================================================
# PIPELINE DE CROPPING ET DE FUSION AVEC DOUBLE GARDE-FOU
# =============================================================================

def compute_effective_bbox(
    img_h: int,
    img_w: int,
    bbox: tuple[int, int, int, int],
    margin: float = 0.0,
) -> tuple[int, int, int, int]:
    """
    Calcule la bounding box effective avec marge contextuelle.
    - Si margin >= 1.0 : interprété en pixels (ex: margin=100 -> 100 px sur chaque bord).
    - Si 0.0 < margin < 1.0 : interprété en ratio (ex: margin=0.2 -> 20% de la largeur/hauteur).
    - Si margin == 0.0 : aucune marge supplémentaire.
    """
    x1, y1, x2, y2 = bbox
    box_w = max(1, x2 - x1)
    box_h = max(1, y2 - y1)

    if margin >= 1.0:
        m_x = int(margin)
        m_y = int(margin)
    elif margin > 0.0:
        m_x = int(box_w * margin)
        m_y = int(box_h * margin)
    else:
        m_x = 0
        m_y = 0

    x1_eff = max(0, x1 - m_x)
    y1_eff = max(0, y1 - m_y)
    x2_eff = min(img_w, x2 + m_x)
    y2_eff = min(img_h, y2 + m_y)

    return (x1_eff, y1_eff, x2_eff, y2_eff)


def crop_region(
    image_path: str,
    bbox: tuple[int, int, int, int],
    output_crop_path: str,
    margin: float = 0.0,
) -> tuple[int, int, int, int]:
    """
    Extrait une zone rectangulaire (x1, y1, x2, y2) avec marge contextuelle optionnelle.
    Retourne la bounding box effective (x1_eff, y1_eff, x2_eff, y2_eff).
    """
    img = imread_unicode(image_path)
    h, w = img.shape[:2]
    eff_bbox = compute_effective_bbox(h, w, bbox, margin=margin)
    x1_eff, y1_eff, x2_eff, y2_eff = eff_bbox

    crop = img[y1_eff:y2_eff, x1_eff:x2_eff]
    imwrite_unicode(output_crop_path, crop, 98)
    return eff_bbox


def create_feather_mask(
    crop_h: int,
    crop_w: int,
    feather_px: int,
    mask_shape: str = "rectangle",
    touch_borders: tuple[bool, bool, bool, bool] = (False, False, False, False),
) -> np.ndarray:
    """
    Génère un masque 2D flottant (0.0 sur les bords extérieurs, 1.0 au cœur)
    avec transition douce (dégradé transparent périphérique / feathering cosinus).
    touch_borders: (left, top, right, bottom) indiquant si le bord touche le bord du canvas de base.
    """
    mask = np.ones((crop_h, crop_w), dtype=np.float32)

    if mask_shape == "ellipse":
        center_x = crop_w // 2
        center_y = crop_h // 2
        radius_x = max(1, center_x - feather_px)
        radius_y = max(1, center_y - feather_px)
        raw_mask = np.zeros((crop_h, crop_w), dtype=np.float32)
        cv2.ellipse(
            raw_mask,
            (center_x, center_y),
            (radius_x, radius_y),
            0,
            0,
            360,
            1.0,
            -1,
        )
        mask = cv2.GaussianBlur(
            raw_mask, (feather_px * 2 + 1, feather_px * 2 + 1), 0
        )
        return mask

    # Dégradé linéaire / cosinus sur les bords
    feather_x = min(feather_px, crop_w // 2)
    feather_y = min(feather_px, crop_h // 2)

    touch_left, touch_top, touch_right, touch_bottom = touch_borders

    # Axe X (gauche et droite)
    if feather_x > 0:
        for x in range(feather_x):
            factor = 0.5 * (1.0 - np.cos(np.pi * x / feather_x))
            if not touch_left:
                mask[:, x] *= factor
            if not touch_right:
                mask[:, crop_w - 1 - x] *= factor

    # Axe Y (haut et bas)
    if feather_y > 0:
        for y in range(feather_y):
            factor = 0.5 * (1.0 - np.cos(np.pi * y / feather_y))
            if not touch_top:
                mask[y, :] *= factor
            if not touch_bottom:
                mask[crop_h - 1 - y, :] *= factor

    return mask


def blend_back_crop(
    base_image_path: str,
    generated_crop_path: str,
    bbox: tuple[int, int, int, int],
    output_image_path: str,
    margin: float = 0.0,
    feather_px: int = 45,
    mask_shape: str = "rectangle",
    max_style_pct: float = 5.0,
    max_border_pct: float = 5.0,
) -> None:
    """
    Réintègre le crop généré dans l'image de base avec transition alpha douce cosinus
    et double vérification médico-légale bloquante :
    1. Sanctuarisation des bords périphériques (MAE <= 12.75 / 255 soit <= 5.0%).
    2. Fidélité stylistique mathématique globale (D_style <= 5.0%).
    """
    base = imread_unicode(base_image_path)
    gen = imread_unicode(generated_crop_path)

    h_base, w_base = base.shape[:2]
    x1, y1, x2, y2 = compute_effective_bbox(h_base, w_base, bbox, margin=margin)

    target_w = x2 - x1
    target_h = y2 - y1

    if target_w <= 0 or target_h <= 0:
        raise ValueError(f"Dimensions de cible invalides : {target_w}x{target_h}")

    # Redimensionnement haute fidélité du crop généré aux dimensions cibles
    if gen.shape[:2] != (target_h, target_w):
        gen = cv2.resize(
            gen, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4
        )

    base_patch = base[y1:y2, x1:x2]

    # Détection des bords touchant les limites du canvas de base
    touch_borders = (x1 == 0, y1 == 0, x2 == w_base, y2 == h_base)

    # Masque de dégradé transparent
    alpha = create_feather_mask(
        target_h, target_w, feather_px, mask_shape=mask_shape, touch_borders=touch_borders
    )

    # -------------------------------------------------------------------------
    # GARDE-FOU 1 : VÉRIFICATION DE SANCTUARISATION DES BORDS (SEUIL <= 5.0%)
    # -------------------------------------------------------------------------
    outer_band = (alpha > 0.001) & (alpha < 0.25)
    if np.count_nonzero(outer_band) >= 20:
        border_diff = np.abs(base_patch.astype(np.float32) - gen.astype(np.float32))
        border_mae = float(np.mean(border_diff[outer_band]))
        border_pct = (border_mae / 255.0) * 100.0
        print(f"[*] Diagnostic de bordure : Écart moyen sur l'anneau périphérique = {border_mae:.2f}/255 ({border_pct:.1f}%)")

        if border_pct > max_border_pct:
            error_msg = (
                f"\n❌ ERREUR DE SANCTUARISATION DES BORDS (> {max_border_pct:.1f}%) :\n"
                f"Le modèle de génération a altéré les bords extérieurs du crop (Écart moyen = {border_mae:.2f} / 255, soit {border_pct:.1f}% > {max_border_pct:.1f}%).\n"
                f"L'image générée ne peut pas être réintégrée car le raccord sera visible.\n"
                f"👉 CONSIGNES POUR L'AGENT :\n"
                f"Relancez generate_image sur l'image croppée en ordonnant de modifier UNIQUEMENT le centre et de sanctuariser les 4 bordures à 100% à l'identique."
            )
            print(error_msg, file=sys.stderr)
            raise ValueError(error_msg)

    # -------------------------------------------------------------------------
    # GARDE-FOU 2 : VÉRIFICATION DE FIDÉLITÉ STYLISTIQUE MATHÉMATIQUE (SEUIL <= 5.0%)
    # -------------------------------------------------------------------------
    style_diff_pct, color_diff, texture_diff, fft_diff = evaluate_style_divergence(
        base_patch, gen
    )
    print(
        f"[*] Diagnostic stylistique : Divergence globale = {style_diff_pct:.1f}% "
        f"(Palette/Couleur = {color_diff:.1f}%, Grain/Texture = {texture_diff:.1f}%, Profil Fréquentiel FFT = {fft_diff:.1f}%)"
    )

    if style_diff_pct > max_style_pct:
        error_msg = (
            f"\n❌ ERREUR DE FIDÉLITÉ STYLISTIQUE (> {max_style_pct:.1f}%) :\n"
            f"Le modèle de génération a trop changé le style de l'image originale (Divergence stylistique globale = {style_diff_pct:.1f}% > {max_style_pct:.1f}%).\n"
            f"Détail : Palette/Couleur = {color_diff:.1f}%, Grain/Texture = {texture_diff:.1f}%, Profil Fréquentiel FFT = {fft_diff:.1f}%.\n"
            f"L'insertion est rejetée car le style généré dévie du rendu artistique original.\n"
            f"👉 CONSIGNES POUR L'AGENT :\n"
            f"Relancez generate_image sur l'image croppée avec des consignes stylistiques renforcées (imiter fidèlement le grain de papier, la palette d'aquarelle/encre, éviter les aplats lisses ou le rendu immaculé/CGI, enrichir les détails organiques)."
        )
        print(error_msg, file=sys.stderr)
        raise ValueError(error_msg)

    # -------------------------------------------------------------------------
    # FUSION ALPHA TRANSPARENTE
    # -------------------------------------------------------------------------
    alpha_3d = np.repeat(alpha[:, :, np.newaxis], 3, axis=2)
    base_patch_f = base_patch.astype(np.float32)
    gen_patch_f = gen.astype(np.float32)
    blended_patch = (gen_patch_f * alpha_3d + base_patch_f * (1.0 - alpha_3d)).astype(
        np.uint8
    )

    result = base.copy()
    result[y1:y2, x1:x2] = blended_patch

    imwrite_unicode(output_image_path, result, 98)
    print(
        f"[OK] Image fusionnée avec succès : {output_image_path} "
        f"(BBox: {x1} {y1} {x2} {y2}, Feather: {feather_px}px, Style diff: {style_diff_pct:.1f}%)"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Targeted In-Painter: Crop & Seamless Alpha-Blender with Style & Border Guardrails (Skill image-retoucher)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Commande crop
    crop_parser = subparsers.add_parser("crop", help="Extraire une sous-zone avec marge contextuelle")
    crop_parser.add_argument("--base", required=True, help="Chemin de l'image source brute")
    crop_parser.add_argument(
        "--bbox",
        required=True,
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="Coordonnées de découpe de la zone d'intérêt (X1 Y1 X2 Y2)",
    )
    crop_parser.add_argument(
        "--out", required=True, help="Chemin du crop résultant"
    )
    crop_parser.add_argument(
        "--margin",
        type=float,
        default=0.0,
        help="Marge contextuelle supplémentaire : pixels si >= 1.0 (ex: 100), ou ratio si < 1.0 (ex: 0.20)",
    )

    # Commande blend
    blend_parser = subparsers.add_parser(
        "blend", help="Réintégrer le crop généré avec dégradé transparent sans raccord et double contrôle"
    )
    blend_parser.add_argument("--base", required=True, help="Chemin de l'image source brute")
    blend_parser.add_argument(
        "--gen", required=True, help="Chemin du crop généré à réinsérer"
    )
    blend_parser.add_argument(
        "--bbox",
        required=True,
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="Coordonnées d'insertion (X1 Y1 X2 Y2)",
    )
    blend_parser.add_argument(
        "--out", required=True, help="Chemin de l'image finale résultante"
    )
    blend_parser.add_argument(
        "--margin",
        type=float,
        default=0.0,
        help="Marge contextuelle appliquée si bbox est la bbox originale (pixels si >= 1.0, ratio si < 1.0)",
    )
    blend_parser.add_argument(
        "--feather",
        type=int,
        default=45,
        help="Rayon d'adoucissement du dégradé transparent en pixels (défaut: 45)",
    )
    blend_parser.add_argument(
        "--shape",
        choices=["rectangle", "ellipse"],
        default="rectangle",
        help="Forme du masque de transition (défaut: rectangle)",
    )
    blend_parser.add_argument(
        "--max-style",
        type=float,
        default=5.0,
        help="Seuil maximal de divergence stylistique en %% (défaut: 5.0)",
    )
    blend_parser.add_argument(
        "--max-border",
        type=float,
        default=5.0,
        help="Seuil maximal de dérive sur les bords en %% (défaut: 5.0)",
    )

    # Commande style (évaluation stylistique autonome)
    style_parser = subparsers.add_parser(
        "style", help="Évaluer la divergence stylistique mathématique entre deux images ou zones"
    )
    style_parser.add_argument("--base", required=True, help="Chemin de l'image ou du patch de référence")
    style_parser.add_argument("--gen", required=True, help="Chemin de l'image ou du patch généré à tester")
    style_parser.add_argument(
        "--bbox",
        nargs=4,
        type=int,
        default=None,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="Zone optionnelle à découper dans l'image de base (X1 Y1 X2 Y2)",
    )
    style_parser.add_argument(
        "--margin",
        type=float,
        default=0.0,
        help="Marge contextuelle si --bbox est spécifié",
    )
    style_parser.add_argument(
        "--max-style",
        type=float,
        default=5.0,
        help="Seuil maximal de divergence stylistique en %% (défaut: 5.0)",
    )

    args = parser.parse_args()

    if args.command == "crop":
        eff_bbox = crop_region(
            args.base, tuple(args.bbox), args.out, margin=args.margin
        )
        print(
            f"[OK] Crop extrait dans {args.out} (BBox d'origine: {' '.join(map(str, args.bbox))}, BBox effective: {eff_bbox[0]} {eff_bbox[1]} {eff_bbox[2]} {eff_bbox[3]})"
        )
    elif args.command == "blend":
        blend_back_crop(
            base_image_path=args.base,
            generated_crop_path=args.gen,
            bbox=tuple(args.bbox),
            output_image_path=args.out,
            margin=args.margin,
            feather_px=args.feather,
            mask_shape=args.shape,
            max_style_pct=args.max_style,
            max_border_pct=args.max_border,
        )
    elif args.command == "style":
        img_b = imread_unicode(args.base)
        img_g = imread_unicode(args.gen)
        if args.bbox:
            h_b, w_b = img_b.shape[:2]
            x1, y1, x2, y2 = compute_effective_bbox(h_b, w_b, tuple(args.bbox), margin=args.margin)
            img_b = img_b[y1:y2, x1:x2]
        if img_b.shape[:2] != img_g.shape[:2]:
            img_g = cv2.resize(img_g, (img_b.shape[1], img_b.shape[0]), interpolation=cv2.INTER_LANCZOS4)

        max_style = args.max_style
        s_pct, c_pct, t_pct, f_pct = evaluate_style_divergence(img_b, img_g)
        status = f"✅ CONFORME (<= {max_style:.1f}%)" if s_pct <= max_style else f"❌ NON-CONFORME (> {max_style:.1f}%)"
        print(f"[{status}] Divergence stylistique globale : {s_pct:.2f}%")
        print(f"  - Palette / Couleur (Moments CIELAB) : {c_pct:.2f}%")
        print(f"  - Grain / Texture (GLCM & Gradients) : {t_pct:.2f}%")
        print(f"  - Profil Fréquentiel (FFT 2D)         : {f_pct:.2f}%")
        if s_pct > max_style:
            sys.exit(1)


if __name__ == "__main__":
    main()
